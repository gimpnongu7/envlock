"""envlock.status — Report the overall health/state of the current env setup."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envlock.remind import check_reminder, ReminderStatus
from envlock.lint import lint_env_file, LintResult
from envlock.snapshot import list_snapshots


class StatusError(Exception):
    pass


@dataclass
class StatusReport:
    env_path: Path
    env_exists: bool
    snapshot_count: int
    latest_snapshot: Optional[str]
    reminder: ReminderStatus
    lint: Optional[LintResult] = None
    warnings: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        """True when no warnings and no lint issues and no stale reminder."""
        lint_ok = self.lint is None or self.lint.ok()
        return not self.warnings and lint_ok and not self.reminder.needs_reminder

    def summary(self) -> str:
        """Return a short one-line summary suitable for logging or CLI output."""
        state = "OK" if self.ok() else "ISSUES FOUND"
        return (
            f"{state} | env={'present' if self.env_exists else 'missing'} "
            f"| snapshots={self.snapshot_count} "
            f"| warnings={len(self.warnings)}"
        )


def get_status(
    env_path: Path,
    snapshot_dir: Path,
    max_age_hours: float = 24.0,
) -> StatusReport:
    """Collect status information for *env_path* and its associated snapshots."""
    if not snapshot_dir.exists():
        raise StatusError(f"Snapshot directory not found: {snapshot_dir}")

    env_exists = env_path.exists()
    warnings: list[str] = []

    snapshots = list_snapshots(snapshot_dir) if snapshot_dir.exists() else []
    snapshot_count = len(snapshots)
    latest_snapshot = snapshots[-1] if snapshots else None

    reminder = check_reminder(env_path, snapshot_dir, max_age_hours=max_age_hours)

    lint_result: Optional[LintResult] = None
    if env_exists:
        try:
            lint_result = lint_env_file(env_path)
        except Exception as exc:  # pragma: no cover
            warnings.append(f"Lint check failed: {exc}")
    else:
        warnings.append(f".env file not found: {env_path}")

    if reminder.needs_reminder:
        warnings.append(reminder.message)

    return StatusReport(
        env_path=env_path,
        env_exists=env_exists,
        snapshot_count=snapshot_count,
        latest_snapshot=latest_snapshot,
        reminder=reminder,
        lint=lint_result,
        warnings=warnings,
    )


def format_status(report: StatusReport) -> str:
    """Return a human-readable summary of *report*."""
    lines: list[str] = []
    status_icon = "✓" if report.ok() else "✗"
    lines.append(f"{status_icon} envlock status for {report.env_path}")
    lines.append(f"  env file present : {report.env_exists}")
    lines.append(f"  snapshots        : {report.snapshot_count}")
    if report.latest_snapshot:
        lines.append(f"  latest snapshot  : {report.latest_snapshot}")
    if report.lint is not None:
        lint_icon = "✓" if report.lint.ok() else "✗"
        issue_count = len(report.lint.issues)
        lines.append(f"  lint             : {lint_icon} ({issue_count} issue(s))")
    if report.warnings:
        lines.append("  warnings:")
        for w in report.warnings:
            lines.append(f"    - {w}")
    return "\n".join(lines)
