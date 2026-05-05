"""Tests for CLI profile sub-commands."""

import argparse
import pytest
from pathlib import Path

from envlock.cli_profile import (
    cmd_profile_add,
    cmd_profile_delete,
    cmd_profile_list,
    cmd_profile_remove,
    cmd_profile_show,
)
from envlock.profile import add_snapshot_to_profile


def _ns(tmp_path, **kwargs):
    return argparse.Namespace(snapshot_dir=str(tmp_path), **kwargs)


def test_cmd_profile_add(tmp_path, capsys):
    args = _ns(tmp_path, profile="dev", label="snap-1")
    cmd_profile_add(args)
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "dev" in out


def test_cmd_profile_list_empty(tmp_path, capsys):
    cmd_profile_list(_ns(tmp_path))
    assert "No profiles" in capsys.readouterr().out


def test_cmd_profile_list_shows_names(tmp_path, capsys):
    add_snapshot_to_profile(tmp_path, "staging", "s1")
    cmd_profile_list(_ns(tmp_path))
    assert "staging" in capsys.readouterr().out


def test_cmd_profile_show(tmp_path, capsys):
    add_snapshot_to_profile(tmp_path, "dev", "snap-x")
    cmd_profile_show(_ns(tmp_path, profile="dev"))
    assert "snap-x" in capsys.readouterr().out


def test_cmd_profile_show_empty(tmp_path, capsys):
    add_snapshot_to_profile(tmp_path, "dev", "snap-x")
    from envlock.profile import remove_snapshot_from_profile
    remove_snapshot_from_profile(tmp_path, "dev", "snap-x")
    cmd_profile_show(_ns(tmp_path, profile="dev"))
    assert "no snapshots" in capsys.readouterr().out


def test_cmd_profile_show_unknown_exits(tmp_path):
    with pytest.raises(SystemExit):
        cmd_profile_show(_ns(tmp_path, profile="ghost"))


def test_cmd_profile_remove(tmp_path, capsys):
    add_snapshot_to_profile(tmp_path, "dev", "snap-1")
    cmd_profile_remove(_ns(tmp_path, profile="dev", label="snap-1"))
    assert "Removed" in capsys.readouterr().out


def test_cmd_profile_remove_missing_exits(tmp_path):
    add_snapshot_to_profile(tmp_path, "dev", "snap-1")
    with pytest.raises(SystemExit):
        cmd_profile_remove(_ns(tmp_path, profile="dev", label="nope"))


def test_cmd_profile_delete(tmp_path, capsys):
    add_snapshot_to_profile(tmp_path, "dev", "s1")
    cmd_profile_delete(_ns(tmp_path, profile="dev"))
    assert "Deleted" in capsys.readouterr().out


def test_cmd_profile_delete_unknown_exits(tmp_path):
    with pytest.raises(SystemExit):
        cmd_profile_delete(_ns(tmp_path, profile="phantom"))
