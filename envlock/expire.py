"""Snapshot expiry — mark snapshots with a TTL and detect expired ones."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class ExpireError(Exception):
    """Raised when expiry operations fail."""


@dataclass
class ExpiryRecord:
    snapshot_id: str
    expires_at: datetime
    expired: bool

    def __str__(self) -> str:
        state = "EXPIRED" if self.expired else "active"
        return f"{self.snapshot_id}  expires={self.expires_at.isoformat()}  [{state}]"


def _meta_path(snapshot_dir: Path, snapshot_id: str) -> Path:
    return snapshot_dir / f"{snapshot_id}.meta.json"


def _load_meta(meta: Path) -> dict:
    """Read and parse a metadata file, raising ExpireError on failure."""
    try:
        return json.loads(meta.read_text())
    except json.JSONDecodeError as exc:
        raise ExpireError(f"Malformed metadata file '{meta}': {exc}") from exc


def set_expiry(snapshot_dir: Path, snapshot_id: str, expires_at: datetime) -> ExpiryRecord:
    """Attach an expiry timestamp to a snapshot's metadata."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise ExpireError(f"No metadata found for snapshot '{snapshot_id}'")

    data = _load_meta(meta)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    data["expires_at"] = expires_at.isoformat()
    meta.write_text(json.dumps(data, indent=2))

    now = datetime.now(tz=timezone.utc)
    return ExpiryRecord(
        snapshot_id=snapshot_id,
        expires_at=expires_at,
        expired=expires_at <= now,
    )


def get_expiry(snapshot_dir: Path, snapshot_id: str) -> Optional[ExpiryRecord]:
    """Return expiry info for a snapshot, or None if no TTL is set."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise ExpireError(f"No metadata found for snapshot '{snapshot_id}'")

    data = _load_meta(meta)
    raw = data.get("expires_at")
    if raw is None:
        return None

    expires_at = datetime.fromisoformat(raw)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    return ExpiryRecord(
        snapshot_id=snapshot_id,
        expires_at=expires_at,
        expired=expires_at <= now,
    )


def list_expired(snapshot_dir: Path) -> List[ExpiryRecord]:
    """Return all snapshots that have passed their expiry time."""
    if not snapshot_dir.exists():
        raise ExpireError(f"Snapshot directory not found: {snapshot_dir}")

    expired = []
    for meta_file in sorted(snapshot_dir.glob("*.meta.json")):
        snapshot_id = meta_file.name.replace(".meta.json", "")
        record = get_expiry(snapshot_dir, snapshot_id)
        if record is not None and record.expired:
            expired.append(record)
    return expired


def clear_expiry(snapshot_dir: Path, snapshot_id: str) -> None:
    """Remove the expiry timestamp from a snapshot's metadata."""
    meta = _meta_path(snapshot_dir, snapshot_id)
    if not meta.exists():
        raise ExpireError(f"No metadata found for snapshot '{snapshot_id}'")

    data = _load_meta(meta)
    if "expires_at" not in data:
        return
    data.pop("expires_at")
    meta.write_text(json.dumps(data, indent=2))
