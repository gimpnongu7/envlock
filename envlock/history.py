"""Snapshot history browsing and inspection for envlock."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from envlock.snapshot import list_snapshots


class HistoryError(Exception):
    """Raised when history operations fail."""


@dataclass
class HistoryEntry:
    index: int          # 0 = most recent
    snapshot_id: str
    label: Optional[str]
    timestamp: str
    key_count: int


def _load_meta(snapshot_path: Path) -> dict:
    meta_path = snapshot_path.with_suffix(".meta.json")
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    return {}


def get_history(snapshot_dir: Path, limit: Optional[int] = None) -> List[HistoryEntry]:
    """Return snapshot history ordered newest-first."""
    snapshots = list_snapshots(snapshot_dir)
    if not snapshots:
        return []

    entries: List[HistoryEntry] = []
    for idx, snap_id in enumerate(snapshots):
        snap_path = snapshot_dir / snap_id
        meta = _load_meta(snap_path)
        try:
            lines = snap_path.read_text().splitlines()
            key_count = sum(1 for l in lines if "=" in l and not l.strip().startswith("#"))
        except OSError:
            key_count = 0

        entries.append(HistoryEntry(
            index=idx,
            snapshot_id=snap_id,
            label=meta.get("label"),
            timestamp=meta.get("timestamp", "unknown"),
            key_count=key_count,
        ))

        if limit is not None and len(entries) >= limit:
            break

    return entries


def format_history(entries: List[HistoryEntry], show_index: bool = True) -> str:
    """Return a human-readable history table."""
    if not entries:
        return "No snapshots found."

    lines = []
    for e in entries:
        label_str = f" [{e.label}]" if e.label else ""
        idx_str = f"#{e.index}  " if show_index else ""
        lines.append(
            f"{idx_str}{e.snapshot_id}{label_str}  "
            f"ts={e.timestamp}  keys={e.key_count}"
        )
    return "\n".join(lines)


def get_entry_by_index(snapshot_dir: Path, index: int) -> HistoryEntry:
    """Fetch a single history entry by its 0-based index."""
    entries = get_history(snapshot_dir)
    if not entries or index >= len(entries) or index < 0:
        raise HistoryError(f"No snapshot at index {index} (total: {len(entries)})")
    return entries[index]
