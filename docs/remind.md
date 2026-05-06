# envlock remind

The `remind` command checks whether your `.env` file needs a new snapshot and prints a human-readable status message.

## When is a reminder triggered?

A reminder is shown (and `stale=True` is returned) when **any** of the following is true:

| Condition | Explanation |
|---|---|
| No snapshot exists | The project has never been snapshotted. |
| `.env` modified after last snapshot | The file has changed since the snapshot was taken. |
| Last snapshot is too old | The snapshot age exceeds `--max-age` seconds (default: 24 h). |

## Usage

```bash
# Basic check
envlock remind

# Custom snapshot directory
envlock remind --snapshot-dir .envlock/snapshots

# Warn if snapshot is older than 1 hour
envlock remind --max-age 3600

# Exit with code 2 when stale (useful in CI pre-flight checks)
envlock remind --exit-code
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Snapshot is up to date. |
| `1` | An error occurred (e.g. `.env` file not found). |
| `2` | Reminder triggered (only when `--exit-code` is passed). |

## Programmatic API

```python
from pathlib import Path
from envlock.remind import check_reminder

status = check_reminder(
    env_path=Path(".env"),
    snapshot_dir=Path(".envlock"),
    max_age_seconds=3600,
)

if status.stale:
    print("Action needed:", status.message)
```

### `ReminderStatus` fields

| Field | Type | Description |
|---|---|---|
| `env_path` | `Path` | Resolved path to the `.env` file. |
| `last_snapshot_ts` | `float \| None` | Unix timestamp of the latest snapshot, or `None`. |
| `env_mtime` | `float` | Last-modified time of the `.env` file. |
| `stale` | `bool` | `True` when a new snapshot is recommended. |
| `message` | `str` | Human-readable status message. |
