"""Unit tests for :mod:`src.utils.seed` (global reproducibility control)."""

from __future__ import annotations

import os
import random

import numpy as np

from src.utils.seed import set_global_seed


def test_python_random_is_reproducible():
    set_global_seed(123)
    first = [random.random() for _ in range(5)]
    set_global_seed(123)
    second = [random.random() for _ in range(5)]
    assert first == second


def test_numpy_random_is_reproducible():
    set_global_seed(7)
    first = np.random.rand(5)
    set_global_seed(7)
    second = np.random.rand(5)
    assert np.array_equal(first, second)


def test_pythonhashseed_env_is_set():
    set_global_seed(99)
    assert os.environ["PYTHONHASHSEED"] == "99"


def test_default_seed_is_42():
    set_global_seed()
    assert os.environ["PYTHONHASHSEED"] == "42"


def test_different_seeds_diverge():
    set_global_seed(1)
    a = [random.random() for _ in range(5)]
    set_global_seed(2)
    b = [random.random() for _ in range(5)]
    assert a != b
