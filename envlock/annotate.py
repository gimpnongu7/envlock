"""Attach and retrieve human-readable notes on snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


class AnnotateError(Exception):
    """Raised when annotation operations fail."""


def _meta_path(snapshot_dir: Path, snapshot_id: str) -> Path:
    return snapshot_dir / f"{snapshot_id}.meta.json"


@dataclass
class Annotation:
    snapshot_id: str
    note: str

    def __str__(self) -> str:
        return f"[{self.snapshot_id}] {self.note}"


def add_note(snapshot_dir: Path, snapshot_id: str, note: str) -> Annotation:
    """Attach a note to a snapshot, overwriting any existing note."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise AnnotateError(f"Snapshot metadata not found: {snapshot_id}")
    data = json.loads(meta.read_text())
    data["note"] = note
    meta.write_text(json.dumps(data, indent=2))
    return Annotation(snapshot_id=snapshot_id, note=note)


def get_note(snapshot_dir: Path, snapshot_id: str) -> Optional[str]:
    """Return the note for a snapshot, or None if no note is set."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise AnnotateError(f"Snapshot metadata not found: {snapshot_id}")
    data = json.loads(meta.read_text())
    return data.get("note")


def remove_note(snapshot_dir: Path, snapshot_id: str) -> None:
    """Remove the note from a snapshot's metadata."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise AnnotateError(f"Snapshot metadata not found: {snapshot_id}")
    data = json.loads(meta.read_text())
    if "note" not in data:
        raise AnnotateError(f"No note found on snapshot: {snapshot_id}")
    del data["note"]
    meta.write_text(json.dumps(data, indent=2))


def list_annotated(snapshot_dir: Path) -> list[Annotation]:
    """Return all snapshots that have a note attached."""
    results: list[Annotation] = []
    for meta_file in sorted(snapshot_dir.glob("*.meta.json")):
        data = json.loads(meta_file.read_text())
        if "note" in data:
            sid = meta_file.name.replace(".meta.json", "")
            results.append(Annotation(snapshot_id=sid, note=data["note"]))
    return results
