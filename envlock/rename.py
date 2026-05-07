"""Rename snapshot files and update associated metadata."""

from __future__ import annotations

import json
import os
from pathlib import Path


class RenameError(Exception):
    """Raised when a snapshot rename operation fails."""


def _meta_path(snapshot_path: Path) -> Path:
    return snapshot_path.with_suffix(".meta.json")


def rename_snapshot(snapshot_dir: str | Path, old_name: str, new_name: str) -> Path:
    """Rename a snapshot file (and its .meta.json) inside *snapshot_dir*.

    Parameters
    ----------
    snapshot_dir:
        Directory that contains snapshot files.
    old_name:
        Current filename stem or full filename (without path).
    new_name:
        Desired filename stem or full filename (without path).

    Returns
    -------
    Path
        The new snapshot path.
    """
    base = Path(snapshot_dir)
    if not base.is_dir():
        raise RenameError(f"Snapshot directory not found: {base}")

    old_stem = Path(old_name).stem if old_name.endswith(".env") else old_name
    new_stem = Path(new_name).stem if new_name.endswith(".env") else new_name

    old_path = base / f"{old_stem}.env"
    new_path = base / f"{new_stem}.env"

    if not old_path.exists():
        raise RenameError(f"Snapshot not found: {old_path}")
    if new_path.exists():
        raise RenameError(f"A snapshot named '{new_stem}' already exists")

    old_path.rename(new_path)

    old_meta = _meta_path(old_path)
    if old_meta.exists():
        new_meta = _meta_path(new_path)
        old_meta.rename(new_meta)
        _update_meta_name(new_meta, new_stem)

    return new_path


def _update_meta_name(meta_path: Path, new_stem: str) -> None:
    """Patch the 'name' field inside a .meta.json file if present."""
    try:
        data = json.loads(meta_path.read_text())
        data["name"] = new_stem
        meta_path.write_text(json.dumps(data, indent=2))
    except (json.JSONDecodeError, KeyError, OSError):
        pass
