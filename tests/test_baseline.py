"""Tests for envlock.baseline."""

import pytest
from pathlib import Path

from envlock.baseline import (
    set_baseline,
    get_baseline,
    clear_baseline,
    compare_to_baseline,
    BaselineError,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return f


def _make_snapshot(snapshot_dir: Path, sid: str, content: str) -> Path:
    p = snapshot_dir / f"{sid}.env"
    p.write_text(content)
    return p


def test_set_and_get_baseline(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "A=1\n")
    set_baseline(snapshot_dir, "snap1")
    assert get_baseline(snapshot_dir) == "snap1"


def test_get_baseline_none_when_unset(snapshot_dir):
    assert get_baseline(snapshot_dir) is None


def test_set_baseline_missing_snapshot_raises(snapshot_dir):
    with pytest.raises(BaselineError, match="Snapshot not found"):
        set_baseline(snapshot_dir, "ghost")


def test_clear_baseline_removes_marker(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "A=1\n")
    set_baseline(snapshot_dir, "snap1")
    clear_baseline(snapshot_dir)
    assert get_baseline(snapshot_dir) is None


def test_clear_baseline_noop_when_unset(snapshot_dir):
    clear_baseline(snapshot_dir)  # should not raise


def test_compare_to_baseline_no_changes(env_file, snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "DB_HOST=localhost\nDB_PORT=5432\n")
    set_baseline(snapshot_dir, "snap1")
    result = compare_to_baseline(env_file, snapshot_dir)
    assert not result.has_changes()
    assert "No changes" in result.summary()


def test_compare_to_baseline_detects_added(env_file, snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "DB_HOST=localhost\n")
    set_baseline(snapshot_dir, "snap1")
    result = compare_to_baseline(env_file, snapshot_dir)
    assert result.has_changes()
    assert "added" in result.summary()


def test_compare_to_baseline_detects_changed(env_file, snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "DB_HOST=remotehost\nDB_PORT=5432\n")
    set_baseline(snapshot_dir, "snap1")
    result = compare_to_baseline(env_file, snapshot_dir)
    assert result.has_changes()
    assert "changed" in result.summary()


def test_compare_no_baseline_raises(env_file, snapshot_dir):
    with pytest.raises(BaselineError, match="No baseline is set"):
        compare_to_baseline(env_file, snapshot_dir)


def test_compare_missing_baseline_file_raises(env_file, snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", "A=1\n")
    set_baseline(snapshot_dir, "snap1")
    (snapshot_dir / "snap1.env").unlink()  # remove after setting
    with pytest.raises(BaselineError, match="Baseline snapshot file missing"):
        compare_to_baseline(env_file, snapshot_dir)
