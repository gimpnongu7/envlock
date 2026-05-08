"""Tests for envlock.status."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envlock.status import get_status, format_status, StatusError, StatusReport
from envlock.remind import ReminderStatus


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDEBUG=true\n")
    return p


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _fresh_reminder(env_path):
    return ReminderStatus(needs_reminder=False, message="", env_path=env_path)


def _stale_reminder(env_path):
    return ReminderStatus(needs_reminder=True, message="Snapshot is stale", env_path=env_path)


def test_get_status_raises_if_snapshot_dir_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("X=1\n")
    with pytest.raises(StatusError, match="Snapshot directory not found"):
        get_status(env, tmp_path / "nonexistent")


def test_get_status_env_missing(snapshot_dir, tmp_path):
    missing_env = tmp_path / ".env"
    with patch("envlock.status.check_reminder", return_value=_fresh_reminder(missing_env)), \
         patch("envlock.status.list_snapshots", return_value=[]):
        report = get_status(missing_env, snapshot_dir)
    assert not report.env_exists
    assert any(".env file not found" in w for w in report.warnings)


def test_get_status_ok_when_fresh_and_clean(env_file, snapshot_dir):
    fake_lint = MagicMock()
    fake_lint.ok.return_value = True
    fake_lint.issues = []
    with patch("envlock.status.check_reminder", return_value=_fresh_reminder(env_file)), \
         patch("envlock.status.list_snapshots", return_value=["snap_001"]), \
         patch("envlock.status.lint_env_file", return_value=fake_lint):
        report = get_status(env_file, snapshot_dir)
    assert report.ok()
    assert report.snapshot_count == 1
    assert report.latest_snapshot == "snap_001"


def test_get_status_not_ok_when_stale(env_file, snapshot_dir):
    fake_lint = MagicMock()
    fake_lint.ok.return_value = True
    fake_lint.issues = []
    with patch("envlock.status.check_reminder", return_value=_stale_reminder(env_file)), \
         patch("envlock.status.list_snapshots", return_value=["snap_001"]), \
         patch("envlock.status.lint_env_file", return_value=fake_lint):
        report = get_status(env_file, snapshot_dir)
    assert not report.ok()
    assert any("stale" in w.lower() for w in report.warnings)


def test_get_status_not_ok_when_lint_issues(env_file, snapshot_dir):
    fake_lint = MagicMock()
    fake_lint.ok.return_value = False
    fake_lint.issues = [MagicMock()]
    with patch("envlock.status.check_reminder", return_value=_fresh_reminder(env_file)), \
         patch("envlock.status.list_snapshots", return_value=[]), \
         patch("envlock.status.lint_env_file", return_value=fake_lint):
        report = get_status(env_file, snapshot_dir)
    assert not report.ok()


def test_format_status_contains_key_info(env_file, snapshot_dir):
    fake_lint = MagicMock()
    fake_lint.ok.return_value = True
    fake_lint.issues = []
    with patch("envlock.status.check_reminder", return_value=_fresh_reminder(env_file)), \
         patch("envlock.status.list_snapshots", return_value=["snap_001", "snap_002"]), \
         patch("envlock.status.lint_env_file", return_value=fake_lint):
        report = get_status(env_file, snapshot_dir)
    output = format_status(report)
    assert "snapshots" in output
    assert "snap_002" in output
    assert "✓" in output


def test_format_status_shows_warnings(env_file, snapshot_dir):
    fake_lint = MagicMock()
    fake_lint.ok.return_value = True
    fake_lint.issues = []
    with patch("envlock.status.check_reminder", return_value=_stale_reminder(env_file)), \
         patch("envlock.status.list_snapshots", return_value=[]), \
         patch("envlock.status.lint_env_file", return_value=fake_lint):
        report = get_status(env_file, snapshot_dir)
    output = format_status(report)
    assert "warnings" in output
    assert "Snapshot is stale" in output
