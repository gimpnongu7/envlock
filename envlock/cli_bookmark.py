"""CLI sub-commands for bookmark management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    update_bookmark,
)


def cmd_bookmark_add(args: argparse.Namespace) -> None:
    try:
        add_bookmark(Path(args.snapshot_dir), args.name, args.snapshot_id)
        print(f"Bookmarked '{args.name}' -> {args.snapshot_id}")
    except BookmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_remove(args: argparse.Namespace) -> None:
    try:
        remove_bookmark(Path(args.snapshot_dir), args.name)
        print(f"Removed bookmark '{args.name}'.")
    except BookmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_resolve(args: argparse.Namespace) -> None:
    try:
        sid = resolve_bookmark(Path(args.snapshot_dir), args.name)
        print(sid)
    except BookmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_list(args: argparse.Namespace) -> None:
    bookmarks = list_bookmarks(Path(args.snapshot_dir))
    if not bookmarks:
        print("No bookmarks defined.")
        return
    for b in bookmarks:
        print(f"{b['name']:20s}  {b['snapshot_id']}")


def cmd_bookmark_update(args: argparse.Namespace) -> None:
    try:
        update_bookmark(Path(args.snapshot_dir), args.name, args.snapshot_id)
        print(f"Updated bookmark '{args.name}' -> {args.snapshot_id}")
    except BookmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_bookmark_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("bookmark", help="Manage snapshot bookmarks")
    sp = p.add_subparsers(dest="bookmark_cmd", required=True)

    add = sp.add_parser("add", help="Add a new bookmark")
    add.add_argument("name")
    add.add_argument("snapshot_id")
    add.set_defaults(func=cmd_bookmark_add)

    rm = sp.add_parser("remove", help="Remove a bookmark")
    rm.add_argument("name")
    rm.set_defaults(func=cmd_bookmark_remove)

    res = sp.add_parser("resolve", help="Print snapshot ID for a bookmark")
    res.add_argument("name")
    res.set_defaults(func=cmd_bookmark_resolve)

    ls = sp.add_parser("list", help="List all bookmarks")
    ls.set_defaults(func=cmd_bookmark_list)

    up = sp.add_parser("update", help="Update an existing bookmark")
    up.add_argument("name")
    up.add_argument("snapshot_id")
    up.set_defaults(func=cmd_bookmark_update)
