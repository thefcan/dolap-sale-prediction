"""
Data Cleaner — Cohort-agnostic cleaning for Dolap raw snapshots.
================================================================
Handles two cohort generations:
  - Old parser (cohort_20250712): brand contains "Brand - Size", category=None,
    description often = page title, subcategory=None
  - New parser (cohort_20260311+): brand clean, category from JSON-LD,
    description from actual <p> tag, size separate

Steps:
  1. Schema normalisation — ensure all columns present with correct dtypes
  2. Duplicate removal — by listing_id (keep first)
  3. Brand / size split — legacy cohorts only (already clean in new parser)
  4. Condition normalisation
  5. Category repair — use category_scraped if category is null
  6. Description cleaning — placeholder detection, text normalization
  7. Missing value handling — impute or flag
  8. Outlier detection — flag (not remove) extreme prices
  9. Dtype enforcement — float, int, bool, datetime
"""

from __future__ import annotations

import re
from typing import Literal

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("cleaner")


# ── Constants ────────────────────────────────────────────────────────────────

EXPECTED_COLUMNS = [
    "listing_id", "url", "brand", "title", "price", "original_price",
    "condition", "color", "size", "description_text", "description_length",
    "description_word_count", "like_count", "comment_count", "photo_count",
    "seller_username", "seller_listing_count", "category", "subcategory",
    "category_scraped", "cohort_id", "scraped_at", "is_sold",
    "has_discount", "shipping_info", "shipping_buyer_pays",
]

CONDITION_NORMALIZE_MAP = {
    "Yeni ve Etiketli": "Yeni & Etiketli",
    "Yeni & Etiketli": "Yeni & Etiketli",
    "Yeni": "Yeni",
    "Az Kullanılmış": "Az Kullanılmış",
    "Kullanılmış": "Kullanılmış",
}

CONDITION_ORDINAL_MAP = {
    "Kullanılmış": 0,
    "Az Kullanılmış": 1,
    "Yeni": 2,
    "Yeni & Etiketli": 3,
}

# Price boundaries (TL) — listings outside these are flagged
PRICE_MIN = 10.0
PRICE_MAX = 50_000.0

# Percentile thresholds for outlier flagging
PRICE_OUTLIER_UPPER_PCTL = 99.0
LIKE_OUTLIER_UPPER_PCTL = 99.0


class DataCleaner:
    """Stateless cleaning pipeline for a single cohort DataFrame.

    Usage::

        cleaner = DataCleaner()
        df_clean = cleaner.transform(df_raw)
    """

    def __init__(
        self,
        price_min: float = PRICE_MIN,
        price_max: float = PRICE_MAX,
        price_outlier_pctl: float = PRICE_OUTLIER_UPPER_PCTL,
        like_outlier_pctl: float = LIKE_OUTLIER_UPPER_PCTL,
    ):
        self.price_min = price_min
        self.price_max = price_max
        self.price_outlier_pctl = price_outlier_pctl
        self.like_outlier_pctl = like_outlier_pctl

    # ── Main entry ───────────────────────────────────────────────────────

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run all cleaning steps. Returns a new DataFrame."""
        df = df.copy()
        n_start = len(df)

        df = self._normalise_schema(df)
        df = self._remove_duplicates(df)
        df = self._clean_brand_size(df)
        df = self._normalise_condition(df)
        df = self._repair_category(df)
        df = self._clean_description(df)
        df = self._handle_missing(df)
        df = self._flag_outliers(df)
        df = self._enforce_dtypes(df)

        n_end = len(df)
        logger.info(f"Cleaning complete: {n_start} → {n_end} rows ({n_start - n_end} removed)")
        return df

    # ── Step 1: Schema normalisation ─────────────────────────────────────

    def _normalise_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all expected columns exist; drop unknown columns."""
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = None
                logger.warning(f"Missing column added: {col}")

        # Keep expected + any new columns added during cleaning
        return df

    # ── Step 2: Duplicate removal ────────────────────────────────────────

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate listing_id rows, keeping the first occurrence."""
        n_before = len(df)
        df = df.drop_duplicates(subset=["listing_id"], keep="first")
        n_removed = n_before - len(df)
        if n_removed > 0:
            logger.info(f"Duplicates removed: {n_removed}")
        return df

    # ── Step 3: Brand / size split ───────────────────────────────────────

    def _clean_brand_size(self, df: pd.DataFrame) -> pd.DataFrame:
        """Split legacy 'brand' field ('Zara - S / 36 Beden') into brand_clean + size_extracted.

        New parser cohorts already have clean brand/size, but we still run
        the split to handle both uniformly.
        """

        def _split(val):
            if pd.isna(val) or not val:
                return "Bilinmiyor", None
            val = str(val).strip()
            if " - " in val:
                parts = val.split(" - ", 1)
                return parts[0].strip(), parts[1].strip()
            return val, None

        splits = df["brand"].apply(_split)
        df["brand_clean"] = splits.apply(lambda x: x[0])
        df["size_extracted"] = splits.apply(lambda x: x[1])

        # Use extracted size if original is missing
        df["size_final"] = df["size"].fillna(df["size_extracted"])

        n_extracted = df["size_extracted"].notna().sum()
        logger.info(f"Brand/size split: {n_extracted} sizes recovered from brand field")
        return df

    # ── Step 4: Condition normalisation ──────────────────────────────────

    def _normalise_condition(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize condition labels + add ordinal encoding."""
        df["condition_clean"] = (
            df["condition"]
            .map(CONDITION_NORMALIZE_MAP)
            .fillna("Bilinmiyor")
        )
        df["condition_ordinal"] = (
            df["condition_clean"]
            .map(CONDITION_ORDINAL_MAP)
            .fillna(-1)
            .astype(int)
        )
        logger.info(f"Condition: {df['condition'].nunique()} raw → {df['condition_clean'].nunique()} normalised")
        return df

    # ── Step 5: Category repair ──────────────────────────────────────────

    def _repair_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """Use category_scraped as fallback when category is null."""
        null_cats = df["category"].isna()
        if null_cats.any():
            df.loc[null_cats, "category"] = df.loc[null_cats, "category_scraped"]
            logger.info(f"Category repaired: {null_cats.sum()} rows filled from category_scraped")

        # Subcategory: fill with 'Bilinmiyor' if null
        df["subcategory"] = df["subcategory"].fillna("Bilinmiyor")
        return df

    # ── Step 6: Description cleaning ─────────────────────────────────────

    def _clean_description(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect placeholder descriptions and normalize text."""
        desc = df["description_text"].fillna("")
        title = df["title"].fillna("")

        # Placeholder: description == title OR empty
        df["desc_is_placeholder"] = (desc == title) | (desc.str.strip() == "")

        # Recalculate length/word_count for cleaned descriptions
        df["description_length"] = desc.str.len()
        df["description_word_count"] = desc.str.split().str.len().fillna(0).astype(int)

        n_placeholder = df["desc_is_placeholder"].sum()
        logger.info(f"Description: {n_placeholder}/{len(df)} placeholders detected")
        return df

    # ── Step 7: Missing value handling ───────────────────────────────────

    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute or flag missing values per-column strategy."""
        # color → "Bilinmiyor"
        df["color"] = df["color"].fillna("Bilinmiyor")

        # size_final → "Bilinmiyor"
        df["size_final"] = df["size_final"].fillna("Bilinmiyor")

        # original_price → None stays (conditional missingness)
        # has_discount already reflects this

        # seller_listing_count → 0 if unknown
        df["seller_listing_count"] = df["seller_listing_count"].fillna(0).astype(int)

        # like_count, comment_count, photo_count → 0 if null
        for col in ["like_count", "comment_count", "photo_count"]:
            df[col] = df[col].fillna(0).astype(int)

        # price → drop rows with null or zero price (critical field)
        bad_price = df["price"].isna() | (df["price"] <= 0)
        if bad_price.any():
            logger.warning(f"Dropping {bad_price.sum()} rows with null/zero price")
            df = df[~bad_price].reset_index(drop=True)

        return df

    # ── Step 8: Outlier flagging ─────────────────────────────────────────

    def _flag_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flag outlier rows (not remove — preserve for analysis)."""
        # Price outliers
        price_upper = np.percentile(df["price"], self.price_outlier_pctl)
        df["is_price_outlier"] = (
            (df["price"] < self.price_min) | (df["price"] > price_upper)
        )

        # Like outliers
        like_upper = np.percentile(df["like_count"], self.like_outlier_pctl)
        df["is_like_outlier"] = df["like_count"] > like_upper

        n_price_out = df["is_price_outlier"].sum()
        n_like_out = df["is_like_outlier"].sum()
        logger.info(
            f"Outliers flagged: {n_price_out} price (>{price_upper:.0f} TL or <{self.price_min} TL), "
            f"{n_like_out} likes (>{like_upper:.0f})"
        )
        return df

    # ── Step 9: Dtype enforcement ────────────────────────────────────────

    def _enforce_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Coerce columns to canonical dtypes."""
        # String columns
        str_cols = [
            "listing_id", "url", "brand", "brand_clean", "title",
            "condition", "condition_clean", "color", "size", "size_final",
            "size_extracted", "description_text", "seller_username",
            "category", "subcategory", "category_scraped", "cohort_id",
            "shipping_info",
        ]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("None", pd.NA)

        # Float columns
        for col in ["price", "original_price"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Int columns
        int_cols = [
            "like_count", "comment_count", "photo_count",
            "seller_listing_count", "description_length", "description_word_count",
            "condition_ordinal",
        ]
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        # Bool columns
        for col in ["has_discount", "is_sold", "shipping_buyer_pays",
                     "desc_is_placeholder", "is_price_outlier", "is_like_outlier"]:
            if col in df.columns:
                df[col] = df[col].astype(bool)

        # Datetime
        if "scraped_at" in df.columns:
            df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")

        return df
