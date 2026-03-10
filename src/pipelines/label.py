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
import sys
from datetime import datetime
from pathlib import Path

from src.labeling.labeler import CohortLabeler
from src.scraping.storage import CohortStateTracker
from src.utils.logger import get_logger, setup_logging


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
