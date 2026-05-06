"""Prune old or excess snapshots from the snapshot directory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from envlock.snapshot import list_snapshots


class PruneError(Exception):
    """Raised when pruning fails."""


def _snapshot_paths(snapshot_dir: Path) -> List[Path]:
    """Return snapshot files sorted oldest-first by modification time."""
    files = [
        snapshot_dir / name
        for name in list_snapshots(snapshot_dir)
    ]
    return sorted(files, key=lambda p: p.stat().st_mtime)


def prune_snapshots(
    snapshot_dir: Path,
    *,
    keep: Optional[int] = None,
    dry_run: bool = False,
) -> List[Path]:
    """Remove old snapshots, keeping only the *keep* most recent ones.

    Args:
        snapshot_dir: Directory that holds snapshot files.
        keep: Number of snapshots to retain. Must be >= 1.
        dry_run: If True, return the list of files that *would* be removed
                 without actually deleting them.

    Returns:
        List of paths that were (or would be) removed.

    Raises:
        PruneError: If *keep* is less than 1 or the directory does not exist.
    """
    if not snapshot_dir.exists():
        raise PruneError(f"Snapshot directory not found: {snapshot_dir}")
    if keep is not None and keep < 1:
        raise PruneError("'keep' must be at least 1")

    paths = _snapshot_paths(snapshot_dir)

    if keep is None or len(paths) <= keep:
        return []

    to_remove = paths[: len(paths) - keep]

    if not dry_run:
        for path in to_remove:
            try:
                path.unlink()
            except OSError as exc:
                raise PruneError(f"Failed to remove {path.name}: {exc}") from exc

    return to_remove
