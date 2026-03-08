"""Quick validation of cohort data quality."""
import json
from collections import Counter

records = []
with open("data/raw_snapshots/cohort_20250712/listings.jsonl") as f:
    for line in f:
        records.append(json.loads(line))

print(f"Total records: {len(records)}")

# Field coverage
fields = {}
for r in records:
    for k, v in r.items():
        if k not in fields:
            fields[k] = {"total": 0, "null": 0, "non_null": 0}
        fields[k]["total"] += 1
        if v is None:
            fields[k]["null"] += 1
        else:
            fields[k]["non_null"] += 1

print("\nField coverage:")
for k, v in sorted(fields.items()):
    pct = v["non_null"] / v["total"] * 100
    print(f"  {k:25s} non_null={v['non_null']:4d}  null={v['null']:4d}  ({pct:.0f}%)")

# Price & like distributions
prices = [r["price"] for r in records if r["price"] is not None]
likes = [r["like_count"] for r in records if r["like_count"] is not None]
sold = sum(1 for r in records if r.get("is_sold"))

print(f"\nPrice: min={min(prices):.0f}, max={max(prices):.0f}, avg={sum(prices)/len(prices):.0f}")
print(f"Likes: min={min(likes)}, max={max(likes)}, avg={sum(likes)/len(likes):.1f}")
print(f"Sold count: {sold}/{len(records)} ({sold/len(records)*100:.1f}%)")

# Unique sellers
sellers = set(r["seller_username"] for r in records if r["seller_username"])
print(f"Unique sellers: {len(sellers)}")

# Category breakdown
cats = Counter(r["category_scraped"] for r in records)
print(f"\nCategory breakdown: {dict(cats)}")

# Brand distribution (top 10)
brands = Counter(r.get("brand", "N/A") for r in records)
print(f"\nTop 10 brands:")
for brand, cnt in brands.most_common(10):
    print(f"  {brand}: {cnt}")

# Condition distribution
conds = Counter(r.get("condition", "N/A") for r in records)
print(f"\nCondition distribution:")
for c, cnt in conds.most_common():
    print(f"  {c}: {cnt}")
