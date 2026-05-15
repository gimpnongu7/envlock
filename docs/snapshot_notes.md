# Snapshot Notes

Snapshot notes let you attach a freeform text description (and optional tags)
to any snapshot. Notes are stored in a `.notes.json` file inside the snapshot
directory and are never part of the `.env` content itself.

## API

### `add_note(snapshot_dir, snapshot_id, text, tags=None) -> SnapshotNote`

Attach a note to a snapshot. If a note already exists for that snapshot it is
replaced. `text` must not be blank.

```python
from envlock.snapshot_notes import add_note

note = add_note(Path(".envlock"), "snap-20240101-abc", "pre-deploy baseline", tags=["prod"])
print(note)  # snap-20240101-abc: pre-deploy baseline [prod]
```

### `get_note(snapshot_dir, snapshot_id) -> SnapshotNote | None`

Retrieve the note for a snapshot. Returns `None` if no note has been added.

```python
from envlock.snapshot_notes import get_note

note = get_note(Path(".envlock"), "snap-20240101-abc")
if note:
    print(note.text)
```

### `remove_note(snapshot_dir, snapshot_id) -> None`

Delete the note for a snapshot. Raises `SnapshotNoteError` if the snapshot has
no note.

### `list_notes(snapshot_dir) -> list[SnapshotNote]`

Return all notes sorted alphabetically by snapshot ID.

```python
from envlock.snapshot_notes import list_notes

for note in list_notes(Path(".envlock")):
    print(note)
```

## Data model

`SnapshotNote` has three fields:

| Field | Type | Description |
|---|---|---|
| `snapshot_id` | `str` | ID of the snapshot this note belongs to |
| `text` | `str` | The note body |
| `tags` | `list[str]` | Optional classification tags |

## Storage

Notes are persisted in `<snapshot_dir>/.notes.json` as a plain JSON object
keyed by snapshot ID. The file is created on first write and is safe to
commit alongside your snapshots (it contains no secret values).
