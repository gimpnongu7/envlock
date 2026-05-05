# Audit Log

envlock keeps an append-only audit log of every snapshot operation so you can
trace exactly when a snapshot was created, restored, or deleted.

## Location

The log is stored as a newline-delimited JSON file (`.envlock_audit.jsonl`)
inside your snapshot directory.  Each line is one JSON object.

## Entry fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO-8601 UTC string | When the action occurred |
| `action` | string | `create`, `restore`, or `delete` |
| `snapshot_name` | string | Filename of the snapshot |
| `env_file` | string | Path to the `.env` file involved |
| `label` | string \| null | Optional human-readable label |
| `note` | string \| null | Optional free-text note |

## Python API

```python
from pathlib import Path
from envlock.audit import record, read_log, format_log

snap_dir = Path(".envlock")

# Record an action
record(snap_dir, "create", "snap_abc123.env", ".env", label="pre-deploy")

# Read all entries
entries = read_log(snap_dir)
for e in entries:
    print(e.action, e.snapshot_name, e.timestamp)

# Pretty-print the log
print(format_log(entries))
```

## Example output

```
2024-06-01T12:00:00+00:00  create     snap_abc123.env [pre-deploy]
2024-06-01T14:30:00+00:00  restore    snap_abc123.env — rolled back after failed deploy
```

> **Tip:** The audit log is plain text — you can `grep`, `jq`, or tail it like
> any other log file.
