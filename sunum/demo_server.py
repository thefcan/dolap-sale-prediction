"""
========================================================
  ML MODEL DEMO — BACKEND SERVER
  Grup: Dolap Sale Prediction
  Proje: Predicting Second-Hand Clothing Sales on Dolap.com
========================================================

KURULUM / SETUP:
  pip install flask flask-cors joblib scikit-learn imbalanced-learn xgboost numpy pandas

ÇALIŞTIRMA / RUN:
  cd sunum/
  python demo_server.py
  → Tarayıcıda / Open in browser: http://localhost:5000

NOTLAR / NOTES:
  - Model 12 en önemli özellik (SHAP rank 1-12) üzerinde eğitilmiştir.
  - Optimal karar eşiği: 0.247 (F1 maximising threshold)
  - AUC = 0.797 (12 feat) / 0.812 (full 60 feat)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__, static_folder=".")
CORS(app)  # allows the HTML file to call this server


# ================================================================
#  STUDENT CONFIG — Dolap Sale Prediction
# ================================================================

MODEL_PATH   = "model.joblib"    # XGBoost (12 key features, SMOTE-balanced)
SCALER_PATH  = "scaler.joblib"   # StandardScaler fitted on training set
IMPUTER_PATH = "imputer.joblib"  # SimpleImputer (median strategy)

MODEL_TYPE = "classification"    # binary: 0=Not Sold, 1=Sold within 7 days

# Optimal decision threshold (F1-maximising, from threshold optimisation)
OPTIMAL_THRESHOLD = 0.247

# Feature names — top 12 by SHAP importance (same order as model training!)
FEATURE_NAMES = [
    "like_count",
    "engagement_score",
    "price_pctile_cat",
    "n_cheaper_in_cat",
    "condition_score",
    "brand_tier",
    "seller_exp_log",
    "listing_quality_score",
    "has_free_shipping",
    "price_log",
    "photo_count",
    "price_vs_brand_median",
]

# Human-readable labels for the UI
FEATURE_LABELS = [
    "Like Count (❤️ Beğeni sayısı)",
    "Engagement Score (2×likes + 3×comments)",
    "Price Percentile in Category (0=cheapest → 1=most expensive)",
    "Fraction Cheaper in Category (0→1)",
    "Condition (1=Used, 2=Lightly Used, 3=New, 4=New & Tagged)",
    "Brand Tier (0=Unknown … 5=Luxury/Sport Premium)",
    "Seller Experience = log(1 + rating_count)",
    "Listing Quality Score (0=incomplete … 7=perfect)",
    "Free Shipping (0=Buyer Pays, 1=Free)",
    "Price Log = log(1 + price_TRY)",
    "Photo Count",
    "Price vs Brand Median (negative=below median)",
]

# Classification labels
CLASS_LABELS = {
    0: "❌ Not Sold (7 gün içinde satılmaz)",
    1: "✅ Sold (7 gün içinde satılır)",
}

# Model performance (shown in UI header)
MODEL_INFO = {
    "model_name"     : "XGBoost Classifier (SMOTE-balanced)",
    "metric1_label"  : "ROC-AUC (test)",
    "metric1_value"  : "0.7969",
    "metric2_label"  : "Optimal Threshold",
    "metric2_value"  : "0.247",
    "training_note"  : "Trained on 6,007 Dolap.com listings · 12 SHAP-top features · Class imbalance 16:1 corrected with SMOTE",
}

# ================================================================
#  END OF STUDENT CONFIG
# ================================================================


# --- load model, scaler and imputer at startup ---
print(f"\n[demo_server] Loading model from: {MODEL_PATH}")
try:
    model = joblib.load(MODEL_PATH)
    print(f"[demo_server] Model loaded: {type(model).__name__}")
except FileNotFoundError:
    print(f"[demo_server] ERROR: Model file not found at '{MODEL_PATH}'")
    print("              Run:  python ../demo/save_model_sunum.py")
    model = None

scaler = None
if SCALER_PATH:
    try:
        scaler = joblib.load(SCALER_PATH)
        print(f"[demo_server] Scaler loaded: {type(scaler).__name__}")
    except FileNotFoundError:
        print(f"[demo_server] WARNING: Scaler not found at '{SCALER_PATH}'")

imputer = None
if 'IMPUTER_PATH' in dir() and IMPUTER_PATH:
    try:
        imputer = joblib.load(IMPUTER_PATH)
        print(f"[demo_server] Imputer loaded: {type(imputer).__name__}")
    except FileNotFoundError:
        print(f"[demo_server] WARNING: Imputer not found at '{IMPUTER_PATH}'")


@app.route("/")
def index():
    """Serve the UI HTML file."""
    return send_from_directory(".", "demo_ui.html")


@app.route("/config")
def get_config():
    """Return model config so the UI can build itself dynamically."""
    return jsonify({
        "model_type":   MODEL_TYPE,
        "feature_names": FEATURE_NAMES,
        "feature_labels": FEATURE_LABELS,
        "target_label": TARGET_LABEL,
        "target_unit":  TARGET_UNIT,
        "target_min":   TARGET_MIN,
        "target_max":   TARGET_MAX,
        "class_labels": CLASS_LABELS,
        "model_info":   MODEL_INFO,
        "model_ready":  model is not None,
    })


@app.route("/predict", methods=["POST"])
def predict():
    """Receive feature values and return model prediction."""
    if model is None:
        return jsonify({"error": f"Model not loaded. Check that '{MODEL_PATH}' exists."}), 500

    data = request.get_json()
    if not data or "features" not in data:
        return jsonify({"error": "Request must include a 'features' dict."}), 400

    raw = data["features"]

    # build feature vector in the correct order
    try:
        values = [float(raw[name]) for name in FEATURE_NAMES]
    except KeyError as e:
        return jsonify({"error": f"Missing feature: {e}. Expected: {FEATURE_NAMES}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid feature value: {e}"}), 400

    # reshape for sklearn
    X = np.array(values).reshape(1, -1)

    # impute missing values
    if imputer is not None:
        X = imputer.transform(X)

    # scale
    if scaler is not None:
        X = scaler.transform(X)

    # predict
    try:
        # --- CLASSIFICATION with optimal threshold ---
        proba = model.predict_proba(X)[0]
        prob_sold = float(proba[1])
        pred_class = int(prob_sold >= OPTIMAL_THRESHOLD)  # 0.247 threshold
        class_name = CLASS_LABELS.get(pred_class, str(pred_class))
        all_proba = {
            CLASS_LABELS.get(i, str(i)): round(float(p), 3)
            for i, p in enumerate(proba)
        }
        result = {
            "predicted_class"     : class_name,
            "predicted_class_int" : pred_class,
            "confidence"          : round(prob_sold, 3),
            "sale_probability_pct": round(prob_sold * 100, 1),
            "threshold_used"      : OPTIMAL_THRESHOLD,
            "all_probabilities"   : all_proba,
        }

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    # feature importances
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        result["feature_importances"] = {
            FEATURE_NAMES[i]: round(float(importances[i]), 4)
            for i in range(len(FEATURE_NAMES))
        }

    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  ML Demo Server")
    print("  Open in browser: http://localhost:5000")
    print("="*55 + "\n")
    app.run(debug=False, port=5000, host="0.0.0.0")
