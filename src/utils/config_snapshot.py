"""
Config snapshot utility.

Copies all YAML configuration files into the experiment directory so that
every run is fully reproducible even if configs are modified later.

Usage:
    from src.utils.config_snapshot import snapshot_configs

    snapshot_configs("artifacts/experiments/exp_20260301_143022")
"""

from __future__ import annotations

import shutil
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────────────

DEFAULT_CONFIGS_DIR = Path("configs")


# ── Public API ──────────────────────────────────────────────────────────────


def snapshot_configs(
    exp_dir: str | Path,
    configs_dir: str | Path = DEFAULT_CONFIGS_DIR,
    glob_pattern: str = "*.yaml",
) -> list[Path]:
    """Copy every config file matching *glob_pattern* into ``<exp_dir>/configs/``.

    Parameters
    ----------
    exp_dir : str | Path
        Root of the experiment directory (must already exist).
    configs_dir : str | Path
        Source directory that contains the YAML files.
    glob_pattern : str
        Glob pattern to match config files. Default ``"*.yaml"``.

    Returns
    -------
    list[Path]
        Paths to the copied files inside ``<exp_dir>/configs/``.
    """
    exp_dir = Path(exp_dir)
    configs_dir = Path(configs_dir)
    dest_dir = exp_dir / "configs"
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []

    for src in sorted(configs_dir.glob(glob_pattern)):
        if not src.is_file():
            continue
        dst = dest_dir / src.name
        shutil.copy2(src, dst)
        copied.append(dst)

    # Also capture any nested YAML files (e.g. configs/overrides/*.yaml)
    for src in sorted(configs_dir.rglob(glob_pattern)):
        relative = src.relative_to(configs_dir)
        # Skip root-level files already handled above
        if relative.parent == Path("."):
            continue
        nested_dst = dest_dir / relative
        nested_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, nested_dst)
        copied.append(nested_dst)

    return copied
