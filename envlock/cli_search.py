"""CLI subcommands for snapshot search."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.search import search_snapshots, SearchError


def cmd_search(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)

    key_pattern = getattr(args, "key", None) or None
    value_pattern = getattr(args, "value", None) or None
    label_pattern = getattr(args, "label", None) or None

    if not any([key_pattern, value_pattern, label_pattern]):
        print("error: provide at least one of --key, --value, or --label", file=sys.stderr)
        sys.exit(1)

    try:
        result = search_snapshots(
            snapshot_dir,
            key_pattern=key_pattern,
            value_pattern=value_pattern,
            label_pattern=label_pattern,
        )
    except SearchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if not result.found():
        sys.exit(1)


def add_search_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("search", help="Search snapshots by key, value, or label")
    p.add_argument(
        "--snapshot-dir",
        default=".envlock/snapshots",
        help="Directory containing snapshots (default: .envlock/snapshots)",
    )
    p.add_argument("--key", metavar="PATTERN", help="Filter by key substring")
    p.add_argument("--value", metavar="PATTERN", help="Filter by value substring")
    p.add_argument("--label", metavar="PATTERN", help="Filter by label substring")
    p.set_defaults(func=cmd_search)
