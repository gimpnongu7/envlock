"""Merge utilities for combining .env snapshots or live files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envlock.snapshot import parse_env_file


class MergeConflictError(Exception):
    """Raised when a merge cannot be completed without manual resolution."""


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, base, other)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        lines = []
        if self.added:
            lines.append(f"Added keys: {', '.join(self.added)}")
        if self.removed:
            lines.append(f"Removed keys: {', '.join(self.removed)}")
        if self.conflicts:
            lines.append(f"Conflicts: {', '.join(k for k, _, _ in self.conflicts)}")
        return "\n".join(lines) if lines else "No changes."


def merge_envs(
    base: Dict[str, str],
    other: Dict[str, str],
    strategy: str = "ours",
) -> MergeResult:
    """Merge two env dicts.

    strategy:
        'ours'   - on conflict keep base value
        'theirs' - on conflict keep other value
        'error'  - raise MergeConflictError on any conflict
    """
    if strategy not in ("ours", "theirs", "error"):
        raise ValueError(f"Unknown strategy: {strategy!r}")

    merged: Dict[str, str] = {}
    conflicts: List[Tuple[str, str, str]] = []
    added: List[str] = []
    removed: List[str] = []

    all_keys = set(base) | set(other)

    for key in sorted(all_keys):
        in_base = key in base
        in_other = key in other

        if in_base and in_other:
            if base[key] == other[key]:
                merged[key] = base[key]
            else:
                conflicts.append((key, base[key], other[key]))
                if strategy == "error":
                    raise MergeConflictError(
                        f"Conflict on key '{key}': {base[key]!r} vs {other[key]!r}"
                    )
                merged[key] = base[key] if strategy == "ours" else other[key]
        elif in_base:
            removed.append(key)
            # key only in base — include it (other removed it, keep base)
            merged[key] = base[key]
        else:
            added.append(key)
            merged[key] = other[key]

    return MergeResult(merged=merged, conflicts=conflicts, added=added, removed=removed)


def merge_env_files(
    base_path: str,
    other_path: str,
    strategy: str = "ours",
) -> MergeResult:
    """Parse two .env files and merge them."""
    base = parse_env_file(base_path)
    other = parse_env_file(other_path)
    return merge_envs(base, other, strategy=strategy)
