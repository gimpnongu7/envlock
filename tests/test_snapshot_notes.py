import pytest
from pathlib import Path

from envlock.snapshot_notes import (
    SnapshotNoteError,
    add_note,
    get_note,
    remove_note,
    list_notes,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_add_note_returns_note(snapshot_dir):
    note = add_note(snapshot_dir, "snap-001", "initial baseline")
    assert note.snapshot_id == "snap-001"
    assert note.text == "initial baseline"
    assert note.tags == []


def test_add_note_with_tags(snapshot_dir):
    note = add_note(snapshot_dir, "snap-002", "staging config", tags=["staging", "v2"])
    assert note.tags == ["staging", "v2"]


def test_add_note_blank_text_raises(snapshot_dir):
    with pytest.raises(SnapshotNoteError, match="blank"):
        add_note(snapshot_dir, "snap-001", "   ")


def test_add_note_overwrites_existing(snapshot_dir):
    add_note(snapshot_dir, "snap-001", "first")
    note = add_note(snapshot_dir, "snap-001", "second")
    assert note.text == "second"


def test_get_note_returns_none_when_missing(snapshot_dir):
    assert get_note(snapshot_dir, "nonexistent") is None


def test_get_note_returns_saved_note(snapshot_dir):
    add_note(snapshot_dir, "snap-003", "production snapshot", tags=["prod"])
    note = get_note(snapshot_dir, "snap-003")
    assert note is not None
    assert note.text == "production snapshot"
    assert note.tags == ["prod"]


def test_remove_note_deletes_entry(snapshot_dir):
    add_note(snapshot_dir, "snap-004", "to be removed")
    remove_note(snapshot_dir, "snap-004")
    assert get_note(snapshot_dir, "snap-004") is None


def test_remove_note_missing_raises(snapshot_dir):
    with pytest.raises(SnapshotNoteError, match="No note found"):
        remove_note(snapshot_dir, "ghost-snap")


def test_list_notes_empty(snapshot_dir):
    assert list_notes(snapshot_dir) == []


def test_list_notes_sorted_by_id(snapshot_dir):
    add_note(snapshot_dir, "snap-b", "second")
    add_note(snapshot_dir, "snap-a", "first")
    notes = list_notes(snapshot_dir)
    assert [n.snapshot_id for n in notes] == ["snap-a", "snap-b"]


def test_str_representation_no_tags(snapshot_dir):
    note = add_note(snapshot_dir, "snap-x", "plain note")
    assert str(note) == "snap-x: plain note"


def test_str_representation_with_tags(snapshot_dir):
    note = add_note(snapshot_dir, "snap-y", "tagged", tags=["dev"])
    assert str(note) == "snap-y: tagged [dev]"
