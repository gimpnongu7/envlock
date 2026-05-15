# Bookmarks

Bookmarks let you assign memorable short names to specific snapshots so you can reference them without remembering long snapshot IDs.

## Concepts

A bookmark is a simple alias: a human-readable name that maps to a snapshot ID.  
Bookmarks are stored per snapshot directory in a `.bookmarks.json` file.

## CLI Usage

### Add a bookmark

```bash
envlock bookmark add <name> <snapshot_id>
```

Example:

```bash
envlock bookmark add stable snap_20240601_120000
```

### Resolve a bookmark

Print the snapshot ID that a bookmark points to:

```bash
envlock bookmark resolve stable
# snap_20240601_120000
```

### Update a bookmark

Move an existing bookmark to a different snapshot:

```bash
envlock bookmark update stable snap_20240615_090000
```

### Remove a bookmark

```bash
envlock bookmark remove stable
```

### List all bookmarks

```bash
envlock bookmark list
```

Output:

```
alpha                snap_20240601_120000
stable               snap_20240615_090000
```

## Python API

```python
from pathlib import Path
from envlock.bookmark import add_bookmark, resolve_bookmark, list_bookmarks

snap_dir = Path(".envlock/snapshots")

add_bookmark(snap_dir, "stable", "snap_001")
print(resolve_bookmark(snap_dir, "stable"))  # snap_001

for b in list_bookmarks(snap_dir):
    print(b["name"], b["snapshot_id"])
```

## Errors

- Adding a bookmark with a name that already exists raises `BookmarkError`.
- Resolving or removing a non-existent bookmark raises `BookmarkError`.
- Updating a bookmark that does not exist raises `BookmarkError` — use `add_bookmark` instead.
- A blank bookmark name raises `BookmarkError`.
