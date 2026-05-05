"""Audit log for snapshot operations (create, restore, delete)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = ".envlock_audit.jsonl"


@dataclass
class AuditEntry:
    timestamp: str
    action: str          # "create", "restore", "delete"
    snapshot_name: str
    env_file: str
    label: Optional[str] = None
    note: Optional[str] = None


def _audit_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / AUDIT_FILENAME


def record(snapshot_dir: Path, action: str, snapshot_name: str,
           env_file: str, label: Optional[str] = None,
           note: Optional[str] = None) -> AuditEntry:
    """Append an audit entry to the log and return it."""
    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    entry = AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        action=action,
        snapshot_name=snapshot_name,
        env_file=str(env_file),
        label=label,
        note=note,
    )

    with _audit_path(snapshot_dir).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(entry)) + "\n")

    return entry


def read_log(snapshot_dir: Path) -> List[AuditEntry]:
    """Return all audit entries, oldest first."""
    path = _audit_path(Path(snapshot_dir))
    if not path.exists():
        return []
    entries: List[AuditEntry] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                data = json.loads(line)
                entries.append(AuditEntry(**data))
    return entries


def format_log(entries: List[AuditEntry]) -> str:
    """Return a human-readable audit log string."""
    if not entries:
        return "(no audit entries)"
    lines = []
    for e in entries:
        label_part = f" [{e.label}]" if e.label else ""
        note_part = f" — {e.note}" if e.note else ""
        lines.append(f"{e.timestamp}  {e.action:<10} {e.snapshot_name}{label_part}{note_part}")
    return "\n".join(lines)
