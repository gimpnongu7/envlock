"""Clone a snapshot under a new name/label within the same snapshot directory."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from envlock.snapshot import list_snapshots


class CloneError(Exception):
    """Raised when a snapshot clone operation fails."""


def _meta_path(snapshot_path: Path) -> Path:
    return snapshot_path.with_suffix(".meta.json")


def clone_snapshot(
    snapshot_dir: Path,
    source_id: str,
    new_label: str,
    new_id: Optional[str] = None,
) -> Path:
    """Copy an existing snapshot file (and its metadata) to a new name.

    Args:
        snapshot_dir: Directory that holds snapshot files.
        source_id: Filename stem (without extension) of the snapshot to clone.
        new_label: Human-readable label stored in the cloned metadata.
        new_id: Optional explicit stem for the new file; auto-generated if omitted.

    Returns:
        Path to the newly created snapshot file.

    Raises:
        CloneError: If the source snapshot does not exist or the target already exists.
    """
    snapshot_dir = Path(snapshot_dir)
    src_file = snapshot_dir / f"{source_id}.env"
    if not src_file.exists():
        raise CloneError(f"Source snapshot not found: {src_file}")

    if new_id is None:
        import uuid
        new_id = uuid.uuid4().hex[:12]

    dst_file = snapshot_dir / f"{new_id}.env"
    if dst_file.exists():
        raise CloneError(f"Target snapshot already exists: {dst_file}")

    shutil.copy2(src_file, dst_file)

    # Copy and update metadata if present
    src_meta = _meta_path(src_file)
    dst_meta = _meta_path(dst_file)
    meta: dict = {}
    if src_meta.exists():
        meta = json.loads(src_meta.read_text())
    meta["label"] = new_label
    meta["cloned_from"] = source_id
    dst_meta.write_text(json.dumps(meta, indent=2))

    return dst_file


def list_clones(snapshot_dir: Path, source_id: str) -> list[str]:
    """Return IDs of all snapshots that were cloned from *source_id*."""
    snapshot_dir = Path(snapshot_dir)
    clones: list[str] = []
    for meta_file in sorted(snapshot_dir.glob("*.meta.json")):
        try:
            data = json.loads(meta_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("cloned_from") == source_id:
            clones.append(meta_file.stem.replace(".meta", ""))
    return clones
