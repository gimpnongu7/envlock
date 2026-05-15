"""CLI subcommands for env file locking."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envlock.lock import LockError, get_lock_info, is_locked, lock_env, unlock_env


def cmd_lock(args: Namespace) -> None:
    env_file = Path(args.env_file)
    try:
        info = lock_env(env_file, reason=args.reason)
        reason_str = f" ({info.reason})" if info.reason else ""
        print(f"Locked {env_file.name} as '{info.locked_by}' at {info.locked_at}{reason_str}")
    except LockError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_unlock(args: Namespace) -> None:
    env_file = Path(args.env_file)
    try:
        info = unlock_env(env_file)
        print(f"Unlocked {env_file.name} (was locked by '{info.locked_by}')")
    except LockError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_lock_status(args: Namespace) -> None:
    env_file = Path(args.env_file)
    if not env_file.exists():
        print(f"error: {env_file} not found", file=sys.stderr)
        sys.exit(1)
    info = get_lock_info(env_file)
    if info is None:
        print(f"{env_file.name}: unlocked")
    else:
        reason_str = f", reason: {info.reason}" if info.reason else ""
        print(f"{env_file.name}: locked by '{info.locked_by}' at {info.locked_at}{reason_str}")


def add_lock_subparser(subparsers) -> None:
    # lock
    p_lock = subparsers.add_parser("lock", help="Lock a .env file against modification")
    p_lock.add_argument("env_file", help="Path to the .env file")
    p_lock.add_argument("--reason", default=None, help="Optional reason for locking")
    p_lock.set_defaults(func=cmd_lock)

    # unlock
    p_unlock = subparsers.add_parser("unlock", help="Unlock a .env file")
    p_unlock.add_argument("env_file", help="Path to the .env file")
    p_unlock.set_defaults(func=cmd_unlock)

    # lock-status
    p_status = subparsers.add_parser("lock-status", help="Show lock status of a .env file")
    p_status.add_argument("env_file", help="Path to the .env file")
    p_status.set_defaults(func=cmd_lock_status)
