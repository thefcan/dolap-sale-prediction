#!/usr/bin/env python3
"""RC4 — Seller-leakage robustness experiment.

Trains XGBoost twice on the canonical engineered feature set:
  (1) stratified random split (the protocol used for the published v3 result)
  (2) temporal group-aware split that prevents the same seller from
      appearing in train and test simultaneously

Reports Δ ROC-AUC + bootstrap 95% CI for both. The Δ quantifies how
much of the headline AUC could plausibly be attributed to seller
leakage rather than learned signal.

Inputs:
  - data/processed/engineered_features.parquet  (Phase 9 output, has seller_username)

Outputs:
  - artifacts/metrics/seller_leakage_robustness.json
  - artifacts/metrics/seller_leakage_robustness.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.split import temporal_group_train_val_test_split  # noqa: E402

INPUT_PATH = Path("data/processed/engineered_features.parquet")
OUT_JSON = Path("artifacts/metrics/seller_leakage_robustness.json")
OUT_MD = Path("artifacts/metrics/seller_leakage_robustness.md")
SEED = 42
TIME_COL = "scraped_at"
GROUP_COL = "seller_username"
TARGET_COL = "sold_within_7_days"


def _load_dataset() -> pd.DataFrame:
    df = pd.read_parquet(INPUT_PATH)
    # engineer.py drops scraped_at from the feature parquet — re-attach from merged_data
    md = pd.read_csv("data/interim/merged_data.csv", usecols=["listing_id", "scraped_at"])
    df = df.merge(md, on="listing_id", how="left")
    df = df[df[TARGET_COL].notna()].copy()
    df[TARGET_COL] = df[TARGET_COL].astype(int)
    df[GROUP_COL] = df[GROUP_COL].fillna("unknown_seller").astype(str)
    df[TIME_COL] = pd.to_datetime(df[TIME_COL], errors="coerce", utc=True)
    df = df.dropna(subset=[TIME_COL]).copy()
    return df


def _feature_columns(df: pd.DataFrame) -> list[str]:
    drop = {
        "listing_id", "cohort_id", TARGET_COL, TIME_COL, GROUP_COL,
        "exclude_from_training", "target_missing", "target_not_binary",
        "label_window_hours", "invalid_early_label", "invalid_late_label",
        "category", "brand_source",  # high-cardinality strings — leave out for parity
    }
    return [c for c in df.columns if c not in drop and df[c].dtype != object]


def _train_xgb(X_train, y_train, X_test, y_test):
    model = xgb.XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        eval_metric="logloss",
        random_state=SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return {
        "auc": float(roc_auc_score(y_test, proba)),
        "f1": float(f1_score(y_test, pred)),
        "y_test": y_test,
        "proba": proba,
    }


def _bootstrap_ci(y_true, y_proba, n_boot: int = 1000) -> tuple[float, float]:
    rng = np.random.RandomState(SEED)
    y_arr = np.asarray(y_true)
    p_arr = np.asarray(y_proba)
    n = len(y_arr)
    aucs: list[float] = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        if len(np.unique(y_arr[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y_arr[idx], p_arr[idx]))
    aucs = np.array(aucs)
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def main() -> None:
    df = _load_dataset()
    print(f"Loaded {len(df)} labeled rows with valid scraped_at + seller_username")
    print(f"Sold rate: {df[TARGET_COL].mean():.4f}")
    print(f"Unique sellers: {df[GROUP_COL].nunique()}")

    feature_cols = _feature_columns(df)
    print(f"Feature columns: {len(feature_cols)}")

    X = df[feature_cols].copy()
    y = df[TARGET_COL].values

    # ── Protocol A: stratified random split (matches v3 notebook recipe) ────
    Xa_train, Xa_test, ya_train, ya_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y, shuffle=True
    )
    res_a = _train_xgb(Xa_train, ya_train, Xa_test, ya_test)
    ci_a_lo, ci_a_hi = _bootstrap_ci(res_a["y_test"], res_a["proba"])
    print(f"\n[A] Random split:        AUC={res_a['auc']:.4f}  "
          f"F1={res_a['f1']:.4f}  CI=[{ci_a_lo:.4f}, {ci_a_hi:.4f}]")

    # ── Protocol B: temporal group-aware split ──────────────────────────────
    df_for_split = df.assign(_y=y)
    splits = temporal_group_train_val_test_split(
        df=df_for_split,
        time_col=TIME_COL,
        group_col=GROUP_COL,
        test_size=0.20,
        val_size=0.001,  # we only need train + test; val is ignored here
    )
    train_df = splits["train"]
    test_df = splits["test"]
    Xb_train = train_df[feature_cols]
    Xb_test = test_df[feature_cols]
    yb_train = train_df["_y"].astype(int).values
    yb_test = test_df["_y"].astype(int).values

    res_b = _train_xgb(Xb_train, yb_train, Xb_test, yb_test)
    ci_b_lo, ci_b_hi = _bootstrap_ci(res_b["y_test"], res_b["proba"])
    print(f"[B] Group-aware split:  AUC={res_b['auc']:.4f}  "
          f"F1={res_b['f1']:.4f}  CI=[{ci_b_lo:.4f}, {ci_b_hi:.4f}]")

    delta = res_b["auc"] - res_a["auc"]
    print(f"\nΔAUC (group - random) = {delta:+.4f}")

    leakage = splits["leakage"]
    print(f"Leakage groups before -> after: "
          f"{leakage['leakage_groups_before']} -> {leakage['leakage_groups_after']}")
    print(f"Train rows dropped to remove leakage: {leakage['dropped_train_rows']}")

    report = {
        "dataset": str(INPUT_PATH),
        "rows_used": int(len(df)),
        "feature_count": len(feature_cols),
        "n_unique_sellers": int(df[GROUP_COL].nunique()),
        "sold_rate": float(df[TARGET_COL].mean()),
        "seed": SEED,
        "protocol_A_random_split": {
            "name": "Stratified random shuffle (matches v3 notebook recipe)",
            "test_size": 0.20,
            "train_size": int(len(Xa_train)),
            "test_size_actual": int(len(Xa_test)),
            "auc": res_a["auc"],
            "f1": res_a["f1"],
            "auc_ci_95": [ci_a_lo, ci_a_hi],
        },
        "protocol_B_group_aware_split": {
            "name": "Temporal group-aware split (no seller leakage)",
            "test_size": 0.20,
            "train_size": int(len(Xb_train)),
            "test_size_actual": int(len(Xb_test)),
            "leakage_groups_before": leakage["leakage_groups_before"],
            "leakage_groups_after": leakage["leakage_groups_after"],
            "dropped_train_rows": leakage["dropped_train_rows"],
            "auc": res_b["auc"],
            "f1": res_b["f1"],
            "auc_ci_95": [ci_b_lo, ci_b_hi],
        },
        "delta_auc_group_minus_random": delta,
        "interpretation": (
            "If group-aware AUC drops sharply, the published random-split AUC "
            "was inflated by seller leakage. A small or null drop indicates the "
            "model learned generalisable signal rather than seller-identity shortcuts."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# RC4 — Seller-Leakage Robustness Experiment",
        "",
        f"- Dataset: `{INPUT_PATH}` (canonical Phase 9 features)",
        f"- Rows used: **{len(df)}** labeled listings with valid `scraped_at`",
        f"- Feature count: {len(feature_cols)}",
        f"- Unique sellers: {df[GROUP_COL].nunique()}",
        f"- Sold rate: {df[TARGET_COL].mean():.2%}",
        f"- Seed: {SEED}",
        "",
        "## Result table",
        "",
        "| Split protocol | Train | Test | ROC-AUC | F1 | 95% CI | ΔAUC vs A |",
        "|---|---:|---:|---:|---:|:---|---:|",
        (f"| **A — stratified random shuffle** | "
         f"{len(Xa_train)} | {len(Xa_test)} | **{res_a['auc']:.4f}** | "
         f"{res_a['f1']:.4f} | [{ci_a_lo:.4f}, {ci_a_hi:.4f}] | – |"),
        (f"| **B — temporal group-aware split** | "
         f"{len(Xb_train)} | {len(Xb_test)} | **{res_b['auc']:.4f}** | "
         f"{res_b['f1']:.4f} | [{ci_b_lo:.4f}, {ci_b_hi:.4f}] | "
         f"{delta:+.4f} |"),
        "",
        "## Leakage diagnostics (Protocol B)",
        "",
        f"- Leakage groups before drop: **{leakage['leakage_groups_before']}**",
        f"- Leakage groups after drop: **{leakage['leakage_groups_after']}**",
        f"- Train rows dropped to remove leakage: **{leakage['dropped_train_rows']}**",
        "",
        "## Interpretation",
        "",
        ("If the AUC under Protocol B is comparable to Protocol A, the headline "
         "result is robust to seller-identity leakage. A meaningful drop would "
         "imply that the random split granted the model an unfair advantage by "
         "exposing it to a seller's behaviour during training and then testing "
         "on the same seller's listings."),
        "",
    ]
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\njson saved: {OUT_JSON}")
    print(f"markdown saved: {OUT_MD}")


if __name__ == "__main__":
    main()
