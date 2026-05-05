"""Watch a .env file for changes and auto-snapshot on modification."""

import time
import os
from pathlib import Path
from typing import Optional, Callable

from envlock.snapshot import create_snapshot, _hash_content


class WatchError(Exception):
    pass


def _get_mtime(path: Path) -> float:
    """Return file modification time or -1 if not found."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return -1.0


def watch_env_file(
    env_path: Path,
    snapshot_dir: Path,
    interval: float = 2.0,
    label_prefix: str = "auto",
    on_snapshot: Optional[Callable[[str], None]] = None,
    max_snapshots: int = 0,
) -> None:
    """
    Poll *env_path* every *interval* seconds and create a snapshot whenever
    the file content changes.  Runs until interrupted (KeyboardInterrupt).

    Args:
        env_path: Path to the .env file to monitor.
        snapshot_dir: Directory where snapshots are stored.
        interval: Polling interval in seconds.
        label_prefix: Prefix used when auto-generating snapshot labels.
        on_snapshot: Optional callback invoked with the snapshot filename.
        max_snapshots: Stop after this many snapshots (0 = run forever).
    """
    env_path = Path(env_path)
    snapshot_dir = Path(snapshot_dir)

    if not env_path.exists():
        raise WatchError(f".env file not found: {env_path}")

    last_hash: Optional[str] = None
    count = 0

    try:
        while True:
            current_hash = _hash_content(env_path.read_bytes())
            if current_hash != last_hash:
                if last_hash is not None:  # skip the very first read
                    label = f"{label_prefix}-{int(time.time())}"
                    filename = create_snapshot(env_path, snapshot_dir, label=label)
                    count += 1
                    if on_snapshot:
                        on_snapshot(filename)
                    if max_snapshots and count >= max_snapshots:
                        break
                last_hash = current_hash
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
