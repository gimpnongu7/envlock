# Snapshot Groups

Groups let you organise snapshots under named collections for easier batch operations, reporting, or logical separation by environment tier.

## Concepts

- A **group** is a named set of snapshot IDs stored in `.envlock_groups.json` inside the snapshot directory.
- Groups are purely organisational; deleting a group does **not** delete the underlying snapshot files.
- A snapshot can belong to multiple groups.

## API

### `add_to_group(snapshot_dir, group, snapshot_id)`

Add a snapshot to a named group. Creates the group if it does not exist. Duplicate additions are silently ignored.

```python
from pathlib import Path
from envlock.group import add_to_group

add_to_group(Path(".snapshots"), "staging", "snap-20240601-abc123")
```

### `remove_from_group(snapshot_dir, group, snapshot_id)`

Remove a snapshot ID from a group. Raises `GroupError` if the group or snapshot ID is not found. Automatically deletes the group when it becomes empty.

### `list_groups(snapshot_dir)`

Return a sorted list of all group names.

```python
from envlock.group import list_groups

for name in list_groups(Path(".snapshots")):
    print(name)
```

### `get_group_members(snapshot_dir, group)`

Return the list of snapshot IDs belonging to a group. Raises `GroupError` if the group does not exist.

### `delete_group(snapshot_dir, group)`

Delete an entire group entry. Raises `GroupError` if the group does not exist.

## Error Handling

All error conditions raise `envlock.group.GroupError` with a descriptive message.

## Storage

Group data is persisted as a JSON object in `<snapshot_dir>/.envlock_groups.json`:

```json
{
  "staging": ["snap-001", "snap-002"],
  "prod": ["snap-003"]
}
```

This file is managed automatically and should not be edited by hand.
