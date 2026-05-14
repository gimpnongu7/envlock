"""Sync: push or pull snapshots to/from a shared directory (e.g. a mounted drive or network share)."""

from __future__ import annotations

import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


class SyncError(Exception):
    """Raised when a sync operation fails."""


@dataclass
class SyncResult:
    pushed: List[str] = field(default_factory=list)
    pulled: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        if self.pushed:
            lines.append(f"Pushed  : {', '.join(self.pushed)}")
        if self.pulled:
            lines.append(f"Pulled  : {', '.join(self.pulled)}")
        if self.skipped:
            lines.append(f"Skipped : {', '.join(self.skipped)}")
        if not lines:
            return "Nothing to sync."
        return "\n".join(lines)


def _snapshot_files(snapshot_dir: Path) -> List[Path]:
    """Return all .env snapshot files found in *snapshot_dir*."""
    return sorted(snapshot_dir.glob("*.env"))


def push_snapshots(snapshot_dir: Path, remote_dir: Path, overwrite: bool = False) -> SyncResult:
    """Copy local snapshots to *remote_dir*."""
    if not snapshot_dir.is_dir():
        raise SyncError(f"Local snapshot directory not found: {snapshot_dir}")
    remote_dir.mkdir(parents=True, exist_ok=True)

    result = SyncResult()
    for src in _snapshot_files(snapshot_dir):
        dst = remote_dir / src.name
        if dst.exists() and not overwrite:
            result.skipped.append(src.name)
            continue
        shutil.copy2(src, dst)
        # copy companion meta file if present
        meta_src = src.with_suffix(".json")
        if meta_src.exists():
            shutil.copy2(meta_src, remote_dir / meta_src.name)
        result.pushed.append(src.name)
    return result


def pull_snapshots(snapshot_dir: Path, remote_dir: Path, overwrite: bool = False) -> SyncResult:
    """Copy snapshots from *remote_dir* to the local *snapshot_dir*."""
    if not remote_dir.is_dir():
        raise SyncError(f"Remote directory not found: {remote_dir}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    result = SyncResult()
    for src in _snapshot_files(remote_dir):
        dst = snapshot_dir / src.name
        if dst.exists() and not overwrite:
            result.skipped.append(src.name)
            continue
        shutil.copy2(src, dst)
        meta_src = src.with_suffix(".json")
        if meta_src.exists():
            shutil.copy2(meta_src, snapshot_dir / meta_src.name)
        result.pulled.append(src.name)
    return result
