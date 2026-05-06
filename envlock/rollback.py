"""Rollback support: revert .env to a previous snapshot by index or label."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envlock.snapshot import list_snapshots, restore_snapshot
from envlock.audit import record


class RollbackError(Exception):
    """Raised when a rollback operation cannot be completed."""


def _resolve_snapshot_id(
    snapshot_dir: Path,
    label: Optional[str] = None,
    steps_back: int = 1,
) -> str:
    """Return the snapshot filename to roll back to.

    If *label* is given it takes priority.  Otherwise *steps_back* selects
    how many entries to go back in the chronologically-sorted list (1 = the
    snapshot just before the most recent one).
    """
    snapshots = list_snapshots(snapshot_dir)
    if not snapshots:
        raise RollbackError("No snapshots found in directory.")

    if label is not None:
        matches = [s for s in snapshots if label in s]
        if not matches:
            raise RollbackError(f"No snapshot matching label '{label}' found.")
        return matches[-1]

    if steps_back < 1:
        raise RollbackError("steps_back must be >= 1.")
    if steps_back >= len(snapshots):
        raise RollbackError(
            f"Cannot go back {steps_back} step(s); only {len(snapshots)} snapshot(s) exist."
        )
    # snapshots are sorted oldest-first by list_snapshots
    target_index = len(snapshots) - 1 - steps_back
    return snapshots[target_index]


def rollback(
    env_path: Path,
    snapshot_dir: Path,
    label: Optional[str] = None,
    steps_back: int = 1,
    dry_run: bool = False,
) -> str:
    """Revert *env_path* to a previous snapshot.

    Returns the name of the snapshot that was restored.
    Logs the operation via :mod:`envlock.audit` unless *dry_run* is True.
    """
    snapshot_name = _resolve_snapshot_id(snapshot_dir, label=label, steps_back=steps_back)

    if dry_run:
        return snapshot_name

    restore_snapshot(env_path, snapshot_dir, snapshot_name)
    record(snapshot_dir, action="rollback", snapshot=snapshot_name, env_path=str(env_path))
    return snapshot_name
