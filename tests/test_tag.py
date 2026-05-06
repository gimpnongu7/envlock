"""Tests for envlock.tag."""

import pytest
from pathlib import Path

from envlock.tag import (
    TagError,
    add_tag,
    remove_tag,
    resolve_tag,
    list_tags,
    find_tags_for_snapshot,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_add_and_resolve_tag(snapshot_dir):
    add_tag(snapshot_dir, "snap-001", "stable")
    assert resolve_tag(snapshot_dir, "stable") == "snap-001"


def test_add_duplicate_tag_raises(snapshot_dir):
    add_tag(snapshot_dir, "snap-001", "stable")
    with pytest.raises(TagError, match="already exists"):
        add_tag(snapshot_dir, "snap-002", "stable")


def test_remove_tag(snapshot_dir):
    add_tag(snapshot_dir, "snap-001", "stable")
    removed_id = remove_tag(snapshot_dir, "stable")
    assert removed_id == "snap-001"
    with pytest.raises(TagError):
        resolve_tag(snapshot_dir, "stable")


def test_remove_missing_tag_raises(snapshot_dir):
    with pytest.raises(TagError, match="not found"):
        remove_tag(snapshot_dir, "ghost")


def test_resolve_missing_tag_raises(snapshot_dir):
    with pytest.raises(TagError, match="not found"):
        resolve_tag(snapshot_dir, "nope")


def test_list_tags_empty(snapshot_dir):
    assert list_tags(snapshot_dir) == []


def test_list_tags_sorted(snapshot_dir):
    add_tag(snapshot_dir, "snap-002", "beta")
    add_tag(snapshot_dir, "snap-001", "alpha")
    result = list_tags(snapshot_dir)
    assert [r["tag"] for r in result] == ["alpha", "beta"]


def test_find_tags_for_snapshot(snapshot_dir):
    add_tag(snapshot_dir, "snap-001", "v1")
    add_tag(snapshot_dir, "snap-001", "release")
    add_tag(snapshot_dir, "snap-002", "v2")
    tags = find_tags_for_snapshot(snapshot_dir, "snap-001")
    assert set(tags) == {"v1", "release"}


def test_find_tags_no_match(snapshot_dir):
    add_tag(snapshot_dir, "snap-001", "v1")
    assert find_tags_for_snapshot(snapshot_dir, "snap-999") == []


def test_tags_persist_across_calls(snapshot_dir):
    add_tag(snapshot_dir, "snap-abc", "persist-me")
    # simulate fresh call by re-importing path logic
    assert resolve_tag(snapshot_dir, "persist-me") == "snap-abc"
