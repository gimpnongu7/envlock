"""Tests for envlock.retention."""
import pytest
from pathlib import Path

from envlock.retention import (
    RetentionPolicy,
    RetentionError,
    set_policy,
    get_policy,
    clear_policy,
    summary,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_set_and_get_policy(snapshot_dir):
    policy = set_policy(snapshot_dir, max_age_days=30, max_count=50)
    assert policy.max_age_days == 30
    assert policy.max_count == 50
    assert policy.keep_tagged is True

    loaded = get_policy(snapshot_dir)
    assert loaded is not None
    assert loaded.max_age_days == 30
    assert loaded.max_count == 50


def test_get_policy_returns_none_when_unset(snapshot_dir):
    assert get_policy(snapshot_dir) is None


def test_set_policy_invalid_max_age(snapshot_dir):
    with pytest.raises(RetentionError, match="max_age_days"):
        set_policy(snapshot_dir, max_age_days=0)


def test_set_policy_invalid_max_count(snapshot_dir):
    with pytest.raises(RetentionError, match="max_count"):
        set_policy(snapshot_dir, max_count=-1)


def test_set_policy_keep_tagged_false(snapshot_dir):
    policy = set_policy(snapshot_dir, max_count=10, keep_tagged=False)
    assert policy.keep_tagged is False
    loaded = get_policy(snapshot_dir)
    assert loaded.keep_tagged is False


def test_clear_policy_removes_file(snapshot_dir):
    set_policy(snapshot_dir, max_age_days=7)
    removed = clear_policy(snapshot_dir)
    assert removed is True
    assert get_policy(snapshot_dir) is None


def test_clear_policy_no_file_returns_false(snapshot_dir):
    assert clear_policy(snapshot_dir) is False


def test_policy_overwrite(snapshot_dir):
    set_policy(snapshot_dir, max_age_days=30)
    set_policy(snapshot_dir, max_age_days=14, max_count=20)
    loaded = get_policy(snapshot_dir)
    assert loaded.max_age_days == 14
    assert loaded.max_count == 20


def test_summary_full_policy():
    policy = RetentionPolicy(max_age_days=7, max_count=100, keep_tagged=True)
    result = summary(policy)
    assert "7 days" in result
    assert "100" in result
    assert "keep tagged: True" in result


def test_summary_partial_policy():
    policy = RetentionPolicy(max_count=25, keep_tagged=False)
    result = summary(policy)
    assert "max age" not in result
    assert "25" in result
    assert "keep tagged: False" in result


def test_corrupt_policy_raises(snapshot_dir):
    (snapshot_dir / ".retention_policy.json").write_text("not-json")
    with pytest.raises(RetentionError, match="Corrupt"):
        get_policy(snapshot_dir)
