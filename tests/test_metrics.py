"""Unit tests for :mod:`src.utils.metrics` (classification metrics + persistence)."""

from __future__ import annotations

import json
import math

import numpy as np

from src.utils.metrics import (
    _json_default,
    compute_classification_metrics,
    save_metrics,
)

# ── compute_classification_metrics ───────────────────────────────────────────


def test_perfect_predictions_score_one():
    y = [0, 1, 0, 1, 1]
    m = compute_classification_metrics(y, y)
    assert m["accuracy"] == 1.0
    assert m["precision"] == 1.0
    assert m["recall"] == 1.0
    assert m["f1"] == 1.0
    # No probabilities supplied -> no ranking metrics.
    assert "roc_auc" not in m


def test_probabilities_add_ranking_metrics():
    m = compute_classification_metrics(
        y_true=[0, 0, 1, 1], y_pred=[0, 0, 1, 1], y_prob=[0.1, 0.2, 0.8, 0.9]
    )
    assert m["roc_auc"] == 1.0
    assert "average_precision" in m


def test_single_class_roc_auc_is_nan():
    # ROC-AUC is undefined with a single class in y_true -> the code degrades to NaN.
    m = compute_classification_metrics(y_true=[1, 1, 1], y_pred=[1, 1, 1], y_prob=[0.6, 0.7, 0.8])
    assert math.isnan(m["roc_auc"])
    # average_precision remains defined (all-positive -> 1.0); it must stay present.
    assert "average_precision" in m
    assert not math.isnan(m["average_precision"])


def test_zero_division_is_handled():
    # Predicts all-negative while positives exist -> precision/recall = 0, no crash.
    m = compute_classification_metrics(y_true=[1, 1, 0], y_pred=[0, 0, 0])
    assert m["precision"] == 0.0
    assert m["recall"] == 0.0


# ── save_metrics ─────────────────────────────────────────────────────────────


def test_save_metrics_roundtrips(tmp_path):
    payload = {"accuracy": 0.9, "f1": 0.8}
    out = save_metrics(tmp_path, payload, model_name="xgb")
    assert out.exists()
    assert out.name == "xgb_metrics.json"
    assert out.parent.name == "metrics"
    assert json.loads(out.read_text(encoding="utf-8")) == payload


def test_save_metrics_custom_filename(tmp_path):
    out = save_metrics(tmp_path, {"a": 1}, filename="custom.json")
    assert out.name == "custom.json"


def test_save_metrics_serialises_numpy(tmp_path):
    payload = {"n": np.int64(5), "score": np.float64(0.5), "arr": np.array([1, 2, 3])}
    out = save_metrics(tmp_path, payload, model_name="m")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["n"] == 5
    assert loaded["score"] == 0.5
    assert loaded["arr"] == [1, 2, 3]


# ── _json_default ────────────────────────────────────────────────────────────


def test_json_default_converts_numpy_scalars_and_arrays():
    assert _json_default(np.int64(3)) == 3
    assert _json_default(np.float64(2.5)) == 2.5
    assert _json_default(np.array([1, 2])) == [1, 2]


def test_json_default_falls_back_to_str():
    assert isinstance(_json_default(object()), str)
