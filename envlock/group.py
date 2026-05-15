"""Group snapshots under named collections for batch operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class GroupError(Exception):
    pass


def _group_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".envlock_groups.json"


def _load_groups(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _group_path(snapshot_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise GroupError(f"Corrupt group index: {exc}") from exc


def _save_groups(snapshot_dir: Path, groups: Dict[str, List[str]]) -> None:
    _group_path(snapshot_dir).write_text(json.dumps(groups, indent=2))


def add_to_group(snapshot_dir: Path, group: str, snapshot_id: str) -> None:
    """Add a snapshot ID to a named group, creating the group if needed."""
    group = group.strip()
    if not group:
        raise GroupError("Group name must not be blank.")
    groups = _load_groups(snapshot_dir)
    members = groups.setdefault(group, [])
    if snapshot_id not in members:
        members.append(snapshot_id)
    _save_groups(snapshot_dir, groups)


def remove_from_group(snapshot_dir: Path, group: str, snapshot_id: str) -> None:
    """Remove a snapshot ID from a group."""
    groups = _load_groups(snapshot_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    try:
        groups[group].remove(snapshot_id)
    except ValueError:
        raise GroupError(f"Snapshot '{snapshot_id}' not in group '{group}'.")
    if not groups[group]:
        del groups[group]
    _save_groups(snapshot_dir, groups)


def list_groups(snapshot_dir: Path) -> List[str]:
    """Return sorted list of group names."""
    return sorted(_load_groups(snapshot_dir).keys())


def get_group_members(snapshot_dir: Path, group: str) -> List[str]:
    """Return snapshot IDs belonging to a group."""
    groups = _load_groups(snapshot_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(groups[group])


def delete_group(snapshot_dir: Path, group: str) -> None:
    """Delete an entire group (does not delete snapshot files)."""
    groups = _load_groups(snapshot_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    del groups[group]
    _save_groups(snapshot_dir, groups)
