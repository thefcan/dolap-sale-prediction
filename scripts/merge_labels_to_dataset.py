#!/usr/bin/env python3
"""
Merge newly labeled data into merged_data.csv — update sold_within_7_days for all rows.

After labeling campaign completes, this script:
1. Loads updated label files from data/labels/
2. Left-joins labels onto merged_data
3. Updates has_real_label, sold_within_7_days, label_status columns
4. Saves merged_data_v2.csv as new canonical dataset
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np


def load_labels(labels_dir: Path = Path("data/labels")) -> pd.DataFrame:
    """Load all label JSONL files and combine into DataFrame."""
    all_labels = []
    
    for label_file in sorted(labels_dir.glob("cohort_*.jsonl")):
        if label_file.name.endswith("_summary.yaml"):
            continue
        
        cohort_id = label_file.stem.replace("cohort_", "")
        with open(label_file) as f:
            for line in f:
                record = json.loads(line)
                record["cohort_id_label"] = cohort_id
                all_labels.append(record)
    
    labels_df = pd.DataFrame(all_labels)
    print(f"✓ Loaded {len(labels_df)} labeled records from {len(list(labels_dir.glob('cohort_*.jsonl')))} files")
    
    return labels_df


def merge_and_update(merged_csv: Path = Path("data/interim/merged_data.csv")) -> None:
    """Main merge & update workflow."""
    
    # Load current merged data
    df = pd.read_csv(merged_csv)
    print(f"Loaded merged_data.csv: {df.shape}")
    
    # Load new labels
    labels_df = load_labels()
    
    # Select relevant columns from labels
    labels_subset = labels_df[["listing_id", "sold_within_7_days", "status", "checked_at"]].copy()
    labels_subset.rename(columns={
        "sold_within_7_days": "sold_within_7_days_new",
        "status": "label_status_new",
        "checked_at": "checked_at_new"
    }, inplace=True)
    
    # Left join labels onto df
    df_merged = df.merge(
        labels_subset,
        on="listing_id",
        how="left"
    )
    
    # Update target columns where new labels exist
    df_merged["sold_within_7_days_updated"] = df_merged["sold_within_7_days_new"].fillna(df_merged["sold_within_7_days"])
    df_merged["has_real_label_updated"] = df_merged["sold_within_7_days_new"].notna().astype(int)
    df_merged["label_status_updated"] = df_merged["label_status_new"].fillna(df_merged["label_status"])
    
    # Count updates
    newly_labeled = df_merged["sold_within_7_days_new"].notna().sum()
    print(f"\n✓ Newly labeled: {newly_labeled}")
    print(f"  Before: {df['sold_within_7_days'].notna().sum()} labeled")
    print(f"  After: {df_merged['sold_within_7_days_updated'].notna().sum()} labeled")
    
    # Final dataset: keep original columns + update key ones
    df_final = df.copy()
    df_final["sold_within_7_days"] = df_merged["sold_within_7_days_updated"]
    df_final["has_real_label"] = df_merged["has_real_label_updated"]
    df_final["label_status"] = df_merged["label_status_updated"]
    if "checked_at_new" in df_merged.columns:
        df_final["checked_at"] = df_merged["checked_at_new"].fillna(df_final["checked_at"])
    
    # Save
    output_path = Path("data/interim/merged_data_labeled.csv")
    df_final.to_csv(output_path, index=False)
    print(f"\n✓ Saved {output_path}: {df_final.shape}")
    
    # Statistics
    labeled = df_final["sold_within_7_days"].notna().sum()
    sold = (df_final["sold_within_7_days"] == 1).sum()
    print(f"\nFinal target stats:")
    print(f"  Total: {len(df_final)}")
    print(f"  Labeled: {labeled} ({100*labeled/len(df_final):.1f}%)")
    print(f"  Sold (in labeled): {sold} ({100*sold/max(1,labeled):.1f}%)")
    print(f"  Not sold (in labeled): {labeled - sold} ({100*(labeled-sold)/max(1,labeled):.1f}%)")


if __name__ == "__main__":
    merge_and_update()
