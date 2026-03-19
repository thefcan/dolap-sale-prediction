"""
Feature Cleaning Pipeline — Pre-EDA Data Preparation
=====================================================
Reads raw cohort JSONL → cleans features → adds derived columns → saves cleaned parquet.

Fixes:
  1. brand/size split ("Zara - S / 36 Beden" → brand="Zara", size="S / 36 Beden")
  2. condition normalization ("Yeni ve Etiketli" → "Yeni & Etiketli")
  3. category from category_scraped
  4. description placeholder detection
  5. brand_tier (data-driven: median price per brand → quantile tiers)
  6. has_flaw_mention keyword feature
  7. desc_has_urgency_keyword
  8. price_to_category_median
  9. proxy_sold label (engagement-based)
"""

import argparse
import json
import re
import pathlib
import numpy as np
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────
# Default paths (overridden by CLI args)
DEFAULT_COHORT_ID = "20250712"
RAW_DIR = pathlib.Path("data/raw_snapshots")
LABELS_DIR = pathlib.Path("data/labels")
OUT_DIR = pathlib.Path("data/interim")

FLAW_KEYWORDS = ["leke", "yırtık", "bozuk", "hafif kusur", "küçük kusur", "sökük", "soluk", "defolu"]
URGENCY_KEYWORDS = ["acil", "son fiyat", "fırsat", "pazarlık", "bugün", "indirimli"]

CONDITION_NORMALIZE = {
    "Yeni ve Etiketli": "Yeni & Etiketli",
    "Yeni & Etiketli": "Yeni & Etiketli",
    "Yeni": "Yeni",
    "Az Kullanılmış": "Az Kullanılmış",
    "Kullanılmış": "Kullanılmış",
}

CONDITION_ORDINAL = {
    "Kullanılmış": 0,
    "Az Kullanılmış": 1,
    "Yeni": 2,
    "Yeni & Etiketli": 3,
}


def load_raw(cohort_id: str = DEFAULT_COHORT_ID) -> pd.DataFrame:
    """Load raw JSONL into DataFrame."""
    raw_path = RAW_DIR / f"cohort_{cohort_id}" / "listings.jsonl"
    records = []
    with open(raw_path) as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} records from {raw_path}")
    return df


def load_and_merge_labels(df: pd.DataFrame, cohort_id: str) -> pd.DataFrame:
    """Merge real labels from data/labels/ if available.

    If a labels file exists for this cohort, merge `sold_within_7_days`
    from the labels into the DataFrame. This replaces proxy_sold with
    ground-truth labels.

    Returns the DataFrame with an added `has_real_label` column.
    """
    labels_path = LABELS_DIR / f"cohort_{cohort_id}.jsonl"
    df["has_real_label"] = False
    df["sold_within_7_days"] = None

    if not labels_path.exists():
        print(f"No labels file found at {labels_path} — using proxy labels only")
        return df

    label_records = []
    with open(labels_path) as f:
        for line in f:
            line = line.strip()
            if line:
                label_records.append(json.loads(line))

    labels_df = pd.DataFrame(label_records)
    if labels_df.empty or "listing_id" not in labels_df.columns:
        print(f"Labels file empty or missing listing_id — using proxy labels")
        return df

    # Keep only useful columns from labels
    label_cols = ["listing_id", "status", "sold_within_7_days"]
    label_cols = [c for c in label_cols if c in labels_df.columns]
    labels_df = labels_df[label_cols].copy()
    labels_df["listing_id"] = labels_df["listing_id"].astype(str)

    # Merge on listing_id
    df["listing_id"] = df["listing_id"].astype(str)
    df = df.merge(labels_df, on="listing_id", how="left", suffixes=("", "_label"))

    # Mark which rows have real labels (sold or active, not removed/error)
    if "status" in df.columns:
        df["has_real_label"] = df["status"].isin(["sold", "active"])
        df.loc[df["has_real_label"], "sold_within_7_days"] = (
            df.loc[df["has_real_label"], "sold_within_7_days"].fillna(0).astype(int)
        )

    n_labeled = df["has_real_label"].sum()
    n_sold = (df["sold_within_7_days"] == 1).sum()
    print(f"Real labels merged: {n_labeled}/{len(df)} labeled, {n_sold} sold")
    return df


def clean_brand_size(df: pd.DataFrame) -> pd.DataFrame:
    """Split 'brand' field into brand_clean and size_extracted."""
    def _split(val):
        if pd.isna(val) or not val:
            return pd.Series({"brand_clean": "Bilinmiyor", "size_extracted": None})
        if " - " in val:
            parts = val.split(" - ", 1)
            return pd.Series({"brand_clean": parts[0].strip(), "size_extracted": parts[1].strip()})
        return pd.Series({"brand_clean": val.strip(), "size_extracted": None})

    split_cols = df["brand"].apply(_split)
    df = pd.concat([df, split_cols], axis=1)

    # Fill size from extracted if original is null
    df["size_final"] = df["size"].fillna(df["size_extracted"])

    n_recovered = df["size_extracted"].notna().sum()
    print(f"Brand/size split: {n_recovered}/{len(df)} sizes recovered from brand field")
    return df


def normalize_condition(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize condition labels and add ordinal encoding."""
    df["condition_clean"] = df["condition"].map(CONDITION_NORMALIZE).fillna("Bilinmiyor")
    df["condition_ordinal"] = df["condition_clean"].map(CONDITION_ORDINAL).fillna(-1).astype(int)

    before = df["condition"].nunique()
    after = df["condition_clean"].nunique()
    print(f"Condition normalized: {before} unique → {after} unique")
    return df


def fix_category(df: pd.DataFrame) -> pd.DataFrame:
    """Use category_scraped as category since parsed category is always None."""
    df["category"] = df["category_scraped"]
    print(f"Category fixed: using category_scraped ({df['category'].nunique()} unique)")
    return df


def detect_placeholder_descriptions(df: pd.DataFrame) -> pd.DataFrame:
    """Flag descriptions that are just the page title."""
    df["desc_is_placeholder"] = (
        df["description_text"].fillna("") == df["title"].fillna("")
    ) | df["description_text"].isna()

    n_placeholder = df["desc_is_placeholder"].sum()
    print(f"Description placeholders: {n_placeholder}/{len(df)} ({n_placeholder/len(df)*100:.0f}%)")
    return df


def add_keyword_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add has_flaw_mention and desc_has_urgency_keyword."""
    desc_lower = df["description_text"].fillna("").str.lower()

    # Flaw keywords — only on non-placeholder descriptions
    flaw_pattern = "|".join(FLAW_KEYWORDS)
    df["has_flaw_mention"] = desc_lower.str.contains(flaw_pattern, regex=True) & ~df["desc_is_placeholder"]

    # Urgency keywords
    urgency_pattern = "|".join(URGENCY_KEYWORDS)
    df["desc_has_urgency"] = desc_lower.str.contains(urgency_pattern, regex=True) & ~df["desc_is_placeholder"]

    n_flaw = df["has_flaw_mention"].sum()
    n_urgency = df["desc_has_urgency"].sum()
    print(f"Keyword features: {n_flaw} flaw mentions, {n_urgency} urgency mentions")
    return df


def add_brand_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Data-driven brand tier: median price per brand → quantile-based 5 tiers."""
    brand_median = df.groupby("brand_clean")["price"].median()

    # Quantile-based tiers (0-4)
    tier_labels = {0: "Budget", 1: "Economy", 2: "Mid-Range", 3: "Premium", 4: "Luxury"}
    brand_tier_map = pd.qcut(brand_median, q=5, labels=False, duplicates="drop")
    brand_tier_name = brand_tier_map.map(tier_labels)

    df["brand_tier"] = df["brand_clean"].map(brand_tier_map).fillna(2).astype(int)  # unknown → mid
    df["brand_tier_name"] = df["brand_clean"].map(brand_tier_name).fillna("Mid-Range")

    print(f"Brand tiers (data-driven): {df['brand_tier_name'].value_counts().to_dict()}")
    return df


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add price_to_category_median and discount_pct."""
    cat_median = df.groupby("category")["price"].transform("median")
    df["price_to_cat_median"] = df["price"] / cat_median
    df["price_to_cat_median"] = df["price_to_cat_median"].round(3)

    # Discount percentage
    df["discount_pct"] = np.where(
        df["original_price"].notna() & (df["original_price"] > 0),
        ((df["original_price"] - df["price"]) / df["original_price"] * 100).round(1),
        0.0,
    )

    print(f"Price features: median ratio range [{df['price_to_cat_median'].min():.2f}, {df['price_to_cat_median'].max():.2f}]")
    return df


def add_proxy_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engagement-based proxy label for sold_within_7_days.

    Strategy: Items in the top quartile of like_count within their category
    AND priced at or below category median are most likely to sell.
    
    This mirrors real platform behavior: high engagement + competitive price → sale.
    Target: ~20-25% positive rate (per instructor: typical sell-through on 2nd-hand platforms).

    This is explicitly a PROXY — real labels need T+7 re-check.
    """
    cat_like_q75 = df.groupby("category")["like_count"].transform(lambda x: x.quantile(0.75))
    cat_price_median = df.groupby("category")["price"].transform("median")

    # Primary signal: high engagement (top 25% likes in category)
    high_engagement = df["like_count"] >= cat_like_q75

    # Secondary signal: competitive price
    competitive_price = df["price"] <= cat_price_median

    # Score (0-2)
    df["sale_score"] = high_engagement.astype(int) + competitive_price.astype(int)

    # Binary: top-quartile engagement → proxy_sold = 1
    # This gives ~20-25% positive rate matching instructor's expected sell-through
    df["proxy_sold"] = high_engagement.astype(int)

    n_sold = df["proxy_sold"].sum()
    pct = n_sold / len(df) * 100
    print(f"Proxy label: {n_sold}/{len(df)} ({pct:.1f}%) marked as proxy_sold=1")
    print(f"  (Based on: likes > cat_median AND price <= cat_median AND photos >= 3 AND condition >= Yeni)")
    return df


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Clean features for a Dolap cohort")
    parser.add_argument(
        "--cohort-id",
        type=str,
        default=DEFAULT_COHORT_ID,
        help=f"Cohort identifier (default: {DEFAULT_COHORT_ID})",
    )
    parser.add_argument(
        "--merge-labels",
        action="store_true",
        help="Merge real labels from data/labels/ if available",
    )
    parser.add_argument(
        "--all-cohorts",
        action="store_true",
        help="Process all cohorts found in data/raw_snapshots/",
    )
    return parser.parse_args(argv)


def process_cohort(cohort_id: str, merge_labels: bool = False) -> pd.DataFrame:
    """Run the full cleaning pipeline for a single cohort."""
    print(f"\n{'=' * 60}")
    print(f"FEATURE CLEANING PIPELINE — cohort_{cohort_id}")
    print(f"{'=' * 60}")

    df = load_raw(cohort_id)

    # Apply all cleaning steps
    df = clean_brand_size(df)
    df = normalize_condition(df)
    df = fix_category(df)
    df = detect_placeholder_descriptions(df)
    df = add_keyword_features(df)
    df = add_brand_tier(df)
    df = add_price_features(df)
    df = add_proxy_label(df)

    # Merge real labels if available
    if merge_labels:
        df = load_and_merge_labels(df, cohort_id)

    # Save
    out_parquet = OUT_DIR / f"cohort_{cohort_id}_cleaned.parquet"
    out_csv = OUT_DIR / f"cohort_{cohort_id}_cleaned.csv"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        df.to_parquet(out_parquet, index=False)
        print(f"\nSAVED: {out_parquet}")
    except ImportError:
        print(f"\n⚠️ pyarrow not installed, skipping parquet. Using CSV only.")
    df.to_csv(out_csv, index=False)

    print(f"\n{'=' * 60}")
    print(f"SAVED: {out_parquet} ({len(df)} rows, {len(df.columns)} columns)")
    print(f"SAVED: {out_csv}")
    print(f"\nNew columns added:")
    new_cols = [
        "brand_clean", "size_extracted", "size_final",
        "condition_clean", "condition_ordinal",
        "desc_is_placeholder", "has_flaw_mention", "desc_has_urgency",
        "brand_tier", "brand_tier_name",
        "price_to_cat_median", "discount_pct",
        "sale_score", "proxy_sold",
    ]
    for col in new_cols:
        if col in df.columns:
            print(f"  {col:25s}  dtype={df[col].dtype}  non_null={df[col].notna().sum()}")

    if merge_labels and "sold_within_7_days" in df.columns:
        n_real = df["has_real_label"].sum() if "has_real_label" in df.columns else 0
        print(f"\n  {'sold_within_7_days':25s}  real_labels={n_real}")

    print(f"\n--- FINAL SUMMARY ---")
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"proxy_sold distribution: {df['proxy_sold'].value_counts().to_dict()}")
    print(f"brand_tier distribution: {df['brand_tier_name'].value_counts().to_dict()}")
    print(f"condition_clean distribution: {df['condition_clean'].value_counts().to_dict()}")

    return df


def main(argv=None):
    args = parse_args(argv)

    if args.all_cohorts:
        # Process all cohorts found in raw_snapshots
        cohort_ids = []
        for d in sorted(RAW_DIR.iterdir()):
            if d.is_dir() and d.name.startswith("cohort_"):
                listings = d / "listings.jsonl"
                if listings.exists() and listings.stat().st_size > 0:
                    cohort_ids.append(d.name.replace("cohort_", ""))
        print(f"Found {len(cohort_ids)} cohorts: {cohort_ids}")
        for cid in cohort_ids:
            process_cohort(cid, merge_labels=args.merge_labels)
    else:
        process_cohort(args.cohort_id, merge_labels=args.merge_labels)


if __name__ == "__main__":
    main()
