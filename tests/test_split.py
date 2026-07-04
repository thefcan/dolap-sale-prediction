"""Unit tests for :mod:`src.utils.split` (temporal, leakage-safe splitting)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.utils.split import (
    temporal_group_train_val_test_split,
    temporal_train_val_test_split,
)

# ── temporal_train_val_test_split ────────────────────────────────────────────


def test_split_sizes_and_chronological_order():
    n = 100
    dates = pd.date_range("2025-01-01", periods=n, freq="h")
    # Shuffle the input so we can prove the splitter sorts by time itself.
    df = (
        pd.DataFrame({"listed_at": dates, "v": range(n)})
        .sample(frac=1, random_state=1)
        .reset_index(drop=True)
    )

    res = temporal_train_val_test_split(df, test_size=0.2, val_size=0.2)

    assert res["split_sizes"] == {"train": 60, "val": 20, "test": 20}
    # No temporal overlap between the three contiguous windows.
    assert res["train"]["listed_at"].max() <= res["val"]["listed_at"].min()
    assert res["val"]["listed_at"].max() <= res["test"]["listed_at"].min()
    # Cutoffs are the last timestamp of the preceding window.
    assert res["cutoff_val"] == res["train"]["listed_at"].iloc[-1]
    assert res["cutoff_test"] == res["val"]["listed_at"].iloc[-1]


def test_split_test_set_holds_newest_rows():
    n = 50
    df = pd.DataFrame(
        {"listed_at": pd.date_range("2025-01-01", periods=n, freq="D"), "v": range(n)}
    )
    res = temporal_train_val_test_split(df, test_size=0.2, val_size=0.2)
    # Newest row must live in the test window, never in train.
    newest = df["listed_at"].max()
    assert newest in set(res["test"]["listed_at"])
    assert newest not in set(res["train"]["listed_at"])


def test_split_missing_time_column_raises():
    df = pd.DataFrame({"a": [1, 2, 3]})
    with pytest.raises(ValueError):
        temporal_train_val_test_split(df, time_col="listed_at")


@pytest.mark.parametrize(
    ("test_size", "val_size"),
    [(0.0, 0.2), (1.0, 0.2), (0.2, 0.0), (0.2, 1.0), (0.6, 0.6)],
)
def test_split_invalid_sizes_raise(test_size, val_size):
    df = pd.DataFrame({"listed_at": pd.date_range("2025-01-01", periods=10, freq="D")})
    with pytest.raises(ValueError):
        temporal_train_val_test_split(df, test_size=test_size, val_size=val_size)


# ── temporal_group_train_val_test_split ──────────────────────────────────────


def test_group_split_removes_leaky_sellers():
    n = 20
    sellers = [f"s{i}" for i in range(n)]
    # A single seller straddles the oldest (train) and newest (test) rows.
    sellers[0] = "dup"
    sellers[-1] = "dup"
    df = (
        pd.DataFrame(
            {
                "listed_at": pd.date_range("2025-01-01", periods=n, freq="D"),
                "seller_username": sellers,
                "x": range(n),
            }
        )
        .sample(frac=1, random_state=0)
        .reset_index(drop=True)
    )

    res = temporal_group_train_val_test_split(
        df, group_col="seller_username", test_size=0.25, val_size=0.25
    )

    train_groups = set(res["train"]["seller_username"])
    val_groups = set(res["val"]["seller_username"])
    test_groups = set(res["test"]["seller_username"])

    # The whole point: no seller may appear in train AND in val/test.
    assert train_groups.isdisjoint(val_groups | test_groups)
    assert res["leakage"]["dropped_train_rows"] >= 1
    assert res["leakage"]["leakage_groups_after"] == 0


def test_group_split_missing_group_column_raises():
    df = pd.DataFrame(
        {"listed_at": pd.date_range("2025-01-01", periods=10, freq="D"), "x": range(10)}
    )
    with pytest.raises(ValueError):
        temporal_group_train_val_test_split(df, group_col="seller_username")
