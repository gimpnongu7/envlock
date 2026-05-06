"""Tests for envlock.cli_rollback."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envlock.snapshot import create_snapshot
from envlock.cli_rollback import cmd_rollback, add_rollback_subparser


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"env_file": ".env", "snapshot_dir": ".envlock", "label": None, "steps": 1, "dry_run": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_snapshots(env_file: Path, snapshot_dir: Path, values: list[str]) -> None:
    for v in values:
        env_file.write_text(f"KEY={v}\n")
        time.sleep(0.01)
        create_snapshot(env_file, snapshot_dir)


def test_cmd_rollback_restores_file(tmp_path: Path, capsys) -> None:
    env_file = tmp_path / ".env"
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    _make_snapshots(env_file, snap_dir, ["v1", "v2"])
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snap_dir), steps=1)
    cmd_rollback(ns)
    assert "KEY=v1" in env_file.read_text()
    out = capsys.readouterr().out
    assert "restored" in out


def test_cmd_rollback_dry_run(tmp_path: Path, capsys) -> None:
    env_file = tmp_path / ".env"
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    _make_snapshots(env_file, snap_dir, ["v1", "v2"])
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snap_dir), dry_run=True)
    cmd_rollback(ns)
    assert "KEY=v2" in env_file.read_text()  # unchanged
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_cmd_rollback_error_exits(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=x\n")
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snap_dir))
    with pytest.raises(SystemExit):
        cmd_rollback(ns)


def test_add_rollback_subparser_registers_command() -> None:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_rollback_subparser(subs)
    args = parser.parse_args(["rollback", "--steps", "2"])
    assert args.steps == 2
    assert args.func is cmd_rollback
