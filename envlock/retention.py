"""Retention policy management for snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


class RetentionError(Exception):
    """Raised when a retention policy operation fails."""


@dataclass
class RetentionPolicy:
    max_age_days: Optional[int] = None
    max_count: Optional[int] = None
    keep_tagged: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RetentionPolicy":
        return cls(
            max_age_days=data.get("max_age_days"),
            max_count=data.get("max_count"),
            keep_tagged=data.get("keep_tagged", True),
        )


def _policy_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".retention_policy.json"


def set_policy(
    snapshot_dir: Path,
    max_age_days: Optional[int] = None,
    max_count: Optional[int] = None,
    keep_tagged: bool = True,
) -> RetentionPolicy:
    """Persist a retention policy for the given snapshot directory."""
    if max_age_days is not None and max_age_days <= 0:
        raise RetentionError("max_age_days must be a positive integer")
    if max_count is not None and max_count <= 0:
        raise RetentionError("max_count must be a positive integer")

    policy = RetentionPolicy(
        max_age_days=max_age_days,
        max_count=max_count,
        keep_tagged=keep_tagged,
    )
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _policy_path(snapshot_dir).write_text(json.dumps(policy.to_dict(), indent=2))
    return policy


def get_policy(snapshot_dir: Path) -> Optional[RetentionPolicy]:
    """Load the retention policy, or return None if none has been set."""
    path = _policy_path(snapshot_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise RetentionError(f"Corrupt retention policy file: {exc}") from exc
    return RetentionPolicy.from_dict(data)


def clear_policy(snapshot_dir: Path) -> bool:
    """Remove the retention policy. Returns True if a file was deleted."""
    path = _policy_path(snapshot_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def summary(policy: RetentionPolicy) -> str:
    """Return a human-readable summary of the policy."""
    parts = []
    if policy.max_age_days is not None:
        parts.append(f"max age: {policy.max_age_days} days")
    if policy.max_count is not None:
        parts.append(f"max count: {policy.max_count}")
    parts.append(f"keep tagged: {policy.keep_tagged}")
    return ", ".join(parts)
