# Snapshot Migration

envlock uses a versioned metadata format for snapshots. As the tool evolves, older snapshots may need to be migrated to the current format version.

## Current Format Version

The current metadata version is **v2**.

## What Changes Between Versions

### v1 → v2

- The `hash` field is renamed to `content_hash` for clarity.
- A `label` field is added (defaults to `null` if absent).
- The `version` field is written explicitly.

## Migrating Snapshots

### Migrate a single snapshot

```python
from pathlib import Path
from envlock.migrate import migrate_snapshot

result = migrate_snapshot(Path(".envlock/snapshots"), "my-snapshot-id")
print(result)  # my-snapshot-id: migrated v1 -> v2
```

### Migrate all snapshots in a directory

```python
from pathlib import Path
from envlock.migrate import migrate_all

results = migrate_all(Path(".envlock/snapshots"))
for r in results:
    print(r)
```

## Behaviour

- Snapshots already at the current version are **skipped** — migration is idempotent.
- If a snapshot has no `version` field it is assumed to be **v1**.
- Migrating a snapshot ID with no corresponding `.meta.json` file raises a `MigrateError`.
- Passing a non-existent directory to `migrate_all` raises a `MigrateError`.

## MigrateResult

Each call returns a `MigrateResult` dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `snapshot_id` | `str` | ID of the snapshot |
| `from_version` | `int` | Version before migration |
| `to_version` | `int` | Version after migration |
| `skipped` | `bool` | `True` if already up to date |

`str(result)` gives a human-readable summary suitable for CLI output.
