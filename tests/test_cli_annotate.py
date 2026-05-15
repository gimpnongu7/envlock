"""Tests for envlock.cli_annotate."""

import json
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envlock.cli_annotate import (
    cmd_annotate_add,
    cmd_annotate_show,
    cmd_annotate_remove,
    cmd_annotate_list,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _ns(snapshot_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snapshot_dir), **kwargs)


def _make_meta(snapshot_dir: Path, sid: str, extra: dict | None = None) -> None:
    """Create a .meta.json file for a snapshot with optional extra fields."""
    meta = snapshot_dir / f"{sid}.meta.json"
    data = {"id": sid}
    if extra:
        data.update(extra)
    meta.write_text(json.dumps(data))


def _read_meta(snapshot_dir: Path, sid: str) -> dict:
    """Read and return the parsed meta.json for a snapshot."""
    meta = snapshot_dir / f"{sid}.meta.json"
    return json.loads(meta.read_text())


def test_cmd_annotate_add_prints_confirmation(snapshot_dir, capsys):
    _make_meta(snapshot_dir, "s1")
    cmd_annotate_add(_ns(snapshot_dir, snapshot_id="s1", note="hello"))
    out = capsys.readouterr().out
    assert "s1" in out
    assert "hello" in out


def test_cmd_annotate_add_persists_note(snapshot_dir):
    """Verify that add actually writes the note to the meta file."""
    _make_meta(snapshot_dir, "s1")
    cmd_annotate_add(_ns(snapshot_dir, snapshot_id="s1", note="persisted"))
    data = _read_meta(snapshot_dir, "s1")
    assert data.get("note") == "persisted"


def test_cmd_annotate_add_missing_meta_exits(snapshot_dir):
    with pytest.raises(SystemExit) as exc:
        cmd_annotate_add(_ns(snapshot_dir, snapshot_id="ghost", note="x"))
    assert exc.value.code == 1


def test_cmd_annotate_show_prints_note(snapshot_dir, capsys):
    _make_meta(snapshot_dir, "s2", {"note": "my note"})
    cmd_annotate_show(_ns(snapshot_dir, snapshot_id="s2"))
    out = capsys.readouterr().out
    assert "my note" in out


def test_cmd_annotate_show_no_note_message(snapshot_dir, capsys):
    _make_meta(snapshot_dir, "s3")
    cmd_annotate_show(_ns(snapshot_dir, snapshot_id="s3"))
    out = capsys.readouterr().out
    assert "No note" in out


def test_cmd_annotate_remove_prints_confirmation(snapshot_dir, capsys):
    _make_meta(snapshot_dir, "s4", {"note": "bye"})
    cmd_annotate_remove(_ns(snapshot_dir, snapshot_id="s4"))
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_annotate_remove_clears_note(snapshot_dir):
    """Verify that remove actually deletes the note key from the meta file."""
    _make_meta(snapshot_dir, "s4", {"note": "bye"})
    cmd_annotate_remove(_ns(snapshot_dir, snapshot_id="s4"))
    data = _read_meta(snapshot_dir, "s4")
    assert "note" not in data


def test_cmd_annotate_remove_missing_note_exits(snapshot_dir):
    _make_meta(snapshot_dir, "s5")
    with pytest.raises(SystemExit) as exc:
        cmd_annotate_remove(_ns(snapshot_dir, snapshot_id="s5"))
    assert exc.value.code == 1


def test_cmd_annotate_list_shows_notes(snapshot_dir, capsys):
    _make_meta(snapshot_dir, "a", {"note": "alpha note"})
    _make_meta(snapshot_dir, "b")
    cmd_annotate_list(_ns(snapshot_dir))
    out = capsys.readouterr().out
    assert "alpha note" in out
    assert "b" not in out


def test_cmd_annotate_list_empty(snapshot_dir, capsys):
    cmd_annotate_list(_ns(snapshot_dir))
    out = capsys.readouterr().out
    assert "No annotated" in out
