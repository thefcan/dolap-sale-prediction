"""
Pipeline entrypoint: Build dataset — merge snapshots + labels → processed.

Usage:
    python -m src.pipelines.build_dataset --cohort-ids 20260301 20260308
    python -m src.pipelines.build_dataset --all
"""

from __future__ import annotations

import argparse
from pathlib import Path

# from src.dataset.merger import merge_snapshot_labels
# from src.preprocessing.cleaner import DataCleaner
# from src.features.engineer import FeatureEngineer
# from src.utils.config import load_config
# from src.utils.logger import get_logger


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build train-ready dataset")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/features.yaml",
        help="Path to features config YAML",
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
        help="Include every cohort found in data/labels/",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Directory for final train/val/test splits",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    print(f"[build_dataset] config     : {args.config}")
    print(f"[build_dataset] cohort_ids : {args.cohort_ids or 'all'}")
    print(f"[build_dataset] output_dir : {args.output_dir}")

    # ── Pipeline skeleton ──────────────────────────────────────────────
    # config = load_config(args.config)
    # logger = get_logger("build_dataset")
    #
    # 1. Discover cohorts (from args or scan data/labels/)
    # 2. For each cohort:
    #    a. Load raw_snapshots/cohort_{id}/listings.jsonl
    #    b. Load raw_snapshots/cohort_{id}/sellers.jsonl
    #    c. Load labels/cohort_{id}.jsonl
    #    d. Merge → interim/merged_{id}.parquet
    # 3. Concatenate all interim files
    # 4. Clean (drop duplicates, handle missing, outlier filter)
    # 5. Feature engineering (brand_tier, price_ratio, text features …)
    # 6. Stratified train / val / test split
    # 7. Save to processed/  (train.parquet, val.parquet, test.parquet)
    # ───────────────────────────────────────────────────────────────────

    print("[build_dataset] ✅ Pipeline skeleton ready — implement in src/dataset/ & src/features/")


if __name__ == "__main__":
    main()
