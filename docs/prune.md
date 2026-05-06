# Snapshot Pruning

Over time the snapshot directory can accumulate many files. The `prune` module
provides a simple way to keep the directory tidy by removing the oldest
snapshots.

## API

### `prune_snapshots(snapshot_dir, *, keep, dry_run=False)`

Remove old snapshots from *snapshot_dir*, retaining only the *keep* most
recent ones.

| Parameter      | Type            | Description                                          |
|----------------|-----------------|------------------------------------------------------|
| `snapshot_dir` | `pathlib.Path`  | Directory containing `.env` snapshot files.          |
| `keep`         | `int` or `None` | Number of snapshots to keep. `None` means keep all.  |
| `dry_run`      | `bool`          | If `True`, list candidates without deleting them.    |

**Returns** a list of `Path` objects that were (or would be) removed.

**Raises** `PruneError` if `keep < 1` or the directory does not exist.

## Example

```python
from pathlib import Path
from envlock.prune import prune_snapshots

removed = prune_snapshots(Path(".envlock/snapshots"), keep=5)
for p in removed:
    print(f"Removed: {p.name}")
```

## Dry-run mode

Pass `dry_run=True` to preview which files *would* be deleted without
actually removing anything:

```python
candidates = prune_snapshots(Path(".envlock/snapshots"), keep=5, dry_run=True)
print(f"{len(candidates)} snapshot(s) would be pruned")
```

## Notes

- Snapshots are ordered by file modification time; the **oldest** files are
  removed first.
- Pinned or tagged snapshots are not treated specially by the prune module —
  resolve pins/tags before pruning if you need to preserve them.
