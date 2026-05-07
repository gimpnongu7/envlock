"""CLI subcommands for snapshot annotations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.annotate import (
    add_note,
    get_note,
    remove_note,
    list_annotated,
    AnnotateError,
)


def cmd_annotate_add(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        ann = add_note(snapshot_dir, args.snapshot_id, args.note)
        print(f"Note added to {ann.snapshot_id}: {ann.note}")
    except AnnotateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_show(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        note = get_note(snapshot_dir, args.snapshot_id)
        if note is None:
            print(f"No note on snapshot {args.snapshot_id}.")
        else:
            print(note)
    except AnnotateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_remove(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        remove_note(snapshot_dir, args.snapshot_id)
        print(f"Note removed from {args.snapshot_id}.")
    except AnnotateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_list(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    results = list_annotated(snapshot_dir)
    if not results:
        print("No annotated snapshots.")
        return
    for ann in results:
        print(ann)


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Manage snapshot notes")
    sub = p.add_subparsers(dest="annotate_cmd", required=True)

    add_p = sub.add_parser("add", help="Add or update a note")
    add_p.add_argument("snapshot_id")
    add_p.add_argument("note")
    add_p.set_defaults(func=cmd_annotate_add)

    show_p = sub.add_parser("show", help="Show note for a snapshot")
    show_p.add_argument("snapshot_id")
    show_p.set_defaults(func=cmd_annotate_show)

    rm_p = sub.add_parser("remove", help="Remove note from a snapshot")
    rm_p.add_argument("snapshot_id")
    rm_p.set_defaults(func=cmd_annotate_remove)

    ls_p = sub.add_parser("list", help="List all annotated snapshots")
    ls_p.set_defaults(func=cmd_annotate_list)
