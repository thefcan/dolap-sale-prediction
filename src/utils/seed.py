"""
Global reproducibility seed control.

Sets seeds for all stochastic libraries used in the project to ensure
deterministic behaviour across runs.

Usage:
    from src.utils.seed import set_global_seed

    set_global_seed(42)
"""

from __future__ import annotations

import os
import random
import warnings


def set_global_seed(seed: int = 42) -> None:
    """Pin every source of randomness to *seed*.

    Covers
    ------
    - :mod:`random` (Python stdlib)
    - :mod:`numpy`
    - :mod:`sklearn` (via numpy — sklearn has no independent RNG)
    - :mod:`xgboost` (via ``PYTHONHASHSEED`` and numpy seed)
    - Hash-based operations (``PYTHONHASHSEED``)

    Parameters
    ----------
    seed : int
        Integer seed value. Default ``42``.

    Notes
    -----
    ``PYTHONHASHSEED`` is set as an environment variable.  For it to take
    full effect on hash randomisation, the interpreter should be started
    **after** the variable is exported.  Within a running process the
    variable is honoured by ``dict`` / ``set`` ordering only from Python
    3.3+ when set before interpreter start.  Setting it here is still
    useful because XGBoost and other C-level libraries read it at runtime.
    """
    # Python stdlib
    random.seed(seed)

    # Hash seed — affects dict ordering & XGBoost internal hashing
    os.environ["PYTHONHASHSEED"] = str(seed)

    # NumPy
    try:
        import numpy as np

        np.random.seed(seed)

        # NumPy ≥ 1.17 Generator API (used by newer sklearn)
        # We don't replace the default_rng singleton, but libraries that
        # accept a `random_state` int will use this seed value.
    except ImportError:
        warnings.warn(
            "numpy not installed — skipping numpy seed.",
            RuntimeWarning,
            stacklevel=2,
        )

    # scikit-learn relies entirely on numpy's RNG when you pass
    # `random_state=seed` as an int, so the numpy seed above covers it.

    # XGBoost — reads PYTHONHASHSEED; also respects numpy seed for
    # data shuffling.  The `seed` / `random_state` param in the estimator
    # constructor should still be set explicitly in model config.

    # LightGBM — same story: numpy seed + `random_state` param.

    # CatBoost — uses `random_seed` param; numpy seed covers data splits.

    # PyTorch (optional — only if installed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass  # torch not required
