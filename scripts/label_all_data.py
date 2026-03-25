#!/usr/bin/env python3
"""
Label all unlabeled listings in merged_data.csv.
- Reads unlabeled rows from merged_data.csv
- Re-checks listing URLs via Selenium
- Updates merged_data.csv with sold_within_7_days status
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.labeling.status_checker import StatusChecker
from src.utils.logger import get_logger, setup_logging

setup_logging(level="INFO")
logger = get_logger("label_all_data")


def main():
    merged_path = Path("data/interim/merged_data.csv")
    
    if not merged_path.exists():
        logger.error(f"merged_data.csv not found: {merged_path}")
        sys.exit(1)
    
    # Load data
    df = pd.read_csv(merged_path)
    logger.info(f"Loaded: {len(df)} rows")
    
    # Identify unlabeled
    unlabeled_mask = df['sold_within_7_days'].isna()
    unlabeled_df = df[unlabeled_mask].copy()
    labeled_df = df[~unlabeled_mask].copy()
    
    logger.info(f"Already labeled: {len(labeled_df)}")
    logger.info(f"Need labeling: {len(unlabeled_df)}")
    
    if len(unlabeled_df) == 0:
        logger.info("✅ All rows already labeled!")
        return
    
    # Re-check unlabeled
    with StatusChecker(headless=True) as checker:
        checker.start()
        results = []
        
        for num, (idx, row) in enumerate(unlabeled_df.iterrows()):
            listing_id = row['listing_id']
            url = row['url']
            
            try:
                result = checker.check(url)
                results.append({
                    'index': idx,
                    'listing_id': listing_id,
                    'status': result['status'],
                    'sold': result['sold_within_7_days']
                })
                
                if (num % 100) == 0 and num > 0:
                    logger.info(f"Progress: {num} / {len(unlabeled_df)}")
            
            except Exception as e:
                logger.warning(f"Error checking {listing_id}: {e}")
                results.append({
                    'index': idx,
                    'listing_id': listing_id,
                    'status': 'error',
                    'sold': None
                })
    
    # Update dataframe
    for result in results:
        idx = result['index']
        if result['sold'] is not None:
            df.loc[idx, 'sold_within_7_days'] = float(result['sold'])
            df.loc[idx, 'status'] = result['status']
    
    # Save
    df.to_csv(merged_path, index=False)
    logger.info(f"✅ Saved updated: {merged_path}")
    
    # Summary
    final_labeled = df['sold_within_7_days'].notna().sum()
    final_unlabeled = df['sold_within_7_days'].isna().sum()
    print(f"\n{'='*60}")
    print(f"FINAL LABEL STATUS:")
    print(f"  Total rows: {len(df):,}")
    print(f"  Labeled:    {final_labeled:,} ({final_labeled*100/len(df):.1f}%)")
    print(f"  Unlabeled:  {final_unlabeled:,} ({final_unlabeled*100/len(df):.1f}%)")
    
    if final_labeled > 0:
        labeled_subset = df[df['sold_within_7_days'].notna()]
        sold = (labeled_subset['sold_within_7_days'] == 1).sum()
        not_sold = (labeled_subset['sold_within_7_days'] == 0).sum()
        print(f"\n  Among labeled:")
        print(f"    Sold:     {sold:,} ({sold*100/final_labeled:.2f}%)")
        print(f"    Not Sold: {not_sold:,} ({not_sold*100/final_labeled:.2f}%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
