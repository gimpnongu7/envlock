"""Compare two snapshots and report what changed between them."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envlock.snapshot import list_snapshots, parse_env_file
from envlock.diff import diff_envs, EnvDiffResult


class CompareError(Exception):
    """Raised when a comparison cannot be completed."""


@dataclass
class CompareResult:
    snapshot_a: str
    snapshot_b: str
    diff: EnvDiffResult
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _load_snapshot_env(snapshot_dir: Path, name: str) -> Dict[str, str]:
    """Locate and parse a snapshot file by name."""
    snapshots = list_snapshots(snapshot_dir)
    match = next((s for s in snapshots if s["name"] == name), None)
    if match is None:
        raise CompareError(f"Snapshot not found: {name!r}")
    return parse_env_file(Path(match["path"]))


def compare_snapshots(
    snapshot_dir: Path,
    name_a: str,
    name_b: str,
    mask_values: bool = True,
) -> CompareResult:
    """Compare two named snapshots and return a CompareResult."""
    env_a = _load_snapshot_env(snapshot_dir, name_a)
    env_b = _load_snapshot_env(snapshot_dir, name_b)

    diff = diff_envs(env_a, env_b, mask_values=mask_values)

    return CompareResult(
        snapshot_a=name_a,
        snapshot_b=name_b,
        diff=diff,
        added=list(diff.added.keys()),
        removed=list(diff.removed.keys()),
        changed=list(diff.changed.keys()),
        unchanged=list(diff.unchanged.keys()),
    )


def format_compare(result: CompareResult) -> str:
    """Return a human-readable summary of a CompareResult."""
    lines = [
        f"Comparing '{result.snapshot_a}' → '{result.snapshot_b}'",
        "-" * 48,
    ]
    if not result.has_changes:
        lines.append("No differences found.")
        return "\n".join(lines)

    for key in result.added:
        lines.append(f"  + {key} = {result.diff.added[key]}")
    for key in result.removed:
        lines.append(f"  - {key} (was {result.diff.removed[key]})")
    for key in result.changed:
        old, new = result.diff.changed[key]
        lines.append(f"  ~ {key}: {old} → {new}")

    lines.append(
        f"\n{len(result.added)} added, {len(result.removed)} removed, "
        f"{len(result.changed)} changed, {len(result.unchanged)} unchanged."
    )
    return "\n".join(lines)
