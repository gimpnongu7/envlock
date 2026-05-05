"""Export snapshots to portable formats (JSON, shell script)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Literal

from envlock.snapshot import list_snapshots, parse_env_file

ExportFormat = Literal["json", "shell"]


class ExportError(Exception):
    pass


def _env_to_shell(env: Dict[str, str], export: bool = True) -> str:
    """Render an env dict as shell variable assignments."""
    lines = []
    prefix = "export " if export else ""
    for key, value in sorted(env.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{prefix}{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def export_snapshot(
    snapshot_dir: Path,
    label: str,
    fmt: ExportFormat = "json",
    output_path: Path | None = None,
    export_keyword: bool = True,
) -> str:
    """Export a named snapshot to *fmt* format.

    Returns the rendered string and optionally writes it to *output_path*.
    Raises ExportError when the label is not found.
    """
    snapshots = list_snapshots(snapshot_dir)
    if label not in snapshots:
        raise ExportError(
            f"Snapshot '{label}' not found. Available: {', '.join(snapshots) or 'none'}"
        )

    snapshot_file = snapshot_dir / f"{label}.env"
    env = parse_env_file(snapshot_file)

    if fmt == "json":
        rendered = json.dumps(env, indent=2, sort_keys=True) + "\n"
    elif fmt == "shell":
        rendered = _env_to_shell(env, export=export_keyword)
    else:
        raise ExportError(f"Unknown format: {fmt!r}. Choose 'json' or 'shell'.")

    if output_path is not None:
        output_path.write_text(rendered, encoding="utf-8")

    return rendered
