"""
Batch labeling orchestrator — 7-day re-check for Dolap.com cohorts.

Reads listing URLs from a scraped cohort's ``listings.jsonl``, re-visits
each URL via :class:`StatusChecker`, and writes labeled output to
``data/labels/cohort_{id}.jsonl``.

Usage::

    from src.labeling.labeler import CohortLabeler

    labeler = CohortLabeler(cohort_id="20250712")
    labeler.run()
    # → data/labels/cohort_20250712.jsonl
    # → data/labels/cohort_20250712_summary.yaml
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.labeling.status_checker import StatusChecker
from src.scraping.storage import CohortStateTracker, SnapshotWriter
from src.utils.logger import get_logger


class CohortLabeler:
    """Orchestrate the 7-day sold-status re-check for a scraped cohort.

    Workflow:
      1. Load listing URLs + IDs from ``data/raw_snapshots/cohort_{id}/listings.jsonl``
      2. Re-visit each URL with ``StatusChecker``
      3. Write per-listing result to ``data/labels/cohort_{id}.jsonl``
      4. Write summary to ``data/labels/cohort_{id}_summary.yaml``
      5. Update ``CohortStateTracker`` status → ``'labeled'``

    Parameters
    ----------
    cohort_id : str
        Cohort identifier (e.g. ``'20250712'``).
    snapshots_dir : str | Path
        Root directory for raw snapshots.
    labels_dir : str | Path
        Root directory for label output.
    config_path : str
        Path to ``scraping.yaml`` (used for Selenium config).
    headless : bool
        Run browser without visible window.
    db_path : str
        Path to SQLite state DB.
    """

    def __init__(
        self,
        cohort_id: str,
        snapshots_dir: str | Path = "data/raw_snapshots",
        labels_dir: str | Path = "data/labels",
        config_path: str = "configs/scraping.yaml",
        headless: bool = True,
        db_path: str = "data/dolap_state.db",
    ) -> None:
        self.cohort_id = cohort_id
        self.snapshots_dir = Path(snapshots_dir)
        self.labels_dir = Path(labels_dir)
        self.config_path = config_path
        self.headless = headless
        self.db_path = db_path
        self.logger = get_logger("labeler")

        # Paths
        self.cohort_dir = self.snapshots_dir / f"cohort_{cohort_id}"
        self.listings_file = self.cohort_dir / "listings.jsonl"
        self.labels_file = self.labels_dir / f"cohort_{cohort_id}.jsonl"
        self.summary_file = self.labels_dir / f"cohort_{cohort_id}_summary.yaml"

    def load_listings(self) -> list[dict[str, Any]]:
        """Load listing records from the cohort's combined JSONL."""
        if not self.listings_file.exists():
            raise FileNotFoundError(
                f"Cohort listings not found: {self.listings_file}"
            )
        records = []
        with open(self.listings_file, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        self.logger.info(
            "Loaded listings for labeling",
            cohort_id=self.cohort_id,
            count=len(records),
        )
        return records

    def run(self, force: bool = False) -> Path:
        """Execute the full labeling pipeline.

        Parameters
        ----------
        force : bool
            If ``True``, overwrite existing labels file.

        Returns
        -------
        Path
            Path to the output labels JSONL file.
        """
        # Guard: don't re-label unless forced
        if self.labels_file.exists() and not force:
            self.logger.warning(
                "Labels already exist — use force=True to overwrite",
                labels_file=str(self.labels_file),
            )
            return self.labels_file

        # 1. Load listings
        listings = self.load_listings()
        urls = []
        for rec in listings:
            url = rec.get("url", "")
            if url:
                urls.append(url)

        if not urls:
            self.logger.error("No URLs found in listings file")
            raise ValueError("No URLs to check")

        self.logger.info(
            "Starting labeling run",
            cohort_id=self.cohort_id,
            total_urls=len(urls),
        )

        # 2. Create output directory
        self.labels_dir.mkdir(parents=True, exist_ok=True)

        # 3. Clear existing labels file if force
        if self.labels_file.exists() and force:
            self.labels_file.unlink()

        # 4. Run status checks
        start_time = datetime.utcnow()
        results: list[dict[str, Any]] = []

        with StatusChecker(
            config_path=self.config_path,
            headless=self.headless,
        ) as checker:
            for idx, url in enumerate(urls, 1):
                self.logger.info(f"[{idx}/{len(urls)}] Checking", url=url[:80])

                result = checker.check(url)

                # Enrich with original listing data
                original = listings[idx - 1]
                result["original_price"] = original.get("price")
                result["category"] = original.get("category_scraped", original.get("category"))
                result["brand"] = original.get("brand")
                result["cohort_id"] = self.cohort_id

                results.append(result)

                # Stream to JSONL (one line at a time for crash safety)
                with open(self.labels_file, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(result, ensure_ascii=False) + "\n")

                # Abort on ban
                if result.get("error_detail") == "ban_detected":
                    self.logger.error("Ban detected — aborting labeling")
                    break

                # Progress every 50 listings
                if idx % 50 == 0:
                    self.logger.info(
                        "Labeling progress",
                        done=idx,
                        total=len(urls),
                        stats=checker.stats,
                    )

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # 5. Write summary
        summary = self._build_summary(results, start_time, end_time, duration)
        with open(self.summary_file, "w", encoding="utf-8") as fh:
            yaml.dump(summary, fh, default_flow_style=False, allow_unicode=True)

        self.logger.info(
            "Labeling complete",
            cohort_id=self.cohort_id,
            total=len(results),
            sold=summary["sold"],
            active=summary["active"],
            removed=summary["removed"],
            errors=summary["errors"],
            duration_seconds=duration,
        )

        # 6. Update cohort state in SQLite
        try:
            tracker = CohortStateTracker(db_path=self.db_path)
            tracker.update_status(
                self.cohort_id,
                status="labeled",
                label_date=end_time.isoformat(),
                labeled_count=len(results),
            )
            tracker.close()
        except Exception as exc:
            self.logger.warning(
                "Failed to update cohort tracker (non-critical)",
                error=str(exc)[:120],
            )

        return self.labels_file

    def _build_summary(
        self,
        results: list[dict[str, Any]],
        start: datetime,
        end: datetime,
        duration: float,
    ) -> dict[str, Any]:
        """Build a YAML-serializable summary of the labeling run."""
        status_counts = {"sold": 0, "active": 0, "removed": 0, "error": 0}
        for r in results:
            s = r.get("status", "error")
            if s in status_counts:
                status_counts[s] += 1
            else:
                status_counts["error"] += 1

        # Per-category breakdown
        cat_breakdown: dict[str, dict[str, int]] = {}
        for r in results:
            cat = r.get("category", "unknown") or "unknown"
            if cat not in cat_breakdown:
                cat_breakdown[cat] = {"sold": 0, "active": 0, "removed": 0, "error": 0}
            s = r.get("status", "error")
            if s in cat_breakdown[cat]:
                cat_breakdown[cat][s] += 1

        total = len(results)
        labeled_valid = status_counts["sold"] + status_counts["active"]
        sell_rate = (status_counts["sold"] / labeled_valid * 100) if labeled_valid > 0 else 0.0

        return {
            "cohort_id": self.cohort_id,
            "label_start": start.isoformat(),
            "label_end": end.isoformat(),
            "duration_seconds": round(duration, 2),
            "total_checked": total,
            "sold": status_counts["sold"],
            "active": status_counts["active"],
            "removed": status_counts["removed"],
            "errors": status_counts["error"],
            "labeled_valid": labeled_valid,
            "sell_rate_pct": round(sell_rate, 1),
            "category_breakdown": cat_breakdown,
        }
