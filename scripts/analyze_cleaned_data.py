"""Quick analysis for cleaned_all dataset."""
import pandas as pd


def main() -> None:
    df = pd.read_csv("data/interim/cleaned_all.csv")

    print("=== GENEL ÖZET ===")
    print(f"Toplam kayıt: {len(df)}")
    print(f"Cohort sayısı: {df['cohort_id'].nunique()}")
    print(df["cohort_id"].value_counts().sort_index().to_string())

    labeled = df[df["has_real_label"] == True].copy()
    print("\n=== LABEL DURUMU ===")
    print(f"Real label olan: {len(labeled)} / {len(df)} (%{len(labeled)/len(df)*100:.1f})")
    if len(labeled):
        sold = (labeled["sold_within_7_days"] == 1).sum()
        active = (labeled["sold_within_7_days"] == 0).sum()
        print(f"Sold: {sold} (%{sold/len(labeled)*100:.1f}) | Not sold: {active} (%{active/len(labeled)*100:.1f})")

    print("\n=== LABEL STATUS DAĞILIMI ===")
    print(df["label_status"].fillna("").replace("", "unlabeled").value_counts().head(10).to_string())

    print("\n=== FİYAT ÖZETİ ===")
    print(df["price"].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99]).round(2).to_string())

    print("\n=== EN YÜKSEK SATIŞ ORANI OLAN KATEGORİLER (>=5 labeled) ===")
    if len(labeled):
        cat = labeled.groupby("category").agg(
            n=("listing_id", "count"),
            sold_rate=("sold_within_7_days", "mean"),
        ).reset_index()
        cat = cat[cat["n"] >= 5].sort_values("sold_rate", ascending=False).head(10)
        if len(cat):
            cat["sold_rate"] = (cat["sold_rate"] * 100).round(1)
            print(cat.to_string(index=False))
        else:
            print("(>=5 labeled kategoride yeterli veri yok)")

    print("\n=== CONDITION BAZLI SATIŞ ORANI (labeled) ===")
    if len(labeled):
        cond = labeled.groupby("condition_clean").agg(
            n=("listing_id", "count"),
            sold_rate=("sold_within_7_days", "mean"),
        ).sort_values("sold_rate", ascending=False)
        cond["sold_rate"] = (cond["sold_rate"] * 100).round(1)
        print(cond.to_string())

    print("\n=== OUTLIER ÖZETİ ===")
    print(f"Price outlier: {int(df['is_price_outlier'].sum())}")
    print(f"Like outlier: {int(df['is_like_outlier'].sum())}")


if __name__ == "__main__":
    main()
