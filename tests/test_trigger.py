import pytest
from pathlib import Path
from envlock.trigger import (
    TriggerRule,
    TriggerError,
    add_rule,
    remove_rule,
    list_rules,
    get_rules_for_event,
)


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_rule_creates_file(base_dir):
    rule = TriggerRule(event="on_change")
    add_rule(base_dir, rule)
    assert (base_dir / ".envlock_triggers.json").exists()


def test_add_rule_returns_rule(base_dir):
    rule = TriggerRule(event="on_change", label_prefix="ci")
    result = add_rule(base_dir, rule)
    assert result.event == "on_change"
    assert result.label_prefix == "ci"


def test_list_rules_empty_when_no_file(base_dir):
    assert list_rules(base_dir) == []


def test_list_rules_returns_all(base_dir):
    add_rule(base_dir, TriggerRule(event="on_change"))
    add_rule(base_dir, TriggerRule(event="on_branch_switch"))
    rules = list_rules(base_dir)
    assert len(rules) == 2
    events = {r.event for r in rules}
    assert events == {"on_change", "on_branch_switch"}


def test_add_multiple_rules_same_event(base_dir):
    add_rule(base_dir, TriggerRule(event="on_change", label_prefix="a"))
    add_rule(base_dir, TriggerRule(event="on_change", label_prefix="b"))
    rules = list_rules(base_dir)
    assert len(rules) == 2


def test_remove_rule_deletes_matching(base_dir):
    add_rule(base_dir, TriggerRule(event="on_change"))
    add_rule(base_dir, TriggerRule(event="on_branch_switch"))
    removed = remove_rule(base_dir, "on_change")
    assert removed == 1
    remaining = list_rules(base_dir)
    assert len(remaining) == 1
    assert remaining[0].event == "on_branch_switch"


def test_remove_rule_removes_all_matching(base_dir):
    add_rule(base_dir, TriggerRule(event="on_change", label_prefix="x"))
    add_rule(base_dir, TriggerRule(event="on_change", label_prefix="y"))
    removed = remove_rule(base_dir, "on_change")
    assert removed == 2
    assert list_rules(base_dir) == []


def test_remove_missing_rule_raises(base_dir):
    with pytest.raises(TriggerError, match="on_change"):
        remove_rule(base_dir, "on_change")


def test_get_rules_for_event_returns_enabled_only(base_dir):
    add_rule(base_dir, TriggerRule(event="on_change", enabled=True))
    add_rule(base_dir, TriggerRule(event="on_change", enabled=False))
    rules = get_rules_for_event(base_dir, "on_change")
    assert len(rules) == 1
    assert rules[0].enabled is True


def test_get_rules_for_event_empty_when_none_match(base_dir):
    add_rule(base_dir, TriggerRule(event="on_branch_switch"))
    assert get_rules_for_event(base_dir, "on_change") == []


def test_interval_minutes_persisted(base_dir):
    add_rule(base_dir, TriggerRule(event="on_interval_minutes", interval_minutes=30))
    rules = list_rules(base_dir)
    assert rules[0].interval_minutes == 30


def test_corrupt_config_raises(base_dir):
    path = base_dir / ".envlock_triggers.json"
    path.write_text("{not valid json")
    with pytest.raises(TriggerError, match="Corrupt"):
        list_rules(base_dir)
