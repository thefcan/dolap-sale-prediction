"""Feature engineering pipeline for Dolap sale prediction.

Phase 9 kickoff scope:
  1. Load merged interim dataset
  2. Apply target quality flags (label window validation)
  3. Engineer core price/listing/temporal/text/categorical features
  4. Save model-ready feature matrix + metadata
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.utils.logger import get_logger, setup_logging

logger = get_logger("feature_engineer")

CONDITION_MAP = {
    "Kullanılmış": 0,
    "Az Kullanılmış": 1,
    "Yeni": 2,
    "Yeni & Etiketli": 3,
}

FLAW_KEYWORDS = ["leke", "yırtık", "bozuk", "kusur", "çizik", "hafif"]


@dataclass
class FeatureEngineerConfig:
    """Runtime configuration for feature engineering."""

    input_path: Path = Path("data/interim/merged_data.csv")
    output_path: Path = Path("data/processed/engineered_features.parquet")
    metadata_path: Path = Path("data/processed/features_metadata.json")
    features_yaml: Path = Path("configs/features.yaml")
    min_valid_window_hours: float = 168.0
    max_valid_window_hours: float = 192.0


class FeatureEngineer:
    """Build model-ready features from merged interim data."""

    def __init__(self, config: FeatureEngineerConfig | None = None):
        self.config = config or FeatureEngineerConfig()
        self._features_config = self._load_features_yaml(self.config.features_yaml)

    @staticmethod
    def _load_features_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            logger.warning(f"Feature config not found: {path} (using defaults)")
            return {}
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def load(self) -> pd.DataFrame:
        """Load merged dataset from CSV or parquet."""
        input_path = self.config.input_path
        if not input_path.exists():
            raise FileNotFoundError(f"Input dataset not found: {input_path}")

        if input_path.suffix.lower() == ".parquet":
            df = pd.read_parquet(input_path)
        else:
            df = pd.read_csv(input_path)

        logger.info(f"Loaded input dataset: {input_path} ({len(df)} rows)")
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering and return a model-ready DataFrame."""
        df = df.copy()

        df = self._normalise_schema(df)
        df = self._parse_datetimes(df)
        df = self._coerce_target(df)
        df = self._add_label_window_flags(df)

        df = self.engineer_price_features(df)
        df = self.engineer_listing_features(df)
        df = self.engineer_temporal_features(df)
        df = self.engineer_text_features(df)
        df = self.engineer_categorical_features(df)

        df["exclude_from_training"] = (
            df["target_missing"]
            | df["invalid_early_label"]
            | df["invalid_late_label"]
            | df["target_not_binary"]
        )

        feature_df = self._select_output_columns(df)
        logger.info(f"Feature engineering complete: {len(feature_df)} rows")
        return feature_df

    @staticmethod
    def _normalise_schema(df: pd.DataFrame) -> pd.DataFrame:
        defaults: dict[str, Any] = {
            "listing_id": "",
            "cohort_id": "",
            "price": np.nan,
            "category": "Bilinmiyor",
            "brand": "Bilinmiyor",
            "brand_clean": "Bilinmiyor",
            "condition": "Bilinmiyor",
            "has_discount": False,
            "shipping_buyer_pays": False,
            "seller_username": "unknown_seller",
            "photo_count": 0,
            "description_length": 0,
            "description_word_count": 0,
            "description_text": "",
            "desc_is_placeholder": False,
            "seller_rating_count": 0,
            "seller_listing_count": 0,
            "like_count": 0,
            "comment_count": 0,
            "sold_within_7_days": np.nan,
            "scraped_at": pd.NaT,
            "labeled_at": pd.NaT,
        }

        for col, default in defaults.items():
            if col not in df.columns:
                df[col] = default

        if "brand_clean" in df.columns:
            df["brand_source"] = df["brand_clean"].fillna(df["brand"])
        else:
            df["brand_source"] = df["brand"]

        return df

    @staticmethod
    def _parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
        df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True)
        df["labeled_at"] = pd.to_datetime(df["labeled_at"], errors="coerce", utc=True)
        return df

    @staticmethod
    def _coerce_target(df: pd.DataFrame) -> pd.DataFrame:
        target = pd.to_numeric(df["sold_within_7_days"], errors="coerce")
        df["target_raw"] = target
        df["target_missing"] = target.isna()
        df["target_not_binary"] = ~target.isin([0, 1]) & ~target.isna()
        df["sold_within_7_days"] = target.where(target.isin([0, 1]), np.nan)
        return df

    def _add_label_window_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        window_hours = (
            (df["labeled_at"] - df["scraped_at"]).dt.total_seconds() / 3600.0
        )
        df["label_window_hours"] = window_hours

        has_window = df["label_window_hours"].notna()
        df["invalid_early_label"] = (
            has_window & (df["label_window_hours"] < self.config.min_valid_window_hours)
        )
        df["invalid_late_label"] = (
            has_window & (df["label_window_hours"] > self.config.max_valid_window_hours)
        )

        logger.info(
            "Label window QC: "
            f"early={int(df['invalid_early_label'].sum())}, "
            f"late={int(df['invalid_late_label'].sum())}, "
            f"missing={int((~has_window).sum())}"
        )
        return df

    def engineer_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["price_log"] = np.log1p(df["price"].clip(lower=0))

        cat_median = df.groupby("category")["price"].transform("median")
        brand_median = df.groupby("brand_source")["price"].transform("median")

        df["price_to_category_median"] = (df["price"] / cat_median).replace([np.inf, -np.inf], np.nan)
        df["price_to_brand_median"] = (df["price"] / brand_median).replace([np.inf, -np.inf], np.nan)

        df["price_to_category_median"] = df["price_to_category_median"].clip(0.1, 10.0)
        df["price_to_brand_median"] = df["price_to_brand_median"].clip(0.1, 10.0)
        return df

    @staticmethod
    def engineer_listing_features(df: pd.DataFrame) -> pd.DataFrame:
        for col in [
            "photo_count",
            "description_length",
            "description_word_count",
            "seller_rating_count",
            "seller_listing_count",
            "like_count",
            "comment_count",
        ]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["seller_rating_log"] = np.log1p(df["seller_rating_count"].clip(lower=0))
        df["seller_listing_log"] = np.log1p(df["seller_listing_count"].clip(lower=0))

        seller_key = df["seller_username"].fillna("unknown_seller").astype(str)
        seller_freq = seller_key.value_counts()
        df["seller_listing_frequency"] = seller_key.map(seller_freq).astype(float)

        freq_cap = float(df["seller_listing_frequency"].quantile(0.95))
        freq_cap = max(freq_cap, 1.0)
        df["seller_listing_frequency_capped"] = df["seller_listing_frequency"].clip(
            lower=1.0,
            upper=freq_cap,
        )
        df["seller_frequency_log"] = np.log1p(df["seller_listing_frequency_capped"])
        df["seller_balance_weight"] = 1.0 / np.sqrt(df["seller_listing_frequency_capped"])
        return df

    @staticmethod
    def engineer_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
        scraped_local = df["scraped_at"].dt.tz_convert("Europe/Istanbul")
        df["listing_hour"] = scraped_local.dt.hour.fillna(-1).astype(int)
        df["listing_dow"] = scraped_local.dt.dayofweek.fillna(-1).astype(int)
        df["is_weekend_listing"] = df["listing_dow"].isin([4, 5, 6])

        now_utc = pd.Timestamp.now(tz="UTC")
        df["days_since_scrape"] = (
            (now_utc - df["scraped_at"]).dt.total_seconds() / 86400.0
        )
        return df

    @staticmethod
    def engineer_text_features(df: pd.DataFrame) -> pd.DataFrame:
        desc = df["description_text"].fillna("").astype(str).str.lower()

        urgency = [kw.lower() for kw in [
            "acil",
            "son fiyat",
            "fırsat",
            "pazarlık",
            "indirim",
            "satılmalı",
        ]]
        urgency_pattern = "|".join(map(re.escape, urgency))
        flaw_pattern = "|".join(map(re.escape, FLAW_KEYWORDS))

        df["desc_has_urgency_keyword"] = desc.str.contains(urgency_pattern, regex=True)
        df["desc_has_flaw_mention"] = desc.str.contains(flaw_pattern, regex=True)

        if "desc_is_placeholder" not in df.columns:
            title = df["title"].fillna("").astype(str)
            df["desc_is_placeholder"] = desc.eq(title.str.lower()) | desc.eq("")

        return df

    def engineer_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df["condition_ordinal"] = df["condition"].map(CONDITION_MAP).fillna(-1).astype(int)

        tier_map = self._build_brand_tier_map(df)
        df["brand_tier"] = (
            df["brand_source"].map(tier_map).fillna(0).astype(int)
        )

        for col in ["has_discount", "shipping_buyer_pays"]:
            df[col] = df[col].astype(bool).astype(int)

        df["category"] = df["category"].fillna("Bilinmiyor").astype(str)
        return df

    def _build_brand_tier_map(self, df: pd.DataFrame) -> dict[str, int]:
        configured: dict[str, int] = {}
        tiers = self._features_config.get("brand_tiers", {})
        for idx, key in enumerate(
            [
                "tier_1_budget",
                "tier_2_mid",
                "tier_3_premium",
                "tier_4_designer",
                "tier_5_luxury",
            ],
            start=1,
        ):
            for brand in tiers.get(key, []):
                configured[str(brand)] = idx

        if configured:
            return configured

        # Fallback: build data-driven tiers from median brand price
        medians = (
            df.groupby("brand_source", dropna=True)["price"]
            .median()
            .dropna()
        )
        if medians.empty:
            return {}

        quantiles = medians.quantile([0.2, 0.4, 0.6, 0.8]).to_list()

        def _to_tier(value: float) -> int:
            if value <= quantiles[0]:
                return 1
            if value <= quantiles[1]:
                return 2
            if value <= quantiles[2]:
                return 3
            if value <= quantiles[3]:
                return 4
            return 5

        return {brand: _to_tier(price) for brand, price in medians.items()}

    @staticmethod
    def _select_output_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns = [
            "listing_id",
            "cohort_id",
            "sold_within_7_days",
            "exclude_from_training",
            "target_missing",
            "target_not_binary",
            "label_window_hours",
            "invalid_early_label",
            "invalid_late_label",
            "price",
            "price_log",
            "price_to_category_median",
            "price_to_brand_median",
            "photo_count",
            "description_length",
            "description_word_count",
            "seller_rating_count",
            "seller_rating_log",
            "seller_listing_count",
            "seller_listing_log",
            "seller_frequency_log",
            "seller_balance_weight",
            "like_count",
            "comment_count",
            "listing_hour",
            "listing_dow",
            "is_weekend_listing",
            "days_since_scrape",
            "condition_ordinal",
            "brand_tier",
            "has_discount",
            "shipping_buyer_pays",
            "desc_has_urgency_keyword",
            "desc_has_flaw_mention",
            "desc_is_placeholder",
            "category",
            "brand_source",
            "seller_username",
        ]
        existing = [c for c in columns if c in df.columns]
        out = df[existing].copy()

        # Make binary booleans explicit 0/1 for modeling compatibility
        for col in [
            "is_weekend_listing",
            "desc_has_urgency_keyword",
            "desc_has_flaw_mention",
            "desc_is_placeholder",
            "invalid_early_label",
            "invalid_late_label",
            "target_missing",
            "target_not_binary",
            "exclude_from_training",
        ]:
            if col in out.columns:
                out[col] = out[col].astype(bool).astype(int)

        return out

    def save(self, features: pd.DataFrame) -> None:
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            features.to_parquet(self.config.output_path, index=False)
            logger.info(f"Saved features: {self.config.output_path}")
        except ImportError:
            fallback = self.config.output_path.with_suffix(".csv")
            features.to_csv(fallback, index=False)
            logger.warning(f"pyarrow not installed; saved CSV fallback: {fallback}")

        meta = {
            "row_count": int(len(features)),
            "column_count": int(len(features.columns)),
            "target": "sold_within_7_days",
            "excluded_from_training": int(features["exclude_from_training"].sum()),
            "feature_columns": [
                c
                for c in features.columns
                if c not in {"listing_id", "cohort_id", "sold_within_7_days"}
            ],
        }
        with self.config.metadata_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved metadata: {self.config.metadata_path}")

    def run(self) -> pd.DataFrame:
        df = self.load()
        features = self.transform(df)
        self.save(features)

        logger.info("=" * 60)
        logger.info("FEATURE ENGINEERING — SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total rows              : {len(features)}")
        if "sold_within_7_days" in features.columns:
            labeled = features["sold_within_7_days"].notna().sum()
            logger.info(f"Rows with valid target  : {labeled}")
        logger.info(f"Excluded from training  : {int(features['exclude_from_training'].sum())}")
        logger.info("=" * 60)

        return features


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run feature engineering pipeline")
    parser.add_argument(
        "--input-path",
        type=str,
        default="data/interim/merged_data.csv",
        help="Input merged dataset path (csv or parquet)",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="data/processed/engineered_features.parquet",
        help="Output feature matrix path",
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default="data/processed/features_metadata.json",
        help="Output metadata JSON path",
    )
    parser.add_argument(
        "--features-yaml",
        type=str,
        default="configs/features.yaml",
        help="Feature configuration YAML path",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    setup_logging(level="INFO")

    config = FeatureEngineerConfig(
        input_path=Path(args.input_path),
        output_path=Path(args.output_path),
        metadata_path=Path(args.metadata_path),
        features_yaml=Path(args.features_yaml),
    )
    FeatureEngineer(config=config).run()


if __name__ == "__main__":
    main()
