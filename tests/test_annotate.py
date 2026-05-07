"""Tests for envlock.annotate."""

import json
import pytest
from pathlib import Path
from envlock.annotate import (
    add_note,
    get_note,
    remove_note,
    list_annotated,
    AnnotateError,
    Annotation,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_meta(snapshot_dir: Path, snapshot_id: str, extra: dict | None = None) -> Path:
    meta = snapshot_dir / f"{snapshot_id}.meta.json"
    data = {"id": snapshot_id, "created_at": "2024-01-01T00:00:00"}
    if extra:
        data.update(extra)
    meta.write_text(json.dumps(data))
    return meta


def test_add_note_writes_to_meta(snapshot_dir):
    _make_meta(snapshot_dir, "snap1")
    ann = add_note(snapshot_dir, "snap1", "initial setup")
    assert ann.note == "initial setup"
    assert ann.snapshot_id == "snap1"
    data = json.loads((snapshot_dir / "snap1.meta.json").read_text())
    assert data["note"] == "initial setup"


def test_add_note_overwrites_existing(snapshot_dir):
    _make_meta(snapshot_dir, "snap1", {"note": "old note"})
    add_note(snapshot_dir, "snap1", "new note")
    data = json.loads((snapshot_dir / "snap1.meta.json").read_text())
    assert data["note"] == "new note"


def test_add_note_missing_meta_raises(snapshot_dir):
    with pytest.raises(AnnotateError, match="not found"):
        add_note(snapshot_dir, "ghost", "hello")


def test_get_note_returns_note(snapshot_dir):
    _make_meta(snapshot_dir, "snap2", {"note": "my note"})
    assert get_note(snapshot_dir, "snap2") == "my note"


def test_get_note_returns_none_when_absent(snapshot_dir):
    _make_meta(snapshot_dir, "snap3")
    assert get_note(snapshot_dir, "snap3") is None


def test_get_note_missing_meta_raises(snapshot_dir):
    with pytest.raises(AnnotateError):
        get_note(snapshot_dir, "no-such-snap")


def test_remove_note_deletes_key(snapshot_dir):
    _make_meta(snapshot_dir, "snap4", {"note": "to be removed"})
    remove_note(snapshot_dir, "snap4")
    data = json.loads((snapshot_dir / "snap4.meta.json").read_text())
    assert "note" not in data


def test_remove_note_missing_note_raises(snapshot_dir):
    _make_meta(snapshot_dir, "snap5")
    with pytest.raises(AnnotateError, match="No note"):
        remove_note(snapshot_dir, "snap5")


def test_list_annotated_returns_only_noted(snapshot_dir):
    _make_meta(snapshot_dir, "a", {"note": "alpha"})
    _make_meta(snapshot_dir, "b")
    _make_meta(snapshot_dir, "c", {"note": "charlie"})
    results = list_annotated(snapshot_dir)
    assert len(results) == 2
    ids = {r.snapshot_id for r in results}
    assert ids == {"a", "c"}


def test_list_annotated_empty_dir(snapshot_dir):
    assert list_annotated(snapshot_dir) == []


def test_annotation_str(snapshot_dir):
    ann = Annotation(snapshot_id="snap1", note="hello world")
    assert str(ann) == "[snap1] hello world"
