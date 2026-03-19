"""
Pipeline entrypoint: Label listings — 7-day sold-status re-check.

Re-visits listing URLs from a previously scraped cohort and determines
whether each listing was sold, is still active, or has been removed.

Usage::

    # Label a specific cohort
    python -m src.pipelines.label --cohort-id 20250712

    # Label with visible browser (debugging)
    python -m src.pipelines.label --cohort-id 20250712 --no-headless

    # Force re-label (overwrite existing)
    python -m src.pipelines.label --cohort-id 20250712 --force

    # Auto-detect cohorts ready for labeling (7+ days old)
    python -m src.pipelines.label --auto

The pipeline:
    1. Loads listing URLs from ``data/raw_snapshots/cohort_{id}/listings.jsonl``
    2. Re-visits each URL via Selenium
    3. Detects: "Satıldı" badge → sold | 404 → removed | still active → not sold
    4. Writes results to ``data/labels/cohort_{id}.jsonl``
    5. Writes summary to ``data/labels/cohort_{id}_summary.yaml``
    6. Updates SQLite cohort state → ``'labeled'``
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.labeling.labeler import CohortLabeler
from src.scraping.storage import CohortStateTracker
from src.utils.logger import get_logger, setup_logging


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime text into UTC-aware datetime."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_cohort_scrape_end(cohort_id: str, db_path: str) -> datetime | None:
    """Resolve cohort scrape end timestamp from DB/meta/listings fallback."""
    # 1) SQLite tracker (preferred)
    try:
        tracker = CohortStateTracker(db_path=db_path)
        row = tracker.get_cohort(cohort_id)
        tracker.close()
        scrape_end = _parse_iso_datetime((row or {}).get("scrape_end"))
        if scrape_end is not None:
            return scrape_end
    except Exception:
        pass

    cohort_dir = Path("data/raw_snapshots") / f"cohort_{cohort_id}"

    # 2) meta.yaml fallback
    meta_path = cohort_dir / "meta.yaml"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as fh:
                meta = yaml.safe_load(fh) or {}
            scrape_end = _parse_iso_datetime(meta.get("scrape_end"))
            if scrape_end is not None:
                return scrape_end
        except Exception:
            pass

    # 3) listings.jsonl fallback (max scraped_at)
    listings_path = cohort_dir / "listings.jsonl"
    if listings_path.exists():
        max_scraped_at: datetime | None = None
        with open(listings_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                scraped_at = _parse_iso_datetime(record.get("scraped_at"))
                if scraped_at is not None and (
                    max_scraped_at is None or scraped_at > max_scraped_at
                ):
                    max_scraped_at = scraped_at
        return max_scraped_at

    return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Label listings with 7-day sold status"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/scraping.yaml",
        help="Path to config YAML (labeling section)",
    )
    parser.add_argument(
        "--cohort-id",
        type=str,
        default=None,
        help="Cohort identifier to re-check (YYYYMMDD)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect cohorts ready for labeling (7+ days since scrape)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-label even if labels file already exists",
    )
    parser.add_argument(
        "--force-early-label",
        action="store_true",
        help="Allow labeling cohorts younger than 7 days (debug/emergency only)",
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
        "--db-path",
        type=str,
        default="data/dolap_state.db",
        help="Path to SQLite state database",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    setup_logging(level="INFO")
    logger = get_logger("pipeline.label")
    headless = not args.no_headless

    # ── Determine which cohorts to label ───────────────────────────────
    cohort_ids: list[str] = []

    if args.auto:
        # Auto-discover cohorts that are 7+ days old and not yet labeled
        logger.info("Auto-detecting cohorts ready for labeling...")
        tracker = CohortStateTracker(db_path=args.db_path)
        pending = tracker.pending_labeling(min_age_days=7)
        tracker.close()

        if pending:
            cohort_ids = [c["cohort_id"] for c in pending]
            logger.info(f"Found {len(cohort_ids)} cohorts ready for labeling", cohorts=cohort_ids)
        else:
            logger.info("No cohorts ready for labeling (need 7+ days since scrape)")
            # Fallback: check filesystem for unlabeled cohorts
            from src.scraping.storage import SnapshotWriter
            all_cohorts = SnapshotWriter.list_cohorts("data/raw_snapshots")
            labels_dir = Path("data/labels")
            for cid in all_cohorts:
                label_file = labels_dir / f"cohort_{cid}.jsonl"
                if not label_file.exists():
                    cohort_ids.append(cid)
                    logger.info(f"Found unlabeled cohort (filesystem): {cid}")
    elif args.cohort_id:
        cohort_ids = [args.cohort_id]
    else:
        logger.error("Specify --cohort-id or --auto")
        sys.exit(1)

    if not cohort_ids:
        logger.info("Nothing to label.")
        return

    # RC1 guard: do not label cohorts younger than 7 days unless explicitly forced
    eligible_cohorts: list[str] = []
    for cohort_id in cohort_ids:
        scrape_end = _read_cohort_scrape_end(cohort_id=cohort_id, db_path=args.db_path)
        if scrape_end is None:
            logger.warning(
                "Could not determine cohort scrape_end; allowing labeling",
                cohort_id=cohort_id,
            )
            eligible_cohorts.append(cohort_id)
            continue

        age_hours = (datetime.now(timezone.utc) - scrape_end).total_seconds() / 3600.0
        if age_hours < 168 and not args.force_early_label:
            logger.error(
                "Early-label guard blocked cohort (<7 days). "
                "Use --force-early-label to bypass.",
                cohort_id=cohort_id,
                age_hours=round(age_hours, 2),
            )
            continue

        if age_hours < 168 and args.force_early_label:
            logger.warning(
                "Bypassing early-label guard via --force-early-label",
                cohort_id=cohort_id,
                age_hours=round(age_hours, 2),
            )

        eligible_cohorts.append(cohort_id)

    cohort_ids = eligible_cohorts

    if not cohort_ids:
        logger.error("All requested cohorts were blocked by early-label guard.")
        sys.exit(1)

    # ── Label each cohort ──────────────────────────────────────────────
    for cohort_id in cohort_ids:
        logger.info(f"{'═' * 50}")
        logger.info(f"Labeling cohort: {cohort_id}")

        labeler = CohortLabeler(
            cohort_id=cohort_id,
            config_path=args.config,
            headless=headless,
            db_path=args.db_path,
        )

        try:
            labels_path = labeler.run(force=args.force)
            logger.info(f"Labels written to: {labels_path}")
        except FileNotFoundError as exc:
            logger.error(f"Cohort not found: {exc}")
            continue
        except ValueError as exc:
            logger.error(f"Labeling failed: {exc}")
            continue
        except Exception as exc:
            logger.error(f"Unexpected error labeling {cohort_id}: {exc}")
            continue

    logger.info("Labeling pipeline complete")


if __name__ == "__main__":
    main()
