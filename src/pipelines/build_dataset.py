"""
Pipeline entrypoint: Build dataset — merge snapshots + labels → clean → save.

Usage:
    python -m src.pipelines.build_dataset --cohort-ids 20260311
    python -m src.pipelines.build_dataset --all
    python -m src.pipelines.build_dataset --cohort-ids 20250712 20260311

End-to-end pipeline:
  1. Discover / specify cohorts
  2. Merge raw snapshots + labels → interim parquet (per cohort)
  3. Concatenate all cohorts
  4. Clean (dedup, missing, outlier, dtype)
    5. Save cleaned dataset to data/interim/
    6. Write canonical merged_data output used by downstream training/FE
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.dataset.merger import DatasetMerger
from src.preprocessing.cleaner import DataCleaner
from src.utils.logger import get_logger, setup_logging


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build train-ready dataset from raw cohort snapshots"
    )
    parser.add_argument(
        "--cohort-ids",
        nargs="*",
        default=None,
        help="Cohort IDs to include (YYYYMMDD). Omit for --all.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include every cohort found in data/raw_snapshots/",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/interim",
        help="Directory for cleaned output files",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip merge step (use existing merged parquets)",
    )
    parser.add_argument(
        "--no-canonical",
        action="store_true",
        help="Skip writing canonical merged_data.csv output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    setup_logging(level="INFO")
    logger = get_logger("build_dataset")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Discover cohorts ─────────────────────────────────────────
    merger = DatasetMerger()

    if args.all:
        cohort_ids = merger.discover_cohorts()
    elif args.cohort_ids:
        cohort_ids = args.cohort_ids
    else:
        cohort_ids = merger.discover_cohorts()

    if not cohort_ids:
        logger.error("No cohorts found. Specify --cohort-ids or use --all.")
        sys.exit(1)

    logger.info(f"Processing cohorts: {cohort_ids}")
    logger.info("Label source policy: only data/labels/cohort_*.jsonl is considered official")

    # ── Step 2: Merge raw + labels (per cohort) ─────────────────────────
    if not args.skip_merge:
        combined = merger.merge_all(cohort_ids=cohort_ids, save=True)
    else:
        # Load existing merged_all.parquet
        merged_path = output_dir / "merged_all.parquet"
        if not merged_path.exists():
            logger.error(f"--skip-merge used but {merged_path} not found.")
            sys.exit(1)
        combined = pd.read_parquet(merged_path)
        logger.info(f"Loaded existing merged data: {len(combined)} rows")

    logger.info(f"Merged dataset: {len(combined)} rows, {len(combined.columns)} columns")

    # ── Step 3: Clean ────────────────────────────────────────────────────
    cleaner = DataCleaner()
    cleaned = cleaner.transform(combined)

    # Unlabeled rows are represented as -1 in merger; normalize to NaN for downstream checks.
    if "sold_within_7_days" in cleaned.columns:
        cleaned["sold_within_7_days"] = pd.to_numeric(
            cleaned["sold_within_7_days"], errors="coerce"
        )
        cleaned.loc[cleaned["sold_within_7_days"] == -1, "sold_within_7_days"] = pd.NA

    # ── Step 4: Save cleaned output ──────────────────────────────────────
    out_parquet = output_dir / "cleaned_all.parquet"
    out_csv = output_dir / "cleaned_all.csv"

    try:
        cleaned.to_parquet(out_parquet, index=False)
        logger.info(f"Saved: {out_parquet} ({len(cleaned)} rows)")
    except ImportError:
        logger.warning("pyarrow not installed — skipping parquet")

    cleaned.to_csv(out_csv, index=False)
    logger.info(f"Saved: {out_csv}")

    # ── Step 5: Canonical merged output (single source of truth) ───────
    if not args.no_canonical:
        canonical_csv = output_dir / "merged_data.csv"
        canonical_parquet = output_dir / "merged_data.parquet"

        cleaned.to_csv(canonical_csv, index=False)
        logger.info(f"Saved canonical CSV: {canonical_csv}")

        try:
            cleaned.to_parquet(canonical_parquet, index=False)
            logger.info(f"Saved canonical parquet: {canonical_parquet}")
        except ImportError:
            logger.warning("pyarrow not installed — skipping canonical parquet")

    # ── Step 6: Summary ──────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("BUILD DATASET — SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Cohorts processed : {cohort_ids}")
    logger.info(f"  Total rows        : {len(cleaned)}")
    logger.info(f"  Total columns     : {len(cleaned.columns)}")
    logger.info(f"  Real labels       : {cleaned['has_real_label'].sum()}")

    if "condition_clean" in cleaned.columns:
        logger.info(f"  Conditions        : {cleaned['condition_clean'].value_counts().to_dict()}")
    if "brand_clean" in cleaned.columns:
        logger.info(f"  Unique brands     : {cleaned['brand_clean'].nunique()}")
    if "category" in cleaned.columns:
        logger.info(f"  Unique categories : {cleaned['category'].nunique()}")
    if "is_price_outlier" in cleaned.columns:
        logger.info(f"  Price outliers    : {cleaned['is_price_outlier'].sum()}")

    logger.info("=" * 60)
    logger.info("✅ build_dataset pipeline complete")


if __name__ == "__main__":
    main()
