# Snapshot Tags

Tags let you attach human-readable names to specific snapshot IDs, making it
easy to reference important states (e.g. `stable`, `pre-deploy`, `v2.1`).

## CLI Usage

### Add a tag

```bash
envlock tag add <snapshot-id> <tag-name>
```

Example:

```bash
envlock tag add 20240501_120000_abc123 stable
```

### Remove a tag

```bash
envlock tag remove <tag-name>
```

### List all tags

```bash
envlock tag list
```

Sample output:

```
release  ->  20240501_120000_abc123
staging  ->  20240430_090000_def456
```

## Python API

```python
from pathlib import Path
from envlock.tag import add_tag, resolve_tag, remove_tag, list_tags

snap_dir = Path(".envlock")

# Tag a snapshot
add_tag(snap_dir, "20240501_120000_abc123", "stable")

# Resolve a tag to its snapshot ID
snap_id = resolve_tag(snap_dir, "stable")

# List all tags
for entry in list_tags(snap_dir):
    print(entry["tag"], "->", entry["snapshot_id"])

# Remove a tag
remove_tag(snap_dir, "stable")
```

## Notes

- Tag names must be unique. Adding a duplicate tag raises `TagError`.
- Tags are stored in `.envlock/.envlock_tags.json` alongside your snapshots.
- Tags are not automatically removed when a snapshot is deleted — clean them up
  manually with `envlock tag remove`.
