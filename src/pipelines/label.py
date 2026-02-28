"""
Pipeline entrypoint: Label listings — 7-day sold-status re-check.

Usage:
    python -m src.pipelines.label --cohort-id 20260301
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# from src.labeling.status_checker import StatusChecker
# from src.utils.config import load_config
# from src.utils.logger import get_logger


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label listings with 7-day sold status")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/scraping.yaml",
        help="Path to config YAML (labeling section)",
    )
    parser.add_argument(
        "--cohort-id",
        type=str,
        required=True,
        help="Cohort identifier to re-check (YYYYMMDD)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-label even if labels file already exists",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    snapshot_dir = Path(f"data/raw_snapshots/cohort_{args.cohort_id}")
    labels_path = Path(f"data/labels/cohort_{args.cohort_id}.jsonl")

    print(f"[label] config      : {args.config}")
    print(f"[label] cohort_id   : {args.cohort_id}")
    print(f"[label] snapshot    : {snapshot_dir}")
    print(f"[label] labels_out  : {labels_path}")

    if labels_path.exists() and not args.force:
        print(f"[label] ⚠️  Labels already exist at {labels_path}. Use --force to overwrite.")
        return

    # ── Pipeline skeleton ──────────────────────────────────────────────
    # config = load_config(args.config)
    # logger = get_logger("label")
    #
    # 1. Load listing URLs from snapshot_dir/listings.jsonl
    # 2. Re-visit each URL
    # 3. Check for "Satıldı" badge OR HTTP 404/410
    # 4. Write cohort_{id}.jsonl  →  {listing_id, url, status, sold_within_7_days}
    # ───────────────────────────────────────────────────────────────────

    print("[label] ✅ Pipeline skeleton ready — implement in src/labeling/")


if __name__ == "__main__":
    main()
