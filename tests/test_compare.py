"""Tests for envlock.compare module."""

import pytest
from pathlib import Path

from envlock.snapshot import create_snapshot
from envlock.compare import compare_snapshots, format_compare, CompareError


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY_A=hello\nKEY_B=world\nSHARED=same\n")
    return p


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshot(env_file, snapshot_dir, name, content):
    env_file.write_text(content)
    create_snapshot(env_file, snapshot_dir, name=name)


def test_compare_detects_added(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "KEY_A=hello\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "KEY_A=hello\nKEY_B=new\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b", mask_values=False)
    assert "KEY_B" in result.added
    assert result.has_changes is True


def test_compare_detects_removed(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "KEY_A=hello\nKEY_B=world\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "KEY_A=hello\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b", mask_values=False)
    assert "KEY_B" in result.removed


def test_compare_detects_changed(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "KEY_A=old\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "KEY_A=new\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b", mask_values=False)
    assert "KEY_A" in result.changed


def test_compare_no_changes(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "KEY_A=same\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "KEY_A=same\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b")
    assert result.has_changes is False
    assert "KEY_A" in result.unchanged


def test_compare_raises_for_missing_snapshot(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "KEY_A=hello\n")

    with pytest.raises(CompareError, match="ghost"):
        compare_snapshots(snapshot_dir, "snap_a", "ghost")


def test_format_compare_no_changes(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "X=1\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "X=1\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b")
    output = format_compare(result)
    assert "No differences" in output


def test_format_compare_shows_diff(env_file, snapshot_dir):
    _make_snapshot(env_file, snapshot_dir, "snap_a", "A=1\nB=old\n")
    _make_snapshot(env_file, snapshot_dir, "snap_b", "A=1\nB=new\nC=3\n")

    result = compare_snapshots(snapshot_dir, "snap_a", "snap_b", mask_values=False)
    output = format_compare(result)
    assert "snap_a" in output
    assert "snap_b" in output
    assert "+ C" in output
    assert "~ B" in output
