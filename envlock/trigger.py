"""Trigger rules: automatically snapshot .env when configured conditions are met."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


class TriggerError(Exception):
    pass


@dataclass
class TriggerRule:
    event: str          # 'on_change' | 'on_branch_switch' | 'on_interval_minutes'
    label_prefix: str = "auto"
    enabled: bool = True
    interval_minutes: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "TriggerRule":
        return TriggerRule(
            event=d["event"],
            label_prefix=d.get("label_prefix", "auto"),
            enabled=d.get("enabled", True),
            interval_minutes=d.get("interval_minutes"),
        )


@dataclass
class TriggerConfig:
    rules: List[TriggerRule] = field(default_factory=list)


def _trigger_path(base_dir: Path) -> Path:
    return base_dir / ".envlock_triggers.json"


def _load_config(base_dir: Path) -> TriggerConfig:
    path = _trigger_path(base_dir)
    if not path.exists():
        return TriggerConfig()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise TriggerError(f"Corrupt trigger config: {exc}") from exc
    rules = [TriggerRule.from_dict(r) for r in data.get("rules", [])]
    return TriggerConfig(rules=rules)


def _save_config(base_dir: Path, config: TriggerConfig) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _trigger_path(base_dir).write_text(
        json.dumps({"rules": [r.to_dict() for r in config.rules]}, indent=2)
    )


def add_rule(base_dir: Path, rule: TriggerRule) -> TriggerRule:
    """Append a trigger rule; duplicate events are allowed (multiple rules per event)."""
    config = _load_config(base_dir)
    config.rules.append(rule)
    _save_config(base_dir, config)
    return rule


def remove_rule(base_dir: Path, event: str) -> int:
    """Remove all rules matching *event*. Returns number of rules removed."""
    config = _load_config(base_dir)
    before = len(config.rules)
    config.rules = [r for r in config.rules if r.event != event]
    removed = before - len(config.rules)
    if removed == 0:
        raise TriggerError(f"No trigger rule found for event '{event}'")
    _save_config(base_dir, config)
    return removed


def list_rules(base_dir: Path) -> List[TriggerRule]:
    """Return all configured trigger rules."""
    return _load_config(base_dir).rules


def get_rules_for_event(base_dir: Path, event: str) -> List[TriggerRule]:
    """Return enabled rules that match the given event."""
    return [r for r in list_rules(base_dir) if r.event == event and r.enabled]
