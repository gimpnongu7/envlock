# Snapshot Quota Management

envlock can enforce a maximum number of snapshots per directory, optionally warning before the limit is reached and automatically pruning old snapshots when the limit is hit.

## Setting a Quota

```python
from pathlib import Path
from envlock.quota import set_quota

set_quota(Path(".envlock"), max_snapshots=20, warn_at=15, auto_prune=True)
```

| Parameter | Description |
|---|---|
| `max_snapshots` | Hard upper limit on stored snapshots |
| `warn_at` | Optional count at which a warning is issued |
| `auto_prune` | If `True`, oldest snapshots are pruned automatically |

## Checking Quota Status

```python
from envlock.quota import check_quota

status = check_quota(Path(".envlock"), current_count=17)
if status["exceeded"]:
    print("Quota exceeded!")
elif status["warned"]:
    print(f"Approaching limit: {status['current']}/{status['max_snapshots']}")
```

The returned dict includes:

- `enforced` — whether a quota is configured
- `max_snapshots` — the configured limit
- `current` — snapshots counted at call time
- `exceeded` — whether the limit has been reached
- `warned` — whether the warn threshold has been crossed
- `auto_prune` — whether automatic pruning is enabled

## Reading and Clearing

```python
from envlock.quota import get_quota, clear_quota

cfg = get_quota(Path(".envlock"))  # QuotaConfig or None
clear_quota(Path(".envlock"))      # removes quota file, returns bool
```

## Storage

Quota configuration is stored in `.envlock_quota.json` inside the snapshot directory and is safe to commit to version control alongside your project.
