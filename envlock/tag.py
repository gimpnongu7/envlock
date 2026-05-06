"""Tag snapshots with human-readable labels for easier retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TagError(Exception):
    pass


def _tag_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".envlock_tags.json"


def _load_tags(snapshot_dir: Path) -> Dict[str, str]:
    """Return mapping of tag -> snapshot_id."""
    p = _tag_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_tags(snapshot_dir: Path, tags: Dict[str, str]) -> None:
    _tag_path(snapshot_dir).write_text(json.dumps(tags, indent=2))


def add_tag(snapshot_dir: Path, snapshot_id: str, tag: str) -> None:
    """Associate *tag* with *snapshot_id*. Raises TagError on duplicate."""
    tags = _load_tags(snapshot_dir)
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists (points to {tags[tag]}). Remove it first.")
    tags[tag] = snapshot_id
    _save_tags(snapshot_dir, tags)


def remove_tag(snapshot_dir: Path, tag: str) -> str:
    """Remove *tag* and return the snapshot_id it pointed to."""
    tags = _load_tags(snapshot_dir)
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found.")
    snapshot_id = tags.pop(tag)
    _save_tags(snapshot_dir, tags)
    return snapshot_id


def resolve_tag(snapshot_dir: Path, tag: str) -> str:
    """Return the snapshot_id for *tag*, or raise TagError."""
    tags = _load_tags(snapshot_dir)
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found.")
    return tags[tag]


def list_tags(snapshot_dir: Path) -> List[Dict[str, str]]:
    """Return list of {tag, snapshot_id} dicts sorted by tag name."""
    tags = _load_tags(snapshot_dir)
    return [{"tag": t, "snapshot_id": sid} for t, sid in sorted(tags.items())]


def find_tags_for_snapshot(snapshot_dir: Path, snapshot_id: str) -> List[str]:
    """Return all tags that point to *snapshot_id*."""
    tags = _load_tags(snapshot_dir)
    return [t for t, sid in tags.items() if sid == snapshot_id]
