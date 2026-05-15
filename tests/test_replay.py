"""Tests for envlock.replay."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envlock.replay import replay_snapshots, ReplayError
from envlock.snapshot import create_snapshot


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY=initial\n")
    return p


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshot(env_file: Path, snapshot_dir: Path, content: str, label: str) -> str:
    env_file.write_text(content)
    sid = create_snapshot(env_file, snapshot_dir, label=label)
    time.sleep(0.01)  # ensure distinct mtimes
    return sid


def test_replay_applies_all_snapshots(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "A=1\n", "snap-a")
    _make_snapshot(env_file, snapshot_dir, "A=2\n", "snap-b")
    sid_c = _make_snapshot(env_file, snapshot_dir, "A=3\n", "snap-c")

    result = replay_snapshots(env_file, snapshot_dir)

    assert len(result.applied) == 3
    assert not result.skipped
    # Final state should match the last snapshot
    assert env_file.read_text() == "A=3\n"


def test_replay_dry_run_does_not_modify(env_file, snapshot_dir):
    original = "KEY=original\n"
    env_file.write_text(original)
    _make_snapshot(env_file, snapshot_dir, "KEY=changed\n", "snap-1")
    env_file.write_text(original)

    result = replay_snapshots(env_file, snapshot_dir, dry_run=True)

    assert result.dry_run is True
    assert len(result.applied) == 1
    assert env_file.read_text() == original


def test_replay_specific_ids(env_file, snapshot_dir):
    sid_a = _make_snapshot(env_file, snapshot_dir, "A=1\n", "snap-a")
    _make_snapshot(env_file, snapshot_dir, "A=2\n", "snap-b")

    result = replay_snapshots(env_file, snapshot_dir, snapshot_ids=[sid_a])

    assert result.applied == [sid_a]
    assert env_file.read_text() == "A=1\n"


def test_replay_skips_missing_snapshot(env_file, snapshot_dir):
    sid = _make_snapshot(env_file, snapshot_dir, "X=1\n", "snap-x")

    result = replay_snapshots(env_file, snapshot_dir, snapshot_ids=[sid, "ghost-id"])

    assert sid in result.applied
    assert "ghost-id" in result.skipped


def test_replay_raises_if_no_snapshots(env_file, snapshot_dir):
    with pytest.raises(ReplayError, match="No snapshots"):
        replay_snapshots(env_file, snapshot_dir, snapshot_ids=[])


def test_replay_raises_if_dir_missing(env_file, tmp_path):
    missing = tmp_path / "no_such_dir"
    with pytest.raises(ReplayError, match="not found"):
        replay_snapshots(env_file, missing)


def test_replay_summary_dry_run(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "Z=9\n", "snap-z")
    result = replay_snapshots(env_file, snapshot_dir, dry_run=True)
    summary = result.summary()
    assert "Would apply" in summary
    assert "1 snapshot" in summary
