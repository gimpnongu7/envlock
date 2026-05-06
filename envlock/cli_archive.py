"""CLI subcommands for archive management."""

import argparse
import sys
from pathlib import Path

from envlock.archive import create_archive, extract_archive, archive_info, ArchiveError


def cmd_archive_create(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    output = Path(args.output)
    ids = args.snapshots if args.snapshots else None
    try:
        path = create_archive(snapshot_dir, output, label=args.label, snapshot_ids=ids)
        print(f"Archive created: {path}")
    except ArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_archive_extract(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    snapshot_dir = Path(args.snapshot_dir)
    try:
        files = extract_archive(archive, snapshot_dir, overwrite=args.overwrite)
        print(f"Extracted {len(files)} snapshot(s) to {snapshot_dir}:")
        for f in files:
            print(f"  {f}")
    except ArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_archive_info(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    try:
        info = archive_info(archive)
        print(f"Label    : {info.get('label') or '(none)'}")
        print(f"Created  : {info.get('created_at', 'unknown')}")
        print(f"Snapshots: {len(info.get('snapshots', []))}")
        for s in info.get("snapshots", []):
            print(f"  {s}")
    except ArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_archive_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("archive", help="Bundle and restore snapshot archives")
    sub = p.add_subparsers(dest="archive_cmd", required=True)

    # create
    pc = sub.add_parser("create", help="Create a snapshot archive")
    pc.add_argument("output", help="Output .zip path")
    pc.add_argument("--snapshot-dir", default=".envlock", help="Snapshot directory")
    pc.add_argument("--label", default="", help="Human-readable label")
    pc.add_argument("--snapshots", nargs="+", metavar="FILE", help="Specific snapshot files")
    pc.set_defaults(func=cmd_archive_create)

    # extract
    pe = sub.add_parser("extract", help="Extract snapshots from an archive")
    pe.add_argument("archive", help="Path to .zip archive")
    pe.add_argument("--snapshot-dir", default=".envlock", help="Destination directory")
    pe.add_argument("--overwrite", action="store_true", help="Overwrite existing snapshots")
    pe.set_defaults(func=cmd_archive_extract)

    # info
    pi = sub.add_parser("info", help="Show archive metadata")
    pi.add_argument("archive", help="Path to .zip archive")
    pi.set_defaults(func=cmd_archive_info)
