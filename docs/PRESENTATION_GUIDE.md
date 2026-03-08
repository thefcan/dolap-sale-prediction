# 🎤 EDA Presentation — Rehearsal Guide

> **Sunum:** 10 dakika | İngilizce | Jupyter Notebook üzerinden  
> **Takım:** Furkan · Utku · Halil  
> **Notebook:** `notebooks/01_eda_presentation.ipynb` (34 cell, tümü çalışıyor)

---

## Genel Kurallar

- Notebook açık, **"Hide Code"** butonu tıklı olsun (kod gizli).
- Scroll hızınız ile konuşma hızınız uyumlu olsun — grafik gelince **2-3 sn** bekleyin.
- Her kişi kendi bölümüne geçerken **"I'll hand over to [name]"** desin.
- Soru gelirse → **"Good question — we address this in our next milestone"** kalıbını kullanın.

---

## Görev Dağılımı Özeti

| Üye | Bölüm | Cell'ler | Süre |
|-----|-------|----------|------|
| **Furkan** | S1 Problem + S2 Data Collection + Target Dist. | Cell 1-6 | ~3 dk |
| **Utku** | S3.1 Schema + S3.2 Stats + S3.3 Distributions | Cell 7-20 | ~3.5 dk |
| **Halil** | S3.4 Correlations + Hypotheses + S4 Feature Eng. + Investigation + Conclusion | Cell 21-34 | ~3.5 dk |

---

## 🔵 FURKAN — Opening + Problem + Data Collection (~3 dk)

| Sıra | Cell # | İçerik | Süre | Konuşma Notu |
|------|--------|--------|------|-------------|
| 1 | Cell 1 (md) | Title Slide | 15s | "Hi everyone, we are Furkan, Utku and Halil. Our project: predicting whether a second-hand fashion listing on Dolap.com will sell within 7 days." |
| 2 | Cell 2 (md) | Problem Formulation | 30s | "This is a **binary classification** problem. Our primary metric is ROC-AUC because we expect class imbalance. Dolap is Turkey's largest second-hand fashion platform — and this is the **first ML study** on it." |
| 3 | Cell 3 (md) | Hypotheses | 30s | "We formulated 4 testable hypotheses before looking at the data — H1: cheaper items sell faster, H2: more photos help, H3: experienced sellers do better, H4: flaw mentions reduce sales." |
| 4 | Cell 5 (code) | Load Data | 20s | "We scraped 411 listings across 3 categories using Selenium — Cloudflare WAF blocks all HTTP clients, so we needed a real browser. After cleaning, we have 40 features." |
| 5 | Cell 6 (code) | Target Distribution | 45s | "Our target is a **proxy label** — since we can't wait 7 days for real sales data yet, we use engagement-based labeling: top quartile of likes per category → proxy_sold=1. We get a 73/27 split. We'll replace this with **real ground truth** via temporal re-checking in Milestone 2." |

**⏱️ Geçiş:** *"Now Utku will walk you through our EDA findings."*

---

## 🟢 UTKU — Schema + Statistics + Distributions (~3.5 dk)

| Sıra | Cell # | İçerik | Süre | Konuşma Notu |
|------|--------|--------|------|-------------|
| 1 | Cell 8 (code) | Schema Check | 25s | "We analyze 25 columns — mix of numeric (price, likes, photos) and categorical (brand, condition, category). All scraped from product pages." |
| 2 | Cell 9 (code) | Missing Values | 30s | "Key finding: `original_price` is **conditionally** missing — NaN means no discount, not random. Color has 100% missing due to parser limitation — acknowledged." |
| 3 | Cell 11 (code) | Descriptive Stats | 25s | "Price ranges from 40 to 12,000 TL with median 300. That 12K max suggests luxury items — we'll handle these as outliers." |
| 4 | Cell 12 (code) | Key Observations | 20s | "Suspicious: max `seller_listing_count` is 1,428 — this is a professional reseller, not a bug. `photo_count` capped at 12 by platform." |
| 5 | Cell 14 (code) | Numeric Histograms | 30s | "Price is **heavily right-skewed** (skew=8.29). Like count follows a power-law — most items get few likes, a few go viral." |
| 6 | Cell 15 (code) | Log Transform | 20s | "Log transform reduces price skew from 8.29 to 0.30 — nearly normal. We'll use `log_price` in modeling." |
| 7 | Cell 17 (code) | Categorical Bars | 25s | "Condition: majority 'Az Kullanılmış'. Brand tier: data-driven quantile binning as instructor required — not manual." |
| 8 | Cell 19 (code) | Class-Conditional | 20s | "`like_count` shows **clear separation** between sold and not-sold. Price shows less separation — interesting." |
| 9 | Cell 20 (code) | Categorical vs Target | 15s | "Brand tier 3-4 and 'New & Tagged' condition have higher proxy_sold rates." |

**⏱️ Geçiş:** *"Halil will now cover correlations, hypothesis results, and our investigation."*

---

## 🟠 HALİL — Relationships + Hypotheses + Feature Eng + Investigation + Conclusion (~3.5 dk)

| Sıra | Cell # | İçerik | Süre | Konuşma Notu |
|------|--------|--------|------|-------------|
| 1 | Cell 22 (code) | Correlation Heatmap | 25s | "Correlation heatmap reveals: `like_count` (+0.66) and `seller_listing_count` (+0.53) are our **top 2 predictors**. Shipping cost is negatively correlated." |
| 2 | Cell 23 (code) | Top Correlations | 15s | "Top 5 ranked — engagement and seller experience dominate." |
| 3 | Cell 25 (code) | Category Analysis | 20s | "Category-level breakdown shows kazak has highest proxy sale rate." |
| 4 | Cell 26 (md) | Top 3 Features | 25s | "Our top 3: likes = buyer interest signal, seller_listing_count = experience proxy, shipping_buyer_pays = cost friction. Notice raw price is NOT a top predictor — this relates to H1." |
| 5 | Cell 28 (code) | Hypothesis Testing | 40s | "Results: **H1 REJECTED** — cheaper items DON'T sell more in our data. Why? Proxy label captures engagement, not purchase. **H2 confirmed** (p=0.0001) — more photos help. **H3 confirmed** (p<0.0001) — seller experience matters most. **H4 untestable** — only 2 flaw mentions due to placeholder descriptions." |
| 6 | Cell 30 (md) | Feature Engineering | 20s | "Key decisions: log transform for price, data-driven brand tiers, condition ordinal encoding, 4 features not yet available — acknowledged as limitations." |
| 7 | Cell 32 (code) | Bug Evidence | 30s | "We found **7 data quality bugs**. Highlights: Bug #1 — 89% of brand fields contaminated with size info → split into brand_clean + size_extracted. Bug #4 — 76% of descriptions are just page titles → `desc_is_placeholder` flag." |
| 8 | Cell 33 (code) | Brand Before/After | 10s | "Here's the fix in action — before: jumbled brands with sizes, after: clean brand names." |
| 9 | Cell 34 (md) | Conclusion | 25s | "6 key findings, main takeaway: **seller experience and engagement beat raw price**. Next: scale to 8 categories, real labels via 7-day re-check, baseline model. Thank you — questions?" |

---

## ❓ Olası Sorular + Hazır Cevaplar

| # | Olası Soru (İngilizce) | Cevap Anahtarı | Kim cevaplar? |
|---|----------------------|---------------|---------------|
| Q1 | "Why proxy label instead of real sales data?" | "Dolap requires 7-day wait for sold badge. Proxy = engagement-based approximation. We explicitly acknowledge this and plan temporal re-checking in M2." | Furkan |
| Q2 | "How did you bypass Cloudflare?" | "Non-headless Chrome via Selenium. We use JS DOM queries (document.querySelector) instead of HTTP requests. All anti-detection flags enabled." | Furkan |
| Q3 | "Why is H1 rejected? Shouldn't cheaper items sell faster?" | "Our proxy label captures engagement (likes), not actual purchase. Expensive branded items get more 'wishlist' likes. Real sale label may show different pattern." | Halil |
| Q4 | "411 samples is small — is this enough?" | "Agreed. This is a pilot cohort for EDA methodology. M2 targets 1000+ listings across 8 categories with real labels." | Utku |
| Q5 | "Why data-driven brand tiers instead of manual?" | "Instructor feedback: must be objective and reproducible. We compute median listing price per brand → quantile-based 5 tiers." | Utku |
| Q6 | "What about description text features?" | "Bug #4: 76% of descriptions are page titles (placeholder). We flag these with `desc_is_placeholder`. Parser fix planned for M2." | Halil |
| Q7 | "What model will you use?" | "Baseline: Logistic Regression (class_weight=balanced). Advanced: XGBoost with SMOTE. Evaluation: ROC-AUC primary, F1 secondary." | Furkan |

---

## ⏱️ Zamanlama Kontrol Listesi

- [ ] Furkan bölümünü 3 dakikada bitiriyor mu?
- [ ] Utku bölümünü 3.5 dakikada bitiriyor mu?
- [ ] Halil bölümünü 3.5 dakikada bitiriyor mu?
- [ ] Geçişler akıcı mı? ("I'll hand over to…")
- [ ] Toplam ≤ 10 dakika mı?
- [ ] Q&A için en az 1-2 dakika kalıyor mu?
