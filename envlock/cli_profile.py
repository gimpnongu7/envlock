"""CLI commands for profile management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envlock.profile import (
    ProfileError,
    add_snapshot_to_profile,
    delete_profile,
    get_profile_snapshots,
    list_profiles,
    remove_snapshot_from_profile,
)

DEFAULT_SNAPSHOT_DIR = ".envlock"


def cmd_profile_add(args: argparse.Namespace) -> None:
    base_dir = Path(args.snapshot_dir)
    try:
        add_snapshot_to_profile(base_dir, args.profile, args.label)
        print(f"Added '{args.label}' to profile '{args.profile}'.")
    except ProfileError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_profile_remove(args: argparse.Namespace) -> None:
    base_dir = Path(args.snapshot_dir)
    try:
        remove_snapshot_from_profile(base_dir, args.profile, args.label)
        print(f"Removed '{args.label}' from profile '{args.profile}'.")
    except ProfileError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_profile_list(args: argparse.Namespace) -> None:
    base_dir = Path(args.snapshot_dir)
    names = list_profiles(base_dir)
    if not names:
        print("No profiles defined.")
    else:
        for name in names:
            print(name)


def cmd_profile_show(args: argparse.Namespace) -> None:
    base_dir = Path(args.snapshot_dir)
    try:
        snaps = get_profile_snapshots(base_dir, args.profile)
        if not snaps:
            print(f"Profile '{args.profile}' has no snapshots.")
        else:
            for s in snaps:
                print(s)
    except ProfileError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_profile_delete(args: argparse.Namespace) -> None:
    base_dir = Path(args.snapshot_dir)
    try:
        delete_profile(base_dir, args.profile)
        print(f"Deleted profile '{args.profile}'.")
    except ProfileError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def build_profile_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("profile", help="Manage snapshot profiles")
    p.add_argument("--snapshot-dir", default=DEFAULT_SNAPSHOT_DIR)
    sub = p.add_subparsers(dest="profile_cmd", required=True)

    add_p = sub.add_parser("add", help="Add snapshot to profile")
    add_p.add_argument("profile")
    add_p.add_argument("label")
    add_p.set_defaults(func=cmd_profile_add)

    rm_p = sub.add_parser("remove", help="Remove snapshot from profile")
    rm_p.add_argument("profile")
    rm_p.add_argument("label")
    rm_p.set_defaults(func=cmd_profile_remove)

    sub.add_parser("list", help="List all profiles").set_defaults(func=cmd_profile_list)

    show_p = sub.add_parser("show", help="Show snapshots in a profile")
    show_p.add_argument("profile")
    show_p.set_defaults(func=cmd_profile_show)

    del_p = sub.add_parser("delete", help="Delete a profile")
    del_p.add_argument("profile")
    del_p.set_defaults(func=cmd_profile_delete)
