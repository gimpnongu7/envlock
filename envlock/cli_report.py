"""CLI subcommands for envlock report generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envlock.report import generate_report, ReportError


def cmd_report(
    args: argparse.Namespace,
    _print=print,
    _exit=sys.exit,
) -> None:
    """Generate a snapshot report and print or save it."""
    env_file = Path(args.env_file)
    snapshot_dir = Path(args.snapshot_dir)
    fmt = getattr(args, "format", "markdown")
    output = Path(args.output) if getattr(args, "output", None) else None

    try:
        rendered = generate_report(
            env_file=env_file,
            snapshot_dir=snapshot_dir,
            fmt=fmt,
            output=output,
        )
    except ReportError as exc:
        _print(f"error: {exc}", file=sys.stderr)
        _exit(1)
        return

    if output:
        _print(f"Report written to {output}")
    else:
        _print(rendered)


def add_report_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("report", help="Generate a snapshot report")
    p.add_argument(
        "--env-file",
        default=".env",
        metavar="PATH",
        help="Path to the .env file (default: .env)",
    )
    p.add_argument(
        "--snapshot-dir",
        default=".envlock",
        metavar="DIR",
        help="Snapshot storage directory (default: .envlock)",
    )
    p.add_argument(
        "--format",
        choices=["markdown", "html"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write report to FILE instead of stdout",
    )
    p.set_defaults(func=cmd_report)
