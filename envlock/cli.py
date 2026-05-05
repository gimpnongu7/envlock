"""Simple CLI entry point for envlock."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.snapshot import (
    create_snapshot,
    restore_snapshot,
    list_snapshots,
    parse_env_file,
)
from envlock.diff import diff_envs


DEFAULT_ENV = ".env"
DEFAULT_SNAPSHOT_DIR = ".envlock"


def cmd_snapshot(args: argparse.Namespace) -> None:
    path = create_snapshot(
        env_path=args.env_file,
        snapshot_dir=args.snapshot_dir,
        label=args.label,
    )
    print(f"Snapshot saved: {path}")


def cmd_restore(args: argparse.Namespace) -> None:
    restore_snapshot(
        snapshot_id=args.snapshot_id,
        snapshot_dir=args.snapshot_dir,
        env_path=args.env_file,
    )
    print(f"Restored snapshot '{args.snapshot_id}' -> {args.env_file}")


def cmd_list(args: argparse.Namespace) -> None:
    snapshots = list_snapshots(snapshot_dir=args.snapshot_dir)
    if not snapshots:
        print("No snapshots found.")
        return
    for snap in snapshots:
        print(snap)


def cmd_diff(args: argparse.Namespace) -> None:
    before = parse_env_file(Path(args.snapshot_dir) / args.snapshot_id)
    after = parse_env_file(Path(args.env_file))
    result = diff_envs(before, after, mask_secrets=args.mask)
    print(result.summary())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envlock",
        description="Snapshot and restore .env file states.",
    )
    parser.add_argument("--env-file", default=DEFAULT_ENV, help="Path to .env file")
    parser.add_argument("--snapshot-dir", default=DEFAULT_SNAPSHOT_DIR)

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all snapshots")

    snap_p = sub.add_parser("snapshot", help="Create a new snapshot")
    snap_p.add_argument("--label", default=None, help="Optional label for snapshot")

    rest_p = sub.add_parser("restore", help="Restore a snapshot")
    rest_p.add_argument("snapshot_id", help="Snapshot ID or filename to restore")

    diff_p = sub.add_parser("diff", help="Diff a snapshot against current .env")
    diff_p.add_argument("snapshot_id", help="Snapshot file to diff against")
    diff_p.add_argument("--mask", action="store_true", help="Mask secret values")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "snapshot": cmd_snapshot,
        "restore": cmd_restore,
        "list": cmd_list,
        "diff": cmd_diff,
    }
    dispatch[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    main()
