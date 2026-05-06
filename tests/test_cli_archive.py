"""Tests for envlock.cli_archive."""

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envlock.cli_archive import cmd_archive_create, cmd_archive_extract, cmd_archive_info
from envlock.archive import ArchiveError


def _ns(**kwargs):
    defaults = {
        "snapshot_dir": ".envlock",
        "output": "bundle.zip",
        "label": "",
        "snapshots": None,
        "archive": "bundle.zip",
        "overwrite": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_archive_create_prints_path(tmp_path, capsys):
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    (snap_dir / "snap1.env").write_text("K=V\n")
    out = tmp_path / "bundle.zip"
    ns = _ns(snapshot_dir=str(snap_dir), output=str(out))
    cmd_archive_create(ns)
    captured = capsys.readouterr()
    assert "Archive created" in captured.out


def test_cmd_archive_create_error_exits(tmp_path, capsys):
    ns = _ns(snapshot_dir=str(tmp_path / "nope"), output=str(tmp_path / "out.zip"))
    with pytest.raises(SystemExit) as exc:
        cmd_archive_create(ns)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_archive_extract_prints_count(tmp_path, capsys):
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    (snap_dir / "snap1.env").write_text("K=V\n")
    out = tmp_path / "bundle.zip"

    from envlock.archive import create_archive
    create_archive(snap_dir, out)

    restore = tmp_path / "restored"
    ns = _ns(archive=str(out), snapshot_dir=str(restore), overwrite=False)
    cmd_archive_extract(ns)
    captured = capsys.readouterr()
    assert "Extracted 1" in captured.out


def test_cmd_archive_extract_error_exits(tmp_path, capsys):
    ns = _ns(archive=str(tmp_path / "nope.zip"), snapshot_dir=str(tmp_path))
    with pytest.raises(SystemExit) as exc:
        cmd_archive_extract(ns)
    assert exc.value.code == 1


def test_cmd_archive_info_prints_metadata(tmp_path, capsys):
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    (snap_dir / "snap1.env").write_text("K=V\n")
    out = tmp_path / "bundle.zip"

    from envlock.archive import create_archive
    create_archive(snap_dir, out, label="test-label")

    ns = _ns(archive=str(out))
    cmd_archive_info(ns)
    captured = capsys.readouterr()
    assert "test-label" in captured.out
    assert "snap1.env" in captured.out


def test_cmd_archive_info_error_exits(tmp_path, capsys):
    ns = _ns(archive=str(tmp_path / "ghost.zip"))
    with pytest.raises(SystemExit) as exc:
        cmd_archive_info(ns)
    assert exc.value.code == 1
