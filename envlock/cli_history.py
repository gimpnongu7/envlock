"""CLI subcommands for snapshot history."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.history import HistoryError, format_history, get_entry_by_index, get_history


def cmd_history(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    limit = args.limit if args.limit and args.limit > 0 else None

    try:
        entries = get_history(snapshot_dir, limit=limit)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_history(entries))


def cmd_history_show(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        entry = get_entry_by_index(snapshot_dir, args.index)
    except HistoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    label = entry.label or "(none)"
    print(f"Index    : {entry.index}")
    print(f"ID       : {entry.snapshot_id}")
    print(f"Label    : {label}")
    print(f"Timestamp: {entry.timestamp}")
    print(f"Keys     : {entry.key_count}")


def add_history_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p_hist = subparsers.add_parser("history", help="Browse snapshot history")
    p_hist.add_argument("--snapshot-dir", default=".envlock", metavar="DIR")
    p_hist.add_argument("--limit", type=int, default=None, metavar="N",
                        help="Show only the N most recent snapshots")
    p_hist.set_defaults(func=cmd_history)

    p_show = subparsers.add_parser("history-show", help="Inspect a specific snapshot by index")
    p_show.add_argument("index", type=int, help="0-based history index")
    p_show.add_argument("--snapshot-dir", default=".envlock", metavar="DIR")
    p_show.set_defaults(func=cmd_history_show)
