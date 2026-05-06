# Snapshot Archives

envlock can bundle multiple snapshots into a single `.zip` archive for backup or sharing across teams.

## Creating an Archive

Bundle all snapshots in the default snapshot directory:

```bash
envlock archive create backup.zip
```

With a human-readable label:

```bash
envlock archive create backup.zip --label "pre-release snapshot"
```

Bundle only specific snapshots:

```bash
envlock archive create backup.zip --snapshots snap_abc123.env snap_def456.env
```

Use a custom snapshot directory:

```bash
envlock archive create backup.zip --snapshot-dir .envlock/staging
```

## Extracting an Archive

Restore all snapshots from an archive:

```bash
envlock archive extract backup.zip
```

Extract into a specific directory:

```bash
envlock archive extract backup.zip --snapshot-dir .envlock/restored
```

Overwrite existing snapshots:

```bash
envlock archive extract backup.zip --overwrite
```

## Viewing Archive Metadata

Inspect the contents of an archive without extracting:

```bash
envlock archive info backup.zip
```

Example output:

```
Label    : pre-release snapshot
Created  : 2024-06-01T12:34:56+00:00
Snapshots: 3
  snap_abc123.env
  snap_def456.env
  snap_ghi789.env
```

## Python API

```python
from envlock.archive import create_archive, extract_archive, archive_info
from pathlib import Path

# Create
create_archive(Path(".envlock"), Path("backup.zip"), label="my backup")

# Extract
extracted = extract_archive(Path("backup.zip"), Path(".envlock"), overwrite=True)

# Inspect
info = archive_info(Path("backup.zip"))
print(info["snapshots"])
```

## Notes

- Archives include a `_envlock_meta.json` file with creation timestamp, label, and snapshot list.
- Encrypted snapshots (`.env.enc`) are **not** automatically included; archive the encrypted files explicitly by passing their names via `--snapshots`.
- Archives are standard zip files and can be opened with any zip-compatible tool.
