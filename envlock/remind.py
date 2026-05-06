"""Remind users to snapshot their .env file based on staleness."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envlock.snapshot import list_snapshots


class RemindError(Exception):
    """Raised when reminder checks fail."""


@dataclass
class ReminderStatus:
    env_path: Path
    last_snapshot_ts: Optional[float]
    env_mtime: float
    stale: bool
    message: str


def _latest_snapshot_ts(snapshot_dir: Path) -> Optional[float]:
    """Return the mtime of the most recently created snapshot, or None."""
    snapshots = list_snapshots(snapshot_dir)
    if not snapshots:
        return None
    # list_snapshots returns dicts with a 'path' key
    mtimes = [Path(s["path"]).stat().st_mtime for s in snapshots]
    return max(mtimes)


def check_reminder(
    env_path: Path,
    snapshot_dir: Path,
    max_age_seconds: int = 86400,
) -> ReminderStatus:
    """Check whether the .env file needs a new snapshot.

    A reminder is triggered when:
    - No snapshot exists yet, or
    - The .env file has been modified after the latest snapshot, or
    - The latest snapshot is older than *max_age_seconds*.
    """
    env_path = Path(env_path)
    if not env_path.exists():
        raise RemindError(f".env file not found: {env_path}")

    env_mtime = env_path.stat().st_mtime
    last_ts = _latest_snapshot_ts(Path(snapshot_dir))
    now = time.time()

    if last_ts is None:
        return ReminderStatus(
            env_path=env_path,
            last_snapshot_ts=None,
            env_mtime=env_mtime,
            stale=True,
            message="No snapshot found — consider running `envlock snapshot`.",
        )

    env_changed = env_mtime > last_ts
    too_old = (now - last_ts) > max_age_seconds

    if env_changed:
        msg = ".env has changed since the last snapshot — snapshot recommended."
    elif too_old:
        msg = f"Last snapshot is older than {max_age_seconds}s — snapshot recommended."
    else:
        msg = "Snapshot is up to date."

    return ReminderStatus(
        env_path=env_path,
        last_snapshot_ts=last_ts,
        env_mtime=env_mtime,
        stale=env_changed or too_old,
        message=msg,
    )
