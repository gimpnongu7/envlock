"""Snapshot quota management — enforce limits on snapshot count per directory."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_QUOTA_FILE = ".envlock_quota.json"


class QuotaError(Exception):
    """Raised when a quota operation fails."""


@dataclass
class QuotaConfig:
    max_snapshots: int
    warn_at: Optional[int] = None
    auto_prune: bool = False

    def to_dict(self) -> dict:
        return {
            "max_snapshots": self.max_snapshots,
            "warn_at": self.warn_at,
            "auto_prune": self.auto_prune,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QuotaConfig":
        return cls(
            max_snapshots=int(data["max_snapshots"]),
            warn_at=data.get("warn_at"),
            auto_prune=bool(data.get("auto_prune", False)),
        )


def _quota_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _QUOTA_FILE


def set_quota(snapshot_dir: Path, max_snapshots: int, warn_at: Optional[int] = None, auto_prune: bool = False) -> QuotaConfig:
    """Write a quota config for the given snapshot directory."""
    if max_snapshots < 1:
        raise QuotaError("max_snapshots must be at least 1")
    if warn_at is not None and warn_at >= max_snapshots:
        raise QuotaError("warn_at must be less than max_snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    cfg = QuotaConfig(max_snapshots=max_snapshots, warn_at=warn_at, auto_prune=auto_prune)
    _quota_path(snapshot_dir).write_text(json.dumps(cfg.to_dict(), indent=2))
    return cfg


def get_quota(snapshot_dir: Path) -> Optional[QuotaConfig]:
    """Return the quota config for the directory, or None if not set."""
    p = _quota_path(snapshot_dir)
    if not p.exists():
        return None
    try:
        return QuotaConfig.from_dict(json.loads(p.read_text()))
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise QuotaError(f"Corrupt quota file: {exc}") from exc


def clear_quota(snapshot_dir: Path) -> bool:
    """Remove the quota config. Returns True if it existed."""
    p = _quota_path(snapshot_dir)
    if p.exists():
        p.unlink()
        return True
    return False


def check_quota(snapshot_dir: Path, current_count: int) -> dict:
    """Check current usage against quota. Returns a status dict."""
    cfg = get_quota(snapshot_dir)
    if cfg is None:
        return {"enforced": False}
    exceeded = current_count >= cfg.max_snapshots
    warned = cfg.warn_at is not None and current_count >= cfg.warn_at
    return {
        "enforced": True,
        "max_snapshots": cfg.max_snapshots,
        "current": current_count,
        "exceeded": exceeded,
        "warned": warned,
        "auto_prune": cfg.auto_prune,
    }
