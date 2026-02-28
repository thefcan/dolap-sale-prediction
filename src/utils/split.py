"""
Temporal (time-based) train / validation / test splitter.

In sale-prediction problems the model must NEVER see future data during
training, otherwise evaluation metrics are unrealistically optimistic
(data leakage).  This module enforces a strict chronological split.

Usage:
    from src.utils.split import temporal_train_val_test_split

    splits = temporal_train_val_test_split(
        df,
        time_col="listed_at",
        test_size=0.15,
        val_size=0.15,
    )
    train_df = splits["train"]
    val_df   = splits["val"]
    test_df  = splits["test"]
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# ── Public API ──────────────────────────────────────────────────────────────


def temporal_train_val_test_split(
    df: pd.DataFrame,
    time_col: str = "listed_at",
    test_size: float = 0.15,
    val_size: float = 0.15,
) -> dict[str, Any]:
    """Split a DataFrame chronologically — **no random shuffle**.

    The data is sorted by *time_col* and sliced into three contiguous
    segments so that:

    .. code-block:: text

        |<──── train ────>|<── val ──>|<── test ──>|
        oldest            cutoff_1    cutoff_2    newest

    Parameters
    ----------
    df : pd.DataFrame
        Must contain *time_col* with datetime-parseable values.
    time_col : str
        Column name holding listing timestamps. Default ``"listed_at"``.
    test_size : float
        Fraction of data reserved for the **test** set (newest rows).
    val_size : float
        Fraction of data reserved for the **validation** set
        (between train and test).

    Returns
    -------
    dict
        ``train``        – training DataFrame
        ``val``          – validation DataFrame
        ``test``         – test DataFrame
        ``cutoff_val``   – datetime boundary between train and val
        ``cutoff_test``  – datetime boundary between val and test
        ``split_sizes``  – ``{"train": N, "val": N, "test": N}``

    Raises
    ------
    ValueError
        If *time_col* is missing or size fractions are invalid.
    """
    # ── Guards ──────────────────────────────────────────────────────────
    if time_col not in df.columns:
        raise ValueError(
            f"Column '{time_col}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )

    if not (0 < test_size < 1):
        raise ValueError(f"test_size must be in (0, 1), got {test_size}")

    if not (0 < val_size < 1):
        raise ValueError(f"val_size must be in (0, 1), got {val_size}")

    if test_size + val_size >= 1.0:
        raise ValueError(
            f"test_size + val_size must be < 1.0, "
            f"got {test_size} + {val_size} = {test_size + val_size}"
        )

    # ── Ensure datetime type ────────────────────────────────────────────
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])

    # ── Sort chronologically — NEVER shuffle ────────────────────────────
    df = df.sort_values(time_col).reset_index(drop=True)

    n = len(df)
    n_test = int(n * test_size)
    n_val = int(n * val_size)
    n_train = n - n_val - n_test

    if n_train < 1:
        raise ValueError(
            f"Not enough samples for training split: "
            f"n={n}, n_train={n_train}, n_val={n_val}, n_test={n_test}"
        )

    # ── Slice ───────────────────────────────────────────────────────────
    train_df = df.iloc[:n_train]
    val_df = df.iloc[n_train : n_train + n_val]
    test_df = df.iloc[n_train + n_val :]

    cutoff_val = train_df[time_col].iloc[-1]
    cutoff_test = val_df[time_col].iloc[-1]

    split_sizes = {
        "train": len(train_df),
        "val": len(val_df),
        "test": len(test_df),
    }

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "cutoff_val": cutoff_val,
        "cutoff_test": cutoff_test,
        "split_sizes": split_sizes,
    }
