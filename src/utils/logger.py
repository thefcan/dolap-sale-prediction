"""
Structured logging with experiment context.

Wraps :pypi:`loguru` with a factory that automatically injects
``experiment_id`` into every log record so that log lines can be
correlated back to the exact experiment run that produced them.

Usage:
    from src.utils.logger import get_logger

    logger = get_logger("train", experiment_id="exp_20260301_143022")
    logger.info("Training started", model="xgboost", n_samples=12345)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger as _loguru_logger


# ── Module-level state ──────────────────────────────────────────────────────

_CONFIGURED = False
_EXPERIMENT_ID: str | None = None


# ── Constants ───────────────────────────────────────────────────────────────

_DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level:<8}</level> | "
    "<cyan>{extra[experiment_id]}</cyan> | "
    "<cyan>{extra[module_name]}</cyan>:{function}:{line} - "
    "<level>{message}</level>"
)

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level:<8} | "
    "{extra[experiment_id]} | "
    "{extra[module_name]}:{function}:{line} - "
    "{message}"
)


# ── Public API ──────────────────────────────────────────────────────────────


def setup_logging(
    level: str = "INFO",
    log_file: str | Path | None = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
    experiment_id: str | None = None,
) -> None:
    """Configure the global loguru logger (idempotent).

    Call this **once** at the beginning of a pipeline run.  Subsequent
    calls are no-ops to prevent duplicate handlers.

    Parameters
    ----------
    level : str
        Minimum log level (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``).
    log_file : str | Path, optional
        If provided, logs are also written to this file with rotation.
    rotation : str
        Loguru rotation spec (e.g. ``"10 MB"``).
    retention : str
        Loguru retention spec (e.g. ``"30 days"``).
    experiment_id : str, optional
        Experiment identifier injected into every log record.
    """
    global _CONFIGURED, _EXPERIMENT_ID  # noqa: PLW0603

    if _CONFIGURED:
        return

    _EXPERIMENT_ID = experiment_id or "no_experiment"

    # Remove loguru default handler
    _loguru_logger.remove()

    # Stderr handler (coloured)
    _loguru_logger.add(
        sys.stderr,
        level=level.upper(),
        format=_DEFAULT_FORMAT,
        colorize=True,
    )

    # File handler (plain text, with rotation)
    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _loguru_logger.add(
            str(log_path),
            level=level.upper(),
            format=_FILE_FORMAT,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
        )

    # Patch default extras so format strings never KeyError
    _loguru_logger.configure(
        extra={"experiment_id": _EXPERIMENT_ID, "module_name": "root"},
    )

    _CONFIGURED = True


def get_logger(
    module_name: str,
    experiment_id: str | None = None,
    **extra: Any,
) -> Any:
    """Return a context-bound loguru logger.

    Parameters
    ----------
    module_name : str
        Logical module name shown in log output (e.g. ``"train"``).
    experiment_id : str, optional
        Overrides the global experiment id for this logger instance.
    **extra
        Additional key-value pairs bound to every record from this logger.

    Returns
    -------
    loguru.Logger
        A bound logger instance.
    """
    # Ensure base logging is configured (safe to call multiple times)
    if not _CONFIGURED:
        setup_logging(experiment_id=experiment_id)

    ctx: dict[str, Any] = {
        "module_name": module_name,
    }

    if experiment_id is not None:
        ctx["experiment_id"] = experiment_id
    elif _EXPERIMENT_ID is not None:
        ctx["experiment_id"] = _EXPERIMENT_ID
    else:
        ctx["experiment_id"] = "no_experiment"

    ctx.update(extra)

    return _loguru_logger.bind(**ctx)


def reset_logging() -> None:
    """Reset the logging state — mainly useful for tests."""
    global _CONFIGURED, _EXPERIMENT_ID  # noqa: PLW0603
    _loguru_logger.remove()
    _CONFIGURED = False
    _EXPERIMENT_ID = None
