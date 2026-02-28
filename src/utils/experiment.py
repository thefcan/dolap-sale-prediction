"""
Experiment lifecycle management.

Creates a timestamped experiment directory under artifacts/experiments/
and persists run metadata (git hash, config snapshot, dataset version, etc.).

Usage:
    from src.utils.experiment import create_experiment, save_metadata

    exp = create_experiment(name="xgboost_baseline")
    # exp = {"exp_id": "exp_20260301_143022", "exp_dir": Path(...), ...}

    save_metadata(exp["exp_dir"], {
        "model": "xgboost",
        "auc_roc": 0.83,
        "dataset_hash": "abc123...",
    })
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Constants ───────────────────────────────────────────────────────────────

EXPERIMENTS_ROOT = Path("artifacts/experiments")


# ── Public API ──────────────────────────────────────────────────────────────


def create_experiment(
    name: str | None = None,
    root: str | Path = EXPERIMENTS_ROOT,
) -> dict[str, Any]:
    """Create a new experiment directory with a unique timestamped ID.

    Parameters
    ----------
    name : str, optional
        Human-readable experiment label (e.g. ``"xgboost_baseline"``).
        Appended to the directory name for readability.
    root : str | Path
        Parent directory for all experiments.

    Returns
    -------
    dict
        ``exp_id``  – unique identifier (``exp_<timestamp>[_<name>]``)
        ``exp_dir`` – :class:`Path` to the created directory
        ``created_at`` – ISO-8601 UTC timestamp
        ``git_hash``   – current HEAD commit hash (or ``"unknown"``)
    """
    root = Path(root)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    exp_id = f"exp_{ts}" if name is None else f"exp_{ts}_{name}"

    exp_dir = root / exp_id
    exp_dir.mkdir(parents=True, exist_ok=True)

    # Create standard sub-directories inside the experiment
    (exp_dir / "configs").mkdir(exist_ok=True)
    (exp_dir / "metrics").mkdir(exist_ok=True)
    (exp_dir / "figures").mkdir(exist_ok=True)
    (exp_dir / "models").mkdir(exist_ok=True)

    git_hash = get_git_commit_hash()
    created_at = datetime.now(timezone.utc).isoformat()

    meta: dict[str, Any] = {
        "exp_id": exp_id,
        "exp_dir": str(exp_dir),
        "created_at": created_at,
        "git_hash": git_hash,
        "python_version": sys.version,
    }

    # Persist initial metadata
    _write_json(exp_dir / "metadata.json", meta)

    return {
        "exp_id": exp_id,
        "exp_dir": exp_dir,
        "created_at": created_at,
        "git_hash": git_hash,
    }


def save_metadata(
    exp_dir: str | Path,
    extra: dict[str, Any],
    filename: str = "metadata.json",
) -> Path:
    """Merge *extra* key-value pairs into the experiment metadata file.

    Existing keys are preserved; new keys are added. If a key already exists
    it will be **overwritten** with the new value, allowing incremental
    updates (e.g. add metrics after training finishes).

    Parameters
    ----------
    exp_dir : str | Path
        Experiment directory that already contains ``metadata.json``.
    extra : dict
        Arbitrary JSON-serialisable payload to persist.
    filename : str
        Name of the metadata file (default ``metadata.json``).

    Returns
    -------
    Path
        Absolute path to the written metadata file.
    """
    exp_dir = Path(exp_dir)
    meta_path = exp_dir / filename

    existing: dict[str, Any] = {}
    if meta_path.exists():
        existing = json.loads(meta_path.read_text(encoding="utf-8"))

    existing.update(extra)
    _write_json(meta_path, existing)
    return meta_path


def get_git_commit_hash(short: bool = False) -> str:
    """Return the current HEAD commit hash.

    Parameters
    ----------
    short : bool
        If ``True`` return the abbreviated (7-char) hash.

    Returns
    -------
    str
        Commit SHA or ``"unknown"`` if git is unavailable / not a repo.
    """
    cmd = ["git", "rev-parse"]
    if short:
        cmd.append("--short")
    cmd.append("HEAD")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return "unknown"


# ── Private helpers ─────────────────────────────────────────────────────────


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Atomically write *data* as pretty-printed JSON."""
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
