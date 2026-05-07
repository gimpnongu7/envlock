"""Tests for envlock.cli_search."""

import json
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envlock.cli_search import cmd_search, add_search_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    snap = d / "snap1.env"
    snap.write_text("API_KEY=secret\nDEBUG=true\n")
    meta = d / "snap1.meta.json"
    meta.write_text(json.dumps({"label": "dev"}))
    return d


def _ns(snapshot_dir, **kwargs):
    defaults = {"snapshot_dir": str(snapshot_dir), "key": None, "value": None, "label": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_search_by_key_prints_result(snapshot_dir, capsys):
    cmd_search(_ns(snapshot_dir, key="API_KEY"))
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_cmd_search_no_match_exits_1(snapshot_dir):
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(_ns(snapshot_dir, key="NONEXISTENT"))
    assert exc_info.value.code == 1


def test_cmd_search_no_criteria_exits_1(snapshot_dir):
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(_ns(snapshot_dir))
    assert exc_info.value.code == 1


def test_cmd_search_bad_dir_exits_1(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(_ns(tmp_path / "missing", key="FOO"))
    assert exc_info.value.code == 1


def test_cmd_search_by_label(snapshot_dir, capsys):
    cmd_search(_ns(snapshot_dir, key="DEBUG", label="dev"))
    out = capsys.readouterr().out
    assert "[dev]" in out


def test_add_search_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_search_subparser(subs)
    args = parser.parse_args(["search", "--key", "FOO"])
    assert args.key == "FOO"
    assert args.func is not None
