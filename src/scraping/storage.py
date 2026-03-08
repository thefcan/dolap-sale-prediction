"""
Snapshot storage and cohort state tracking for Dolap scraper.

Two main components:

1. **SnapshotWriter** — manages cohort directories, writes listings as
   append-only JSONL files, generates ``meta.yaml`` summaries, and
   enforces the "never overwrite" rule.

2. **CohortStateTracker** — lightweight SQLite-backed registry that
   records when each cohort was scraped, how many listings were
   collected, duration, and current lifecycle status (scraped → labeled
   → merged).

Usage::

    from src.scraping.storage import SnapshotWriter, CohortStateTracker

    writer = SnapshotWriter("data/raw_snapshots", cohort_id="20260308")
    writer.append("kazak", {"listing_id": "123", "price": 249, ...})
    writer.finalise(category_stats={...}, duration=123.4)

    tracker = CohortStateTracker("data/dolap_state.db")
    tracker.register_cohort("20260308", total_listings=500, duration=123.4)
    tracker.list_cohorts()
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.utils.logger import get_logger


# ── Snapshot Writer ─────────────────────────────────────────────────────────


class SnapshotWriter:
    """Manages cohort directories and append-only JSONL snapshot files.

    Each scrape run = 1 cohort.  Inside a cohort directory every category
    gets its own JSONL file **and** all listings are mirrored into a
    combined ``listings.jsonl`` for easy downstream consumption.

    Directory layout::

        data/raw_snapshots/
        └── cohort_20260308/
            ├── kazak.jsonl          # per-category file
            ├── elbise.jsonl
            ├── listings.jsonl       # combined (all categories)
            └── meta.yaml            # summary

    Parameters
    ----------
    base_dir : str | Path
        Root snapshot directory (default: ``data/raw_snapshots``).
    cohort_id : str
        Cohort identifier, typically ``YYYYMMDD``.
    """

    def __init__(
        self,
        base_dir: str | Path = "data/raw_snapshots",
        cohort_id: str | None = None,
    ) -> None:
        self._cohort_id = cohort_id or datetime.now().strftime("%Y%m%d")
        self._base_dir = Path(base_dir)
        self._cohort_dir = self._base_dir / f"cohort_{self._cohort_id}"
        self._logger = get_logger("snapshot_writer")

        # Seen listing IDs for dedup within this session
        self._seen_ids: set[str] = set()
        self._category_counts: dict[str, int] = {}
        self._total_written: int = 0
        self._duplicates_skipped: int = 0

    # ── lifecycle ────────────────────────────────────────────────────────

    def setup(self) -> Path:
        """Create the cohort directory.  Returns its path.

        Safe to call multiple times (idempotent).
        """
        self._cohort_dir.mkdir(parents=True, exist_ok=True)
        self._logger.info(
            "Snapshot directory ready",
            cohort_id=self._cohort_id,
            path=str(self._cohort_dir),
        )
        return self._cohort_dir

    # ── writing ──────────────────────────────────────────────────────────

    def append(self, category_slug: str, record: dict[str, Any]) -> bool:
        """Append a single listing record to the category + combined JSONL.

        Duplicate ``listing_id`` values within the same session are
        silently skipped (first-seen wins).

        Parameters
        ----------
        category_slug : str
            Category that this listing was scraped from.
        record : dict
            Listing data dict (from ``parsers.parse_product_detail``).

        Returns
        -------
        bool
            ``True`` if the record was written, ``False`` if it was a
            duplicate.
        """
        listing_id = str(record.get("listing_id", ""))

        # Dedup guard
        if listing_id and listing_id in self._seen_ids:
            self._duplicates_skipped += 1
            return False
        if listing_id:
            self._seen_ids.add(listing_id)

        # Remove internal parser metadata from persisted data
        clean = {k: v for k, v in record.items() if not k.startswith("_")}

        # Ensure scrape metadata is present
        if "scraped_at" not in clean:
            clean["scraped_at"] = datetime.utcnow().isoformat()
        if "cohort_id" not in clean:
            clean["cohort_id"] = self._cohort_id
        if "category_scraped" not in clean:
            clean["category_scraped"] = category_slug

        line = json.dumps(clean, ensure_ascii=False) + "\n"

        # Write to per-category file (append-only)
        cat_path = self._cohort_dir / f"{category_slug}.jsonl"
        with open(cat_path, "a", encoding="utf-8") as fh:
            fh.write(line)

        # Write to combined listings file (append-only)
        combined_path = self._cohort_dir / "listings.jsonl"
        with open(combined_path, "a", encoding="utf-8") as fh:
            fh.write(line)

        # Bookkeeping
        self._category_counts[category_slug] = (
            self._category_counts.get(category_slug, 0) + 1
        )
        self._total_written += 1
        return True

    def append_batch(
        self, category_slug: str, records: list[dict[str, Any]]
    ) -> int:
        """Append multiple records.  Returns the number actually written."""
        written = 0
        for rec in records:
            if self.append(category_slug, rec):
                written += 1
        return written

    # ── finalisation ─────────────────────────────────────────────────────

    def finalise(
        self,
        *,
        scrape_start: str | None = None,
        scrape_end: str | None = None,
        duration_seconds: float | None = None,
        max_pages_per_category: int | None = None,
        config_path: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Path:
        """Write ``meta.yaml`` with cohort summary information.

        Returns the path to the meta file.
        """
        meta: dict[str, Any] = {
            "cohort_id": self._cohort_id,
            "scrape_start": scrape_start or datetime.utcnow().isoformat(),
            "scrape_end": scrape_end or datetime.utcnow().isoformat(),
            "duration_seconds": duration_seconds,
            "total_listings": self._total_written,
            "duplicates_skipped": self._duplicates_skipped,
            "categories": {
                slug: {"listings_written": count}
                for slug, count in self._category_counts.items()
            },
            "config_path": config_path,
            "max_pages_per_category": max_pages_per_category,
        }
        if extra:
            meta.update(extra)

        meta_path = self._cohort_dir / "meta.yaml"
        with open(meta_path, "w", encoding="utf-8") as fh:
            yaml.dump(meta, fh, default_flow_style=False, allow_unicode=True)

        self._logger.info(
            "Snapshot finalised",
            cohort_id=self._cohort_id,
            total_listings=self._total_written,
            duplicates_skipped=self._duplicates_skipped,
            categories=len(self._category_counts),
            meta_path=str(meta_path),
        )
        return meta_path

    # ── queries ──────────────────────────────────────────────────────────

    @property
    def cohort_dir(self) -> Path:
        return self._cohort_dir

    @property
    def cohort_id(self) -> str:
        return self._cohort_id

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "cohort_id": self._cohort_id,
            "total_written": self._total_written,
            "duplicates_skipped": self._duplicates_skipped,
            "categories": dict(self._category_counts),
        }

    @staticmethod
    def load_cohort(cohort_dir: str | Path) -> list[dict[str, Any]]:
        """Load all listings from a cohort's combined JSONL file.

        Parameters
        ----------
        cohort_dir : str | Path
            Path to the cohort directory (e.g. ``data/raw_snapshots/cohort_20260308``).

        Returns
        -------
        list[dict]
            List of listing dicts.
        """
        combined = Path(cohort_dir) / "listings.jsonl"
        if not combined.exists():
            return []
        records = []
        with open(combined, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    @staticmethod
    def list_cohorts(base_dir: str | Path = "data/raw_snapshots") -> list[str]:
        """List all cohort IDs found under *base_dir*.

        Returns sorted cohort IDs (e.g. ``['20260301', '20260308']``).
        """
        base = Path(base_dir)
        if not base.exists():
            return []
        cohorts = []
        for d in sorted(base.iterdir()):
            if d.is_dir() and d.name.startswith("cohort_"):
                cohort_id = d.name.replace("cohort_", "")
                cohorts.append(cohort_id)
        return cohorts


# ── Cohort State Tracker (SQLite) ───────────────────────────────────────────


class CohortStateTracker:
    """SQLite-backed registry for tracking cohort lifecycle.

    Stores:
    - When each cohort was scraped
    - How many listings were collected
    - Duration of the scrape
    - Current lifecycle status: ``scraped`` → ``labeled`` → ``merged``

    Parameters
    ----------
    db_path : str | Path
        Path to the SQLite database file.
    """

    _CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS cohorts (
        cohort_id       TEXT PRIMARY KEY,
        status          TEXT NOT NULL DEFAULT 'scraped',
        scrape_start    TEXT,
        scrape_end      TEXT,
        duration_seconds REAL,
        total_listings  INTEGER DEFAULT 0,
        categories      TEXT,
        label_date      TEXT,
        labeled_count   INTEGER DEFAULT 0,
        merge_date      TEXT,
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    );
    """

    def __init__(self, db_path: str | Path = "data/dolap_state.db") -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger("cohort_tracker")
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(self._CREATE_TABLE)
        self._conn.commit()
        self._logger.debug("CohortStateTracker ready", db=str(self._db_path))

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def __enter__(self) -> "CohortStateTracker":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ── registration ─────────────────────────────────────────────────────

    def register_cohort(
        self,
        cohort_id: str,
        *,
        total_listings: int = 0,
        duration_seconds: float | None = None,
        scrape_start: str | None = None,
        scrape_end: str | None = None,
        categories: list[str] | None = None,
    ) -> None:
        """Register a newly scraped cohort (or update if it exists)."""
        now = datetime.utcnow().isoformat()
        cats_json = json.dumps(categories) if categories else None

        self._conn.execute(
            """
            INSERT INTO cohorts (
                cohort_id, status, scrape_start, scrape_end,
                duration_seconds, total_listings, categories,
                created_at, updated_at
            ) VALUES (?, 'scraped', ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cohort_id) DO UPDATE SET
                status = 'scraped',
                scrape_start = excluded.scrape_start,
                scrape_end = excluded.scrape_end,
                duration_seconds = excluded.duration_seconds,
                total_listings = excluded.total_listings,
                categories = excluded.categories,
                updated_at = excluded.updated_at
            """,
            (
                cohort_id, scrape_start, scrape_end,
                duration_seconds, total_listings, cats_json,
                now, now,
            ),
        )
        self._conn.commit()
        self._logger.info(
            "Cohort registered",
            cohort_id=cohort_id,
            total_listings=total_listings,
            duration=duration_seconds,
        )

    def update_status(self, cohort_id: str, status: str, **kwargs: Any) -> None:
        """Update a cohort's lifecycle status.

        Parameters
        ----------
        cohort_id : str
        status : str
            One of ``'scraped'``, ``'labeled'``, ``'merged'``.
        **kwargs
            Additional columns to update (e.g. ``label_date``,
            ``labeled_count``, ``merge_date``).
        """
        now = datetime.utcnow().isoformat()
        sets = ["status = ?", "updated_at = ?"]
        vals: list[Any] = [status, now]

        for col, val in kwargs.items():
            sets.append(f"{col} = ?")
            vals.append(val)

        vals.append(cohort_id)
        sql = f"UPDATE cohorts SET {', '.join(sets)} WHERE cohort_id = ?"
        self._conn.execute(sql, vals)
        self._conn.commit()
        self._logger.info("Cohort status updated", cohort_id=cohort_id, status=status)

    # ── queries ──────────────────────────────────────────────────────────

    def get_cohort(self, cohort_id: str) -> dict[str, Any] | None:
        """Retrieve a single cohort record."""
        row = self._conn.execute(
            "SELECT * FROM cohorts WHERE cohort_id = ?", (cohort_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_cohorts(self, status: str | None = None) -> list[dict[str, Any]]:
        """List all cohorts, optionally filtered by status."""
        if status:
            rows = self._conn.execute(
                "SELECT * FROM cohorts WHERE status = ? ORDER BY cohort_id",
                (status,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM cohorts ORDER BY cohort_id"
            ).fetchall()
        return [dict(r) for r in rows]

    def pending_labeling(self, min_age_days: int = 7) -> list[dict[str, Any]]:
        """Return cohorts that were scraped at least *min_age_days* ago
        but have not yet been labeled.

        Useful for the labeling pipeline to discover which cohorts are
        ready for the 7-day re-check.
        """
        rows = self._conn.execute(
            """
            SELECT * FROM cohorts
            WHERE status = 'scraped'
              AND scrape_end IS NOT NULL
              AND julianday('now') - julianday(scrape_end) >= ?
            ORDER BY cohort_id
            """,
            (min_age_days,),
        ).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> dict[str, Any]:
        """Return an aggregate summary of all cohorts."""
        row = self._conn.execute(
            """
            SELECT
                COUNT(*) as total_cohorts,
                SUM(CASE WHEN status = 'scraped' THEN 1 ELSE 0 END) as scraped,
                SUM(CASE WHEN status = 'labeled' THEN 1 ELSE 0 END) as labeled,
                SUM(CASE WHEN status = 'merged'  THEN 1 ELSE 0 END) as merged,
                SUM(total_listings) as total_listings,
                SUM(duration_seconds) as total_duration
            FROM cohorts
            """,
        ).fetchone()
        return dict(row) if row else {}
