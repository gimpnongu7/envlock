"""Classify snapshots by environment type (e.g. dev, staging, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


class ClassifyError(Exception):
    """Raised when classification operations fail."""


_CLASSIFY_FILE = ".envlock_classes.json"


def _classify_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _CLASSIFY_FILE


def _load_classes(snapshot_dir: Path) -> dict:
    p = _classify_path(snapshot_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise ClassifyError(f"Corrupt classification file: {exc}") from exc


def _save_classes(snapshot_dir: Path, data: dict) -> None:
    _classify_path(snapshot_dir).write_text(json.dumps(data, indent=2))


@dataclass
class ClassifyResult:
    snapshot_id: str
    env_class: str

    def __str__(self) -> str:
        return f"{self.snapshot_id} -> {self.env_class}"


def classify_snapshot(
    snapshot_dir: Path, snapshot_id: str, env_class: str
) -> ClassifyResult:
    """Assign an environment class label to a snapshot."""
    if not snapshot_dir.exists():
        raise ClassifyError(f"Snapshot directory not found: {snapshot_dir}")
    env_class = env_class.strip().lower()
    if not env_class:
        raise ClassifyError("env_class must not be blank.")
    data = _load_classes(snapshot_dir)
    data[snapshot_id] = env_class
    _save_classes(snapshot_dir, data)
    return ClassifyResult(snapshot_id=snapshot_id, env_class=env_class)


def get_class(snapshot_dir: Path, snapshot_id: str) -> Optional[str]:
    """Return the environment class for a snapshot, or None if unclassified."""
    data = _load_classes(snapshot_dir)
    return data.get(snapshot_id)


def list_by_class(snapshot_dir: Path, env_class: str) -> List[str]:
    """Return all snapshot IDs assigned to the given environment class."""
    env_class = env_class.strip().lower()
    data = _load_classes(snapshot_dir)
    return [sid for sid, cls in data.items() if cls == env_class]


def remove_class(snapshot_dir: Path, snapshot_id: str) -> None:
    """Remove the classification label from a snapshot."""
    data = _load_classes(snapshot_dir)
    if snapshot_id not in data:
        raise ClassifyError(f"Snapshot '{snapshot_id}' has no classification.")
    del data[snapshot_id]
    _save_classes(snapshot_dir, data)
