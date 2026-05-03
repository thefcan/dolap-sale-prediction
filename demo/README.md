# Live Demo — Dolap 7-Day Sale Prediction

Self-contained Flask + HTML demo for the 4-May presentation. Loads the
trained XGBoost pipeline from `models/dolap_xgboost_pipeline.joblib`
(produced by Section 17 of `notebooks/dolap_classification_final.ipynb`)
and lets the audience input feature values through a browser UI to
get a live probability of "sold within 7 days".

## Quick start

```bash
# 1. Make sure the model artefacts exist
ls models/
# expected:
#   dolap_xgboost_pipeline.joblib
#   feature_schema.json

# If they're missing, open notebooks/dolap_classification_final.ipynb
# and run Section 17 (or just Restart & Run All).

# 2. Install demo dependencies (one-time)
pip install flask flask-cors joblib pandas xgboost

# 3. Start the server (from the project root)
python demo/demo_server.py

# 4. Open the UI in a browser
#    http://127.0.0.1:5000/
```

## What the audience sees

- **60 numeric feature inputs**, pre-filled with median defaults from the
  training data, with a filter box (search by name) and a "Reset to
  defaults" button.
- **Decision threshold slider** (τ) — default 0.50, optimal F1
  threshold from §11 = 0.247.
- **Live prediction panel** showing:
  - Predicted class (SOLD / NOT SOLD within 7 days) with colour coding
  - Probability percentage (large display)
  - Probability gauge with the threshold marker
  - Headline metrics card: test AUC, CV AUC ± std, F1 default vs
    optimal, group-aware leakage-free AUC, CI width.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Serve `demo_ui.html` |
| GET | `/api/schema` | Feature names, defaults, ranges, headline metrics |
| GET | `/api/health` | Sanity check |
| POST | `/api/predict` | `{ features: {...}, threshold: 0.5 }` → probability + label |

Example POST body:

```json
{
  "features": { "price": 150, "photo_count": 5, "brand_tier": 4 },
  "threshold": 0.247
}
```

Any feature not provided falls back to its default.

## Demo script for the 5-minute live segment

1. **Open the page** (URL bar visible) — read the header line aloud:
   "60 features, test AUC 0.8150 with 95% CI of about ±0.06."
2. **Reset to defaults**, click **Predict** — show that the median
   listing has a low probability of selling (~5–7%), consistent with
   the marketplace's true sold rate.
3. **Search "price"** → drop `price` from default to a low value
   (e.g. 80 TL) → predict again. Probability goes up: cheaper items
   sell faster.
4. **Search "photo"** → set `photo_count` to 1 → predict. Probability
   drops: poor visual marketing.
5. **Search "brand"** → set `brand_tier` to 5 (luxury) → predict.
   Probability changes; explain price–brand interaction (H1 vs H2).
6. **Slide the τ threshold** to 0.247 (the F1-optimal value from §11)
   to show how flipping the operating point changes the predicted
   label without retraining. Tie this back to §15 (STATIC_ONLY
   threshold tuning) and the B.2 reviewer comment.

## Files

- `demo/demo_server.py` — Flask app (60 features, 1 model)
- `demo/demo_ui.html` — single-file vanilla-JS UI
- `demo/README.md` — this file
- (Reads from project root): `models/dolap_xgboost_pipeline.joblib`,
  `models/feature_schema.json`

## STUDENT CONFIG (lives in `demo_server.py`)

If the lecturer's template is required instead of this self-contained
version, copy these values into the template's STUDENT CONFIG block:

```python
MODEL_PATH     = "models/dolap_xgboost_pipeline.joblib"
FEATURE_SCHEMA = "models/feature_schema.json"   # if the template supports it
MODEL_TYPE     = "binary_classifier"
THRESHOLD      = 0.50          # default; F1-optimal is 0.247
METRICS = {
    "test_roc_auc": 0.8150,
    "test_roc_auc_ci": [0.7613, 0.8722],
    "test_f1_default": 0.2680,
    "test_f1_optimal": 0.3544,
    "cv_roc_auc_mean": 0.7517,
    "cv_roc_auc_std":  0.0239,
    "robustness_group_aware_auc": 0.6832,
}
```

`models/feature_schema.json` already lists the 60 feature names (`features` key),
their medians (`defaults` key), and 1st/99th-percentile ranges (`ranges` key),
so the UI does not need to be hand-coded if the template supports loading from
JSON.

## Lecturer's LMS template — comparison & migration path

If you ended up downloading the lecturer-provided files (LMS resource IDs
20527 / 20528 / 20529: `demo_server.py`, `demo_ui.html`, `README.txt`),
here is how they relate to ours:

- **Both follow the same structure**: a Flask server that loads a
  serialised model and returns `{ probability, predicted_label }` from a
  POST endpoint, plus a static HTML page that renders inputs.
- **Likely differences**: the lecturer's template hard-codes the feature
  list inside the HTML and reads only a single model artefact path; our
  version is data-driven (pulls names/defaults/ranges/presets from
  `feature_schema.json`) so adding a feature is a re-run of Section 17
  rather than an HTML edit.

If you must submit the lecturer's template, the minimum migration is:

1. Open the lecturer's `demo_server.py` and find the `STUDENT CONFIG`
   block; paste the values listed above.
2. Open `models/feature_schema.json` → copy the `features` array
   (60 names, in order) into the lecturer's template wherever feature
   names are listed.
3. Re-run the lecturer's server and confirm `/predict` returns the same
   probability our version returns for `defaults` (~0.067).

**Recommendation:** keep our version as the primary demo. It is
self-contained, has presets baked in (next section), and renders both
the prediction *and* the headline metrics card live, which makes the
5-minute demo block more impactful.

## Quick-scenario presets (built in)

To keep all 60 feature values mutually consistent (price ↔ price_log ↔
price_pctile_cat …), the UI ships with four pre-loaded scenarios that
are real rows pulled from the training data. Click any preset button
to populate every feature simultaneously, then press **Predict** to see
the probability:

| Senaryo | Açıklama | Live model P(sold) | Ground truth |
|---|---|---:|---|
| Hızlı satılan (yüksek olasılık) | Modelin %96 olasılıkla SOLD dediği gerçek bir listing | ~95.9% | Sold |
| Cold-start (henüz beğeni/yorum yok) | like_count=0, comment_count=0 ile satılmış bir listing | ~50.8% | Sold |
| Premium / lüks marka | brand_tier=4, is_known_brand=1, premium pricing | ~94.5% | Sold |
| Tipik / medyan ilan | Dataset'in tam ortası (defaults ile aynı) | ~2.3% | Not sold |

Presets ship in `models/feature_schema.json` under the `presets` key;
you can regenerate them by re-running notebook Section 17 (loads from
the trained model + v3 dataset and writes 4 representative rows).

## Demo script for the 5-minute live segment (preset-first, recommended)

1. **Open the page**, read the header line aloud:
   "60 features, test AUC 0.8150 with 95% CI of about ±0.06."
2. **Click "Tipik / medyan ilan"** — model returns ~2% probability.
   Tie this to the headline number: "the platform's true sold rate is
   about 5%, so the median listing has below-average odds."
3. **Click "Hızlı satılan"** — model returns ~96%. The contrast (2% vs
   96%) shows the model genuinely separates classes.
4. **Click "Cold-start"** — model returns ~51%. Tie this to §15:
   "engagement signals are unavailable here, but the listing still has
   structural quality that lifts it well above the median."
5. **Click "Premium / lüks marka"** — model returns ~94%. Tie back to
   H2 (brand-tier confirmatory analysis).
6. **Slide the τ threshold** to 0.247 (F1-optimal from §11) — the
   threshold marker on the gauge shifts. Pick the cold-start preset
   again: at τ = 0.50 it stays SOLD, but show how the gauge marker
   crosses the probability bar at τ = 0.247 to motivate B.2 (cold-start
   threshold tuning).

This sequence takes ~3 minutes and leaves time for one custom edit
(e.g. searching `price` in the filter and dropping it manually) before
the demo block ends.
