"""CLI subcommands for snapshot tagging."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.tag import TagError, add_tag, remove_tag, list_tags


def cmd_tag_add(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        add_tag(snapshot_dir, args.snapshot_id, args.tag)
        print(f"Tagged '{args.snapshot_id}' as '{args.tag}'.")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        snapshot_id = remove_tag(snapshot_dir, args.tag)
        print(f"Removed tag '{args.tag}' (was pointing to {snapshot_id}).")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    entries = list_tags(snapshot_dir)
    if not entries:
        print("No tags defined.")
        return
    width = max(len(e["tag"]) for e in entries)
    for entry in entries:
        print(f"{entry['tag']:<{width}}  ->  {entry['snapshot_id']}")


def add_tag_subparser(subparsers: argparse._SubParsersAction) -> None:
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Tag a snapshot")
    p_add.add_argument("snapshot_id", help="Snapshot ID to tag")
    p_add.add_argument("tag", help="Tag name")
    p_add.add_argument("--snapshot-dir", default=".envlock", dest="snapshot_dir")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag")
    p_rm.add_argument("tag", help="Tag name to remove")
    p_rm.add_argument("--snapshot-dir", default=".envlock", dest="snapshot_dir")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List all tags")
    p_ls.add_argument("--snapshot-dir", default=".envlock", dest="snapshot_dir")
    p_ls.set_defaults(func=cmd_tag_list)
