"""Tests for envlock.stash."""

import pytest
from pathlib import Path

from envlock.stash import (
    StashError,
    stash_push,
    stash_pop,
    stash_list,
    stash_drop,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("KEY=value\nOTHER=123\n")
    return f


@pytest.fixture
def stash_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_stash_push_creates_entry(env_file, stash_dir):
    entry_id = stash_push(env_file, stash_dir)
    assert entry_id == "stash@{0}"
    entries = stash_list(stash_dir)
    assert len(entries) == 1
    assert entries[0]["id"] == "stash@{0}"


def test_stash_push_with_message(env_file, stash_dir):
    stash_push(env_file, stash_dir, message="WIP: testing")
    entries = stash_list(stash_dir)
    assert entries[0]["message"] == "WIP: testing"


def test_stash_push_missing_env_raises(stash_dir, tmp_path):
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(StashError, match="not found"):
        stash_push(missing, stash_dir)


def test_stash_pop_restores_content(env_file, stash_dir):
    original = env_file.read_text()
    stash_push(env_file, stash_dir)
    env_file.write_text("CHANGED=yes\n")
    stash_pop(env_file, stash_dir)
    assert env_file.read_text() == original


def test_stash_pop_removes_entry(env_file, stash_dir):
    stash_push(env_file, stash_dir)
    stash_pop(env_file, stash_dir)
    assert stash_list(stash_dir) == []


def test_stash_pop_empty_raises(env_file, stash_dir):
    with pytest.raises(StashError, match="empty"):
        stash_pop(env_file, stash_dir)


def test_stash_list_newest_first(env_file, stash_dir):
    stash_push(env_file, stash_dir, message="first")
    env_file.write_text("SECOND=1\n")
    stash_push(env_file, stash_dir, message="second")
    entries = stash_list(stash_dir)
    assert entries[0]["message"] == "second"
    assert entries[1]["message"] == "first"


def test_stash_drop_removes_without_restoring(env_file, stash_dir):
    stash_push(env_file, stash_dir)
    env_file.write_text("CHANGED=yes\n")
    stash_drop(stash_dir, index_pos=0)
    assert env_file.read_text() == "CHANGED=yes\n"
    assert stash_list(stash_dir) == []


def test_stash_drop_invalid_index_raises(env_file, stash_dir):
    stash_push(env_file, stash_dir)
    with pytest.raises(StashError, match="no stash entry"):
        stash_drop(stash_dir, index_pos=5)


def test_stash_drop_empty_raises(stash_dir):
    with pytest.raises(StashError, match="empty"):
        stash_drop(stash_dir)
