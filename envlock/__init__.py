"""envlock — Snapshot and restore .env file states across project branches."""

from .snapshot import (
    parse_env_file,
    create_snapshot,
    restore_snapshot,
    list_snapshots,
)

__version__ = "0.1.0"
__all__ = [
    "parse_env_file",
    "create_snapshot",
    "restore_snapshot",
    "list_snapshots",
]
