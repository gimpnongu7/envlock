# Rollback

The rollback feature lets you revert your `.env` file to a previously captured snapshot without having to remember exact snapshot filenames.

## How it works

Snapshots are stored chronologically in your snapshot directory (default `.envlock/`).  
Rollback walks backward through that history and restores the chosen entry.

## CLI usage

```bash
# Revert one step back (default)
envlock rollback

# Revert two steps back
envlock rollback --steps 2

# Revert to a snapshot whose filename contains a specific label
envlock rollback --label baseline

# Preview what would be restored without touching the file
envlock rollback --dry-run

# Custom paths
envlock rollback --env-file config/.env --snapshot-dir .envlock/config
```

## Python API

```python
from pathlib import Path
from envlock.rollback import rollback, RollbackError

try:
    name = rollback(
        env_path=Path(".env"),
        snapshot_dir=Path(".envlock"),
        steps_back=1,       # or label="my-label"
        dry_run=False,
    )
    print(f"Restored: {name}")
except RollbackError as e:
    print(f"Could not roll back: {e}")
```

## Audit log

Every successful rollback is recorded in the audit log automatically.  
Use `envlock audit` (or `envlock.audit.read_log`) to review the history.

## Notes

- `steps_back=1` targets the snapshot just **before** the most recent one.
- Passing a `label` always takes priority over `steps_back`.
- Dry-run mode prints the target snapshot name but leaves the `.env` file untouched.
