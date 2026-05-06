"""Tests for envlock.cli_history."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envlock.cli_history import cmd_history, cmd_history_show
from envlock.snapshot import create_snapshot


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"snapshot_dir": ".envlock", "limit": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    return p


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envlock"
    d.mkdir()
    return d


def _make(env_file, snapshot_dir, label=None):
    snap_id = create_snapshot(env_file, snapshot_dir, label=label)
    meta = {"label": label, "timestamp": "2024-06-01T12:00:00"}
    (snapshot_dir / snap_id).with_suffix(".meta.json").write_text(json.dumps(meta))
    return snap_id


def test_cmd_history_empty(snapshot_dir, capsys):
    cmd_history(_ns(snapshot_dir=str(snapshot_dir)))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_history_lists_snapshots(env_file, snapshot_dir, capsys):
    _make(env_file, snapshot_dir, label="beta")
    cmd_history(_ns(snapshot_dir=str(snapshot_dir)))
    out = capsys.readouterr().out
    assert "beta" in out


def test_cmd_history_limit(env_file, snapshot_dir, capsys):
    for i in range(3):
        _make(env_file, snapshot_dir, label=f"v{i}")
    cmd_history(_ns(snapshot_dir=str(snapshot_dir), limit=1))
    out = capsys.readouterr().out
    assert out.count("#") == 1


def test_cmd_history_show_prints_details(env_file, snapshot_dir, capsys):
    _make(env_file, snapshot_dir, label="prod")
    cmd_history_show(argparse.Namespace(snapshot_dir=str(snapshot_dir), index=0))
    out = capsys.readouterr().out
    assert "prod" in out
    assert "Keys" in out


def test_cmd_history_show_bad_index_exits(snapshot_dir):
    with pytest.raises(SystemExit):
        cmd_history_show(argparse.Namespace(snapshot_dir=str(snapshot_dir), index=5))
