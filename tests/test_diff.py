"""Tests for envlock.diff module."""

import pytest

from envlock.diff import EnvDiffResult, diff_envs, _maybe_mask


BEFORE = {
    "APP_ENV": "development",
    "DB_HOST": "localhost",
    "SECRET_KEY": "old_secret",
    "UNCHANGED": "same",
}

AFTER = {
    "APP_ENV": "production",
    "DB_HOST": "localhost",  # unchanged
    "NEW_VAR": "hello",
    "UNCHANGED": "same",
}


def test_diff_detects_added():
    result = diff_envs(BEFORE, AFTER)
    assert "NEW_VAR" in result.added
    assert result.added["NEW_VAR"] == "hello"


def test_diff_detects_removed():
    result = diff_envs(BEFORE, AFTER)
    assert "SECRET_KEY" in result.removed
    assert result.removed["SECRET_KEY"] == "old_secret"


def test_diff_detects_changed():
    result = diff_envs(BEFORE, AFTER)
    assert "APP_ENV" in result.changed
    old, new = result.changed["APP_ENV"]
    assert old == "development"
    assert new == "production"


def test_diff_detects_unchanged():
    result = diff_envs(BEFORE, AFTER)
    assert "DB_HOST" in result.unchanged
    assert "UNCHANGED" in result.unchanged


def test_has_changes_true():
    result = diff_envs(BEFORE, AFTER)
    assert result.has_changes is True


def test_has_changes_false():
    result = diff_envs(BEFORE, BEFORE)
    assert result.has_changes is False


def test_summary_no_changes():
    result = diff_envs(BEFORE, BEFORE)
    assert result.summary() == "No differences found."


def test_summary_with_changes():
    result = diff_envs(BEFORE, AFTER)
    summary = result.summary()
    assert "+ NEW_VAR=hello" in summary
    assert "- SECRET_KEY=old_secret" in summary
    assert "~ APP_ENV" in summary


def test_mask_secrets():
    result = diff_envs(BEFORE, AFTER, mask_secrets=True)
    assert result.removed["SECRET_KEY"] != "old_secret"
    assert result.removed["SECRET_KEY"].startswith("o")
    assert result.removed["SECRET_KEY"].endswith("t")


def test_maybe_mask_short_value():
    assert _maybe_mask("ab", True) == "ab"


def test_maybe_mask_disabled():
    assert _maybe_mask("secret", False) == "secret"


def test_diff_empty_dicts():
    result = diff_envs({}, {})
    assert not result.has_changes
