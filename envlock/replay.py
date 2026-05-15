"""Replay a sequence of snapshots onto the env file in chronological order."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .snapshot import restore_snapshot, list_snapshots


class ReplayError(Exception):
    """Raised when replay cannot proceed."""


@dataclass
class ReplayResult:
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    dry_run: bool = False

    def summary(self) -> str:
        verb = "Would apply" if self.dry_run else "Applied"
        lines = [f"{verb} {len(self.applied)} snapshot(s)."]
        if self.applied:
            lines.append("  " + "\n  ".join(self.applied))
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} snapshot(s) (not found).")
        return "\n".join(lines)


def _snapshot_timestamp(snapshot_dir: Path, snapshot_id: str) -> float:
    """Return the mtime of a snapshot file, or 0.0 if missing."""
    meta = snapshot_dir / f"{snapshot_id}.meta.json"
    if meta.exists():
        try:
            data = json.loads(meta.read_text())
            return float(data.get("created_at", 0.0))
        except (ValueError, KeyError):
            pass
    env_file = snapshot_dir / f"{snapshot_id}.env"
    if env_file.exists():
        return env_file.stat().st_mtime
    return 0.0


def replay_snapshots(
    env_path: Path,
    snapshot_dir: Path,
    snapshot_ids: Optional[List[str]] = None,
    *,
    dry_run: bool = False,
) -> ReplayResult:
    """Replay snapshots in chronological order onto *env_path*.

    If *snapshot_ids* is None, all snapshots in *snapshot_dir* are replayed
    sorted by creation timestamp (oldest first).
    """
    if not snapshot_dir.exists():
        raise ReplayError(f"Snapshot directory not found: {snapshot_dir}")

    if snapshot_ids is None:
        snapshot_ids = list_snapshots(snapshot_dir)

    if not snapshot_ids:
        raise ReplayError("No snapshots to replay.")

    # Sort by timestamp so replay is deterministic
    ordered = sorted(snapshot_ids, key=lambda sid: _snapshot_timestamp(snapshot_dir, sid))

    result = ReplayResult(dry_run=dry_run)
    for sid in ordered:
        snap_file = snapshot_dir / f"{sid}.env"
        if not snap_file.exists():
            result.skipped.append(sid)
            continue
        if not dry_run:
            restore_snapshot(env_path, snapshot_dir, sid)
        result.applied.append(sid)

    return result
