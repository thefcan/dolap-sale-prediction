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

                # Phase 1: Collect URLs from seller profiles
                seed_sellers = []
                for cat_cfg in cfg.get("categories", []):
                    if cat_cfg.get("slug") == slug:
                        seed_sellers = cat_cfg.get("seed_sellers", [])
                        break

                all_urls: list[str] = []
                seen_urls: set[str] = set()

                if seed_sellers:
                    for username in seed_sellers:
                        profile_urls = scraper.crawl_seller_profile(
                            username, max_pages=max_pages,
                        )
                        for u in profile_urls:
                            if u not in seen_urls:
                                seen_urls.add(u)
                                all_urls.append(u)
                    logger.info(
                        "URL collection complete",
                        category=slug,
                        total_urls=len(all_urls),
                        sellers=len(seed_sellers),
                    )
                else:
                    all_urls = scraper.crawl_category(slug, max_pages=max_pages)
                    logger.info("URLs from category page", total=len(all_urls))

                if not all_urls:
                    logger.warning("No URLs found, skipping", category=slug)
                    continue

                # Phase 2: Scrape each listing and write IMMEDIATELY to disk
                cat_written = 0
                cat_errors = 0

                for idx, url in enumerate(all_urls, 1):
                    logger.info(f"[{idx}/{len(all_urls)}] Scraping", url=url[:80])

                    data = scraper.scrape_listing(url)

                    # Write immediately — crash-safe
                    if data and not data.get("_ban_detected"):
                        if writer.append(slug, data):
                            cat_written += 1
                        else:
                            pass  # duplicate
                    else:
                        cat_errors += 1

                    # Abort on ban
                    if data.get("_ban_detected"):
                        logger.error("Ban detected — aborting category", category=slug)
                        break

                    # Progress every 25 listings
                    if idx % 25 == 0:
                        logger.info(
                            "Progress",
                            category=slug,
                            done=idx,
                            total=len(all_urls),
                            written=cat_written,
                            errors=cat_errors,
                        )

                total_listings += cat_written

                logger.info(
                    "Category complete",
                    category=slug,
                    urls=len(all_urls),
                    written=cat_written,
                    errors=cat_errors,
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
