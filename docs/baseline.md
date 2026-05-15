# Baseline

A **baseline** is a pinned snapshot that represents the known-good or reference state of your `.env` file. You can compare the current environment against the baseline at any time to see what has drifted.

## Setting a baseline

```bash
# First take a snapshot
envlock snapshot --label before-deploy

# Then mark it as the baseline
envlock baseline set <snapshot-id>
```

## Checking the current baseline

```bash
envlock baseline get
# prints the snapshot id, or "No baseline set."
```

## Comparing against the baseline

```bash
envlock baseline diff
```

Output example:

```
Diff from baseline 'abc123': +1 added, ~1 changed
  + NEW_KEY
  ~ DB_HOST  remotehost -> localhost
```

## Clearing the baseline

```bash
envlock baseline clear
```

This removes the baseline marker without deleting the underlying snapshot.

## Python API

```python
from pathlib import Path
from envlock.baseline import set_baseline, get_baseline, clear_baseline, compare_to_baseline

snap_dir = Path(".envlock/snapshots")

set_baseline(snap_dir, "abc123")
print(get_baseline(snap_dir))  # "abc123"

result = compare_to_baseline(Path(".env"), snap_dir)
if result.has_changes():
    print(result.summary())

clear_baseline(snap_dir)
```

## Notes

- The baseline marker is stored in `.envlock/snapshots/.baseline` as a small JSON file.
- Only one baseline can be active at a time; calling `set_baseline` again replaces the previous one.
- The baseline snapshot itself is never deleted when you call `clear_baseline`.
