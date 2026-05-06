"""Tests for envlock.rollback."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envlock.snapshot import create_snapshot
from envlock.rollback import rollback, RollbackError, _resolve_snapshot_id


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY=value1\n")
    return p


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshots(env_file: Path, snapshot_dir: Path, values: list[str]) -> list[str]:
    names = []
    for v in values:
        env_file.write_text(f"KEY={v}\n")
        time.sleep(0.01)
        names.append(create_snapshot(env_file, snapshot_dir))
    return names


def test_rollback_one_step(env_file: Path, snapshot_dir: Path) -> None:
    _make_snapshots(env_file, snapshot_dir, ["v1", "v2", "v3"])
    rollback(env_file, snapshot_dir, steps_back=1)
    assert "KEY=v2" in env_file.read_text()


def test_rollback_two_steps(env_file: Path, snapshot_dir: Path) -> None:
    _make_snapshots(env_file, snapshot_dir, ["v1", "v2", "v3"])
    rollback(env_file, snapshot_dir, steps_back=2)
    assert "KEY=v1" in env_file.read_text()


def test_rollback_by_label(env_file: Path, snapshot_dir: Path) -> None:
    env_file.write_text("KEY=initial\n")
    create_snapshot(env_file, snapshot_dir, label="baseline")
    env_file.write_text("KEY=changed\n")
    create_snapshot(env_file, snapshot_dir)
    rollback(env_file, snapshot_dir, label="baseline")
    assert "KEY=initial" in env_file.read_text()


def test_rollback_dry_run_does_not_modify(env_file: Path, snapshot_dir: Path) -> None:
    _make_snapshots(env_file, snapshot_dir, ["v1", "v2"])
    env_file.write_text("KEY=v2\n")
    name = rollback(env_file, snapshot_dir, steps_back=1, dry_run=True)
    assert name  # returns snapshot name
    assert "KEY=v2" in env_file.read_text()  # file unchanged


def test_rollback_no_snapshots_raises(env_file: Path, snapshot_dir: Path) -> None:
    with pytest.raises(RollbackError, match="No snapshots"):
        rollback(env_file, snapshot_dir)


def test_rollback_steps_exceed_history_raises(env_file: Path, snapshot_dir: Path) -> None:
    _make_snapshots(env_file, snapshot_dir, ["v1", "v2"])
    with pytest.raises(RollbackError, match="Cannot go back"):
        rollback(env_file, snapshot_dir, steps_back=5)


def test_rollback_missing_label_raises(env_file: Path, snapshot_dir: Path) -> None:
    _make_snapshots(env_file, snapshot_dir, ["v1"])
    with pytest.raises(RollbackError, match="No snapshot matching label"):
        rollback(env_file, snapshot_dir, label="nonexistent")


def test_rollback_writes_audit_entry(env_file: Path, snapshot_dir: Path) -> None:
    from envlock.audit import read_log
    _make_snapshots(env_file, snapshot_dir, ["v1", "v2"])
    rollback(env_file, snapshot_dir, steps_back=1)
    entries = read_log(snapshot_dir)
    assert any(e.action == "rollback" for e in entries)
