"""Tests for envlock.cli_report."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envlock.cli_report import cmd_report, add_report_subparser
from envlock.snapshot import create_snapshot


def _ns(**kwargs):
    defaults = {
        "env_file": ".env",
        "snapshot_dir": ".envlock",
        "format": "markdown",
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


@pytest.fixture()
def snapshot_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def test_cmd_report_prints_markdown(env_file, snapshot_dir, capsys):
    create_snapshot(env_file, snapshot_dir)
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snapshot_dir))
    cmd_report(ns)
    out = capsys.readouterr().out
    assert "envlock Snapshot Report" in out


def test_cmd_report_html_format(env_file, snapshot_dir, capsys):
    create_snapshot(env_file, snapshot_dir)
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snapshot_dir), format="html")
    cmd_report(ns)
    out = capsys.readouterr().out
    assert "<!DOCTYPE html>" in out


def test_cmd_report_writes_file(env_file, snapshot_dir, tmp_path, capsys):
    create_snapshot(env_file, snapshot_dir)
    out_file = tmp_path / "report.md"
    ns = _ns(
        env_file=str(env_file),
        snapshot_dir=str(snapshot_dir),
        output=str(out_file),
    )
    cmd_report(ns)
    assert out_file.exists()
    printed = capsys.readouterr().out
    assert "written to" in printed


def test_cmd_report_bad_format_exits(env_file, snapshot_dir):
    ns = _ns(env_file=str(env_file), snapshot_dir=str(snapshot_dir), format="pdf")
    exit_calls = []
    with patch("envlock.report.generate_report", side_effect=__import__("envlock.report", fromlist=["ReportError"]).ReportError("Unknown format 'pdf'")):
        cmd_report(ns, _exit=exit_calls.append)
    assert 1 in exit_calls


def test_add_report_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_report_subparser(sub)
    args = parser.parse_args(["report", "--format", "html"])
    assert args.format == "html"
