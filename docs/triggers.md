# Trigger Rules

envlock can automatically snapshot your `.env` file when specific events occur.
Trigger rules let you define *when* a snapshot should be taken without manual
intervention.

## Supported Events

| Event | Description |
|---|---|
| `on_change` | Snapshot whenever the `.env` file content changes |
| `on_branch_switch` | Snapshot before switching git branches |
| `on_interval_minutes` | Snapshot periodically (requires `interval_minutes`) |

## Adding a Rule

```python
from pathlib import Path
from envlock.trigger import TriggerRule, add_rule

rule = TriggerRule(
    event="on_change",
    label_prefix="auto",
    enabled=True,
)
add_rule(Path(".envlock"), rule)
```

For interval-based snapshots, set `interval_minutes`:

```python
rule = TriggerRule(
    event="on_interval_minutes",
    interval_minutes=60,
    label_prefix="hourly",
)
add_rule(Path(".envlock"), rule)
```

## Listing Rules

```python
from envlock.trigger import list_rules

for rule in list_rules(Path(".envlock")):
    print(rule.event, rule.enabled)
```

## Removing Rules

All rules for a given event are removed at once:

```python
from envlock.trigger import remove_rule

remove_rule(Path(".envlock"), "on_change")
```

Raises `TriggerError` if no matching rule exists.

## Querying Rules for an Event

Use `get_rules_for_event` to retrieve only **enabled** rules for a specific
event — useful when implementing the actual snapshot logic in hooks or watchers:

```python
from envlock.trigger import get_rules_for_event

rules = get_rules_for_event(Path(".envlock"), "on_change")
if rules:
    # take snapshot
    ...
```

## Storage

Rules are persisted in `.envlock/.envlock_triggers.json` as a JSON array.
This file is safe to commit if you want trigger configuration shared across
your team.
