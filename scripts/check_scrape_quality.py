"""cohort_20260311 scrape kalite kontrolü."""
import json
from collections import Counter

with open("data/raw_snapshots/cohort_20260311/listings.jsonl") as f:
    listings = [json.loads(line) for line in f]

print(f"Toplam listing: {len(listings)}")

# description_text alanını kontrol et
desc_text = sum(1 for l in listings if l.get("description_text") and l.get("description_text") != "")
print(f"description_text doluluk: {desc_text} / {len(listings)} ({desc_text/len(listings)*100:.1f}%)")

# original_price
has_discount = sum(1 for l in listings if l.get("has_discount"))
print(f"has_discount=True: {has_discount} / {len(listings)} ({has_discount/len(listings)*100:.1f}%)")

# is_sold dağılımı
sold = sum(1 for l in listings if l.get("is_sold"))
print(f"is_sold=True: {sold} / {len(listings)} ({sold/len(listings)*100:.1f}%)")

# Kategori dağılımı
cats = Counter(l["category"] for l in listings)
print("\n=== KATEGORİ DAĞILIMI ===")
for cat, cnt in cats.most_common():
    print(f"  {cat:20s}: {cnt:4d}")

# Brand top 15
brands = Counter(l["brand"] for l in listings)
print("\n=== TOP 15 MARKA ===")
for brand, cnt in brands.most_common(15):
    print(f"  {brand:20s}: {cnt:4d}")

# Fiyat istatistikleri
prices = [l["price"] for l in listings if l.get("price")]
print(f"\n=== FİYAT İSTATİSTİKLERİ ===")
print(f"  Min: {min(prices):.0f} TL")
print(f"  Max: {max(prices):.0f} TL")
print(f"  Ortalama: {sum(prices)/len(prices):.0f} TL")
sorted_prices = sorted(prices)
print(f"  Medyan: {sorted_prices[len(sorted_prices)//2]:.0f} TL")

# Condition dağılımı
conditions = Counter(l["condition"] for l in listings)
print("\n=== DURUM (CONDITION) DAĞILIMI ===")
for cond, cnt in conditions.most_common():
    print(f"  {cond:25s}: {cnt:4d}")

# Size doluluk
size_filled = sum(1 for l in listings if l.get("size"))
print(f"\nsize doluluk: {size_filled} / {len(listings)} ({size_filled/len(listings)*100:.1f}%)")

# Color doluluk
color_filled = sum(1 for l in listings if l.get("color"))
print(f"color doluluk: {color_filled} / {len(listings)} ({color_filled/len(listings)*100:.1f}%)")

# Like count dağılımı
likes = [l["like_count"] for l in listings]
print(f"\n=== BEĞENİ İSTATİSTİKLERİ ===")
print(f"  Min: {min(likes)}")
print(f"  Max: {max(likes)}")
print(f"  Ortalama: {sum(likes)/len(likes):.1f}")
print(f"  0 beğeni: {sum(1 for x in likes if x == 0)}")

# Photo count
photos = [l["photo_count"] for l in listings]
print(f"\n=== FOTOĞRAF İSTATİSTİKLERİ ===")
print(f"  Min: {min(photos)}")
print(f"  Max: {max(photos)}")
print(f"  Ortalama: {sum(photos)/len(photos):.1f}")
