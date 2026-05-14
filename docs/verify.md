# Snapshot Verification

The `verify` module checks that snapshot files have not been modified or corrupted since they were created.

## How It Works

When a snapshot is created, its SHA-256 hash is stored in the companion `.meta.json` file alongside other metadata.  
The verifier recomputes the hash of the current `.env` snapshot file and compares it against the stored value.

## Functions

### `verify_snapshot(snapshot_path)`

Verifies a single snapshot file.

```python
from pathlib import Path
from envlock.verify import verify_snapshot

result = verify_snapshot(Path(".envlock/snapshots/main-2024-01-10.env"))
print(result)  # [OK] main-2024-01-10  expected=abc123...  actual=abc123...
```

Returns a `VerifyResult` with:
- `snapshot_id` — stem of the snapshot filename
- `path` — full path to the snapshot
- `expected_hash` — hash stored in `.meta.json` (or `None` if missing)
- `actual_hash` — freshly computed SHA-256 hash
- `passed` — `True` only when both hashes match

### `verify_all(snapshot_dir)`

Verifies every `.env` file in a directory and returns a list of `VerifyResult`.

```python
from envlock.verify import verify_all, format_verify_results

results = verify_all(Path(".envlock/snapshots"))
print(format_verify_results(results))
```

### `format_verify_results(results)`

Formats a list of results into a human-readable string with a summary line.

## Errors

`VerifyError` is raised when:
- The snapshot file does not exist
- The snapshot directory does not exist

## Notes

- A snapshot with no `.meta.json` (or a meta file missing the `hash` key) is always reported as **FAIL**.
- Verification is read-only and never modifies any files.
