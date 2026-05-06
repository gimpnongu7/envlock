"""Tests for envlock.history."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envlock.history import (
    HistoryError,
    format_history,
    get_entry_by_index,
    get_history,
)
from envlock.snapshot import create_snapshot


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return p


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envlock"
    d.mkdir()
    return d


def _make_snapshot_with_meta(env_file, snapshot_dir, label=None, timestamp="2024-01-01T00:00:00"):
    snap_id = create_snapshot(env_file, snapshot_dir, label=label)
    meta = {"label": label, "timestamp": timestamp}
    (snapshot_dir / snap_id).with_suffix(".meta.json").write_text(json.dumps(meta))
    return snap_id


def test_get_history_empty(snapshot_dir):
    assert get_history(snapshot_dir) == []


def test_get_history_returns_entries(env_file, snapshot_dir):
    _make_snapshot_with_meta(env_file, snapshot_dir, label="v1")
    entries = get_history(snapshot_dir)
    assert len(entries) == 1
    assert entries[0].label == "v1"
    assert entries[0].index == 0
    assert entries[0].key_count == 2


def test_get_history_limit(env_file, snapshot_dir):
    for i in range(4):
        _make_snapshot_with_meta(env_file, snapshot_dir, label=f"v{i}")
    entries = get_history(snapshot_dir, limit=2)
    assert len(entries) == 2


def test_get_history_no_meta(env_file, snapshot_dir):
    create_snapshot(env_file, snapshot_dir)
    entries = get_history(snapshot_dir)
    assert len(entries) == 1
    assert entries[0].label is None
    assert entries[0].timestamp == "unknown"


def test_get_entry_by_index(env_file, snapshot_dir):
    snap_id = _make_snapshot_with_meta(env_file, snapshot_dir, label="first")
    entry = get_entry_by_index(snapshot_dir, 0)
    assert entry.snapshot_id == snap_id
    assert entry.label == "first"


def test_get_entry_by_index_out_of_range(snapshot_dir):
    with pytest.raises(HistoryError, match="No snapshot at index"):
        get_entry_by_index(snapshot_dir, 99)


def test_format_history_empty():
    result = format_history([])
    assert "No snapshots" in result


def test_format_history_shows_label(env_file, snapshot_dir):
    _make_snapshot_with_meta(env_file, snapshot_dir, label="release")
    entries = get_history(snapshot_dir)
    output = format_history(entries)
    assert "release" in output
    assert "#0" in output
