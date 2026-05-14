"""Generate a human-readable HTML or Markdown report of snapshots and their metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envlock.history import get_history, HistoryEntry
from envlock.audit import read_log, AuditEntry


class ReportError(Exception):
    """Raised when report generation fails."""


@dataclass
class ReportData:
    snapshot_dir: Path
    entries: List[HistoryEntry] = field(default_factory=list)
    audit: List[AuditEntry] = field(default_factory=list)


def _collect(snapshot_dir: Path, env_file: Path) -> ReportData:
    try:
        entries = get_history(env_file, snapshot_dir)
    except Exception:
        entries = []
    try:
        audit = read_log(snapshot_dir)
    except Exception:
        audit = []
    return ReportData(snapshot_dir=snapshot_dir, entries=entries, audit=audit)


def _render_markdown(data: ReportData) -> str:
    lines = ["# envlock Snapshot Report", ""]
    lines.append(f"**Snapshot directory:** `{data.snapshot_dir}`  ")
    lines.append(f"**Total snapshots:** {len(data.entries)}  ")
    lines.append("")
    lines.append("## Snapshots")
    if not data.entries:
        lines.append("_No snapshots found._")
    else:
        lines.append("| ID | Label | Created |")
        lines.append("|---|---|---|")
        for e in data.entries:
            lines.append(f"| `{e.snapshot_id}` | {e.label or '—'} | {e.created_at} |")
    lines.append("")
    lines.append("## Audit Log")
    if not data.audit:
        lines.append("_No audit entries._")
    else:
        for entry in data.audit:
            lines.append(f"- **{entry.action}** `{entry.snapshot_id}` at {entry.timestamp}")
    return "\n".join(lines)


def _render_html(data: ReportData) -> str:
    rows = ""
    for e in data.entries:
        rows += f"<tr><td><code>{e.snapshot_id}</code></td><td>{e.label or '—'}</td><td>{e.created_at}</td></tr>\n"
    audit_items = "".join(
        f"<li><b>{a.action}</b> <code>{a.snapshot_id}</code> at {a.timestamp}</li>\n"
        for a in data.audit
    )
    return f"""<!DOCTYPE html>
<html><head><title>envlock Report</title></head><body>
<h1>envlock Snapshot Report</h1>
<p><b>Directory:</b> <code>{data.snapshot_dir}</code></p>
<h2>Snapshots ({len(data.entries)})</h2>
<table border="1"><tr><th>ID</th><th>Label</th><th>Created</th></tr>
{rows or '<tr><td colspan="3">No snapshots</td></tr>'}</table>
<h2>Audit Log</h2>
<ul>{audit_items or '<li>No entries</li>'}</ul>
</body></html>"""


def generate_report(
    env_file: Path,
    snapshot_dir: Path,
    fmt: str = "markdown",
    output: Optional[Path] = None,
) -> str:
    """Generate a report in *fmt* (``markdown`` or ``html``).

    Returns the rendered string and optionally writes it to *output*.
    """
    if fmt not in ("markdown", "html"):
        raise ReportError(f"Unknown format {fmt!r}. Choose 'markdown' or 'html'.")
    data = _collect(snapshot_dir, env_file)
    rendered = _render_markdown(data) if fmt == "markdown" else _render_html(data)
    if output is not None:
        output.write_text(rendered, encoding="utf-8")
    return rendered
