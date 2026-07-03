"""Unit tests for :mod:`src.utils.data_version` (content-hash dataset versioning)."""

from __future__ import annotations

import hashlib

import pytest

from src.utils.data_version import compute_dataset_hash, compute_file_hash

# ── compute_file_hash ────────────────────────────────────────────────────────


def test_compute_file_hash_matches_hashlib(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello world")
    assert compute_file_hash(f) == hashlib.sha256(b"hello world").hexdigest()


def test_compute_file_hash_honours_algorithm(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"data")
    assert compute_file_hash(f, algorithm="md5") == hashlib.md5(b"data").hexdigest()


# ── compute_dataset_hash ─────────────────────────────────────────────────────


def test_dataset_hash_is_deterministic(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"aaa")
    (tmp_path / "b.txt").write_bytes(b"bbb")
    first = compute_dataset_hash(tmp_path)
    second = compute_dataset_hash(tmp_path)
    assert first == second
    assert len(first) == 64  # sha256 hex digest


def test_dataset_hash_changes_when_content_changes(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"aaa")
    before = compute_dataset_hash(tmp_path)
    (tmp_path / "a.txt").write_bytes(b"aaaX")
    assert compute_dataset_hash(tmp_path) != before


def test_dataset_hash_changes_when_file_renamed(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"aaa")
    before = compute_dataset_hash(tmp_path)
    (tmp_path / "a.txt").rename(tmp_path / "renamed.txt")
    # Same bytes, different relative path -> different digest.
    assert compute_dataset_hash(tmp_path) != before


def test_dataset_hash_respects_glob_pattern(tmp_path):
    (tmp_path / "keep.csv").write_bytes(b"1")
    (tmp_path / "skip.txt").write_bytes(b"2")
    csv_only = compute_dataset_hash(tmp_path, glob_pattern="*.csv")
    # Deleting a non-matching file must not affect a filtered hash.
    (tmp_path / "skip.txt").unlink()
    assert compute_dataset_hash(tmp_path, glob_pattern="*.csv") == csv_only


def test_dataset_hash_identical_dirs_match(tmp_path):
    d1 = tmp_path / "d1"
    d2 = tmp_path / "d2"
    d1.mkdir()
    d2.mkdir()
    for d in (d1, d2):
        (d / "x.txt").write_bytes(b"same")
    assert compute_dataset_hash(d1) == compute_dataset_hash(d2)


def test_dataset_hash_missing_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        compute_dataset_hash(tmp_path / "does-not-exist")


def test_dataset_hash_no_matching_files_raises(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"1")
    with pytest.raises(ValueError):
        compute_dataset_hash(tmp_path, glob_pattern="*.parquet")
