# Profiles

Profiles let you group snapshots under a named environment label (e.g. `dev`,
`staging`, `prod`). This makes it easy to track which snapshots belong to which
deployment context.

## Storage

Profile metadata is stored in `.envlock/.envlock_profiles.json` as a simple
JSON object mapping profile names to lists of snapshot labels.

```json
{
  "dev": ["snap-20240101-120000", "snap-20240102-090000"],
  "prod": ["snap-20240101-180000"]
}
```

## CLI Usage

### Add a snapshot to a profile

```bash
envlock profile add dev snap-20240101-120000
```

### List all profiles

```bash
envlock profile list
```

### Show snapshots in a profile

```bash
envlock profile show dev
```

### Remove a snapshot from a profile

```bash
envlock profile remove dev snap-20240101-120000
```

### Delete a profile entirely

```bash
envlock profile delete dev
```

## Python API

```python
from pathlib import Path
from envlock.profile import (
    add_snapshot_to_profile,
    get_profile_snapshots,
    list_profiles,
    delete_profile,
)

base = Path(".envlock")
add_snapshot_to_profile(base, "dev", "snap-001")
print(list_profiles(base))          # ['dev']
print(get_profile_snapshots(base, "dev"))  # ['snap-001']
delete_profile(base, "dev")
```

## Notes

- Profile names are arbitrary strings; keep them short and meaningful.
- A snapshot label can appear in multiple profiles.
- Deleting a profile does **not** delete the underlying snapshot files.
