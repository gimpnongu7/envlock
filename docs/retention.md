# Retention Policies

envlock lets you define a **retention policy** for a snapshot directory so you can automatically control how many snapshots are kept and for how long.

## Setting a Policy

```python
from pathlib import Path
from envlock.retention import set_policy

policy = set_policy(
    Path(".envlock/snapshots"),
    max_age_days=30,   # remove snapshots older than 30 days
    max_count=50,      # keep at most 50 snapshots
    keep_tagged=True,  # never remove tagged snapshots (default)
)
```

The policy is persisted as `.retention_policy.json` inside the snapshot directory.

## Reading a Policy

```python
from envlock.retention import get_policy

policy = get_policy(Path(".envlock/snapshots"))
if policy:
    print(policy.max_age_days)  # e.g. 30
    print(policy.max_count)     # e.g. 50
```

Returns `None` when no policy has been configured.

## Clearing a Policy

```python
from envlock.retention import clear_policy

clear_policy(Path(".envlock/snapshots"))
```

## Human-Readable Summary

```python
from envlock.retention import summary

print(summary(policy))
# max age: 30 days, max count: 50, keep tagged: True
```

## Policy Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `max_age_days` | `int \| None` | `None` | Delete snapshots older than this many days |
| `max_count` | `int \| None` | `None` | Keep only the N most recent snapshots |
| `keep_tagged` | `bool` | `True` | Exempt tagged snapshots from pruning |

## Integration with Prune

The `prune_snapshots` function in `envlock.prune` respects the retention policy when one is present, so you can automate cleanup by calling prune after each snapshot.
