"""CLI commands for rollback functionality."""

from __future__ import annotations

import argparse
from pathlib import Path

from envlock.rollback import rollback, RollbackError


def cmd_rollback(args: argparse.Namespace) -> None:
    """Handle the ``envlock rollback`` subcommand."""
    env_path = Path(args.env_file)
    snapshot_dir = Path(args.snapshot_dir)

    label: str | None = getattr(args, "label", None) or None
    steps_back: int = getattr(args, "steps", 1) or 1
    dry_run: bool = getattr(args, "dry_run", False)

    try:
        name = rollback(
            env_path,
            snapshot_dir,
            label=label,
            steps_back=steps_back,
            dry_run=dry_run,
        )
    except RollbackError as exc:
        print(f"[rollback] error: {exc}")
        raise SystemExit(1) from exc

    if dry_run:
        print(f"[rollback] dry-run — would restore: {name}")
    else:
        print(f"[rollback] restored: {name}")


def add_rollback_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the rollback subcommand on *subparsers*."""
    p = subparsers.add_parser(
        "rollback",
        help="Revert .env to a previous snapshot.",
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
        "--label",
        default=None,
        help="Restore the snapshot whose filename contains this label.",
    )
    p.add_argument(
        "--steps",
        type=int,
        default=1,
        help="How many snapshots to go back (default: 1).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print which snapshot would be restored without modifying the file.",
    )
    p.set_defaults(func=cmd_rollback)
