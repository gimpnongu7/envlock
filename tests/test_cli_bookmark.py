"""Tests for envlock.cli_bookmark."""

import argparse
import sys
import pytest
from pathlib import Path

from envlock.bookmark import add_bookmark
from envlock.cli_bookmark import (
    cmd_bookmark_add,
    cmd_bookmark_remove,
    cmd_bookmark_resolve,
    cmd_bookmark_list,
    cmd_bookmark_update,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _ns(snapshot_dir, **kwargs):
    ns = argparse.Namespace(snapshot_dir=str(snapshot_dir), **kwargs)
    return ns


def test_cmd_bookmark_add_prints_confirmation(snapshot_dir, capsys):
    cmd_bookmark_add(_ns(snapshot_dir, name="stable", snapshot_id="snap_001"))
    out = capsys.readouterr().out
    assert "stable" in out
    assert "snap_001" in out


def test_cmd_bookmark_add_duplicate_exits(snapshot_dir):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_add(_ns(snapshot_dir, name="stable", snapshot_id="snap_002"))
    assert exc.value.code == 1


def test_cmd_bookmark_remove_prints_confirmation(snapshot_dir, capsys):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    cmd_bookmark_remove(_ns(snapshot_dir, name="stable"))
    out = capsys.readouterr().out
    assert "stable" in out


def test_cmd_bookmark_remove_missing_exits(snapshot_dir):
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_remove(_ns(snapshot_dir, name="ghost"))
    assert exc.value.code == 1


def test_cmd_bookmark_resolve_prints_id(snapshot_dir, capsys):
    add_bookmark(snapshot_dir, "prod", "snap_prod")
    cmd_bookmark_resolve(_ns(snapshot_dir, name="prod"))
    out = capsys.readouterr().out
    assert "snap_prod" in out


def test_cmd_bookmark_resolve_missing_exits(snapshot_dir):
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_resolve(_ns(snapshot_dir, name="nope"))
    assert exc.value.code == 1


def test_cmd_bookmark_list_empty(snapshot_dir, capsys):
    cmd_bookmark_list(_ns(snapshot_dir))
    out = capsys.readouterr().out
    assert "No bookmarks" in out


def test_cmd_bookmark_list_shows_entries(snapshot_dir, capsys):
    add_bookmark(snapshot_dir, "alpha", "snap_a")
    add_bookmark(snapshot_dir, "beta", "snap_b")
    cmd_bookmark_list(_ns(snapshot_dir))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_bookmark_update_prints_confirmation(snapshot_dir, capsys):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    cmd_bookmark_update(_ns(snapshot_dir, name="stable", snapshot_id="snap_002"))
    out = capsys.readouterr().out
    assert "snap_002" in out


def test_cmd_bookmark_update_missing_exits(snapshot_dir):
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_update(_ns(snapshot_dir, name="ghost", snapshot_id="snap_x"))
    assert exc.value.code == 1
