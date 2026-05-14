"""Tests for envlock.sync."""

import pytest
from pathlib import Path
from envlock.sync import push_snapshots, pull_snapshots, SyncError, SyncResult


@pytest.fixture
def local_dir(tmp_path):
    d = tmp_path / "local"
    d.mkdir()
    return d


@pytest.fixture
def remote_dir(tmp_path):
    d = tmp_path / "remote"
    d.mkdir()
    return d


def _make_snapshot(directory: Path, name: str, content: str = "KEY=value\n") -> Path:
    p = directory / name
    p.write_text(content)
    return p


# --- push ---

def test_push_copies_snapshots(local_dir, remote_dir):
    _make_snapshot(local_dir, "snap1.env")
    _make_snapshot(local_dir, "snap2.env")
    result = push_snapshots(local_dir, remote_dir)
    assert set(result.pushed) == {"snap1.env", "snap2.env"}
    assert (remote_dir / "snap1.env").exists()
    assert (remote_dir / "snap2.env").exists()


def test_push_copies_companion_meta(local_dir, remote_dir):
    snap = _make_snapshot(local_dir, "snap1.env")
    snap.with_suffix(".json").write_text('{"id": "snap1"}')
    push_snapshots(local_dir, remote_dir)
    assert (remote_dir / "snap1.json").exists()


def test_push_skips_existing_without_overwrite(local_dir, remote_dir):
    _make_snapshot(local_dir, "snap1.env", "NEW=1\n")
    _make_snapshot(remote_dir, "snap1.env", "OLD=1\n")
    result = push_snapshots(local_dir, remote_dir, overwrite=False)
    assert "snap1.env" in result.skipped
    assert (remote_dir / "snap1.env").read_text() == "OLD=1\n"


def test_push_overwrites_when_flag_set(local_dir, remote_dir):
    _make_snapshot(local_dir, "snap1.env", "NEW=1\n")
    _make_snapshot(remote_dir, "snap1.env", "OLD=1\n")
    result = push_snapshots(local_dir, remote_dir, overwrite=True)
    assert "snap1.env" in result.pushed
    assert (remote_dir / "snap1.env").read_text() == "NEW=1\n"


def test_push_raises_if_local_missing(tmp_path, remote_dir):
    with pytest.raises(SyncError, match="Local snapshot directory not found"):
        push_snapshots(tmp_path / "nonexistent", remote_dir)


# --- pull ---

def test_pull_copies_snapshots(local_dir, remote_dir):
    _make_snapshot(remote_dir, "snap1.env")
    result = pull_snapshots(local_dir, remote_dir)
    assert "snap1.env" in result.pulled
    assert (local_dir / "snap1.env").exists()


def test_pull_skips_existing_without_overwrite(local_dir, remote_dir):
    _make_snapshot(remote_dir, "snap1.env", "REMOTE=1\n")
    _make_snapshot(local_dir, "snap1.env", "LOCAL=1\n")
    result = pull_snapshots(local_dir, remote_dir, overwrite=False)
    assert "snap1.env" in result.skipped
    assert (local_dir / "snap1.env").read_text() == "LOCAL=1\n"


def test_pull_raises_if_remote_missing(local_dir, tmp_path):
    with pytest.raises(SyncError, match="Remote directory not found"):
        pull_snapshots(local_dir, tmp_path / "nonexistent")


# --- SyncResult.summary ---

def test_summary_nothing_to_sync():
    assert SyncResult().summary() == "Nothing to sync."


def test_summary_lists_actions():
    r = SyncResult(pushed=["a.env"], skipped=["b.env"])
    s = r.summary()
    assert "a.env" in s
    assert "b.env" in s
