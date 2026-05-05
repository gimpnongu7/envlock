"""Tests for the envlock snapshot module."""

import json
import pytest
from pathlib import Path

from envlock.snapshot import (
    parse_env_file,
    create_snapshot,
    restore_snapshot,
    list_snapshots,
)

SAMPLE_ENV_CONTENT = """# Sample env file
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=supersecret
DEBUG=true
"""


@pytest.fixture
def env_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text(SAMPLE_ENV_CONTENT)
    return env


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path / ".envlock")


def test_parse_env_file(env_file):
    result = parse_env_file(str(env_file))
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["SECRET_KEY"] == "supersecret"
    assert result["DEBUG"] == "true"
    assert len(result) == 4  # comments and blank lines excluded


def test_parse_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_create_snapshot(env_file, snapshot_dir):
    meta = create_snapshot(str(env_file), label="test_snap", snapshot_dir=snapshot_dir)
    assert meta["label"] == "test_snap"
    assert "timestamp" in meta
    assert "hash" in meta
    assert meta["vars"]["DB_HOST"] == "localhost"

    snap_file = Path(snapshot_dir) / "test_snap.json"
    assert snap_file.exists()


def test_create_snapshot_auto_label(env_file, snapshot_dir):
    meta = create_snapshot(str(env_file), snapshot_dir=snapshot_dir)
    assert meta["label"].startswith("snapshot_")


def test_restore_snapshot(env_file, snapshot_dir, tmp_path):
    create_snapshot(str(env_file), label="restore_test", snapshot_dir=snapshot_dir)

    target = tmp_path / "restored.env"
    restore_snapshot("restore_test", target_path=str(target), snapshot_dir=snapshot_dir)

    assert target.exists()
    restored = parse_env_file(str(target))
    assert restored["DB_HOST"] == "localhost"
    assert restored["SECRET_KEY"] == "supersecret"


def test_restore_snapshot_not_found(snapshot_dir):
    with pytest.raises(FileNotFoundError):
        restore_snapshot("ghost_snap", snapshot_dir=snapshot_dir)


def test_list_snapshots(env_file, snapshot_dir):
    assert list_snapshots(snapshot_dir=snapshot_dir) == []

    create_snapshot(str(env_file), label="alpha", snapshot_dir=snapshot_dir)
    create_snapshot(str(env_file), label="beta", snapshot_dir=snapshot_dir)

    snaps = list_snapshots(snapshot_dir=snapshot_dir)
    labels = [s["label"] for s in snaps]
    assert "alpha" in labels
    assert "beta" in labels
    assert len(snaps) == 2
