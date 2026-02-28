"""
Dataset versioning via content hashing.

Computes a deterministic SHA-256 fingerprint for any set of data files,
enabling cheap equality checks between training runs without storing
full copies of large datasets.

Usage:
    from src.utils.data_version import compute_dataset_hash

    h = compute_dataset_hash("data/processed")
    # "a3f7c2..."  (64-char hex digest)

    h = compute_dataset_hash("data/processed", glob_pattern="*.parquet")
    # hash only parquet files
"""

from __future__ import annotations

import hashlib
from pathlib import Path


# ── Constants ───────────────────────────────────────────────────────────────

_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB read chunks


# ── Public API ──────────────────────────────────────────────────────────────


def compute_dataset_hash(
    data_dir: str | Path,
    glob_pattern: str = "*",
    algorithm: str = "sha256",
) -> str:
    """Compute a single hash over all files in *data_dir*.

    Files are sorted lexicographically by relative path so the hash is
    **deterministic** regardless of filesystem traversal order.
    Both the file path (relative) and its content contribute to the hash,
    so renaming a file changes the digest.

    Parameters
    ----------
    data_dir : str | Path
        Directory to hash.
    glob_pattern : str
        Only include files matching this glob (default ``"*"`` = everything).
        Common choices: ``"*.parquet"``, ``"*.csv"``, ``"*.jsonl"``.
    algorithm : str
        Any algorithm accepted by :func:`hashlib.new`.
        Default ``"sha256"``.

    Returns
    -------
    str
        Hex digest of the combined hash.

    Raises
    ------
    FileNotFoundError
        If *data_dir* does not exist.
    ValueError
        If no files match the pattern.
    """
    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    files = sorted(
        f for f in data_dir.rglob(glob_pattern) if f.is_file()
    )

    if not files:
        raise ValueError(
            f"No files matching '{glob_pattern}' found in {data_dir}"
        )

    hasher = hashlib.new(algorithm)

    for filepath in files:
        # Include relative path so renames change the hash
        rel = filepath.relative_to(data_dir)
        hasher.update(str(rel).encode("utf-8"))

        # Stream file content in chunks for memory efficiency
        with open(filepath, "rb") as fh:
            while True:
                chunk = fh.read(_CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)

    return hasher.hexdigest()


def compute_file_hash(
    filepath: str | Path,
    algorithm: str = "sha256",
) -> str:
    """Compute hash of a single file.

    Parameters
    ----------
    filepath : str | Path
        Path to the file.
    algorithm : str
        Hash algorithm (default ``"sha256"``).

    Returns
    -------
    str
        Hex digest.
    """
    filepath = Path(filepath)
    hasher = hashlib.new(algorithm)

    with open(filepath, "rb") as fh:
        while True:
            chunk = fh.read(_CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
