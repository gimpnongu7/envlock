"""Compute and verify content digests for snapshot integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from dataclasses import dataclass


class DigestError(Exception):
    """Raised when a digest operation fails."""


@dataclass
class DigestRecord:
    snapshot_id: str
    algorithm: str
    hex_digest: str

    def __str__(self) -> str:
        return f"{self.snapshot_id}  [{self.algorithm}]  {self.hex_digest}"


def _digest_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "digests.json"


def _load_digests(snapshot_dir: Path) -> dict:
    p = _digest_path(snapshot_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_digests(snapshot_dir: Path, data: dict) -> None:
    _digest_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def compute_digest(content: str, algorithm: str = "sha256") -> str:
    """Return hex digest of *content* using *algorithm*."""
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise DigestError(f"Unsupported algorithm: {algorithm}") from exc
    h.update(content.encode())
    return h.hexdigest()


def record_digest(snapshot_dir: Path, snapshot_id: str, content: str, algorithm: str = "sha256") -> DigestRecord:
    """Compute and persist a digest for *snapshot_id*."""
    hex_digest = compute_digest(content, algorithm)
    data = _load_digests(snapshot_dir)
    data[snapshot_id] = {"algorithm": algorithm, "hex_digest": hex_digest}
    _save_digests(snapshot_dir, data)
    return DigestRecord(snapshot_id=snapshot_id, algorithm=algorithm, hex_digest=hex_digest)


def verify_digest(snapshot_dir: Path, snapshot_id: str, content: str) -> bool:
    """Return True if *content* matches the stored digest for *snapshot_id*."""
    data = _load_digests(snapshot_dir)
    if snapshot_id not in data:
        raise DigestError(f"No digest recorded for snapshot '{snapshot_id}'")
    entry = data[snapshot_id]
    expected = entry["hex_digest"]
    actual = compute_digest(content, entry["algorithm"])
    return actual == expected


def get_digest(snapshot_dir: Path, snapshot_id: str) -> DigestRecord:
    """Retrieve the stored DigestRecord for *snapshot_id*."""
    data = _load_digests(snapshot_dir)
    if snapshot_id not in data:
        raise DigestError(f"No digest recorded for snapshot '{snapshot_id}'")
    entry = data[snapshot_id]
    return DigestRecord(snapshot_id=snapshot_id, **entry)


def list_digests(snapshot_dir: Path) -> list[DigestRecord]:
    """Return all recorded DigestRecords sorted by snapshot_id."""
    data = _load_digests(snapshot_dir)
    return [
        DigestRecord(snapshot_id=sid, **entry)
        for sid, entry in sorted(data.items())
    ]
