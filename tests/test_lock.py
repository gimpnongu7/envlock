"""Tests for envlock.lock module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envlock.lock import (
    LockError,
    LockInfo,
    lock_env,
    unlock_env,
    is_locked,
    get_lock_info,
)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def test_lock_creates_lock_file(env_file):
    lock_env(env_file)
    lock_file = env_file.parent / f".{env_file.name}.lock"
    assert lock_file.exists()


def test_lock_returns_lock_info(env_file):
    info = lock_env(env_file, reason="deploy")
    assert isinstance(info, LockInfo)
    assert info.reason == "deploy"
    assert info.locked_by != ""


def test_lock_missing_env_raises(tmp_path):
    with pytest.raises(LockError, match="not found"):
        lock_env(tmp_path / "missing.env")


def test_lock_already_locked_raises(env_file):
    lock_env(env_file)
    with pytest.raises(LockError, match="already locked"):
        lock_env(env_file)


def test_unlock_removes_lock_file(env_file):
    lock_env(env_file)
    unlock_env(env_file)
    lock_file = env_file.parent / f".{env_file.name}.lock"
    assert not lock_file.exists()


def test_unlock_returns_info(env_file):
    lock_env(env_file, reason="test")
    info = unlock_env(env_file)
    assert isinstance(info, LockInfo)
    assert info.reason == "test"


def test_unlock_not_locked_raises(env_file):
    with pytest.raises(LockError, match="not locked"):
        unlock_env(env_file)


def test_is_locked_true(env_file):
    lock_env(env_file)
    assert is_locked(env_file) is True


def test_is_locked_false(env_file):
    assert is_locked(env_file) is False


def test_get_lock_info_none_when_unlocked(env_file):
    assert get_lock_info(env_file) is None


def test_get_lock_info_returns_info(env_file):
    lock_env(env_file, reason="ci")
    info = get_lock_info(env_file)
    assert info is not None
    assert info.reason == "ci"
    assert "T" in info.locked_at  # ISO timestamp
