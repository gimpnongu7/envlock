"""CLI subcommands for snapshot digest management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.digest import DigestError, record_digest, verify_digest, get_digest, list_digests


def cmd_digest_record(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        sys.exit(1)
    content = env_path.read_text()
    try:
        rec = record_digest(snapshot_dir, args.snapshot_id, content, algorithm=args.algorithm)
        print(f"Recorded digest for '{rec.snapshot_id}': {rec.hex_digest} ({rec.algorithm})")
    except DigestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_digest_verify(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        sys.exit(1)
    content = env_path.read_text()
    try:
        ok = verify_digest(snapshot_dir, args.snapshot_id, content)
    except DigestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if ok:
        print(f"OK  '{args.snapshot_id}' digest matches.")
    else:
        print(f"FAIL  '{args.snapshot_id}' digest mismatch — file may have been tampered.", file=sys.stderr)
        sys.exit(2)


def cmd_digest_show(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    try:
        rec = get_digest(snapshot_dir, args.snapshot_id)
        print(str(rec))
    except DigestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_digest_list(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    records = list_digests(snapshot_dir)
    if not records:
        print("No digests recorded.")
        return
    for rec in records:
        print(str(rec))


def add_digest_subparser(subparsers) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("digest", help="Manage snapshot content digests")
    sub = p.add_subparsers(dest="digest_cmd", required=True)

    rec = sub.add_parser("record", help="Record digest for a snapshot")
    rec.add_argument("snapshot_id")
    rec.add_argument("--env-file", default=".env")
    rec.add_argument("--snapshot-dir", default=".envlock")
    rec.add_argument("--algorithm", default="sha256")
    rec.set_defaults(func=cmd_digest_record)

    ver = sub.add_parser("verify", help="Verify snapshot digest against current env file")
    ver.add_argument("snapshot_id")
    ver.add_argument("--env-file", default=".env")
    ver.add_argument("--snapshot-dir", default=".envlock")
    ver.set_defaults(func=cmd_digest_verify)

    show = sub.add_parser("show", help="Show stored digest for a snapshot")
    show.add_argument("snapshot_id")
    show.add_argument("--snapshot-dir", default=".envlock")
    show.set_defaults(func=cmd_digest_show)

    lst = sub.add_parser("list", help="List all recorded digests")
    lst.add_argument("--snapshot-dir", default=".envlock")
    lst.set_defaults(func=cmd_digest_list)
