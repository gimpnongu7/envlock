"""Namespace support — group snapshots under named namespaces for multi-env projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


class NamespaceError(Exception):
    """Raised when a namespace operation fails."""


def _namespace_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".namespaces.json"


def _load_namespaces(snapshot_dir: Path) -> dict:
    p = _namespace_path(snapshot_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise NamespaceError(f"Corrupt namespace index: {exc}") from exc


def _save_namespaces(snapshot_dir: Path, data: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _namespace_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def assign_namespace(snapshot_dir: Path, snapshot_id: str, namespace: str) -> None:
    """Assign *snapshot_id* to *namespace*, creating the namespace if needed."""
    if not namespace.strip():
        raise NamespaceError("Namespace name must not be blank.")
    data = _load_namespaces(snapshot_dir)
    members: List[str] = data.setdefault(namespace, [])
    if snapshot_id not in members:
        members.append(snapshot_id)
    _save_namespaces(snapshot_dir, data)


def remove_from_namespace(snapshot_dir: Path, snapshot_id: str, namespace: str) -> None:
    """Remove *snapshot_id* from *namespace*."""
    data = _load_namespaces(snapshot_dir)
    if namespace not in data:
        raise NamespaceError(f"Namespace '{namespace}' does not exist.")
    members: List[str] = data[namespace]
    if snapshot_id not in members:
        raise NamespaceError(f"Snapshot '{snapshot_id}' not in namespace '{namespace}'.")
    members.remove(snapshot_id)
    if not members:
        del data[namespace]
    _save_namespaces(snapshot_dir, data)


def list_namespaces(snapshot_dir: Path) -> List[str]:
    """Return sorted list of all namespace names."""
    return sorted(_load_namespaces(snapshot_dir).keys())


def get_namespace_members(snapshot_dir: Path, namespace: str) -> List[str]:
    """Return snapshot IDs belonging to *namespace*."""
    data = _load_namespaces(snapshot_dir)
    if namespace not in data:
        raise NamespaceError(f"Namespace '{namespace}' does not exist.")
    return list(data[namespace])


def find_namespace(snapshot_dir: Path, snapshot_id: str) -> Optional[str]:
    """Return the namespace that contains *snapshot_id*, or None."""
    for ns, members in _load_namespaces(snapshot_dir).items():
        if snapshot_id in members:
            return ns
    return None
