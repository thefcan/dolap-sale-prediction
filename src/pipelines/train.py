"""
Pipeline entrypoint: Train models.

Usage:
    python -m src.pipelines.train
    python -m src.pipelines.train --model xgboost --tune
"""

from __future__ import annotations

import argparse

# from src.models.trainer import ModelTrainer
# from src.utils.config import load_config
# from src.utils.logger import get_logger


AVAILABLE_MODELS = [
    "logistic_regression",
    "random_forest",
    "xgboost",
    "lightgbm",
    "catboost",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train classification models")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model.yaml",
        help="Path to model config YAML",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/processed",
        help="Directory containing train/val/test parquets",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=AVAILABLE_MODELS,
        default=None,
        help="Train a single model (default: all enabled in config)",
    )
    parser.add_argument(
        "--tune",
        action="store_true",
        help="Run Optuna hyperparameter tuning",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts/models",
        help="Directory to save trained model artifacts",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    print(f"[train] config     : {args.config}")
    print(f"[train] data_dir   : {args.data_dir}")
    print(f"[train] model      : {args.model or 'all enabled'}")
    print(f"[train] tune       : {args.tune}")
    print(f"[train] output_dir : {args.output_dir}")

    # ── Pipeline skeleton ──────────────────────────────────────────────
    # config = load_config(args.config)
    # logger = get_logger("train")
    #
    # 1. Load train.parquet + val.parquet
    # 2. Separate X, y
    # 3. Handle class imbalance (SMOTE / class_weight)
    # 4. For each enabled model:
    #    a. Instantiate with config params
    #    b. If --tune: run Optuna study
    #    c. Fit on train, evaluate on val
    #    d. Save model artifact → artifacts/models/{model_name}.pkl
    #    e. Log metrics → artifacts/metrics/{model_name}.json
    # 5. Print comparison table
    # ───────────────────────────────────────────────────────────────────

    print("[train] ✅ Pipeline skeleton ready — implement in src/models/")


if __name__ == "__main__":
    main()
