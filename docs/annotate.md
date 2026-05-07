# Snapshot Annotations

Annotations let you attach free-form notes to any snapshot, making it easier to remember the context in which a snapshot was taken.

## Commands

### Add or update a note

```bash
envlock annotate add <snapshot-id> "<note text>"
```

Attaches the given note to the snapshot. If the snapshot already has a note it will be overwritten.

### Show a note

```bash
envlock annotate show <snapshot-id>
```

Prints the note attached to a snapshot, or reports that no note is set.

### Remove a note

```bash
envlock annotate remove <snapshot-id>
```

Deletes the note from the snapshot metadata. Raises an error if no note exists.

### List annotated snapshots

```bash
envlock annotate list
```

Shows all snapshots that have a note attached, in the format:

```
[<snapshot-id>] <note text>
```

## Python API

```python
from pathlib import Path
from envlock.annotate import add_note, get_note, remove_note, list_annotated

snap_dir = Path(".envlock/snapshots")

# Add a note
add_note(snap_dir, "20240101-120000", "Before merging feature branch")

# Read it back
note = get_note(snap_dir, "20240101-120000")
print(note)  # Before merging feature branch

# List everything that has a note
for ann in list_annotated(snap_dir):
    print(ann)

# Remove the note
remove_note(snap_dir, "20240101-120000")
```

## Notes are stored in metadata

Annotations are persisted inside the snapshot's `.meta.json` file under the `"note"` key. They do not affect the `.env` content and are preserved across exports and archives.
