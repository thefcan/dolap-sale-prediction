"""
Pipeline entrypoint: Reproducible model training.

Orchestrates the full experiment lifecycle:

    1. create_experiment    → timestamped experiment directory
    2. snapshot_configs     → freeze YAML configs into experiment
    3. set_global_seed      → pin all stochastic sources
    4. compute_dataset_hash → fingerprint data for versioning
    5. load dataset         → read processed parquet
    6. temporal split       → strictly time-based train/val/test
    7. train                → fit model(s)
    8. save model           → persist artefact into experiment
    9. save metrics         → persist evaluation metrics
   10. update metadata      → final experiment record

Usage:
    python -m src.pipelines.train
    python -m src.pipelines.train --model xgboost --tune
    python -m src.pipelines.train --experiment-name baseline_v1
"""

from __future__ import annotations

import argparse
import pickle
import time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.utils.experiment import create_experiment, save_metadata
from src.utils.config_snapshot import snapshot_configs
from src.utils.seed import set_global_seed
from src.utils.data_version import compute_dataset_hash
from src.utils.split import temporal_train_val_test_split
from src.utils.metrics import compute_classification_metrics, save_metrics
from src.utils.logger import setup_logging, get_logger


# ── Constants ───────────────────────────────────────────────────────────────

AVAILABLE_MODELS = [
    "logistic_regression",
    "random_forest",
    "xgboost",
]


# ── CLI ─────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reproducible model training pipeline",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model.yaml",
        help="Path to model config YAML",
    )
    parser.add_argument(
        "--pipeline-config",
        type=str,
        default="configs/pipeline.yaml",
        help="Path to pipeline config YAML",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/processed",
        help="Directory containing the processed dataset (parquet)",
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
        "--experiment-name",
        type=str,
        default=None,
        help="Human-readable experiment label",
    )
    return parser.parse_args(argv)


# ── Config loader ───────────────────────────────────────────────────────────


def _load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ── Model factory ──────────────────────────────────────────────────────────


def _build_model(model_name: str, params: dict[str, Any], seed: int) -> Any:
    """Instantiate a sklearn-compatible estimator by name.

    This is a factory that lazily imports the model class to avoid
    heavy import overhead at module level.
    """
    if model_name == "logistic_regression":
        from sklearn.linear_model import LogisticRegression

        return LogisticRegression(random_state=seed, **params)

    if model_name == "random_forest":
        from sklearn.ensemble import RandomForestClassifier

        return RandomForestClassifier(random_state=seed, **params)

    if model_name == "xgboost":
        from xgboost import XGBClassifier

        p = {k: v for k, v in params.items() if k != "early_stopping_rounds"}
        return XGBClassifier(
            random_state=seed,
            use_label_encoder=False,
            verbosity=0,
            **p,
        )

    raise ValueError(f"Unknown model: {model_name}")


# ── Model persistence ──────────────────────────────────────────────────────


def _save_model(model: Any, exp_dir: Path, model_name: str) -> Path:
    """Pickle a trained model into the experiment directory."""
    models_dir = exp_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    out_path = models_dir / f"{model_name}.pkl"
    with open(out_path, "wb") as fh:
        pickle.dump(model, fh, protocol=pickle.HIGHEST_PROTOCOL)
    return out_path


# ── Main pipeline ───────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # ── 1. Create experiment ────────────────────────────────────────────
    exp = create_experiment(name=args.experiment_name or "train")
    exp_id: str = exp["exp_id"]
    exp_dir: Path = exp["exp_dir"]

    # ── Setup structured logging ────────────────────────────────────────
    log_file = exp_dir / "train.log"
    setup_logging(
        level="INFO",
        log_file=str(log_file),
        experiment_id=exp_id,
    )
    logger = get_logger("train", experiment_id=exp_id)
    logger.info("Experiment created: {}", exp_id)

    # ── 2. Snapshot configs ─────────────────────────────────────────────
    copied = snapshot_configs(exp_dir)
    logger.info("Config snapshot saved ({} files)", len(copied))

    # ── 3. Set global seed ──────────────────────────────────────────────
    model_cfg = _load_yaml(args.config)
    seed = model_cfg.get("experiment", {}).get("seed", 42)
    set_global_seed(seed)
    logger.info("Global seed set to {}", seed)

    # ── 4. Compute dataset hash ─────────────────────────────────────────
    data_dir = Path(args.data_dir)
    if data_dir.exists() and any(data_dir.iterdir()):
        dataset_hash = compute_dataset_hash(data_dir, glob_pattern="*.parquet")
        logger.info("Dataset hash: {}", dataset_hash[:16] + "…")
    else:
        dataset_hash = "no_data"
        logger.warning("Data directory empty or missing: {}", data_dir)

    save_metadata(exp_dir, {"dataset_hash": dataset_hash, "seed": seed})

    # ── 5. Load dataset ─────────────────────────────────────────────────
    dataset_path = data_dir / "dataset.parquet"
    if not dataset_path.exists():
        logger.warning(
            "Processed dataset not found at {}. "
            "Pipeline skeleton complete — run scrape → label → build_dataset first.",
            dataset_path,
        )
        save_metadata(exp_dir, {"status": "skipped:no_data"})
        logger.info("Experiment directory: {}", exp_dir)
        return

    df = pd.read_parquet(dataset_path)
    logger.info("Loaded dataset: {} rows × {} cols", len(df), len(df.columns))

    # ── 6. Temporal split — strictly time-based ─────────────────────────
    test_size = model_cfg.get("experiment", {}).get("test_size", 0.15)
    val_size = model_cfg.get("experiment", {}).get("val_size", 0.15)

    splits = temporal_train_val_test_split(
        df,
        time_col="listed_at",
        test_size=test_size,
        val_size=val_size,
    )

    train_df = splits["train"]
    val_df = splits["val"]
    test_df = splits["test"]

    logger.info(
        "Temporal split → train={}, val={}, test={}",
        len(train_df),
        len(val_df),
        len(test_df),
    )
    logger.info("Val cutoff:  {}", splits["cutoff_val"])
    logger.info("Test cutoff: {}", splits["cutoff_test"])

    save_metadata(
        exp_dir,
        {
            "split_sizes": splits["split_sizes"],
            "cutoff_val": str(splits["cutoff_val"]),
            "cutoff_test": str(splits["cutoff_test"]),
        },
    )

    # ── Separate features / target ──────────────────────────────────────
    target_col = "sold_within_7_days"
    feature_cols = [c for c in train_df.columns if c not in (target_col, "listed_at")]

    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_val, y_val = val_df[feature_cols], val_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]

    # ── 7. Determine which models to train ──────────────────────────────
    if args.model:
        models_to_train = [args.model]
    else:
        models_to_train = [
            name
            for name in AVAILABLE_MODELS
            if model_cfg.get(name, {}).get("enabled", False)
        ]

    if not models_to_train:
        logger.warning("No models enabled in config — nothing to train.")
        save_metadata(exp_dir, {"status": "skipped:no_models"})
        return

    logger.info("Models to train: {}", models_to_train)
    all_results: dict[str, dict[str, Any]] = {}

    for model_name in models_to_train:
        logger.info("─── Training: {} ───", model_name)
        params = model_cfg.get(model_name, {}).get("params", {})

        # ── Build model ─────────────────────────────────────────────
        model = _build_model(model_name, params, seed)

        # ── Train ───────────────────────────────────────────────────
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_time = time.perf_counter() - t0

        logger.info("{} trained in {:.2f}s", model_name, train_time)

        # ── 8. Save model artefact ──────────────────────────────────
        model_path = _save_model(model, exp_dir, model_name)
        logger.info("Model saved → {}", model_path)

        # ── 9. Evaluate & save metrics ──────────────────────────────
        y_val_pred = model.predict(X_val)
        y_val_prob = (
            model.predict_proba(X_val)[:, 1]
            if hasattr(model, "predict_proba")
            else None
        )

        val_metrics = compute_classification_metrics(y_val, y_val_pred, y_val_prob)
        val_metrics["train_time_seconds"] = round(train_time, 4)
        val_metrics["split"] = "val"

        metrics_path = save_metrics(exp_dir, val_metrics, model_name=model_name)
        logger.info("{} val metrics saved → {}", model_name, metrics_path)

        for k, v in sorted(val_metrics.items()):
            if isinstance(v, float):
                logger.info("  {}: {:.4f}", k, v)

        all_results[model_name] = val_metrics

    # ── 10. Update final metadata ───────────────────────────────────────
    save_metadata(
        exp_dir,
        {
            "status": "completed",
            "models_trained": models_to_train,
            "feature_count": len(feature_cols),
            "features": feature_cols,
            "target": target_col,
            "tune": args.tune,
            "results_summary": {
                name: {
                    k: round(v, 4) if isinstance(v, float) else v
                    for k, v in res.items()
                }
                for name, res in all_results.items()
            },
        },
    )

    logger.info("✅ Training pipeline complete — {}", exp_dir)


if __name__ == "__main__":
    main()
