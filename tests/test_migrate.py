"""Tests for envlock.migrate."""

import json
import pytest
from pathlib import Path

from envlock.migrate import (
    CURRENT_VERSION,
    MigrateError,
    MigrateResult,
    migrate_snapshot,
    migrate_all,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write_meta(snapshot_dir: Path, snapshot_id: str, meta: dict) -> Path:
    path = snapshot_dir / f"{snapshot_id}.meta.json"
    with path.open("w") as fh:
        json.dump(meta, fh)
    return path


def _read_meta(snapshot_dir: Path, snapshot_id: str) -> dict:
    path = snapshot_dir / f"{snapshot_id}.meta.json"
    with path.open() as fh:
        return json.load(fh)


def test_migrate_v1_to_v2_adds_label(snapshot_dir):
    _write_meta(snapshot_dir, "snap1", {"version": 1, "hash": "abc123"})
    result = migrate_snapshot(snapshot_dir, "snap1")
    assert result.from_version == 1
    assert result.to_version == 2
    assert not result.skipped
    meta = _read_meta(snapshot_dir, "snap1")
    assert meta["label"] is None
    assert meta["content_hash"] == "abc123"
    assert "hash" not in meta


def test_migrate_v1_no_hash_field(snapshot_dir):
    _write_meta(snapshot_dir, "snap2", {"version": 1, "created": "2024-01-01"})
    result = migrate_snapshot(snapshot_dir, "snap2")
    meta = _read_meta(snapshot_dir, "snap2")
    assert meta["label"] is None
    assert "content_hash" not in meta
    assert result.to_version == CURRENT_VERSION


def test_migrate_already_current_skips(snapshot_dir):
    _write_meta(snapshot_dir, "snap3", {"version": 2, "label": "prod"})
    result = migrate_snapshot(snapshot_dir, "snap3")
    assert result.skipped is True
    assert result.from_version == 2


def test_migrate_missing_meta_raises(snapshot_dir):
    with pytest.raises(MigrateError, match="No metadata found"):
        migrate_snapshot(snapshot_dir, "nonexistent")


def test_migrate_no_version_field_treated_as_v1(snapshot_dir):
    _write_meta(snapshot_dir, "snap4", {"hash": "xyz"})
    result = migrate_snapshot(snapshot_dir, "snap4")
    assert result.from_version == 1
    meta = _read_meta(snapshot_dir, "snap4")
    assert meta["version"] == 2


def test_migrate_all_processes_all_snapshots(snapshot_dir):
    for i in range(3):
        _write_meta(snapshot_dir, f"snap{i}", {"version": 1, "hash": f"h{i}"})
    results = migrate_all(snapshot_dir)
    assert len(results) == 3
    assert all(r.to_version == CURRENT_VERSION for r in results)


def test_migrate_all_empty_dir(snapshot_dir):
    results = migrate_all(snapshot_dir)
    assert results == []


def test_migrate_all_missing_dir_raises(tmp_path):
    with pytest.raises(MigrateError, match="Snapshot directory not found"):
        migrate_all(tmp_path / "no_such_dir")


def test_migrate_result_str_migrated(snapshot_dir):
    _write_meta(snapshot_dir, "snap5", {"version": 1})
    result = migrate_snapshot(snapshot_dir, "snap5")
    assert "migrated" in str(result)
    assert "v1" in str(result)
    assert "v2" in str(result)


def test_migrate_result_str_skipped(snapshot_dir):
    _write_meta(snapshot_dir, "snap6", {"version": 2})
    result = migrate_snapshot(snapshot_dir, "snap6")
    assert "skipped" in str(result)
