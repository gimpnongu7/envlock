"""CLI sub-commands for envlock remind."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.remind import RemindError, check_reminder


def cmd_remind(args: argparse.Namespace) -> None:
    """Check whether the .env file needs a new snapshot and print a reminder."""
    try:
        status = check_reminder(
            env_path=Path(args.env_file),
            snapshot_dir=Path(args.snapshot_dir),
            max_age_seconds=args.max_age,
        )
    except RemindError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(status.message)

    if args.exit_code and status.stale:
        sys.exit(2)


def add_remind_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "remind",
        help="Check whether a new snapshot is recommended.",
    )
    p.add_argument(
        "--env-file",
        default=".env",
        help="Path to the .env file (default: .env).",
    )
    p.add_argument(
        "--snapshot-dir",
        default=".envlock",
        help="Directory where snapshots are stored (default: .envlock).",
    )
    p.add_argument(
        "--max-age",
        type=int,
        default=86400,
        metavar="SECONDS",
        help="Warn if the latest snapshot is older than this many seconds (default: 86400).",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 2 when a reminder is triggered (useful in CI).",
    )
    p.set_defaults(func=cmd_remind)
