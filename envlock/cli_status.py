"""CLI commands for displaying the current envlock status report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.status import StatusError, format_status, get_status


def cmd_status(args: argparse.Namespace) -> None:
    """Print a full status report for the current .env file and snapshot directory."""
    env_path = Path(args.env_file)
    snapshot_dir = Path(args.snapshot_dir)

    try:
        report = get_status(env_path, snapshot_dir)
    except StatusError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = format_status(report)
    print(output)

    # Exit with a non-zero code when the environment is stale or has issues,
    # so callers / CI pipelines can react programmatically.
    if not report.ok:
        sys.exit(1)


def add_status_subparser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """Register the *status* sub-command on *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "status",
        help="show the current .env snapshot status",
        description=(
            "Display a summary of the current .env file, the latest snapshot, "
            "lint issues, validation results, and whether a new snapshot is "
            "recommended."
        ),
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        metavar="PATH",
        help="path to the .env file to inspect (default: .env)",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".envlock",
        metavar="DIR",
        help="directory that holds snapshots (default: .envlock)",
    )
    parser.set_defaults(func=cmd_status)
