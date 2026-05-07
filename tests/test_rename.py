"""Tests for envlock.rename."""

import json
import pytest
from pathlib import Path

from envlock.rename import rename_snapshot, RenameError


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_snapshot(directory: Path, stem: str, meta: bool = True) -> Path:
    snap = directory / f"{stem}.env"
    snap.write_text(f"KEY=value\n")
    if meta:
        meta_file = directory / f"{stem}.meta.json"
        meta_file.write_text(json.dumps({"name": stem, "created_at": "2024-01-01"}))
    return snap


def test_rename_moves_env_file(snapshot_dir):
    _make_snapshot(snapshot_dir, "old")
    new_path = rename_snapshot(snapshot_dir, "old", "new")
    assert new_path.exists()
    assert not (snapshot_dir / "old.env").exists()


def test_rename_moves_meta_file(snapshot_dir):
    _make_snapshot(snapshot_dir, "old")
    rename_snapshot(snapshot_dir, "old", "new")
    meta = snapshot_dir / "new.meta.json"
    assert meta.exists()
    assert not (snapshot_dir / "old.meta.json").exists()


def test_rename_updates_name_in_meta(snapshot_dir):
    _make_snapshot(snapshot_dir, "old")
    rename_snapshot(snapshot_dir, "old", "new")
    data = json.loads((snapshot_dir / "new.meta.json").read_text())
    assert data["name"] == "new"


def test_rename_without_meta_file(snapshot_dir):
    _make_snapshot(snapshot_dir, "old", meta=False)
    new_path = rename_snapshot(snapshot_dir, "old", "new")
    assert new_path.exists()


def test_rename_missing_snapshot_raises(snapshot_dir):
    with pytest.raises(RenameError, match="not found"):
        rename_snapshot(snapshot_dir, "ghost", "new")


def test_rename_target_exists_raises(snapshot_dir):
    _make_snapshot(snapshot_dir, "old")
    _make_snapshot(snapshot_dir, "new")
    with pytest.raises(RenameError, match="already exists"):
        rename_snapshot(snapshot_dir, "old", "new")


def test_rename_missing_dir_raises(tmp_path):
    with pytest.raises(RenameError, match="not found"):
        rename_snapshot(tmp_path / "no_such_dir", "old", "new")


def test_rename_accepts_full_filename(snapshot_dir):
    _make_snapshot(snapshot_dir, "old")
    new_path = rename_snapshot(snapshot_dir, "old.env", "new.env")
    assert new_path.name == "new.env"
