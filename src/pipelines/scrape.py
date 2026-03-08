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
    1. Loads ``configs/scraping.yaml`` + ``configs/pipeline.yaml``
    2. For each target category, crawls listing URLs
    3. Scrapes individual listing detail pages
    4. Streams results through **SnapshotWriter** (append-only JSONL + dedup)
    5. Registers cohort in **CohortStateTracker** (SQLite lifecycle)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.scraping.scraper import DolapScraper, load_scraping_config
from src.scraping.storage import CohortStateTracker, SnapshotWriter
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
    base_dir = Path(cfg.get("output_dir", "data/raw_snapshots"))
    headless = not args.no_headless

    # Pipeline config for database path
    pipeline_cfg_path = Path("configs/pipeline.yaml")
    if pipeline_cfg_path.exists():
        with open(pipeline_cfg_path, "r", encoding="utf-8") as fh:
            pipeline_cfg = yaml.safe_load(fh) or {}
    else:
        pipeline_cfg = {}

    db_url = pipeline_cfg.get("database", {}).get("url", "sqlite:///data/dolap_state.db")
    # Extract file path from sqlite URL  ("sqlite:///data/dolap_state.db" → "data/dolap_state.db")
    db_path = db_url.replace("sqlite:///", "") if db_url.startswith("sqlite:///") else "data/dolap_state.db"

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
        base_dir=str(base_dir),
        categories=categories,
        max_pages=max_pages,
        headless=headless,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        logger.info("Dry run — printing plan and exiting")
        for slug in categories:
            print(f"  → Would scrape category: {slug} (max {max_pages} pages)")
        print(f"  → Output: {base_dir / f'cohort_{cohort_id}'}")
        return

    # ── Initialise storage layer ───────────────────────────────────────
    writer = SnapshotWriter(base_dir=base_dir, cohort_id=cohort_id)
    writer.setup()

    tracker = CohortStateTracker(db_path=db_path)

    # ── Execute ────────────────────────────────────────────────────────
    scrape_start = datetime.utcnow()
    total_listings: int = 0

    try:
        with DolapScraper(config_path=args.config, headless=headless) as scraper:
            for slug in categories:
                logger.info(f"{'─' * 40}")
                logger.info(f"Category: {slug}")

                # Scrape without output_path — writing is delegated to SnapshotWriter
                results = scraper.scrape_category(
                    category_slug=slug,
                    max_pages=max_pages,
                    output_path=None,
                )

                # Stream results through SnapshotWriter (handles dedup + combined JSONL)
                written = writer.append_batch(slug, results)
                total_listings += written

                logger.info(
                    "Category complete",
                    category=slug,
                    scraped=len(results),
                    written=written,
                    duplicates=len(results) - written,
                )
    finally:
        scrape_end = datetime.utcnow()
        duration = (scrape_end - scrape_start).total_seconds()

        # ── Finalise snapshot (meta.yaml) ──────────────────────────────
        meta_path = writer.finalise(
            scrape_start=scrape_start.isoformat(),
            scrape_end=scrape_end.isoformat(),
            duration_seconds=duration,
            max_pages_per_category=max_pages,
            config_path=args.config,
        )

        # ── Register in CohortStateTracker ─────────────────────────────
        tracker.register_cohort(
            cohort_id,
            total_listings=writer.stats["total_written"],
            duration_seconds=duration,
            scrape_start=scrape_start.isoformat(),
            scrape_end=scrape_end.isoformat(),
            categories=categories,
        )
        tracker.close()

        logger.info(
            "Scrape pipeline complete",
            cohort_id=cohort_id,
            total_listings=writer.stats["total_written"],
            duplicates_skipped=writer.stats["duplicates_skipped"],
            duration_seconds=duration,
            output_dir=str(writer.cohort_dir),
            meta=str(meta_path),
        )


if __name__ == "__main__":
    main()
