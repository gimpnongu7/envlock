"""Tests for envlock.prune."""

import time
from pathlib import Path

import pytest

from envlock.prune import PruneError, prune_snapshots
from envlock.snapshot import create_snapshot


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshots(env_file: Path, snapshot_dir: Path, count: int) -> list:
    names = []
    for i in range(count):
        env_file.write_text(f"KEY=value{i}\n")
        name = create_snapshot(env_file, snapshot_dir, label=f"snap{i}")
        names.append(name)
        # ensure distinct mtimes on fast filesystems
        time.sleep(0.01)
    return names


def test_prune_removes_oldest(env_file, snapshot_dir):
    _make_snapshots(env_file, snapshot_dir, 5)
    removed = prune_snapshots(snapshot_dir, keep=3)
    assert len(removed) == 2
    remaining = list(snapshot_dir.iterdir())
    assert len(remaining) == 3


def test_prune_dry_run_does_not_delete(env_file, snapshot_dir):
    _make_snapshots(env_file, snapshot_dir, 4)
    removed = prune_snapshots(snapshot_dir, keep=2, dry_run=True)
    assert len(removed) == 2
    # files should still be there
    assert len(list(snapshot_dir.iterdir())) == 4


def test_prune_keep_more_than_existing_is_noop(env_file, snapshot_dir):
    _make_snapshots(env_file, snapshot_dir, 2)
    removed = prune_snapshots(snapshot_dir, keep=10)
    assert removed == []
    assert len(list(snapshot_dir.iterdir())) == 2


def test_prune_keep_none_is_noop(env_file, snapshot_dir):
    _make_snapshots(env_file, snapshot_dir, 3)
    removed = prune_snapshots(snapshot_dir, keep=None)
    assert removed == []


def test_prune_invalid_keep_raises(snapshot_dir):
    with pytest.raises(PruneError, match="at least 1"):
        prune_snapshots(snapshot_dir, keep=0)


def test_prune_missing_dir_raises(tmp_path):
    missing = tmp_path / "no_such_dir"
    with pytest.raises(PruneError, match="not found"):
        prune_snapshots(missing, keep=2)


def test_prune_returns_removed_paths_as_path_objects(env_file, snapshot_dir):
    _make_snapshots(env_file, snapshot_dir, 3)
    removed = prune_snapshots(snapshot_dir, keep=1)
    assert all(isinstance(p, Path) for p in removed)
