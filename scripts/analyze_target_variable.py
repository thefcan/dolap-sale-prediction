#!/usr/bin/env python3
"""Target variable QC analysis with schema fallbacks.

Reads canonical ``data/interim/merged_data.csv`` and reports:
- label coverage
- sold/not-sold distribution
- window QC metrics (valid/early/late) using labeled_at or checked_at
- per-cohort label coverage
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

INPUT_PATH = Path("data/interim/merged_data.csv")
OUT_PATH = Path("artifacts/metrics/target_variable_report.json")


def _get_label_timestamp(df: pd.DataFrame) -> pd.Series:
    if "labeled_at" in df.columns:
        ts = pd.to_datetime(df["labeled_at"], errors="coerce", utc=True)
        if ts.notna().sum() > 0:
            return ts
    if "checked_at" in df.columns:
        return pd.to_datetime(df["checked_at"], errors="coerce", utc=True)
    return pd.Series([pd.NaT] * len(df), index=df.index)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    df["scraped_at"] = pd.to_datetime(df.get("scraped_at"), errors="coerce", utc=True)
    label_ts = _get_label_timestamp(df)
    target = pd.to_numeric(df.get("sold_within_7_days"), errors="coerce")

    window_hours = (label_ts - df["scraped_at"]).dt.total_seconds() / 3600.0
    window_valid = window_hours.notna()

    valid_window_count = int(((window_hours >= 168) & (window_hours <= 192)).sum())
    early_window_count = int((window_hours < 168).sum())
    late_window_count = int((window_hours > 192).sum())
    non_null_window_count = int(window_valid.sum())
    early_window_ratio = (
        round(early_window_count / non_null_window_count, 4)
        if non_null_window_count > 0
        else 0.0
    )

    target_non_null = int(target.notna().sum())
    total_rows = int(len(df))

    report = {
        "total_rows": total_rows,
        "cohort_count": int(df["cohort_id"].astype(str).nunique()) if "cohort_id" in df.columns else 0,
        "target_non_null": target_non_null,
        "target_null": int(target.isna().sum()),
        "target_distribution_non_null": {str(k): int(v) for k, v in target.dropna().value_counts().to_dict().items()},
        "window_non_null": non_null_window_count,
        "valid_window_count": valid_window_count,
        "early_window_count": early_window_count,
        "late_window_count": late_window_count,
        "early_window_ratio": early_window_ratio,
    }

    if "cohort_id" in df.columns:
        cohort_stats = {}
        for cid, g in df.groupby("cohort_id"):
            t = pd.to_numeric(g.get("sold_within_7_days"), errors="coerce")
            cohort_stats[str(cid)] = {
                "rows": int(len(g)),
                "target_non_null": int(t.notna().sum()),
                "target_null": int(t.isna().sum()),
            }
        report["cohort_stats"] = cohort_stats

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 80)
    print("TARGET VARIABLE QC REPORT")
    print("=" * 80)
    print(f"rows: {report['total_rows']}")
    print(f"target_non_null: {report['target_non_null']}")
    print(f"target_null: {report['target_null']}")
    print(f"valid_window_count: {report['valid_window_count']}")
    print(f"early_window_count: {report['early_window_count']}")
    print(f"early_window_ratio: {report['early_window_ratio']}")
    print(f"report_saved_to: {OUT_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
