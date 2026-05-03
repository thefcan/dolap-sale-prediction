# Fallback Plan — If the Live Demo Fails During the Presentation

If anything goes wrong with the Flask + browser demo on stage (port
already in use, browser cache, network glitch, JS error, projector
DPI weirdness), here is how to keep the 5-minute demo block alive
**without leaving the notebook**.

## Tier-1 fallback — Manual prediction inside notebook (≈ 90 seconds)

Open `notebooks/dolap_classification_final.ipynb`, scroll to **Section
17**, and run a one-liner cell beneath the existing one. The trained
pipeline is already in memory under the name `demo_pipeline`; if the
kernel was restarted recently, run the line below first.

### One-time setup (only if kernel was restarted)

```python
import joblib, json, pandas as pd
demo_pipeline = joblib.load("../models/dolap_xgboost_pipeline.joblib")
SCHEMA        = json.load(open("../models/feature_schema.json", encoding="utf-8"))
DEFAULTS      = SCHEMA["defaults"]
PRESETS       = {p["id"]: p for p in SCHEMA["presets"]}
FEATURE_ORDER = SCHEMA["features"]
```

### Run a preset

```python
def run_preset(preset_id, threshold=0.50):
    p = PRESETS[preset_id]
    row = pd.DataFrame([p["features"]])[FEATURE_ORDER]
    proba = float(demo_pipeline.predict_proba(row)[0, 1])
    label = "SOLD within 7 days" if proba >= threshold else "NOT SOLD within 7 days"
    print(f"  Preset      : {p['label']}")
    print(f"  Description : {p['description']}")
    print(f"  Ground truth: {'SOLD' if p['true_label']==1 else 'NOT SOLD'}")
    print(f"  Threshold τ : {threshold}")
    print(f"  Model P(sold): {proba:.4f}  ({proba*100:.2f}%)")
    print(f"  Predicted   : {label}")

run_preset("median_listing")        # ~2.3%
run_preset("sold_high_conf")        # ~95.9%
run_preset("cold_start")            # ~50.8%
run_preset("premium_brand")         # ~94.5%
run_preset("cold_start", threshold=0.247)  # B.2 threshold story
```

### Run a custom edit (e.g. drop the price)

```python
import pandas as pd
row = dict(DEFAULTS)         # start from medians
row["price"] = 80            # cheap listing
row["price_log"] = 4.4       # keep derived feature consistent
row["photo_count"] = 8       # more photos
row["brand_tier"] = 5        # luxury

df_in = pd.DataFrame([row])[FEATURE_ORDER]
proba = float(demo_pipeline.predict_proba(df_in)[0, 1])
print(f"P(sold) = {proba:.4f}")
```

> **Note:** custom edits leave most derived features at the median, so
> the probability shift will be smaller than with a preset. The presets
> are the recommended demo path because every feature stays consistent.

## Tier-2 fallback — Show pre-computed numbers from §16

If the kernel itself is in trouble (restart loop, Python crash), the
**§16 inline ablation cell** has already-rendered output that the
audience can read directly:

- Headline AUC = 0.8150 [0.7613, 0.8722]
- Ablation table FULL / NO_ENGAGEMENT / STATIC_ONLY
- 2-panel bar chart with confidence intervals

Pair it with the §14 robustness chart and the §15 STATIC_ONLY threshold
sweep — you have three rendered figures that summarise the entire
modelling story without needing live inference.

## Tier-3 fallback — Static screenshots

If the laptop won't open the notebook at all, show:

- `reports/methodology_addendum.md` Section 2 (Tablo 7 with bootstrap CI)
- `reports/methodology_addendum.md` Section 6 (RC4 robustness table)
- `reports/methodology_addendum.md` Section 5 + 8.Y.1 (ablation + F1
  trade-off)

These are plain markdown and render cleanly in any text viewer.

## Pre-presentation 5-minute checklist

```
[ ] Notebook Run All clean (no red error stripes)
[ ] models/dolap_xgboost_pipeline.joblib exists  (ls -la models/)
[ ] models/feature_schema.json exists with "presets" key
[ ] Flask deps installed:   pip install flask flask-cors joblib pandas xgboost
[ ] Port 5000 free          (lsof -i :5000  →  empty)
[ ] python demo/demo_server.py  starts and prints "Test AUC: 0.8150"
[ ] Browser http://127.0.0.1:5000/  loads, sees 4 senaryo buttons
[ ] Click "Hızlı satılan"  →  prediction lands within 1 second
[ ] Threshold slider moves the gauge marker visibly
```

If any of these fail at the venue, drop down a tier in this document
and keep going — the audience won't notice the difference if you're
calm and the numbers on screen are right.
