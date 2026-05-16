"""Branch-aware snapshot binding: associate snapshots with git branches."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional


class BranchError(Exception):
    """Raised when branch operations fail."""


def _branch_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".branch_bindings.json"


def _load_bindings(snapshot_dir: Path) -> dict:
    p = _branch_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bindings(snapshot_dir: Path, data: dict) -> None:
    _branch_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def current_branch() -> str:
    """Return the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise BranchError("could not determine current git branch") from exc


def bind_snapshot(snapshot_dir: Path, snapshot_id: str, branch: Optional[str] = None) -> str:
    """Bind a snapshot ID to a branch (defaults to current branch)."""
    if not snapshot_dir.exists():
        raise BranchError(f"snapshot directory not found: {snapshot_dir}")
    branch = branch or current_branch()
    bindings = _load_bindings(snapshot_dir)
    bindings[branch] = snapshot_id
    _save_bindings(snapshot_dir, bindings)
    return branch


def resolve_branch(snapshot_dir: Path, branch: Optional[str] = None) -> str:
    """Return the snapshot ID bound to a branch."""
    branch = branch or current_branch()
    bindings = _load_bindings(snapshot_dir)
    if branch not in bindings:
        raise BranchError(f"no snapshot bound to branch '{branch}'")
    return bindings[branch]


def unbind_branch(snapshot_dir: Path, branch: Optional[str] = None) -> str:
    """Remove the snapshot binding for a branch."""
    branch = branch or current_branch()
    bindings = _load_bindings(snapshot_dir)
    if branch not in bindings:
        raise BranchError(f"no binding found for branch '{branch}'")
    del bindings[branch]
    _save_bindings(snapshot_dir, bindings)
    return branch


def list_bindings(snapshot_dir: Path) -> dict:
    """Return all branch -> snapshot_id bindings."""
    return _load_bindings(snapshot_dir)
