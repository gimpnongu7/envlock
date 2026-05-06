# Snapshot Pins

Pins let you attach a memorable alias (e.g. `stable`, `release`, `pre-deploy`) to a specific snapshot ID so you can reference it by name instead of a hash.

## Concepts

| Term | Meaning |
|------|---------|
| **alias** | A short human-readable name you choose |
| **snapshot_id** | The underlying snapshot filename / identifier |

## Python API

```python
from pathlib import Path
from envlock.pin import pin_snapshot, resolve_pin, unpin, list_pins

base = Path(".envlock")

# Create a pin
pin_snapshot(base, "stable", "20240601_120000_abc123")

# Resolve it later
snap_id = resolve_pin(base, "stable")

# Overwrite an existing pin
pin_snapshot(base, "stable", "20240615_090000_def456", overwrite=True)

# List all pins
for alias, snap_id in list_pins(base).items():
    print(f"{alias} -> {snap_id}")

# Remove a pin
unpin(base, "stable")
```

## Error Handling

- `PinError` is raised when:
  - Pinning an alias that already exists (without `overwrite=True`)
  - Resolving or removing an alias that does not exist

## Storage

Pins are stored in `.envlock_pins.json` inside the snapshot directory. The file is a simple JSON object mapping alias names to snapshot IDs.

```json
{
  "stable": "20240601_120000_abc123",
  "canary": "20240615_090000_def456"
}
```

> **Tip:** Commit `.envlock_pins.json` alongside your snapshots to share pin definitions with your team.
