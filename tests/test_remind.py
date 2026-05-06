"""Tests for envlock.remind."""

import time
from pathlib import Path

import pytest

from envlock.remind import RemindError, check_reminder
from envlock.snapshot import create_snapshot


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    return p


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_no_snapshot_triggers_reminder(env_file, snapshot_dir):
    status = check_reminder(env_file, snapshot_dir)
    assert status.stale is True
    assert "No snapshot" in status.message
    assert status.last_snapshot_ts is None


def test_env_changed_after_snapshot_triggers_reminder(env_file, snapshot_dir):
    create_snapshot(env_file, snapshot_dir)
    # Bump mtime of env file into the future
    future = time.time() + 10
    import os
    os.utime(env_file, (future, future))
    status = check_reminder(env_file, snapshot_dir)
    assert status.stale is True
    assert "changed" in status.message


def test_old_snapshot_triggers_reminder(env_file, snapshot_dir):
    create_snapshot(env_file, snapshot_dir)
    # Set snapshot mtime to the past
    snap = list(snapshot_dir.iterdir())[0]
    past = time.time() - 200
    import os
    os.utime(snap, (past, past))
    status = check_reminder(env_file, snapshot_dir, max_age_seconds=100)
    assert status.stale is True
    assert "older than" in status.message


def test_fresh_snapshot_not_stale(env_file, snapshot_dir):
    # Snapshot env, then set env mtime before snapshot
    past_env = time.time() - 50
    import os
    os.utime(env_file, (past_env, past_env))
    create_snapshot(env_file, snapshot_dir)
    status = check_reminder(env_file, snapshot_dir, max_age_seconds=86400)
    assert status.stale is False
    assert "up to date" in status.message


def test_missing_env_raises(snapshot_dir, tmp_path):
    with pytest.raises(RemindError, match="not found"):
        check_reminder(tmp_path / "missing.env", snapshot_dir)


def test_status_contains_env_path(env_file, snapshot_dir):
    status = check_reminder(env_file, snapshot_dir)
    assert status.env_path == env_file
