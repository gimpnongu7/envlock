"""Generate a status badge (SVG or JSON) reflecting the current env snapshot health."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from envlock.remind import ReminderStatus, check_reminder
from envlock.verify import VerifyError, verify_snapshot
from envlock.snapshot import list_snapshots

BadgeFormat = Literal["json", "svg"]

_COLORS = {
    "ok": "#4c9e3f",
    "stale": "#e6a817",
    "missing": "#cc3c2f",
    "error": "#9b59b6",
}

_SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="140" height="20">
  <rect width="140" height="20" rx="3" fill="#555"/>
  <rect x="60" width="80" height="20" rx="3" fill="{color}"/>
  <text x="30" y="14" fill="#fff" font-size="11" font-family="sans-serif" text-anchor="middle">envlock</text>
  <text x="100" y="14" fill="#fff" font-size="11" font-family="sans-serif" text-anchor="middle">{label}</text>
</svg>"""


class BadgeError(Exception):
    """Raised when badge generation fails."""


def _badge_state(env_file: Path, snapshot_dir: Path) -> tuple[str, str]:
    """Return (state_key, label) describing the current snapshot health."""
    snapshots = list_snapshots(snapshot_dir)
    if not snapshots:
        return "missing", "no snapshot"

    latest_id = snapshots[-1]
    try:
        result = verify_snapshot(latest_id, snapshot_dir)
        verified = result.ok
    except VerifyError:
        return "error", "verify error"

    if not verified:
        return "error", "tampered"

    try:
        status = check_reminder(env_file, snapshot_dir)
    except Exception:
        return "error", "check failed"

    if status.needs_reminder:
        return "stale", "stale"

    return "ok", "up to date"


def generate_badge(
    env_file: Path,
    snapshot_dir: Path,
    fmt: BadgeFormat = "svg",
) -> str:
    """Generate a badge string in the requested format."""
    if fmt not in ("json", "svg"):
        raise BadgeError(f"Unsupported badge format: {fmt!r}")

    state, label = _badge_state(env_file, snapshot_dir)
    color = _COLORS[state]

    if fmt == "json":
        return json.dumps({"state": state, "label": label, "color": color}, indent=2)

    return _SVG_TEMPLATE.format(color=color, label=label)


def write_badge(
    env_file: Path,
    snapshot_dir: Path,
    output: Path,
    fmt: BadgeFormat = "svg",
) -> Path:
    """Write the badge to *output* and return the path."""
    content = generate_badge(env_file, snapshot_dir, fmt)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output
