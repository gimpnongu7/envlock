"""Attach and retrieve freeform notes on snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class SnapshotNoteError(Exception):
    pass


@dataclass
class SnapshotNote:
    snapshot_id: str
    text: str
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag_part = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"{self.snapshot_id}: {self.text}{tag_part}"


def _notes_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".notes.json"


def _load_notes(snapshot_dir: Path) -> dict:
    p = _notes_path(snapshot_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise SnapshotNoteError(f"Corrupt notes file: {exc}") from exc


def _save_notes(snapshot_dir: Path, data: dict) -> None:
    _notes_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_note(
    snapshot_dir: Path,
    snapshot_id: str,
    text: str,
    tags: Optional[List[str]] = None,
) -> SnapshotNote:
    """Add or replace a note for *snapshot_id*."""
    if not text.strip():
        raise SnapshotNoteError("Note text must not be blank.")
    data = _load_notes(snapshot_dir)
    entry = {"text": text.strip(), "tags": tags or []}
    data[snapshot_id] = entry
    _save_notes(snapshot_dir, data)
    return SnapshotNote(snapshot_id=snapshot_id, **entry)


def get_note(snapshot_dir: Path, snapshot_id: str) -> Optional[SnapshotNote]:
    """Return the note for *snapshot_id*, or None if absent."""
    data = _load_notes(snapshot_dir)
    entry = data.get(snapshot_id)
    if entry is None:
        return None
    return SnapshotNote(snapshot_id=snapshot_id, **entry)


def remove_note(snapshot_dir: Path, snapshot_id: str) -> None:
    """Remove the note for *snapshot_id*. Raises if not found."""
    data = _load_notes(snapshot_dir)
    if snapshot_id not in data:
        raise SnapshotNoteError(f"No note found for snapshot '{snapshot_id}'.")
    del data[snapshot_id]
    _save_notes(snapshot_dir, data)


def list_notes(snapshot_dir: Path) -> List[SnapshotNote]:
    """Return all notes, sorted by snapshot_id."""
    data = _load_notes(snapshot_dir)
    return [
        SnapshotNote(snapshot_id=sid, **entry)
        for sid, entry in sorted(data.items())
    ]
