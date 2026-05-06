# Snapshot History

`envlock` keeps a browsable history of every snapshot you create, letting you
inspect, navigate, and restore any previous state.

## Commands

### `envlock history`

List all snapshots, newest first.

```
envlock history [--snapshot-dir DIR] [--limit N]
```

Example output:

```
#0  env-2024-06-01T120000.snap [prod]  ts=2024-06-01T12:00:00  keys=8
#1  env-2024-05-30T090000.snap         ts=2024-05-30T09:00:00  keys=7
```

| Flag | Default | Description |
|------|---------|-------------|
| `--snapshot-dir` | `.envlock` | Directory that stores snapshots |
| `--limit N` | all | Show only the N most recent entries |

---

### `envlock history-show <index>`

Display full details for a single snapshot by its 0-based history index.

```
envlock history-show 0 [--snapshot-dir DIR]
```

Example output:

```
Index    : 0
ID       : env-2024-06-01T120000.snap
Label    : prod
Timestamp: 2024-06-01T12:00:00
Keys     : 8
```

---

## Python API

```python
from pathlib import Path
from envlock.history import get_history, get_entry_by_index, format_history

snap_dir = Path(".envlock")

# All entries, newest first
entries = get_history(snap_dir)
print(format_history(entries))

# Fetch a specific entry
entry = get_entry_by_index(snap_dir, 0)
print(entry.snapshot_id, entry.label)
```

## Notes

- History metadata (label, timestamp) is read from `.meta.json` sidecar files
  written automatically by `create_snapshot`.
- If no sidecar exists the entry is still listed; `timestamp` will show
  `"unknown"` and `label` will be `None`.
