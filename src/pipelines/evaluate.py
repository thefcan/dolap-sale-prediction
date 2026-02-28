"""
Pipeline entrypoint: Evaluate best model on held-out test set.

Usage:
    python -m src.pipelines.evaluate --model-path artifacts/models/xgboost.pkl
    python -m src.pipelines.evaluate --best
"""

from __future__ import annotations

import argparse
from pathlib import Path

# from src.evaluation.metrics import compute_all_metrics
# from src.evaluation.shap_analysis import run_shap
# from src.evaluation.plots import generate_plots
# from src.utils.config import load_config
# from src.utils.logger import get_logger


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate model on test set")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model.yaml",
        help="Path to model config YAML",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path to a specific model artifact (.pkl / .cbm)",
    )
    parser.add_argument(
        "--best",
        action="store_true",
        help="Auto-select the best model from artifacts/metrics/",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/processed",
        help="Directory containing test.parquet",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts",
        help="Root artifacts directory for figures & metrics output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    print(f"[evaluate] config     : {args.config}")
    print(f"[evaluate] model_path : {args.model_path or 'auto (--best)'}")
    print(f"[evaluate] data_dir   : {args.data_dir}")
    print(f"[evaluate] output_dir : {args.output_dir}")

    # ── Pipeline skeleton ──────────────────────────────────────────────
    # config = load_config(args.config)
    # logger = get_logger("evaluate")
    #
    # 1. Load test.parquet
    # 2. Load model artifact
    # 3. Predict probabilities on test set
    # 4. Compute metrics (AUC-ROC, F1, Precision, Recall, PR-AUC)
    # 5. Optimal threshold search (F1-maximize / Youden's J)
    # 6. Generate figures:
    #    a. ROC curve
    #    b. Precision-Recall curve
    #    c. Confusion matrix
    #    d. Calibration plot
    #    e. Feature importance bar chart
    # 7. SHAP analysis → beeswarm, waterfall, dependence plots
    # 8. Save everything:
    #    - artifacts/metrics/eval_results.json
    #    - artifacts/figures/roc_curve.png
    #    - artifacts/figures/shap_beeswarm.png
    #    - …
    # ───────────────────────────────────────────────────────────────────

    print("[evaluate] ✅ Pipeline skeleton ready — implement in src/evaluation/")


if __name__ == "__main__":
    main()
