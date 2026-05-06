"""Tests for envlock.cli_tag."""

import argparse
import sys
from pathlib import Path

import pytest

from envlock.cli_tag import cmd_tag_add, cmd_tag_remove, cmd_tag_list
from envlock.tag import add_tag


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _ns(snapshot_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snapshot_dir), **kwargs)


def test_cmd_tag_add_prints_confirmation(snapshot_dir, capsys):
    cmd_tag_add(_ns(snapshot_dir, snapshot_id="snap-1", tag="v1"))
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "v1" in out


def test_cmd_tag_add_duplicate_exits(snapshot_dir):
    add_tag(snapshot_dir, "snap-1", "v1")
    with pytest.raises(SystemExit):
        cmd_tag_add(_ns(snapshot_dir, snapshot_id="snap-2", tag="v1"))


def test_cmd_tag_remove_prints_confirmation(snapshot_dir, capsys):
    add_tag(snapshot_dir, "snap-1", "v1")
    cmd_tag_remove(_ns(snapshot_dir, tag="v1"))
    out = capsys.readouterr().out
    assert "v1" in out
    assert "snap-1" in out


def test_cmd_tag_remove_missing_exits(snapshot_dir):
    with pytest.raises(SystemExit):
        cmd_tag_remove(_ns(snapshot_dir, tag="ghost"))


def test_cmd_tag_list_empty(snapshot_dir, capsys):
    cmd_tag_list(_ns(snapshot_dir))
    assert "No tags" in capsys.readouterr().out


def test_cmd_tag_list_shows_entries(snapshot_dir, capsys):
    add_tag(snapshot_dir, "snap-1", "alpha")
    add_tag(snapshot_dir, "snap-2", "beta")
    cmd_tag_list(_ns(snapshot_dir))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
    assert "snap-1" in out
