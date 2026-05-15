"""Baseline management — mark a snapshot as the project baseline and compare against it."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from envlock.diff import diff_envs, EnvDiffResult
from envlock.snapshot import parse_env_file


class BaselineError(Exception):
    """Raised when a baseline operation fails."""


def _baseline_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".baseline"


def set_baseline(snapshot_dir: Path, snapshot_id: str) -> None:
    """Record *snapshot_id* as the current baseline."""
    snap_file = snapshot_dir / f"{snapshot_id}.env"
    if not snap_file.exists():
        raise BaselineError(f"Snapshot not found: {snapshot_id}")
    _baseline_path(snapshot_dir).write_text(json.dumps({"snapshot_id": snapshot_id}))


def get_baseline(snapshot_dir: Path) -> Optional[str]:
    """Return the current baseline snapshot id, or None if not set."""
    bp = _baseline_path(snapshot_dir)
    if not bp.exists():
        return None
    data = json.loads(bp.read_text())
    return data.get("snapshot_id")


def clear_baseline(snapshot_dir: Path) -> None:
    """Remove the baseline marker."""
    bp = _baseline_path(snapshot_dir)
    if bp.exists():
        bp.unlink()


@dataclass
class BaselineDiff:
    baseline_id: str
    diff: EnvDiffResult

    def has_changes(self) -> bool:
        return bool(self.diff.added or self.diff.removed or self.diff.changed)

    def summary(self) -> str:
        if not self.has_changes():
            return f"No changes from baseline '{self.baseline_id}'."
        parts = []
        if self.diff.added:
            parts.append(f"+{len(self.diff.added)} added")
        if self.diff.removed:
            parts.append(f"-{len(self.diff.removed)} removed")
        if self.diff.changed:
            parts.append(f"~{len(self.diff.changed)} changed")
        return f"Diff from baseline '{self.baseline_id}': {', '.join(parts)}"


def compare_to_baseline(env_file: Path, snapshot_dir: Path) -> BaselineDiff:
    """Diff the current *env_file* against the stored baseline snapshot."""
    baseline_id = get_baseline(snapshot_dir)
    if baseline_id is None:
        raise BaselineError("No baseline is set. Run 'envlock baseline set <id>' first.")
    snap_file = snapshot_dir / f"{baseline_id}.env"
    if not snap_file.exists():
        raise BaselineError(f"Baseline snapshot file missing: {snap_file}")
    baseline_env = parse_env_file(snap_file)
    current_env = parse_env_file(env_file)
    return BaselineDiff(baseline_id=baseline_id, diff=diff_envs(baseline_env, current_env))
