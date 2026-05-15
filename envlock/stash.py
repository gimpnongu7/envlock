"""Temporary stash for .env files — save and pop without creating named snapshots."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional


class StashError(Exception):
    pass


def _stash_dir(base_dir: Path) -> Path:
    return base_dir / ".stash"


def _stash_index_path(base_dir: Path) -> Path:
    return _stash_dir(base_dir) / "index.json"


def _load_index(base_dir: Path) -> list[dict]:
    path = _stash_index_path(base_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_index(base_dir: Path, index: list[dict]) -> None:
    _stash_dir(base_dir).mkdir(parents=True, exist_ok=True)
    _stash_index_path(base_dir).write_text(json.dumps(index, indent=2))


def stash_push(env_file: Path, base_dir: Path, message: Optional[str] = None) -> str:
    """Push current .env onto the stash stack. Returns stash entry id."""
    if not env_file.exists():
        raise StashError(f"env file not found: {env_file}")

    _stash_dir(base_dir).mkdir(parents=True, exist_ok=True)
    index = _load_index(base_dir)
    entry_id = f"stash@{{{len(index)}}}"
    dest = _stash_dir(base_dir) / f"{len(index)}.env"
    shutil.copy2(env_file, dest)
    index.append({"id": entry_id, "message": message or "", "file": dest.name})
    _save_index(base_dir, index)
    return entry_id


def stash_pop(env_file: Path, base_dir: Path) -> str:
    """Pop the most recent stash entry and restore it to env_file."""
    index = _load_index(base_dir)
    if not index:
        raise StashError("stash is empty")

    entry = index.pop()
    src = _stash_dir(base_dir) / entry["file"]
    if not src.exists():
        raise StashError(f"stash entry file missing: {src}")

    shutil.copy2(src, env_file)
    src.unlink()
    _save_index(base_dir, index)
    return entry["id"]


def stash_list(base_dir: Path) -> list[dict]:
    """Return all stash entries, newest first."""
    return list(reversed(_load_index(base_dir)))


def stash_drop(base_dir: Path, index_pos: int = 0) -> str:
    """Drop a stash entry by position (0 = most recent) without restoring."""
    index = _load_index(base_dir)
    if not index:
        raise StashError("stash is empty")
    real_pos = len(index) - 1 - index_pos
    if real_pos < 0 or real_pos >= len(index):
        raise StashError(f"no stash entry at position {index_pos}")
    entry = index.pop(real_pos)
    src = _stash_dir(base_dir) / entry["file"]
    if src.exists():
        src.unlink()
    _save_index(base_dir, index)
    return entry["id"]
