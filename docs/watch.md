# Auto-Watch Mode

`envlock` can monitor a `.env` file for changes and automatically snapshot it
whenever the content changes.

## How it works

The watcher polls the file at a configurable interval (default **2 s**).  On
each tick it hashes the file content; if the hash differs from the previous
read a new snapshot is written to the snapshot directory.

The very first read is treated as a baseline — no snapshot is created until an
actual change is detected.

## Python API

```python
from pathlib import Path
from envlock.watch import watch_env_file

watch_env_file(
    env_path=Path(".env"),
    snapshot_dir=Path(".env-snapshots"),
    interval=2.0,          # seconds between polls
    label_prefix="auto",   # snapshot label: auto-<unix-timestamp>
    on_snapshot=print,     # called with the snapshot filename on each save
    max_snapshots=0,       # 0 = run until Ctrl-C
)
```

## CLI (coming soon)

```
envlock watch [--interval 2] [--label-prefix auto] [--env .env]
```

## Notes

- The watcher runs in the **foreground** and exits cleanly on `KeyboardInterrupt`.
- Snapshots are named `<label_prefix>-<unix_timestamp>.json` and stored
  alongside regular `envlock` snapshots.
- Combine with `envlock diff` to review what changed between two auto-snapshots.
