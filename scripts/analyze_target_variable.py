#!/usr/bin/env python3
"""Target Variable Labeling Analysis"""
import pandas as pd
from datetime import datetime

df = pd.read_csv('data/interim/merged_data.csv')
df['label_window_days'] = (pd.to_datetime(df['labeled_at']) - pd.to_datetime(df['scraped_at'])).dt.total_seconds() / 86400

print("\n" + "="*80)
print("TARGET VARIABLE LABELING ANALYSIS REPORT")
print("="*80)

print(f"\n📊 DATASET OVERVIEW")
print(f"   Total rows: {len(df)}")

print(f"\n🎯 TARGET VARIABLE DISTRIBUTION (sold_within_7_days)")
for val in [False, True]:
    count = (df['sold_within_7_days'] == val).sum()
    pct = 100 * count / len(df)
    print(f"   {val}: {count} ({pct:.1f}%)")

print(f"\n⏰ LABEL WINDOW STATISTICS (labeled_at - scraped_at)")
print(f"   Mean: {df['label_window_days'].mean():.2f} days")
print(f"   Median: {df['label_window_days'].median():.2f} days")
print(f"   Min: {df['label_window_days'].min():.2f} days")
print(f"   Max: {df['label_window_days'].max():.2f} days")
print(f"   Std: {df['label_window_days'].std():.2f} days")

# Anomalies
print(f"\n⚠️ ANOMALIES")
negative = (df['label_window_days'] < 0).sum()
too_early = (df['label_window_days'] < 3).sum()
too_late = (df['label_window_days'] > 15).sum()
print(f"   Negative window (labeled before scraped): {negative}")
print(f"   Too early re-check (< 3 days): {too_early}")
print(f"   Too late re-check (> 15 days): {too_late}")

print(f"\n🔍 COHORT ANALYSIS")
for cohort in sorted(df['cohort_id'].unique()):
    subset = df[df['cohort_id'] == cohort]
    sold = (subset['sold_within_7_days'] == True).sum()
    not_sold = (subset['sold_within_7_days'] == False).sum()
    na_count = subset['sold_within_7_days'].isna().sum()
    print(f"   {cohort}:")
    print(f"      Total: {len(subset)} listings")
    print(f"      Sold (True): {sold}")
    print(f"      Not sold (False): {not_sold}")
    print(f"      Unknown/NULL: {na_count}")
    print(f"      Avg label window: {subset['label_window_days'].mean():.2f} days")

# Training readiness
ready = df[(df['label_window_days'] >= 6) & (df['label_window_days'] <= 8) & (df['sold_within_7_days'].notna())]
print(f"\n✅ TRAINING READINESS")
print(f"   Rows with ideal label window (6-8 days) + valid target: {len(ready)} ({100*len(ready)/len(df):.1f}%)")

print("\n" + "="*80)
