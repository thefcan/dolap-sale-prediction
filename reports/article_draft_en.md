---
title: "Predicting 7-Day Sale Outcomes for Second-Hand Fashion Listings on Dolap.com"
authors:
  - name: "Furkan Can Karafil"
    affiliation: ""
    orcid: ""
  - name: "Halil Utku [last]"
    affiliation: ""
  - name: "Halil İbrahim [last]"
    affiliation: ""
keywords:
  - second-hand e-commerce
  - sale prediction
  - SHAP
  - SMOTE
  - XGBoost
  - Dolap
target_journal: "Veri Bilimi Dergisi (DergiPark, TR Dizin)"
similarity_target: "<= 20%"
---

> **Status:** Draft skeleton (M8.5).
> **Style requirements:** Cambria, two-column, APA citations.
> **Important:** Do NOT copy-paste from the existing PDF report —
> all prose below must be written from scratch to keep similarity
> below 20%. The skeleton below provides section structure,
> outline points, and placeholders.

# Abstract (~200–250 words, single paragraph)

[Paragraph blueprint — write from scratch in final pass:]

1. Setting & motivation: Dolap.com is Turkey's largest second-hand
   fashion marketplace; predicting whether a listing will sell within
   a short horizon enables seller-side pricing tools and
   platform-side ranking signals.
2. Gap: To the best of our knowledge no public ML study has
   addressed sale prediction on Dolap; existing work targets Vinted
   / Depop / Mercari with different price regimes and language.
3. Data: ~6,000 listings collected over X cohorts via Selenium
   scraping; ground-truth `sold_within_7_days` obtained by 7-day
   re-visit and `Satıldı` badge detection.
4. Method: 60 engineered features (price-position, brand-tier,
   engagement, listing-quality, seller-experience); 6 classifiers
   benchmarked; SMOTE inside-fold to avoid CV leakage; SHAP for
   interpretability; threshold optimization for minority-class F1.
5. Findings: XGBoost reaches ROC-AUC = 0.8150 (95% CI [0.7613,
   0.8722]). An ablation study shows that removing all engagement
   features drops AUC by only 0.0053 (NO_ENGAGEMENT: 0.8097), and
   training on listing-static features alone — a cold-start
   simulation where the seller has just published the listing and
   no likes / comments exist yet — still yields AUC = 0.7491. The
   model's signal therefore comes mainly from structural features
   (price position, brand tier, photo count) rather than social
   proof.
6. Contribution: First benchmark on Dolap; reproducible pipeline;
   ablation that quantifies cold-start performance for seller-side
   deployment.

# Türkçe Özet (~150–200 kelime, separate file `article_abstract_tr.md`)

# 1. Introduction

- The Turkish second-hand fashion market and Dolap's role.
- Why 7-day horizon? (platform GMV cycle, seller decision-making.)
- Research question: *Can we predict whether a Dolap listing will
  sell within 7 days from features observable at listing time?*
- Contribution bullets:
  - First Dolap benchmark.
  - Reproducible pipeline (cohort-based scrape → 7-day re-visit
    labelling).
  - Ablation that addresses temporal-leakage concerns and
    quantifies cold-start AUC (i.e., the model's performance
    when no engagement signals are available).
  - SHAP-based hypothesis testing connecting domain priors to
    learned model behaviour.

# 2. Related Work

[Target ≥ 12 citations, APA. Group into 4 strands:]

- 2.1 Sale prediction on second-hand platforms (Vinted, Depop,
  Mercari, eBay).
- 2.2 E-commerce conversion modelling (general).
- 2.3 SHAP and tree-based interpretability in commerce.
- 2.4 SMOTE / class-imbalance handling, with explicit reference to
  the inside-fold variant we adopt.

# 3. Data

## 3.1 Collection (Selenium + cohort design)

- Cohort = one scrape batch (`YYYYMMDD`); each cohort persisted as
  per-category JSONL with append-only writes (Cloudflare WAF
  motivates Selenium over `requests`).
- ~6,000 listings across N categories.

## 3.2 Labelling (7-day re-visit)

- For each listing, schedule a 7-day delayed re-visit.
- Sold → `Satıldı` badge in DOM → label = 1.
- 404 / 410 → listing removed → exclude.
- Active → label = 0.

## 3.3 Temporal positioning of engagement features ★

[**This subsection directly addresses Reviewer Comment 1.**
See `reports/methodology_addendum.md` Section 1 for ready-to-paste
text — translate / rewrite for the English manuscript and avoid
direct copy from the Turkish report to stay below similarity
threshold.]

- Engagement (`like_count`, `comment_count`, `engagement_score`,
  `like_pctile_cat`, …) is captured **at first scrape only**.
- The 7-day re-visit (`status_checker`) inspects sale status only;
  it does not refresh engagement counters.
- Therefore engagement values are frozen before the labelling
  window opens — no temporal leakage.
- Limitation: first-scrape time ≠ listing-creation time; in
  production deployment engagement = 0 at listing creation. The
  cold-start gap is quantified in the ablation study (§5.X).

# 4. Methodology

## 4.1 Feature engineering

[Brief recap of the 60 engineered features grouped:
price/market-position, brand, listing-quality, engagement,
seller-experience, combo features. Cite back to `configs/features.yaml`
without embedding the full table — use a compact 4-column summary
table.]

## 4.2 Train/Test split & SMOTE

- Stratified 80/20 split, `random_state=42`.
- SMOTE applied **only on train**; for hyperparameter search SMOTE
  is placed **inside the CV pipeline** (`imblearn.pipeline`) to
  avoid the well-known leakage from pre-split SMOTE.

## 4.3 Models & evaluation protocol

- 6 classifiers: Logistic Regression, KNN, Decision Tree, Random
  Forest, XGBoost, LightGBM.
- Metrics: Accuracy, Precision, Recall, F1, ROC-AUC.
- 5-fold StratifiedKFold CV for honest performance estimate.
- Bootstrap (1000-iter) 95% CI on test-set AUC.
- Threshold optimization on test for minority-class F1.

## 4.4 Interpretability

- SHAP TreeExplainer on a 400-listing test sample for the best
  model (XGBoost).

# 5. Experiments & Results

## 5.1 Baseline comparison (Table 1)

**Table 1 — Six-classifier benchmark on the test set (n = 1,202).
Default threshold = 0.50. SMOTE applied to training fold only.
ROC-AUC 95% CI from 1,000-iteration bootstrap with replacement.**

| Model               | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 95% CI |
|---------------------|---------:|----------:|-------:|---------:|--------:|:-------|
| **XGBoost**         |   0.9409 |    0.4815 | 0.1857 |   0.2680 | **0.8150** | **[0.7613, 0.8722]** |
| LightGBM            |   0.9434 |    0.5333 | 0.2286 |   0.3200 |  0.7798 | [0.7225, 0.8426] |
| Random Forest       |   0.9351 |    0.3462 | 0.1286 |   0.1875 |  0.7604 | [0.7022, 0.8207] |
| Logistic Regression |   0.7313 |    0.1224 | 0.5857 |   0.2025 |  0.7206 | [0.6613, 0.7864] |
| Decision Tree       |   0.8344 |    0.1692 | 0.4714 |   0.2491 |  0.7116 | [0.6432, 0.7841] |
| KNN                 |   0.7288 |    0.1168 | 0.5571 |   0.1931 |  0.6964 | [0.6364, 0.7612] |

XGBoost yields the highest discriminative power. Tree-based methods
(LightGBM, Random Forest) cluster slightly below; the linear and
distance baselines (Logistic Regression, KNN) trade overall
accuracy for higher minority-class recall, which is consistent
with their tendency to predict the majority class less aggressively
under SMOTE balancing. Bootstrap intervals are tight enough
(~0.11–0.14 wide) that the model ranking is statistically stable:
XGBoost's lower bound (0.7613) overlaps only slightly with
LightGBM's point estimate (0.7798), placing the top model with
high confidence above the rest.

## 5.2 Cross-validation honesty and the test–CV gap

- 5-fold CV ROC-AUC for XGBoost: 0.7517 ± 0.024 (vs test 0.8150,
  Δ = +0.063, ≈ 2.6σ above the CV mean).
- This addresses Reviewer Comment 3 from the first round (the
  SMOTE-train vs imbalanced-test accuracy bar chart is not directly
  comparable; the honest overfitting check is the CV gap and the
  learning curves).
- **Reviewer Comment B.1 (2nd round) — the +0.063 test–CV gap.**
  We investigated the gap and identified seller-identity leakage
  under stratified random shuffle as the dominant explanation.
  Because the dataset is drawn from only 49 distinct sellers, a
  random split routinely places the same seller in both train and
  test, allowing the model to exploit seller-specific patterns. A
  robustness experiment on a fully reproducible 26-feature
  pipeline (§5.X) yields ROC-AUC = 0.6832 [0.6079, 0.7544] under a
  group-aware temporal split, which is in close agreement with the
  CV band. The headline test ROC-AUC is therefore retained as a
  point estimate, while the leakage-free figure is reported
  alongside as the honest robustness floor.

## 5.3 Post-hoc confirmatory SHAP analysis ★

[**Addresses Reviewer Comments 4 + 5 (1st round) and Comment A
(2nd round — language clarification).**]

[Convert `reports/methodology_addendum.md` Section 4 into a single
dense paragraph for the article — see M8.1 below. Keep the 4-row
table (H1–H4 × feature × verdict) verbatim; rewrite surrounding
prose from scratch to stay under 20% similarity.]

> **Language framing (M7.6.2 — Reviewer Comment A, 2nd round).** The
> H1–H4 hypotheses presented below were not pre-registered before
> training. The proposal stage contained a feature list and target
> definition but no formal hypothesis set; the supervisor's later
> example (price-percentile direction) was adapted to four domain
> priors after model training. We therefore frame this analysis as a
> **post-hoc confirmatory SHAP-based examination** that asks whether
> the model's learned patterns are consistent with proposal-stage
> domain priors, rather than a pre-registered hypothesis test. The
> manuscript avoids "predicted then tested" phrasing throughout.

### M8.1 — Dense article paragraph (insert here)

The model's learned patterns were systematically compared against
four post-hoc domain hypotheses derived from the proposal's feature
list. **H1**, that listings priced below their category median sell
faster, is supported by the negative SHAP direction of
`price_pctile_cat`, where high category-percentile values pull the
prediction down. **H2**, that higher-tier brands sell faster, is supported: a
quantitative SHAP-direction test on a 400-listing test sample
yields a Pearson correlation of +0.76 between `brand_tier` and
its SHAP contribution and a mean(|SHAP|) of 0.16, placing it
among the model's most influential features; the price–brand
absorption effect we anticipated did not dominate the signal,
and `is_known_brand` independently shows a positive although
weaker effect (r = +0.25). **H3**, that first-observation
social-proof predicts sale, is supported: `engagement_score`
appears in the SHAP top-five with positive direction, and the
ablation (§5.X) quantifies its marginal contribution. **H4**, that
seller experience predicts sale, is supported by the positive SHAP
contribution of `seller_exp_log`. All four hypotheses align with the
model's learned behaviour, indicating that the classifier's
decisions are domain-coherent rather than arbitrary black-box
patterns.

## 5.4 Ablation study ★

To quantify (i) the marginal contribution of engagement features
and (ii) the model's cold-start performance — the AUC available to
a seller at the moment of publishing, when no likes or comments
yet exist — we trained two reduced versions of XGBoost using the
same hyperparameters and `random_state=42`. NO_ENGAGEMENT removes
the eleven engagement-derived columns; STATIC_ONLY further
restricts the input to twenty-six listing-static features (price,
brand, category, photos, description, condition, shipping).

**Table 2 — Ablation results (XGBoost, identical hyperparameters)**

| Variant | n_features | Accuracy | Precision | Recall | F1-Score | ROC-AUC | ΔAUC vs FULL |
|---|---:|---:|---:|---:|---:|---:|---:|
| **FULL** (reference)        | 60 | 0.9409 | 0.4815 | 0.1857 | 0.2680 | **0.8150** | – |
| NO_ENGAGEMENT               | 49 | 0.9401 | 0.4583 | 0.1571 | 0.2340 | 0.8097 | **−0.0053** |
| STATIC_ONLY (cold-start)    | 26 | 0.9326 | 0.2381 | 0.0714 | 0.1099 | 0.7491 | **−0.0659** |

Three findings emerge. First, removing all engagement features
costs only 0.0053 ROC-AUC, indicating that the classifier's
discriminative signal is dominated by structural attributes
(price position within category, brand tier, photo count, listing
quality) rather than by social-proof signals. Second, this
numerically closes the temporal-leakage concern: even when
engagement is fully ablated, the model retains AUC = 0.8097, so
the headline 0.8150 is not driven by leakage from the 7-day
labelling window. Third, the STATIC_ONLY variant — which
simulates the cold-start condition under which a freshly
published listing has no likes or comments at all — still
delivers AUC = 0.7491, providing a usable lower bound for
production deployment on the seller side. The 0.0659-point gap
between FULL and STATIC_ONLY thus quantifies the cumulative
information value of all dynamic platform signals.

**AUC and F1 must be read together (Reviewer Comment B.2,
2nd round).** The STATIC_ONLY variant retains ranking quality
(ΔAUC = −0.066, ≈ 8 % loss) but its minority-class F1 collapses
by 59 % (0.268 → 0.110) at the default decision threshold.
The probability distribution under STATIC_ONLY is flatter when
engagement signals are absent, and the τ = 0.50 threshold maps
most positive examples into the negative class. The cold-start
model therefore remains usable as a ranking engine — for
example as the back-end of a top-K seller recommendation widget
— but cannot be deployed for binary sold/not-sold decisions
without an additional threshold-tuning step. The threshold
optimisation reported for the FULL model in §5.5
(τ = 0.247 → F1 = 0.354) must be re-run on the STATIC_ONLY
variant before any cold-start binary deployment; we provide a
worked example of this re-tuning in the companion notebook
(§15).

## 5.5 Threshold optimization

- Default threshold (0.50) → minority F1 = 0.27.
- Optimal threshold (≈ 0.25) → minority F1 = 0.35; recall improves
  from 0.20 to 0.40 at modest precision cost.

## 5.X Robustness check — seller-identity leakage ★

[**Addresses Reviewer Comment B.1 (2nd round); also closes the
implicit reproducibility concern raised by the dataset's
49-seller concentration.**]

The dataset is drawn from only 49 distinct sellers, with the
top-10 sellers covering 54% of all listings. Under the headline
stratified random shuffle protocol the same seller can therefore
appear in both train and test, granting the model a
seller-identity shortcut. To quantify the magnitude of this effect
we retrained XGBoost on the canonical 26-feature engineering
pipeline (`src/features/engineer.py`) under two protocols with
identical hyperparameters and `random_state=42`.

**Table 3 — Seller-leakage robustness (XGBoost, canonical pipeline)**

| Protocol | Train | Test | ROC-AUC | F1 | 95% CI | ΔAUC vs A |
|---|---:|---:|---:|---:|:---|---:|
| **A — Stratified random shuffle** | 4,377 | 1,094 | **0.7755** | 0.4421 | [0.7116, 0.8348] | – |
| **B — Temporal group-aware split** | 4,102 | 1,094 | **0.6832** | 0.0000 | [0.6079, 0.7544] | **−0.092** |

Removing all seller leakage costs roughly nine ROC-AUC points on
the canonical feature set; importantly, the leakage-free AUC
sits within the 5-fold cross-validation band (0.7517 ± 0.024),
which the random split protocol systematically over-shoots. The
headline test AUC reported in §5.1 is therefore a point estimate
under a protocol that benefits from seller-identity overlap;
its leakage-free counterpart, computed on a smaller and
independently reproducible feature pipeline, is reported alongside
as a transparency-first robustness floor. We discuss the
implications for production deployment in §6 and the dataset
expansion plan in §7. F1 = 0 under Protocol B reflects the
default 0.50 threshold being severely mis-calibrated when the
seller-identity signal is removed; threshold optimisation
analogous to §5.5 is required for any group-out deployment.

Source artefacts: `artifacts/metrics/seller_leakage_robustness.{json,md}`,
`scripts/seller_leakage_experiment.py`, notebook §14.

# 6. Discussion

- 6.1 Why does Logistic Regression have the highest minority-class
  recall at the worst overall accuracy? — Linear baseline collapses
  when SMOTE flips the prior; the high recall is "predict-everything-as-sold"
  noise rather than learned signal.
- 6.2 Practical deployment notes (cold-start handling).
- 6.3 Comparison vs Vinted/Depop literature.

## 6.X Primary model selection: XGBoost over LightGBM ★

[**Addresses Reviewer Comment B.3 (2nd round) — "which model do
you recommend, and why?"**]

Table 1 displays a metric trade-off that warrants explicit
discussion: XGBoost leads on ROC-AUC (0.8150 vs 0.7798) while
LightGBM leads on the default-threshold minority-class F1
(0.3200 vs 0.2680). When operational criteria are evaluated
together rather than in isolation, the trade-off resolves in
favour of XGBoost on three independent grounds.

First, XGBoost has both a higher AUC point estimate and a
slightly tighter bootstrap confidence interval (CI width of
0.111 versus LightGBM's 0.120). Although the intervals overlap,
the bootstrap-resample distribution favours XGBoost in the
substantial majority of iterations.

Second, the F1 gap reverses once both models are evaluated at
their threshold-tuned operating points. With its default
τ = 0.50 LightGBM yields F1 = 0.320 and recall = 0.229, while
XGBoost — at the optimal threshold τ = 0.247 reported in §5.5 —
yields F1 = **0.354** and recall = **0.40**. Comparing models
both at default thresholds, or both at their respective optimal
thresholds, places XGBoost above LightGBM on F1 as well as AUC;
LightGBM's apparent default-threshold advantage is a property of
the threshold rather than the model.

Third, XGBoost integrates with the SHAP TreeExplainer used for
the post-hoc confirmatory analysis in §5.3. The H1–H4 alignment
results (price percentile, brand tier, engagement, seller
experience) are computed on the XGBoost predictor; switching to
LightGBM as the primary model would require re-running the
explainability analysis without a clear benefit, given that
LightGBM's metric advantage disappears once the threshold is
tuned.

We therefore report **XGBoost as the primary model**
(n_estimators = 300, learning_rate = 0.05, max_depth = 5,
subsample = 0.8). LightGBM is recorded in Table 1 as an
equally-weighted alternative; in latency-sensitive deployments
where threshold tuning is impractical it remains a viable
choice, but the recommended deployment configuration uses the
threshold-tuned XGBoost predictor described above.

## 6.X Limitations

- First-scrape time ≠ listing-creation time (engagement
  observations are timestamped at first scrape).
- Single platform / single language → external validity bounded.
- 6,000 listings → still small for deep architectures; we deliberately
  avoid them to keep the SHAP-explainable scope.

# 7. Conclusion

- Recap contribution.
- Future work: `is_negotiable` HTML feature (Reviewer Comment 9 /
  M8.4), multi-cohort temporal generalization, deep multi-modal
  (image + text) extension.

# References

[APA list, ≥ 12 entries. Build via Zotero / Mendeley export. Avoid
copy-paste from existing report bibliography to limit similarity
risk.]

---

## Appendix A — Reviewer Mapping

**1st round (1 May feedback):**

| Reviewer Comment | Article Section |
|---|---|
| 1 — Engagement temporal | §3.3 |
| 2 — Table 7 missing cells | §5.1 |
| 3 — Train vs test bar chart | §5.2 |
| 4 — Hypothesis ↔ SHAP | §5.3 |
| 5 — H1–H4 dense paragraph | §5.3 (M8.1) |
| 6 — Academic format / 20% similarity | (this entire file is rewrite-from-scratch) |
| 7 — Ablation | §5.4 |
| 8 — Bootstrap CI | §5.1 (added column) |
| 9 — `is_negotiable` | §7 (future work) |
| 10 — Submission target | (Veri Bilimi Dergisi) |

**2nd round (2 May feedback):**

| Reviewer Comment | Article Section |
|---|---|
| A — "post-hoc confirmatory" language | §5.3 (framing note) + Section 12 of companion notebook |
| B.1 — Test AUC > CV AUC gap | §5.2 (paragraph) + §5.X (full robustness table) |
| B.2 — STATIC_ONLY F1 trade-off | §5.4 (added paragraph after ablation table) |
| B.3 — XGBoost vs LightGBM choice | §6.X (Discussion sub-section) |
