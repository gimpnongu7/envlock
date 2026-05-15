"""Bookmark snapshots with memorable short names for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class BookmarkError(Exception):
    """Raised when a bookmark operation fails."""


def _bookmark_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".bookmarks.json"


def _load_bookmarks(snapshot_dir: Path) -> Dict[str, str]:
    path = _bookmark_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_bookmarks(snapshot_dir: Path, data: Dict[str, str]) -> None:
    _bookmark_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_bookmark(snapshot_dir: Path, name: str, snapshot_id: str) -> None:
    """Bookmark *snapshot_id* under *name*. Raises if name already exists."""
    name = name.strip()
    if not name:
        raise BookmarkError("Bookmark name must not be blank.")
    data = _load_bookmarks(snapshot_dir)
    if name in data:
        raise BookmarkError(f"Bookmark '{name}' already exists (points to {data[name]}).")
    data[name] = snapshot_id
    _save_bookmarks(snapshot_dir, data)


def remove_bookmark(snapshot_dir: Path, name: str) -> None:
    """Remove bookmark *name*. Raises if it does not exist."""
    data = _load_bookmarks(snapshot_dir)
    if name not in data:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    del data[name]
    _save_bookmarks(snapshot_dir, data)


def resolve_bookmark(snapshot_dir: Path, name: str) -> str:
    """Return the snapshot ID for *name*. Raises if not found."""
    data = _load_bookmarks(snapshot_dir)
    if name not in data:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    return data[name]


def list_bookmarks(snapshot_dir: Path) -> List[Dict[str, str]]:
    """Return all bookmarks as a list of {name, snapshot_id} dicts."""
    data = _load_bookmarks(snapshot_dir)
    return [{"name": k, "snapshot_id": v} for k, v in sorted(data.items())]


def update_bookmark(snapshot_dir: Path, name: str, snapshot_id: str) -> None:
    """Update an existing bookmark to point to a new snapshot ID."""
    data = _load_bookmarks(snapshot_dir)
    if name not in data:
        raise BookmarkError(f"Bookmark '{name}' not found; use add_bookmark to create it.")
    data[name] = snapshot_id
    _save_bookmarks(snapshot_dir, data)
