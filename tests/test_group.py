import pytest
from pathlib import Path
from envlock.group import (
    GroupError,
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    delete_group,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_add_creates_group(snapshot_dir):
    add_to_group(snapshot_dir, "staging", "snap-001")
    assert "staging" in list_groups(snapshot_dir)


def test_add_no_duplicates(snapshot_dir):
    add_to_group(snapshot_dir, "staging", "snap-001")
    add_to_group(snapshot_dir, "staging", "snap-001")
    assert get_group_members(snapshot_dir, "staging").count("snap-001") == 1


def test_add_multiple_members(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap-001")
    add_to_group(snapshot_dir, "prod", "snap-002")
    members = get_group_members(snapshot_dir, "prod")
    assert "snap-001" in members
    assert "snap-002" in members


def test_add_blank_name_raises(snapshot_dir):
    with pytest.raises(GroupError, match="blank"):
        add_to_group(snapshot_dir, "  ", "snap-001")


def test_list_groups_empty(snapshot_dir):
    assert list_groups(snapshot_dir) == []


def test_list_groups_sorted(snapshot_dir):
    add_to_group(snapshot_dir, "zebra", "snap-001")
    add_to_group(snapshot_dir, "alpha", "snap-002")
    assert list_groups(snapshot_dir) == ["alpha", "zebra"]


def test_get_members_missing_group_raises(snapshot_dir):
    with pytest.raises(GroupError, match="does not exist"):
        get_group_members(snapshot_dir, "nope")


def test_remove_from_group(snapshot_dir):
    add_to_group(snapshot_dir, "dev", "snap-001")
    add_to_group(snapshot_dir, "dev", "snap-002")
    remove_from_group(snapshot_dir, "dev", "snap-001")
    assert "snap-001" not in get_group_members(snapshot_dir, "dev")


def test_remove_last_member_deletes_group(snapshot_dir):
    add_to_group(snapshot_dir, "solo", "snap-001")
    remove_from_group(snapshot_dir, "solo", "snap-001")
    assert "solo" not in list_groups(snapshot_dir)


def test_remove_missing_snapshot_raises(snapshot_dir):
    add_to_group(snapshot_dir, "dev", "snap-001")
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group(snapshot_dir, "dev", "snap-999")


def test_remove_missing_group_raises(snapshot_dir):
    with pytest.raises(GroupError, match="does not exist"):
        remove_from_group(snapshot_dir, "ghost", "snap-001")


def test_delete_group(snapshot_dir):
    add_to_group(snapshot_dir, "temp", "snap-001")
    delete_group(snapshot_dir, "temp")
    assert "temp" not in list_groups(snapshot_dir)


def test_delete_missing_group_raises(snapshot_dir):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group(snapshot_dir, "ghost")
