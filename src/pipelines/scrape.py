"""
Pipeline entrypoint: Scrape dolap.com listings.

Usage:
    python -m src.pipelines.scrape --cohort-id 20260301
    python -m src.pipelines.scrape --config configs/scraping.yaml
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# These imports will resolve once the actual modules are implemented.
# For now they serve as the contract / skeleton.
# ---------------------------------------------------------------------------
# from src.scraping.category_crawler import CategoryCrawler
# from src.scraping.listing_scraper import ListingScraper
# from src.scraping.seller_scraper import SellerScraper
# from src.utils.config import load_config
# from src.utils.logger import get_logger


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Dolap.com listings")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/scraping.yaml",
        help="Path to scraping config YAML",
    )
    parser.add_argument(
        "--cohort-id",
        type=str,
        default=None,
        help="Cohort identifier (YYYYMMDD). Defaults to today.",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=None,
        help="Override: only scrape these category slugs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without actually scraping",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    cohort_id = args.cohort_id or datetime.now().strftime("%Y%m%d")
    output_dir = Path(f"data/raw_snapshots/cohort_{cohort_id}")

    # TODO: replace with real implementation
    print(f"[scrape] config     : {args.config}")
    print(f"[scrape] cohort_id  : {cohort_id}")
    print(f"[scrape] output_dir : {output_dir}")
    print(f"[scrape] dry_run    : {args.dry_run}")
    print(f"[scrape] categories : {args.categories or 'all (from config)'}")

    if args.dry_run:
        print("[scrape] Dry run — exiting.")
        return

    # ── Pipeline skeleton ──────────────────────────────────────────────
    # config = load_config(args.config)
    # logger = get_logger("scrape")
    #
    # output_dir.mkdir(parents=True, exist_ok=True)
    #
    # 1. Crawl category pages → collect listing URLs
    # 2. Scrape each listing detail page → listings.jsonl
    # 3. Scrape seller profiles → sellers.jsonl
    # 4. Write meta.yaml (cohort_id, scrape_date, counts, filters)
    # ───────────────────────────────────────────────────────────────────

    print("[scrape] ✅ Pipeline skeleton ready — implement in src/scraping/")


if __name__ == "__main__":
    main()
