"""Tests for envlock.clone."""

import json
import pytest
from pathlib import Path

from envlock.clone import clone_snapshot, list_clones, CloneError


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshot(snapshot_dir: Path, stem: str, content: str = "KEY=val\n", label: str = "orig") -> Path:
    f = snapshot_dir / f"{stem}.env"
    f.write_text(content)
    meta = snapshot_dir / f"{stem}.meta.json"
    meta.write_text(json.dumps({"label": label}))
    return f


def test_clone_creates_new_file(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1")
    dst = clone_snapshot(snapshot_dir, "snap1", new_label="my-clone", new_id="snap2")
    assert dst.exists()
    assert dst.read_text() == "KEY=val\n"


def test_clone_writes_metadata(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1")
    clone_snapshot(snapshot_dir, "snap1", new_label="cloned", new_id="snap2")
    meta = json.loads((snapshot_dir / "snap2.meta.json").read_text())
    assert meta["label"] == "cloned"
    assert meta["cloned_from"] == "snap1"


def test_clone_missing_source_raises(snapshot_dir):
    with pytest.raises(CloneError, match="Source snapshot not found"):
        clone_snapshot(snapshot_dir, "nonexistent", new_label="x", new_id="y")


def test_clone_existing_target_raises(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1")
    _make_snapshot(snapshot_dir, "snap2")
    with pytest.raises(CloneError, match="already exists"):
        clone_snapshot(snapshot_dir, "snap1", new_label="dup", new_id="snap2")


def test_clone_auto_generates_id(snapshot_dir):
    _make_snapshot(snapshot_dir, "snap1")
    dst = clone_snapshot(snapshot_dir, "snap1", new_label="auto")
    assert dst.exists()
    assert dst.stem != "snap1"


def test_clone_without_existing_meta(snapshot_dir):
    # snapshot file exists but no .meta.json
    f = snapshot_dir / "bare.env"
    f.write_text("A=1\n")
    dst = clone_snapshot(snapshot_dir, "bare", new_label="from-bare", new_id="bare2")
    meta = json.loads((snapshot_dir / "bare2.meta.json").read_text())
    assert meta["label"] == "from-bare"
    assert meta["cloned_from"] == "bare"


def test_list_clones_returns_ids(snapshot_dir):
    _make_snapshot(snapshot_dir, "origin")
    clone_snapshot(snapshot_dir, "origin", new_label="c1", new_id="clone1")
    clone_snapshot(snapshot_dir, "origin", new_label="c2", new_id="clone2")
    clones = list_clones(snapshot_dir, "origin")
    assert set(clones) == {"clone1", "clone2"}


def test_list_clones_empty_when_none(snapshot_dir):
    _make_snapshot(snapshot_dir, "origin")
    assert list_clones(snapshot_dir, "origin") == []
