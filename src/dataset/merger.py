"""
Dataset Merger — Combine raw snapshots + labels into interim datasets.
=====================================================================
Responsibilities:
  1. Load raw JSONL snapshots for one or more cohorts
  2. Load corresponding label files (if exist)
  3. Merge on listing_id
  4. Save as interim parquet (one per cohort + combined)

Usage::

    from src.dataset.merger import DatasetMerger

    merger = DatasetMerger()
    df = merger.merge_cohort("20260311")
    df_all = merger.merge_all()
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("merger")


# ── Constants ────────────────────────────────────────────────────────────────

RAW_DIR = Path("data/raw_snapshots")
LABELS_DIR = Path("data/labels")
INTERIM_DIR = Path("data/interim")


class DatasetMerger:
    """Merge raw snapshots with labels into clean interim DataFrames.

    Parameters
    ----------
    raw_dir : Path
        Directory containing ``cohort_{id}/listings.jsonl`` files.
    labels_dir : Path
        Directory containing ``cohort_{id}.jsonl`` label files.
    interim_dir : Path
        Output directory for merged parquet files.
    """

    def __init__(
        self,
        raw_dir: Path = RAW_DIR,
        labels_dir: Path = LABELS_DIR,
        interim_dir: Path = INTERIM_DIR,
    ):
        self.raw_dir = Path(raw_dir)
        self.labels_dir = Path(labels_dir)
        self.interim_dir = Path(interim_dir)
        self.interim_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ───────────────────────────────────────────────────────

    def discover_cohorts(self) -> list[str]:
        """Find all cohort IDs that have raw snapshots."""
        cohorts = []
        for d in sorted(self.raw_dir.iterdir()):
            if d.is_dir() and d.name.startswith("cohort_"):
                listings = d / "listings.jsonl"
                if listings.exists() and listings.stat().st_size > 0:
                    cohorts.append(d.name.replace("cohort_", ""))
        logger.info(f"Discovered {len(cohorts)} cohorts: {cohorts}")
        return cohorts

    def load_raw(self, cohort_id: str) -> pd.DataFrame:
        """Load raw JSONL snapshot for a cohort."""
        path = self.raw_dir / f"cohort_{cohort_id}" / "listings.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"Raw snapshot not found: {path}")

        records = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        df = pd.DataFrame(records)
        df["cohort_id"] = cohort_id  # Ensure cohort_id is set
        logger.info(f"Loaded {len(df)} raw records from cohort_{cohort_id}")
        return df

    def load_labels(self, cohort_id: str) -> pd.DataFrame | None:
        """Load labels for a cohort. Returns None if not available."""
        path = self.labels_dir / f"cohort_{cohort_id}.jsonl"
        if not path.exists():
            logger.info(f"No labels for cohort_{cohort_id} (file not found)")
            return None

        records = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        if not records:
            logger.warning(f"Labels file empty for cohort_{cohort_id}")
            return None

        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} labels for cohort_{cohort_id}")
        return df

    def merge_cohort(
        self,
        cohort_id: str,
        save: bool = True,
    ) -> pd.DataFrame:
        """Load raw + labels for a single cohort, merge, and optionally save.

        Returns
        -------
        pd.DataFrame
            Merged DataFrame with label columns added (if labels exist).
            ``has_real_label`` column indicates rows with ground-truth labels.
        """
        df = self.load_raw(cohort_id)

        # Initialize label columns with concrete types (avoids all-NA concat warnings)
        df["has_real_label"] = False
        df["sold_within_7_days"] = -1  # -1 = unlabeled, 0 = not sold, 1 = sold
        df["label_status"] = ""
        df["label_source"] = "none"

        # Merge labels if available
        labels = self.load_labels(cohort_id)
        if labels is not None and "listing_id" in labels.columns:
            df["listing_id"] = df["listing_id"].astype(str)
            labels["listing_id"] = labels["listing_id"].astype(str)

            # Select label columns
            label_cols = [c for c in ["listing_id", "status", "sold_within_7_days", "checked_at"]
                          if c in labels.columns]
            labels_subset = labels[label_cols].copy()

            # Merge
            df = df.merge(labels_subset, on="listing_id", how="left", suffixes=("", "_from_label"))

            # Reconcile status
            if "status" in df.columns:
                df["label_status"] = df["status"]
                df["has_real_label"] = df["status"].isin(["sold", "active"])
            elif "status_from_label" in df.columns:
                df["label_status"] = df["status_from_label"]
                df["has_real_label"] = df["status_from_label"].isin(["sold", "active"])

            df.loc[df["has_real_label"], "label_source"] = "official_labels_jsonl"

            # Reconcile sold_within_7_days
            if "sold_within_7_days_from_label" in df.columns:
                # Prefer label value over raw
                mask = df["sold_within_7_days_from_label"].notna()
                df.loc[mask, "sold_within_7_days"] = df.loc[mask, "sold_within_7_days_from_label"]
                df = df.drop(columns=["sold_within_7_days_from_label"], errors="ignore")

            # Coerce
            df.loc[df["has_real_label"], "sold_within_7_days"] = (
                df.loc[df["has_real_label"], "sold_within_7_days"]
                .fillna(0)
                .astype(int)
            )

            n_labeled = df["has_real_label"].sum()
            n_sold = (df["sold_within_7_days"] == 1).sum()
            logger.info(f"Labels merged: {n_labeled}/{len(df)} labeled, {n_sold} sold")

            # Clean up merge artifacts
            drop_cols = [c for c in df.columns if c.endswith("_from_label")]
            df = df.drop(columns=drop_cols, errors="ignore")

        if save:
            out_path = self.interim_dir / f"merged_{cohort_id}.parquet"
            self._save_parquet(df, out_path)

        return df

    def merge_all(
        self,
        cohort_ids: list[str] | None = None,
        save: bool = True,
    ) -> pd.DataFrame:
        """Merge all (or specified) cohorts into a single DataFrame.

        Parameters
        ----------
        cohort_ids : list[str] | None
            If None, discovers all available cohorts.
        save : bool
            Save combined parquet to interim dir.

        Returns
        -------
        pd.DataFrame
            Combined DataFrame from all cohorts.
        """
        if cohort_ids is None:
            cohort_ids = self.discover_cohorts()

        if not cohort_ids:
            raise ValueError("No cohorts found to merge")

        dfs = []
        for cid in cohort_ids:
            try:
                df = self.merge_cohort(cid, save=save)
                dfs.append(df)
            except FileNotFoundError:
                logger.warning(f"Skipping cohort_{cid}: raw snapshot not found")
                continue

        if not dfs:
            raise ValueError("No cohorts could be loaded")

        # Pre-fill all-NA columns before concat to avoid FutureWarning
        for df in dfs:
            if "sold_within_7_days" in df.columns:
                df["sold_within_7_days"] = pd.to_numeric(
                    df["sold_within_7_days"], errors="coerce"
                ).fillna(-1).astype(int)
            # Ensure string columns are str (not all-NA object)
            for col in ["category", "subcategory", "original_price", "label_status"]:
                if col in df.columns and df[col].isna().all():
                    if col == "original_price":
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    else:
                        df[col] = df[col].fillna("")
            if "label_source" in df.columns:
                df["label_source"] = df["label_source"].fillna("none").astype(str)

        combined = pd.concat(dfs, ignore_index=True)

        # Fill NA in label columns before dedup to avoid FutureWarning
        combined["has_real_label"] = combined["has_real_label"].fillna(False)
        combined["label_status"] = combined["label_status"].fillna("")

        # Remove cross-cohort duplicates (same listing scraped in multiple cohorts)
        n_before = len(combined)
        combined = combined.drop_duplicates(subset=["listing_id"], keep="last")
        n_deduped = n_before - len(combined)
        if n_deduped > 0:
            logger.info(f"Cross-cohort dedup: {n_deduped} duplicates removed (kept latest)")

        if save:
            out_path = self.interim_dir / "merged_all.parquet"
            self._save_parquet(combined, out_path)

        logger.info(
            f"All cohorts merged: {len(combined)} rows, "
            f"{combined['cohort_id'].nunique()} cohorts, "
            f"{combined['has_real_label'].sum()} with real labels"
        )
        return combined

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _save_parquet(df: pd.DataFrame, path: Path) -> None:
        """Save DataFrame to parquet with CSV fallback."""
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            df.to_parquet(path, index=False)
            logger.info(f"Saved: {path} ({len(df)} rows, {len(df.columns)} cols)")
        except ImportError:
            csv_path = path.with_suffix(".csv")
            df.to_csv(csv_path, index=False)
            logger.warning(f"pyarrow not installed — saved CSV: {csv_path}")
