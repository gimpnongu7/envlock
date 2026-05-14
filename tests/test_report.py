"""Tests for envlock.report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envlock.report import generate_report, ReportError
from envlock.snapshot import create_snapshot


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nAPI_KEY=secret\n")
    return f


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshot(env_file, snapshot_dir, label=None):
    return create_snapshot(env_file, snapshot_dir, label=label)


def test_generate_markdown_returns_string(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, label="first")
    result = generate_report(env_file, snapshot_dir, fmt="markdown")
    assert isinstance(result, str)
    assert "# envlock Snapshot Report" in result


def test_generate_markdown_contains_snapshot_id(env_file, snapshot_dir):
    sid = _make_snapshot(env_file, snapshot_dir, label="v1")
    result = generate_report(env_file, snapshot_dir, fmt="markdown")
    assert sid in result


def test_generate_markdown_shows_label(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, label="my-label")
    result = generate_report(env_file, snapshot_dir, fmt="markdown")
    assert "my-label" in result


def test_generate_html_returns_html(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir)
    result = generate_report(env_file, snapshot_dir, fmt="html")
    assert "<!DOCTYPE html>" in result
    assert "<table" in result


def test_generate_html_contains_snapshot_id(env_file, snapshot_dir):
    sid = _make_snapshot(env_file, snapshot_dir)
    result = generate_report(env_file, snapshot_dir, fmt="html")
    assert sid in result


def test_unknown_format_raises(env_file, snapshot_dir):
    with pytest.raises(ReportError, match="Unknown format"):
        generate_report(env_file, snapshot_dir, fmt="pdf")


def test_generate_writes_to_output_file(env_file, snapshot_dir, tmp_path):
    out = tmp_path / "report.md"
    generate_report(env_file, snapshot_dir, fmt="markdown", output=out)
    assert out.exists()
    assert "envlock" in out.read_text()


def test_generate_no_snapshots_graceful(env_file, snapshot_dir):
    result = generate_report(env_file, snapshot_dir, fmt="markdown")
    assert "No snapshots" in result


def test_generate_html_no_snapshots_graceful(env_file, snapshot_dir):
    result = generate_report(env_file, snapshot_dir, fmt="html")
    assert "No snapshots" in result
