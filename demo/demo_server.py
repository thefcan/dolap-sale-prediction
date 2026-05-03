"""Flask server for the live demo of the Dolap 7-Day Sale Prediction model.

Loads the joblib pipeline + feature schema produced by Section 17 of
``notebooks/dolap_classification_final.ipynb`` and exposes:

  GET  /                  -> demo_ui.html
  GET  /api/schema        -> feature schema (names, defaults, ranges, metrics)
  POST /api/predict       -> { features: { ... } } -> probability + label

Run from the project root:

    python demo/demo_server.py

Then open http://127.0.0.1:5000/ in a browser.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ─────────────────────────── STUDENT CONFIG ────────────────────────────
# Paths are resolved relative to the repository root (parent of this file).
REPO_ROOT      = Path(__file__).resolve().parent.parent
MODEL_PATH     = REPO_ROOT / "models" / "dolap_xgboost_pipeline.joblib"
SCHEMA_PATH    = REPO_ROOT / "models" / "feature_schema.json"
MODEL_TYPE     = "binary_classifier"
THRESHOLD_DEF  = 0.50
THRESHOLD_OPT  = 0.247  # F1-maximising threshold from §11
# ───────────────────────────────────────────────────────────────────────

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model artefact missing: {MODEL_PATH}. "
        f"Run Section 17 of dolap_classification_final.ipynb to produce it."
    )
if not SCHEMA_PATH.exists():
    raise FileNotFoundError(f"Schema missing: {SCHEMA_PATH}")

PIPELINE = joblib.load(MODEL_PATH)
SCHEMA   = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
FEATURES = SCHEMA["features"]
DEFAULTS = SCHEMA["defaults"]

app = Flask(__name__, static_folder=str(Path(__file__).parent), static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "demo_ui.html")


@app.route("/api/schema")
def schema():
    return jsonify(SCHEMA)


@app.route("/api/presets")
def presets():
    """Return ready-made demo scenarios (real rows from training data).

    Each preset contains all 60 feature values that stay mutually consistent
    (price ↔ price_log ↔ price_pctile_cat …) so single-feature edits in the
    UI don't break the derived-feature relationships.
    """
    return jsonify(SCHEMA.get("presets", []))


@app.route("/api/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    user_features = payload.get("features", {}) or {}

    row = {}
    for feat in FEATURES:
        if feat in user_features and user_features[feat] not in (None, ""):
            try:
                row[feat] = float(user_features[feat])
            except (TypeError, ValueError):
                row[feat] = float(DEFAULTS[feat])
        else:
            row[feat] = float(DEFAULTS[feat])

    df_in = pd.DataFrame([row])[FEATURES]
    proba = float(PIPELINE.predict_proba(df_in)[0, 1])

    threshold = float(payload.get("threshold", THRESHOLD_DEF))
    label = 1 if proba >= threshold else 0

    return jsonify({
        "probability_sold": proba,
        "probability_not_sold": 1.0 - proba,
        "threshold_used": threshold,
        "predicted_label": label,
        "predicted_text": "SOLD within 7 days" if label == 1 else "NOT SOLD within 7 days",
        "headline_auc": SCHEMA["headline_metrics"]["test_roc_auc"],
        "row_used": row,
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": SCHEMA["model_name"], "features": len(FEATURES)})


if __name__ == "__main__":
    print("=" * 70)
    print(f"  Dolap 7-Day Sale Prediction — Live Demo")
    print(f"  Model     : {SCHEMA['model_name']}")
    print(f"  Features  : {len(FEATURES)}")
    print(f"  Test AUC  : {SCHEMA['headline_metrics']['test_roc_auc']:.4f}  "
          f"(95% CI: {SCHEMA['headline_metrics']['test_roc_auc_ci']})")
    print(f"  Threshold : default={THRESHOLD_DEF}, optimal={THRESHOLD_OPT}")
    print(f"  URL       : http://127.0.0.1:5000/")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=False)
