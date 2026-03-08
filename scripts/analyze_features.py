"""Analyze feature quality issues in cohort data."""
import json
from collections import Counter

records = []
with open("data/raw_snapshots/cohort_20250712/listings.jsonl") as f:
    for line in f:
        records.append(json.loads(line))

# 1. Brand field has size mixed in
brands_raw = [r["brand"] for r in records if r["brand"]]
print("=== BRAND field samples (first 20 unique) ===")
for b in sorted(set(brands_raw))[:20]:
    print(f"  {b}")
print(f"\nUnique raw brand values: {len(set(brands_raw))}")

# Can we split brand from size?
print("\n=== Brand/Size split attempt ===")
for b in list(set(brands_raw))[:10]:
    if " - " in b:
        parts = b.split(" - ", 1)
        print(f"  '{b}' -> brand='{parts[0]}', size='{parts[1]}'")
    else:
        print(f"  '{b}' -> brand='{b}', size=None")

# 2. Null fields
print(f"\n=== Null field analysis ===")
print(f"  category always None: {all(r['category'] is None for r in records)}")
print(f"  subcategory always None: {all(r['subcategory'] is None for r in records)}")
print(f"  size None: {sum(1 for r in records if r['size'] is None)} / {len(records)}")
print(f"  is_sold always False: {all(not r['is_sold'] for r in records)}")
print(f"  original_price None: {sum(1 for r in records if r['original_price'] is None)} / {len(records)}")

# 3. Description quality
same_as_title = sum(1 for r in records if r["description_text"] == r["title"])
print(f"\n=== Description quality ===")
print(f"  description_text == title: {same_as_title}/{len(records)}")
print(f"  description_text is None: {sum(1 for r in records if r['description_text'] is None)}/{len(records)}")

# 4. Unique brands after split
clean_brands = []
sizes_from_brand = []
for r in records:
    b = r["brand"] or ""
    if " - " in b:
        parts = b.split(" - ", 1)
        clean_brands.append(parts[0].strip())
        sizes_from_brand.append(parts[1].strip())
    else:
        clean_brands.append(b.strip())
        sizes_from_brand.append(None)

print(f"\n=== After brand/size split ===")
print(f"  Unique clean brands: {len(set(clean_brands))}")
print(f"  Top 15 brands:")
for brand, cnt in Counter(clean_brands).most_common(15):
    print(f"    {brand}: {cnt}")
print(f"\n  Sizes extracted: {sum(1 for s in sizes_from_brand if s)} / {len(records)}")
print(f"  Top 10 sizes:")
for sz, cnt in Counter(s for s in sizes_from_brand if s).most_common(10):
    print(f"    {sz}: {cnt}")

# 5. condition normalization issue
print(f"\n=== Condition values ===")
for c, cnt in Counter(r["condition"] for r in records).most_common():
    print(f"  '{c}': {cnt}")

# 6. color distribution
print(f"\n=== Color distribution (top 10) ===")
for c, cnt in Counter(r["color"] for r in records if r["color"]).most_common(10):
    print(f"  {c}: {cnt}")

# 7. category_scraped as proxy for category
print(f"\n=== category_scraped distribution ===")
for c, cnt in Counter(r["category_scraped"] for r in records).most_common():
    print(f"  {c}: {cnt}")
