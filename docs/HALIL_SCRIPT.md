# 🎤 Halil — Speaking Script (~3.5 min)

> Utku'dan devraldıktan sonra başla. Cell 21'den itibaren.

---

### [Cell 21 — Section 3.4 Header] ⏱️ skip

> *(markdown — hızlıca geç)*

---

### [Cell 22 — Correlation Heatmap] ⏱️ 25s

Alright, let's look at how our features relate to each other — and more importantly, to our target.

This is our Pearson correlation matrix. The key column to focus on is the **last one**: `proxy_sold`.

Two features jump out immediately: **like_count** at plus 0.66, and **seller_listing_count** at plus 0.53. These are strong positive correlations.

On the negative side, **shipping_buyer_pays** at minus 0.25 — when the buyer pays for shipping, the listing is less likely to sell.

> *(parmakla heatmap'in son sütununu göster, 2 sn bekle)*

---

### [Cell 23 — Top Correlations Bar Chart] ⏱️ 15s

Here's the same information ranked. Engagement and seller experience clearly dominate the top. Notice that raw price is way down the list — barely correlated with our target. We'll come back to why in a moment.

> *(scroll ↓)*

---

### [Cell 24 — Scatter/Violin Plots] ⏱️ skip

> *(bu cell'i atla, zaman kazanmak için — sorulursa "we have detailed plots in the notebook")*

---

### [Cell 25 — Category-Level Analysis] ⏱️ 20s

Looking at categories individually: kazak — sweaters — has the highest proxy sale rate. Mont — coats — and elbise — dresses — are lower. This makes sense seasonally, but with only three categories we can't draw strong conclusions yet. Scaling to eight categories is planned for Milestone 2.

> *(scroll ↓)*

---

### [Cell 26 — Top 3 Features (markdown)] ⏱️ 25s

So here are our **top three predictive features** with domain explanations:

**Number one: like_count.** Likes are a direct signal of buyer interest. On platforms like Dolap, users "like" a listing to bookmark it — and that often precedes a purchase.

**Number two: seller_listing_count.** Experienced sellers know how to price, how to photograph, and how to write descriptions that convert. They also tend to rank higher in Dolap's search algorithm.

**Number three: shipping_buyer_pays.** This is a cost friction signal. When shipping is on the buyer, the total perceived price goes up — and that kills conversions.

And here's the interesting part: raw **price is NOT a top predictor**. This directly relates to our first hypothesis — let me show you the test results.

> *(scroll ↓ — Cell 27 Hypothesis Testing header markdown, hızlıca geç)*

---

### [Cell 28 — Hypothesis Testing Results Table] ⏱️ 40s

We tested all four hypotheses with proper statistical tests.

**H1 — Price Effect: REJECTED.** We expected cheaper items to sell faster, but the Mann-Whitney test says no — actually, sold items have a *higher* median price. Why? Because our proxy label is based on likes, and higher-priced branded items attract more "wishlist" likes. This is an honest limitation of the proxy label — the real sale label from our seven-day re-check may tell a different story.

**H2 — Photo Effect: CONFIRMED**, p equals 0.0001. Sold listings have a median of 6 photos versus 5 for unsold. More photos help — buyers want to see the actual condition of a used item.

**H3 — Seller Experience: CONFIRMED**, p less than 0.0001. This is our strongest result. Experienced sellers dominate the sold group.

**H4 — Flaw Disclosure: UNTESTABLE.** We only found 2 flaw mentions in the entire dataset. Why? Because 76 percent of descriptions are just page titles — that's Bug number 4, which we'll show in a moment.

> *(Cell 29 — Hypothesis Box Plots — parmakla göster ama üzerinde durma, scroll ↓)*

---

### [Cell 30 — Feature Engineering (markdown)] ⏱️ 20s

Here's our preprocessing decision table. Key highlights:

Log transform for price — skewness dropped from 8.29 to 0.30. Data-driven brand tiers using median price quantiles — as the instructor required, not manual. Condition encoded as ordinal with a natural order.

And at the bottom — four features we **couldn't** get: day of week, negotiation option, seller rating. We acknowledge these as limitations, not hide them.

> *(scroll ↓ — Cell 31 Investigation header markdown, hızlıca geç)*

---

### [Cell 32 — Bug Evidence Table] ⏱️ 30s

Now the investigation — this is the most important part.

We found **seven data quality bugs** during data collection. Let me highlight the two biggest ones:

**Bug number 1 — Brand/Size Contamination.** 89 percent of brand fields looked like "Zara - S / 36 Beden". The brand and size were stuck together. We split them into `brand_clean` and `size_extracted`, recovering size information for 365 listings.

**Bug number 4 — Description equals Page Title.** 76 percent of what we thought were descriptions were actually just the HTML page title repeated. This is why our keyword features — flaw mention, urgency keywords — have near-zero coverage. We flag these as `desc_is_placeholder` and plan to fix the parser in Milestone 2.

> *(tablodaki diğer bug'ları parmakla göster — "the other five are documented here")*

---

### [Cell 33 — Brand Before/After Chart] ⏱️ 10s

And here's the fix in action. On the left: raw brand names — jumbled with sizes, duplicated. On the right: clean brand names — Zara, Koton, DeFacto properly separated. This is Bug number 1 resolved.

> *(scroll ↓)*

---

### [Cell 34 — Conclusion (markdown)] ⏱️ 25s

To wrap up — six key findings:

First, class imbalance at 27 percent positive — we'll use balanced class weights and ROC-AUC.

Second, price is NOT a simple signal — brand desirability matters more.

Third, photos matter — confirmed statistically.

Fourth, seller experience is our strongest predictor — both correlation and hypothesis testing agree.

Fifth, we identified and fixed seven data quality bugs — turning problems into features.

And sixth, our proxy label has known limitations that we've been transparent about throughout.

**Next steps:** scale to eight categories, get real labels via seven-day re-checking, and build our first baseline model.

Thank you. We're happy to take questions.

> *(gülümse, bekle)*

---

## ❓ Halil'e Gelebilecek Sorular

| Soru | Cevap |
|------|-------|
| "Why is H1 rejected?" | "Proxy label captures engagement — likes — not actual purchase. Expensive branded items get 'wishlist' likes. Real sale label may reverse this." |
| "What about description text features?" | "Bug #4: 76% placeholder descriptions. We flag with desc_is_placeholder. Parser fix planned for M2." |
| "Only 7 bugs — is that enough for investigation?" | "These are bugs we actually discovered and fixed with evidence. Quality over quantity." |
| "How did you decide on brand tiers?" | "Data-driven: median listing price per brand → quantile-based 5 tiers. Instructor explicitly required this approach." |
| Bilmediğin bir soru gelirse | "Good question — we plan to address this in our next milestone." |
