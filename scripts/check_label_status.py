#!/usr/bin/env python3
"""
Quick test: Show current labeled vs unlabeled breakdown in merged_data.csv
"""

import pandas as pd

df = pd.read_csv("data/interim/merged_data.csv")

print("="*70)
print("CURRENT DATA STATUS")
print("="*70)

print(f"\nTotal rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# Current label status
labeled = df['sold_within_7_days'].notna().sum()
unlabeled = df['sold_within_7_days'].isna().sum()

print(f"\n📊 LABELING STATUS:")
print(f"  Labeled:   {labeled:,} ({100*labeled/len(df):.1f}%)")
print(f"  Unlabeled: {unlabeled:,} ({100*unlabeled/len(df):.1f}%)")

# Among labeled
if labeled > 0:
    sold = (df['sold_within_7_days'] == 1).sum()
    not_sold = (df['sold_within_7_days'] == 0).sum()
    print(f"\n📈 CLASS DISTRIBUTION (among {labeled:,} labeled):")
    print(f"  Sold (1):     {sold:,} ({100*sold/labeled:.1f}%)")
    print(f"  Not sold (0): {not_sold:,} ({100*not_sold/labeled:.1f}%)")

# By cohort
print(f"\n🏢 BY COHORT:")
cohort_status = df.groupby('cohort_id').agg({
    'sold_within_7_days': ['count', lambda x: x.notna().sum()]
}).round(0)
cohort_status.columns = ['total', 'labeled']
cohort_status['unlabeled'] = cohort_status['total'] - cohort_status['labeled']
print(cohort_status)

print("\n" + "="*70)
print("✓ Data ready for EDA with real labels")
print("="*70)
