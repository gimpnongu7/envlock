# Snapshot Rename

The `rename` module lets you rename an existing snapshot (and its associated
metadata) without touching the `.env` content.

## API

```python
from envlock.rename import rename_snapshot, RenameError

new_path = rename_snapshot(
    snapshot_dir=".envlock/snapshots",
    old_name="feature-login",
    new_name="feature-auth",
)
print(f"Renamed to {new_path}")
```

### `rename_snapshot(snapshot_dir, old_name, new_name) -> Path`

| Parameter | Type | Description |
|-----------|------|-------------|
| `snapshot_dir` | `str \| Path` | Directory containing snapshots |
| `old_name` | `str` | Current snapshot name or filename |
| `new_name` | `str` | Desired snapshot name or filename |

Returns the `Path` of the renamed snapshot file.

**Raises `RenameError` when:**
- `snapshot_dir` does not exist
- The source snapshot is not found
- A snapshot with `new_name` already exists

## Behaviour

- Both the `.env` file and the corresponding `.meta.json` file are renamed
  atomically (sequential `rename` calls).
- If a `.meta.json` exists, the `name` field inside it is updated to match the
  new stem so that history and audit logs stay consistent.
- You may pass either a bare stem (`feature-login`) or a full filename
  (`feature-login.env`) — both forms are accepted.

## Errors

```python
try:
    rename_snapshot(".envlock/snapshots", "old", "already-taken")
except RenameError as exc:
    print(f"Could not rename: {exc}")
```
