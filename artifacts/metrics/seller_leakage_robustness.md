# RC4 — Seller-Leakage Robustness Experiment

- Dataset: `data/processed/engineered_features.parquet` (canonical Phase 9 features)
- Rows used: **5472** labeled listings with valid `scraped_at`
- Feature count: 26
- Unique sellers: 48
- Sold rate: 6.34%
- Seed: 42

## Result table

| Split protocol | Train | Test | ROC-AUC | F1 | 95% CI | ΔAUC vs A |
|---|---:|---:|---:|---:|:---|---:|
| **A — stratified random shuffle** | 4377 | 1095 | **0.7755** | 0.4421 | [0.7116, 0.8348] | – |
| **B — temporal group-aware split** | 4098 | 1094 | **0.6832** | 0.0000 | [0.6079, 0.7544] | -0.0922 |

## Leakage diagnostics (Protocol B)

- Leakage groups before drop: **1**
- Leakage groups after drop: **0**
- Train rows dropped to remove leakage: **275**

## Interpretation

If the AUC under Protocol B is comparable to Protocol A, the headline result is robust to seller-identity leakage. A meaningful drop would imply that the random split granted the model an unfair advantage by exposing it to a seller's behaviour during training and then testing on the same seller's listings.
