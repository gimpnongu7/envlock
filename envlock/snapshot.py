"""Core module for snapshotting and restoring .env file states."""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

DEFAULT_SNAPSHOT_DIR = ".envlock"


def _hash_content(content: str) -> str:
    """Return a short SHA256 hash of the given content."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def parse_env_file(filepath: str) -> dict:
    """Parse a .env file into a dictionary, ignoring comments and blank lines."""
    env_vars = {}
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {filepath}")

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    return env_vars


def create_snapshot(env_path: str = ".env", label: str = None, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> dict:
    """Snapshot the current .env file and save it to the snapshot directory."""
    env_path = Path(env_path)
    if not env_path.exists():
        raise FileNotFoundError(f"No .env file found at: {env_path}")

    content = env_path.read_text()
    timestamp = datetime.utcnow().isoformat()
    content_hash = _hash_content(content)
    snapshot_name = label or f"snapshot_{content_hash}"

    snapshot_dir_path = Path(snapshot_dir)
    snapshot_dir_path.mkdir(parents=True, exist_ok=True)

    snapshot_meta = {
        "label": snapshot_name,
        "timestamp": timestamp,
        "hash": content_hash,
        "source": str(env_path),
        "vars": parse_env_file(str(env_path)),
    }

    snapshot_file = snapshot_dir_path / f"{snapshot_name}.json"
    with open(snapshot_file, "w") as f:
        json.dump(snapshot_meta, f, indent=2)

    return snapshot_meta


def restore_snapshot(label: str, target_path: str = ".env", snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> None:
    """Restore a previously saved snapshot to the target .env file."""
    snapshot_file = Path(snapshot_dir) / f"{label}.json"
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot not found: {label}")

    with open(snapshot_file, "r") as f:
        snapshot_meta = json.load(f)

    env_lines = [f"{k}={v}" for k, v in snapshot_meta["vars"].items()]
    env_content = "\n".join(env_lines) + "\n"

    with open(target_path, "w") as f:
        f.write(env_content)


def list_snapshots(snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> list:
    """Return a list of all available snapshots with their metadata."""
    snapshot_dir_path = Path(snapshot_dir)
    if not snapshot_dir_path.exists():
        return []

    snapshots = []
    for snap_file in sorted(snapshot_dir_path.glob("*.json")):
        with open(snap_file, "r") as f:
            meta = json.load(f)
        snapshots.append({"label": meta["label"], "timestamp": meta["timestamp"], "hash": meta["hash"]})
    return snapshots
