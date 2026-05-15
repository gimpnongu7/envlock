"""Lock/unlock mechanism to prevent accidental .env modifications."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class LockError(Exception):
    """Raised when a lock operation fails."""


@dataclass
class LockInfo:
    env_path: str
    locked_by: str
    locked_at: str
    reason: Optional[str] = None


def _lock_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.name}.lock"


def lock_env(env_file: Path, reason: Optional[str] = None) -> LockInfo:
    """Create a lock file for the given .env file."""
    env_file = Path(env_file)
    if not env_file.exists():
        raise LockError(f"env file not found: {env_file}")

    lock_file = _lock_path(env_file)
    if lock_file.exists():
        existing = _read_lock(lock_file)
        raise LockError(
            f"{env_file.name} is already locked by '{existing.locked_by}' "
            f"at {existing.locked_at}"
        )

    import getpass
    from datetime import datetime, timezone

    info = LockInfo(
        env_path=str(env_file.resolve()),
        locked_by=getpass.getuser(),
        locked_at=datetime.now(timezone.utc).isoformat(),
        reason=reason,
    )
    lock_file.write_text(json.dumps(info.__dict__, indent=2))
    return info


def unlock_env(env_file: Path) -> LockInfo:
    """Remove the lock file for the given .env file."""
    env_file = Path(env_file)
    lock_file = _lock_path(env_file)
    if not lock_file.exists():
        raise LockError(f"{env_file.name} is not locked")
    info = _read_lock(lock_file)
    lock_file.unlink()
    return info


def is_locked(env_file: Path) -> bool:
    """Return True if the env file has an active lock."""
    return _lock_path(Path(env_file)).exists()


def get_lock_info(env_file: Path) -> Optional[LockInfo]:
    """Return lock info if locked, else None."""
    lock_file = _lock_path(Path(env_file))
    if not lock_file.exists():
        return None
    return _read_lock(lock_file)


def _read_lock(lock_file: Path) -> LockInfo:
    data = json.loads(lock_file.read_text())
    return LockInfo(**data)
