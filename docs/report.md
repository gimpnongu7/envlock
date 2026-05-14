# envlock report

Generate a human-readable summary of your snapshots and audit history.

## Overview

The `report` command collects snapshot metadata and audit log entries then
renders them as **Markdown** (default) or **HTML**.

## Usage

```bash
# Print a Markdown report to stdout
envlock report

# Save an HTML report to a file
envlock report --format html --output report.html

# Use a custom snapshot directory
envlock report --snapshot-dir .envlock/prod --format markdown
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--env-file` | `.env` | Path to the monitored `.env` file |
| `--snapshot-dir` | `.envlock` | Directory containing snapshots |
| `--format` | `markdown` | Output format: `markdown` or `html` |
| `--output` | *(stdout)* | Write report to this file instead of printing |

## Output — Markdown

```
# envlock Snapshot Report

**Snapshot directory:** `.envlock`
**Total snapshots:** 3

## Snapshots
| ID | Label | Created |
|---|---|---|
| `a1b2c3` | staging | 2024-06-01T12:00:00 |
...

## Audit Log
- **create** `a1b2c3` at 2024-06-01T12:00:00
```

## Output — HTML

An `<!DOCTYPE html>` document containing the same information in a styled
table, suitable for sharing with teammates or embedding in CI artefacts.

## Python API

```python
from pathlib import Path
from envlock.report import generate_report

md = generate_report(
    env_file=Path(".env"),
    snapshot_dir=Path(".envlock"),
    fmt="markdown",
)
print(md)

# Write HTML directly to disk
generate_report(
    env_file=Path(".env"),
    snapshot_dir=Path(".envlock"),
    fmt="html",
    output=Path("report.html"),
)
```

## Errors

`ReportError` is raised when an unsupported format is requested.
All other failures (missing snapshot dir, empty history) are handled
gracefully — the report is still produced with a *no entries* notice.
