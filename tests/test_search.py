"""Tests for envlock.search."""

import json
import pytest
from pathlib import Path

from envlock.search import search_snapshots, SearchError, SearchResult


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def _make_snapshot(directory: Path, name: str, env: dict, label: str = None):
    directory.mkdir(parents=True, exist_ok=True)
    snap = directory / f"{name}.env"
    snap.write_text("\n".join(f"{k}={v}" for k, v in env.items()))
    if label:
        meta = directory / f"{name}.meta.json"
        meta.write_text(json.dumps({"label": label}))
    return snap


def test_search_missing_dir_raises(snapshot_dir):
    with pytest.raises(SearchError, match="not found"):
        search_snapshots(snapshot_dir, key_pattern="FOO")


def test_search_no_criteria_raises(snapshot_dir):
    snapshot_dir.mkdir()
    with pytest.raises(SearchError, match="At least one"):
        search_snapshots(snapshot_dir)


def test_search_by_key(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"DATABASE_URL": "postgres://localhost", "DEBUG": "true"})
    _make_snapshot(snapshot_dir, "snap2", {"REDIS_URL": "redis://localhost"})

    result = search_snapshots(snapshot_dir, key_pattern="DATABASE")

    assert result.found()
    assert len(result.hits) == 1
    assert result.hits[0].key == "DATABASE_URL"
    assert result.hits[0].snapshot_id == "snap1"


def test_search_by_value(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"DB": "postgres://prod", "CACHE": "redis://prod"})
    _make_snapshot(snapshot_dir, "snap2", {"DB": "sqlite://local"})

    result = search_snapshots(snapshot_dir, value_pattern="postgres")

    assert result.found()
    assert len(result.hits) == 1
    assert result.hits[0].value == "postgres://prod"


def test_search_by_label(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"FOO": "bar"}, label="production")
    _make_snapshot(snapshot_dir, "snap2", {"FOO": "baz"}, label="staging")

    result = search_snapshots(snapshot_dir, key_pattern="FOO", label_pattern="prod")

    assert result.found()
    assert len(result.hits) == 1
    assert result.hits[0].label == "production"


def test_search_no_match_returns_empty(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"FOO": "bar"})

    result = search_snapshots(snapshot_dir, key_pattern="NONEXISTENT")

    assert not result.found()
    assert "No matches" in result.summary()


def test_search_multiple_hits(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"API_KEY": "abc", "API_SECRET": "xyz"})
    _make_snapshot(snapshot_dir, "snap2", {"API_KEY": "def"})

    result = search_snapshots(snapshot_dir, key_pattern="API_KEY")

    assert len(result.hits) == 2


def test_summary_format(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1", {"FOO": "bar"}, label="dev")

    result = search_snapshots(snapshot_dir, key_pattern="FOO")
    summary = result.summary()

    assert "snap1" in summary
    assert "[dev]" in summary
    assert "FOO=bar" in summary
