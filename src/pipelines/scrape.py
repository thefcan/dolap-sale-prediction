"""
Pipeline entrypoint: Scrape dolap.com listings.

Usage::

    # Scrape all categories (from config)
    python -m src.pipelines.scrape --cohort-id 20260301

    # Scrape specific categories
    python -m src.pipelines.scrape --categories kazak elbise

    # Dry-run mode — print plan without scraping
    python -m src.pipelines.scrape --dry-run

    # Limit pages per category
    python -m src.pipelines.scrape --max-pages 3

The pipeline:
    1. Loads ``configs/scraping.yaml``
    2. For each target category, crawls listing URLs
    3. Scrapes individual listing detail pages
    4. Saves results as JSONL files + ``meta.yaml``
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.scraping.scraper import DolapScraper, load_scraping_config
from src.utils.logger import get_logger, setup_logging


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
        "--max-pages",
        type=int,
        default=None,
        help="Override max pages per category",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser with visible window (for debugging)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without actually scraping",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # ── Setup ──────────────────────────────────────────────────────────
    setup_logging(level="INFO")
    logger = get_logger("pipeline.scrape")

    cfg = load_scraping_config(args.config)
    cohort_id = args.cohort_id or datetime.now().strftime("%Y%m%d")
    output_dir = Path(cfg.get("output_dir", "data/raw_snapshots")) / f"cohort_{cohort_id}"
    headless = not args.no_headless

    # Determine target categories
    if args.categories:
        categories = args.categories
    else:
        categories = [c["slug"] for c in cfg.get("categories", [])]

    max_pages = args.max_pages or cfg.get("max_pages_per_category", 50)

    # ── Dry-run report ─────────────────────────────────────────────────
    logger.info(
        "Scrape pipeline configuration",
        config=args.config,
        cohort_id=cohort_id,
        output_dir=str(output_dir),
        categories=categories,
        max_pages=max_pages,
        headless=headless,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        logger.info("Dry run — printing plan and exiting")
        for slug in categories:
            print(f"  → Would scrape category: {slug} (max {max_pages} pages)")
        print(f"  → Output: {output_dir}")
        return

    # ── Execute ────────────────────────────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)
    scrape_start = datetime.utcnow()

    total_listings: int = 0
    category_stats: dict[str, dict] = {}

    with DolapScraper(config_path=args.config, headless=headless) as scraper:
        for slug in categories:
            logger.info(f"{'─' * 40}")
            logger.info(f"Category: {slug}")

            jsonl_path = output_dir / f"{slug}.jsonl"

            results = scraper.scrape_category(
                category_slug=slug,
                max_pages=max_pages,
                output_path=jsonl_path,
            )

            category_stats[slug] = {
                "listings_scraped": len(results),
                "output_file": str(jsonl_path),
            }
            total_listings += len(results)

            logger.info(
                "Category complete",
                category=slug,
                listings=len(results),
            )

    scrape_end = datetime.utcnow()

    # ── Write meta.yaml ────────────────────────────────────────────────
    meta = {
        "cohort_id": cohort_id,
        "scrape_start": scrape_start.isoformat(),
        "scrape_end": scrape_end.isoformat(),
        "duration_seconds": (scrape_end - scrape_start).total_seconds(),
        "categories": category_stats,
        "total_listings": total_listings,
        "config_path": args.config,
        "max_pages_per_category": max_pages,
    }

    meta_path = output_dir / "meta.yaml"
    with open(meta_path, "w", encoding="utf-8") as fh:
        yaml.dump(meta, fh, default_flow_style=False, allow_unicode=True)

    logger.info(
        "Scrape pipeline complete",
        cohort_id=cohort_id,
        total_listings=total_listings,
        duration_seconds=meta["duration_seconds"],
        output_dir=str(output_dir),
    )


if __name__ == "__main__":
    main()
