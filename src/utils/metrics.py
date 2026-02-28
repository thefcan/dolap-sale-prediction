"""
Metrics persistence for experiment tracking.

Computes standard classification metrics and persists them as JSON
inside the experiment directory so that every run is auditable.

Usage:
    from src.utils.metrics import save_metrics, compute_classification_metrics

    metrics = compute_classification_metrics(y_true, y_pred, y_prob)
    save_metrics(exp_dir, metrics, model_name="xgboost")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


# ── Public API ──────────────────────────────────────────────────────────────


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray | None = None,
) -> dict[str, float]:
    """Compute a comprehensive set of binary classification metrics.

    Parameters
    ----------
    y_true : array-like
        Ground truth labels (0 / 1).
    y_pred : array-like
        Predicted labels (0 / 1).
    y_prob : array-like, optional
        Predicted probabilities for the positive class.
        Required for ROC-AUC and PR-AUC.

    Returns
    -------
    dict[str, float]
        Metric name → value mapping.
    """
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    metrics: dict[str, float] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if y_prob is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            # Only one class present in y_true — AUC is undefined
            metrics["roc_auc"] = float("nan")

        try:
            metrics["average_precision"] = float(
                average_precision_score(y_true, y_prob)
            )
        except ValueError:
            metrics["average_precision"] = float("nan")

    return metrics


def save_metrics(
    exp_dir: str | Path,
    metrics: dict[str, Any],
    model_name: str = "model",
    filename: str | None = None,
) -> Path:
    """Persist *metrics* as JSON inside ``<exp_dir>/metrics/``.

    Parameters
    ----------
    exp_dir : str | Path
        Root of the experiment directory.
    metrics : dict
        Arbitrary JSON-serialisable metrics payload.
    model_name : str
        Used to construct the default filename (e.g. ``xgboost_metrics.json``).
    filename : str, optional
        Override the output filename. If ``None``, defaults to
        ``<model_name>_metrics.json``.

    Returns
    -------
    Path
        Absolute path to the written metrics file.
    """
    exp_dir = Path(exp_dir)
    metrics_dir = exp_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"{model_name}_metrics.json"

    out_path = metrics_dir / filename

    out_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False, default=_json_default)
        + "\n",
        encoding="utf-8",
    )
    return out_path


# ── Private helpers ─────────────────────────────────────────────────────────


def _json_default(obj: Any) -> Any:
    """Handle non-serialisable types that commonly appear in metrics."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)
