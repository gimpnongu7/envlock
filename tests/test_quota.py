"""Tests for envlock.quota."""

import pytest
from pathlib import Path

from envlock.quota import (
    QuotaConfig,
    QuotaError,
    set_quota,
    get_quota,
    clear_quota,
    check_quota,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def test_set_and_get_quota(snapshot_dir):
    cfg = set_quota(snapshot_dir, max_snapshots=10)
    assert cfg.max_snapshots == 10
    loaded = get_quota(snapshot_dir)
    assert loaded is not None
    assert loaded.max_snapshots == 10


def test_set_quota_with_warn_at(snapshot_dir):
    cfg = set_quota(snapshot_dir, max_snapshots=10, warn_at=7)
    assert cfg.warn_at == 7
    loaded = get_quota(snapshot_dir)
    assert loaded.warn_at == 7


def test_set_quota_with_auto_prune(snapshot_dir):
    cfg = set_quota(snapshot_dir, max_snapshots=5, auto_prune=True)
    assert cfg.auto_prune is True
    loaded = get_quota(snapshot_dir)
    assert loaded.auto_prune is True


def test_set_quota_invalid_max(snapshot_dir):
    with pytest.raises(QuotaError, match="at least 1"):
        set_quota(snapshot_dir, max_snapshots=0)


def test_set_quota_warn_at_gte_max(snapshot_dir):
    with pytest.raises(QuotaError, match="warn_at must be less"):
        set_quota(snapshot_dir, max_snapshots=5, warn_at=5)


def test_get_quota_none_when_unset(snapshot_dir):
    assert get_quota(snapshot_dir) is None


def test_clear_quota_returns_true_when_existed(snapshot_dir):
    set_quota(snapshot_dir, max_snapshots=3)
    assert clear_quota(snapshot_dir) is True
    assert get_quota(snapshot_dir) is None


def test_clear_quota_returns_false_when_missing(snapshot_dir):
    assert clear_quota(snapshot_dir) is False


def test_check_quota_not_enforced_when_no_config(snapshot_dir):
    result = check_quota(snapshot_dir, current_count=99)
    assert result == {"enforced": False}


def test_check_quota_not_exceeded(snapshot_dir):
    set_quota(snapshot_dir, max_snapshots=10, warn_at=7)
    result = check_quota(snapshot_dir, current_count=4)
    assert result["enforced"] is True
    assert result["exceeded"] is False
    assert result["warned"] is False


def test_check_quota_warned(snapshot_dir):
    set_quota(snapshot_dir, max_snapshots=10, warn_at=7)
    result = check_quota(snapshot_dir, current_count=8)
    assert result["warned"] is True
    assert result["exceeded"] is False


def test_check_quota_exceeded(snapshot_dir):
    set_quota(snapshot_dir, max_snapshots=5)
    result = check_quota(snapshot_dir, current_count=5)
    assert result["exceeded"] is True


def test_quota_config_roundtrip():
    cfg = QuotaConfig(max_snapshots=8, warn_at=6, auto_prune=True)
    restored = QuotaConfig.from_dict(cfg.to_dict())
    assert restored.max_snapshots == 8
    assert restored.warn_at == 6
    assert restored.auto_prune is True
