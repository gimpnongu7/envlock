"""Utilities for diffing two .env snapshots or env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class EnvDiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        if not lines:
            return "No differences found."
        return "\n".join(lines)


def diff_envs(
    before: Dict[str, str],
    after: Dict[str, str],
    mask_secrets: bool = False,
) -> EnvDiffResult:
    """Compare two env dicts and return a structured diff result."""
    result = EnvDiffResult()

    all_keys = set(before) | set(after)
    for key in all_keys:
        if key in before and key not in after:
            result.removed[key] = _maybe_mask(before[key], mask_secrets)
        elif key not in before and key in after:
            result.added[key] = _maybe_mask(after[key], mask_secrets)
        elif before[key] != after[key]:
            result.changed[key] = (
                _maybe_mask(before[key], mask_secrets),
                _maybe_mask(after[key], mask_secrets),
            )
        else:
            result.unchanged[key] = before[key]

    return result


def _maybe_mask(value: str, mask: bool) -> str:
    if mask and len(value) > 2:
        return value[0] + "*" * (len(value) - 2) + value[-1]
    return value
