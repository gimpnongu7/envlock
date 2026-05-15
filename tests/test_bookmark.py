"""Tests for envlock.bookmark."""

import pytest
from pathlib import Path

from envlock.bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    update_bookmark,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_add_and_resolve_bookmark(snapshot_dir):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    assert resolve_bookmark(snapshot_dir, "stable") == "snap_001"


def test_add_duplicate_raises(snapshot_dir):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    with pytest.raises(BookmarkError, match="already exists"):
        add_bookmark(snapshot_dir, "stable", "snap_002")


def test_add_blank_name_raises(snapshot_dir):
    with pytest.raises(BookmarkError, match="blank"):
        add_bookmark(snapshot_dir, "   ", "snap_001")


def test_remove_bookmark(snapshot_dir):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    remove_bookmark(snapshot_dir, "stable")
    with pytest.raises(BookmarkError):
        resolve_bookmark(snapshot_dir, "stable")


def test_remove_missing_raises(snapshot_dir):
    with pytest.raises(BookmarkError, match="not found"):
        remove_bookmark(snapshot_dir, "ghost")


def test_resolve_missing_raises(snapshot_dir):
    with pytest.raises(BookmarkError, match="not found"):
        resolve_bookmark(snapshot_dir, "nope")


def test_list_bookmarks_empty(snapshot_dir):
    assert list_bookmarks(snapshot_dir) == []


def test_list_bookmarks_sorted(snapshot_dir):
    add_bookmark(snapshot_dir, "zulu", "snap_z")
    add_bookmark(snapshot_dir, "alpha", "snap_a")
    names = [b["name"] for b in list_bookmarks(snapshot_dir)]
    assert names == ["alpha", "zulu"]


def test_update_bookmark(snapshot_dir):
    add_bookmark(snapshot_dir, "stable", "snap_001")
    update_bookmark(snapshot_dir, "stable", "snap_002")
    assert resolve_bookmark(snapshot_dir, "stable") == "snap_002"


def test_update_missing_raises(snapshot_dir):
    with pytest.raises(BookmarkError, match="not found"):
        update_bookmark(snapshot_dir, "ghost", "snap_001")


def test_bookmarks_persist_across_calls(snapshot_dir):
    add_bookmark(snapshot_dir, "prod", "snap_prod")
    add_bookmark(snapshot_dir, "dev", "snap_dev")
    result = {b["name"]: b["snapshot_id"] for b in list_bookmarks(snapshot_dir)}
    assert result == {"prod": "snap_prod", "dev": "snap_dev"}
