"""Migrate snapshots between envlock format versions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


CURRENT_VERSION = 2


class MigrateError(Exception):
    """Raised when a migration fails."""


@dataclass
class MigrateResult:
    snapshot_id: str
    from_version: int
    to_version: int
    skipped: bool = False

    def __str__(self) -> str:
        if self.skipped:
            return f"{self.snapshot_id}: already at v{self.to_version}, skipped"
        return f"{self.snapshot_id}: migrated v{self.from_version} -> v{self.to_version}"


def _meta_path(snapshot_dir: Path, snapshot_id: str) -> Path:
    return snapshot_dir / f"{snapshot_id}.meta.json"


def _load_meta(meta_file: Path) -> dict:
    if not meta_file.exists():
        return {}
    with meta_file.open() as fh:
        return json.load(fh)


def _save_meta(meta_file: Path, meta: dict) -> None:
    with meta_file.open("w") as fh:
        json.dump(meta, fh, indent=2)


def migrate_snapshot(snapshot_dir: Path, snapshot_id: str) -> MigrateResult:
    """Migrate a single snapshot's metadata to the current format version."""
    meta_file = _meta_path(snapshot_dir, snapshot_id)
    if not meta_file.exists():
        raise MigrateError(f"No metadata found for snapshot '{snapshot_id}'")

    meta = _load_meta(meta_file)
    from_version = meta.get("version", 1)

    if from_version >= CURRENT_VERSION:
        return MigrateResult(
            snapshot_id=snapshot_id,
            from_version=from_version,
            to_version=CURRENT_VERSION,
            skipped=True,
        )

    # v1 -> v2: ensure 'label' field exists and rename 'hash' to 'content_hash'
    if from_version < 2:
        meta.setdefault("label", None)
        if "hash" in meta and "content_hash" not in meta:
            meta["content_hash"] = meta.pop("hash")
        meta["version"] = 2

    _save_meta(meta_file, meta)
    return MigrateResult(
        snapshot_id=snapshot_id,
        from_version=from_version,
        to_version=CURRENT_VERSION,
    )


def migrate_all(snapshot_dir: Path) -> List[MigrateResult]:
    """Migrate all snapshots in a directory to the current format version."""
    if not snapshot_dir.exists():
        raise MigrateError(f"Snapshot directory not found: {snapshot_dir}")

    meta_files = sorted(snapshot_dir.glob("*.meta.json"))
    results = []
    for meta_file in meta_files:
        snapshot_id = meta_file.name.replace(".meta.json", "")
        results.append(migrate_snapshot(snapshot_dir, snapshot_id))
    return results
