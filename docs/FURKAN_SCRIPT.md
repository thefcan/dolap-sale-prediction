# 🎤 Furkan — Speaking Script (~3 min)

> Notebook açık, "Hide Code" tıklı. Cell 1'den başla.

---

### [Cell 1 — Title Slide] ⏱️ 15s

Hi everyone. We are Furkan, Utku and Halil.

Our project is about predicting whether a second-hand fashion listing on Dolap.com will sell within seven days.

> *(scroll ↓)*

---

### [Cell 2 — Problem Formulation] ⏱️ 30s

So what exactly are we solving?

This is a **binary classification** problem. Given a listing on Dolap — with its price, photos, brand, seller info — we predict: will it sell in the next seven days, yes or no?

Our primary metric is **ROC-AUC**, because we expect significant class imbalance — around 73% of listings don't sell. So accuracy would be misleading.

One important thing: Dolap.com is Turkey's largest second-hand fashion marketplace — it's owned by Trendyol. And when we searched Google Scholar, we found **zero** ML studies on Dolap. So this is the first one.

> *(scroll ↓)*

---

### [Cell 3 — Hypotheses] ⏱️ 30s

Before touching the data, we wrote down four testable hypotheses — because this is science, not just exploration.

**H1:** We expected cheaper items to sell faster — makes sense for a second-hand platform, right?

**H2:** More photos should help — buyers want to see the actual condition of used items.

**H3:** Experienced sellers — those with many active listings — should have an advantage. Better photos, better pricing, more trust.

**H4:** If a seller mentions a flaw in the description — like a stain or tear — that listing should sell slower.

We'll test all four of these later with statistical tests. Some of the results will surprise you.

> *(scroll ↓ — Cell 4 is the Show/Hide Code button, skip past it)*

---

### [Cell 5 — Load Data] ⏱️ 20s

Here's our dataset. We scraped **411 listings** across three fashion categories — sweaters, dresses, and coats — from twelve different sellers on Dolap.

Now, a quick note on *how* we scraped: Dolap is protected by **Cloudflare WAF**, which blocks all normal HTTP requests. So we had to use Selenium with a real Chrome browser — no shortcuts.

After cleaning, we have **40 features** per listing — price, brand, photos, likes, seller stats, and several derived features.

> *(scroll ↓)*

---

### [Cell 6 — Target Distribution] ⏱️ 45s

Now, the target variable. This is important — let me explain.

The ideal approach is: scrape a listing today, come back in seven days, check if it shows a "Sold" badge. That gives us ground truth.

But we haven't had seven days yet. So we built a **proxy label** — an engagement-based approximation. If a listing's like count is in the **top quartile** within its category, we label it as `proxy_sold = 1`. Think of it as: the market voted with likes.

The result: **73% not sold, 27% sold**. This class imbalance is exactly why we chose ROC-AUC over accuracy.

We want to be very transparent: this is a proxy. It captures engagement, not actual purchase. In our next milestone, we'll replace it with **real ground truth** by re-checking each listing after seven days.

> *(2 sn bekle, sonra geçiş)*

---

### ⏱️ Geçiş

Now Utku will walk you through our EDA findings — starting with the schema and distributions.

> *(Utku'ya bırak)*
