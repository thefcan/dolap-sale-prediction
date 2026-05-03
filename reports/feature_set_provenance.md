# Feature Set Provenance — `model_ready_v3.csv`

> **Status:** Open issue documenting a reproducibility gap discovered on
> 2026-05-02. The classification + ablation notebooks both load
> `data/processed/model_ready_v3.csv`, but **no script in the repository
> produces this file**. This document records the gap, the column-level
> evidence, and the recommended resolution for the journal submission.

## 1. The dataset

- **File:** `data/processed/model_ready_v3.csv` (3.0 MB)
- **Shape:** 6,007 listings × 61 columns (60 features + `sold_within_7_days`)
- **Target distribution:** 5,658 not-sold (94.19%) | 349 sold (5.81%)
- **First committed:** 2026-04-19 in commit `82ac3d5`
  ("model_ready.csv, training ve evaluation notebook eklendi")
- **Consumers:**
  - `notebooks/dolap_classification_final.ipynb` cell[3]
  - `notebooks/dolap_ablation_study.ipynb` cell[2]

## 2. The two production candidates that DO exist in the repo

### 2.1 `src/features/engineer.py` → `engineered_features.parquet`

- **Shape:** 6,059 × 38
- **Run via:** `python -m src.features.engineer`
- **Designed as the canonical Phase 9 output**
- Contains: price_log, price_to_category_median, price_to_brand_median,
  brand_tier, condition_ordinal, seller_frequency_log,
  seller_balance_weight, listing_hour, listing_dow, is_weekend_listing,
  desc_has_urgency_keyword, desc_has_flaw_mention, desc_is_placeholder,
  exclude_from_training, etc.

### 2.2 `notebooks/Dolap_EDA_Feature_Engineering.ipynb` cell[17]

- In-memory feature engineering (~19 features added)
- Contains: scrape_hour, scrape_dayofweek, scrape_time_segment,
  price_segment, seller_tier, is_power_seller, has_real_desc,
  photo_score, desc_quality_score, engagement_score, likes_per_photo,
  price_x_condition, power_seller_cheap, free_ship_new
- **Does not write `model_ready_v3.csv`** — only assembles
  `X_scaled` for in-notebook use

## 3. The diff: v3 vs `engineer.py` output

**Common (11 columns)** — both pipelines compute these identically:

```
brand_tier, comment_count, description_length, description_word_count,
like_count, photo_count, price, price_log, seller_listing_count,
seller_rating_count, sold_within_7_days
```

**Only in v3 (49 columns)** — produced by an unknown source:

```
brand_enc, buyer_pays_shipping, cat_competition_log, category_enc,
category_freq, cheap_and_new, color_family_enc, comment_per_photo,
condition_score, desc_depth_per_photo, desc_has_defect,
desc_has_measurement, desc_has_price_talk, desc_has_quality,
engagement_pctile, engagement_score, engagement_x_new, has_color,
has_comments, has_free_shipping, has_likes, has_size, hour,
is_experienced_seller, is_known_brand, is_new_item, is_super_seller,
like_pctile_cat, like_per_photo, like_vs_seller_avg,
listing_quality_score, n_cheaper_in_cat, photo_pctile_cat,
photo_vs_cat_mean, premium_cheap, price_bucket, price_pctile_brand,
price_pctile_cat, price_per_photo, price_vs_brand_median,
price_vs_seller_avg, seller_exp_log, size_numeric, size_type,
subcategory_enc, subcategory_freq, title_has_new, title_length,
title_word_count, value_score
```

**Only in `engineer.py` (27 columns)** — *not* used by the notebooks:

```
brand_source, category, cohort_id, condition_ordinal, days_since_scrape,
desc_has_flaw_mention, desc_has_urgency_keyword, desc_is_placeholder,
exclude_from_training, has_discount, invalid_early_label,
invalid_late_label, is_weekend_listing, label_window_hours,
listing_dow, listing_hour, listing_id, price_to_brand_median,
price_to_category_median, seller_balance_weight, seller_frequency_log,
seller_listing_log, seller_rating_log, seller_username,
shipping_buyer_pays, target_missing, target_not_binary
```

## 4. Why this matters

The journal manuscript will claim that the model was trained on a
specific feature set. With `model_ready_v3.csv` consumed but not
reproducibly produced, three things break:

1. **Anonymous reviewer reproducibility check** — a reviewer who
   downloads the repo cannot regenerate Tables 1–2 because the input
   to the training notebook is a static artifact of unknown origin.
2. **Methodology section coherence** — the manuscript's Feature
   Engineering subsection currently references `configs/features.yaml`
   and `src/features/engineer.py`; neither produced the file the
   notebook actually reads. The text and the code disagree.
3. **Future re-runs** — if the labeled dataset is updated (new cohort,
   new RC4 fix), v3 cannot be regenerated; the model would have to be
   retrained on a different feature set, invalidating the reported AUC.

## 5. What was likely the source

Inspecting v3 column names, the feature set is consistent with a
**single, ad-hoc feature engineering script** that:

- Computes within-category and within-brand price percentiles
  (`price_pctile_cat`, `price_pctile_brand`)
- Frequency-encodes categorical columns (`category_freq`,
  `subcategory_freq`, `category_enc`)
- Aggregates listing-quality combos (`cheap_and_new`, `premium_cheap`,
  `engagement_x_new`, `listing_quality_score`, `value_score`)
- Engineers seller-side features (`seller_exp_log`,
  `is_experienced_seller`, `is_super_seller`)
- Normalizes engagement (`engagement_score`, `like_per_photo`,
  `comment_per_photo`)

This is **not** the EDA notebook's `df_fe` pipeline (different names,
different transformations). The script that produced it appears to be
external to the repository — likely written interactively (locally or
in an assistant session) and the resulting CSV committed without the
generator.

## 6. Resolution options

### Option A — Accept and document (lowest cost, ~30 min)

- Add a Methodology footnote in `article_draft_en.md`: "The 60
  engineered features in `model_ready_v3.csv` were derived through an
  iterative exploratory process; the canonical `engineer.py` pipeline
  is the production-grade subset (38 features) and produces a model
  whose AUC will be reported alongside the v3 result for transparency."
- Risk: a reviewer may push back on reproducibility.

### Option B — Reverse-engineer and reconstruct (medium cost, ~3-4 h)

- Walk the v3 column list, identify each transformation, and write a
  new `src/features/engineer_v3.py` that reproduces the file
  byte-for-byte (or as close as possible) from `merged_data.csv`.
- Verify by hashing.
- Risk: some features may depend on hidden ordering or random splits;
  exact byte match might be impossible, in which case fallback to
  Option C.

### Option C — Retrain on `engineer.py` output and re-report (medium cost, ~1-2 h)

- Run the classification notebook against `engineered_features.parquet`
  (38 features) instead of v3 (60 features).
- Report new AUC; the manuscript's Methodology and Results then
  describe a single, fully reproducible pipeline.
- Risk: AUC may drop (some v3 features may be load-bearing); the
  cold-start ablation needs re-running too.

### Recommendation

**Option B** is the academically sound choice for the journal
submission, but is the most time-consuming. **Option A + commit
note** is the pragmatic short-term move for the 26 May deadline,
with Option B as a follow-up before final acceptance.

## 7. Action items

- [ ] Decide between A / B / C (user decision required)
- [ ] If A: add footnote text to `article_draft_en.md` §4.1
- [ ] If B: implement `src/features/engineer_v3.py` and verify hash
- [ ] If C: re-run notebooks with `engineered_features.parquet` and
      update Tables 1–2, ablation, and bootstrap CI in all reports
- [ ] Update `todo.md` Phase 9 to flag the v3 provenance gap
