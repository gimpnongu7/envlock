"""Tests for envlock.profile."""

import pytest
from pathlib import Path

from envlock.profile import (
    ProfileError,
    add_snapshot_to_profile,
    remove_snapshot_from_profile,
    list_profiles,
    get_profile_snapshots,
    delete_profile,
    load_profiles,
)


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_snapshot_creates_profile(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "snap-001")
    profiles = load_profiles(base_dir)
    assert "dev" in profiles
    assert "snap-001" in profiles["dev"]


def test_add_snapshot_no_duplicates(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "snap-001")
    add_snapshot_to_profile(base_dir, "dev", "snap-001")
    assert load_profiles(base_dir)["dev"].count("snap-001") == 1


def test_add_multiple_snapshots_to_profile(base_dir):
    add_snapshot_to_profile(base_dir, "staging", "snap-a")
    add_snapshot_to_profile(base_dir, "staging", "snap-b")
    snaps = get_profile_snapshots(base_dir, "staging")
    assert snaps == ["snap-a", "snap-b"]


def test_list_profiles_empty(base_dir):
    assert list_profiles(base_dir) == []


def test_list_profiles_returns_names(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "s1")
    add_snapshot_to_profile(base_dir, "prod", "s2")
    names = list_profiles(base_dir)
    assert set(names) == {"dev", "prod"}


def test_get_profile_snapshots_unknown_raises(base_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        get_profile_snapshots(base_dir, "ghost")


def test_remove_snapshot_from_profile(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "snap-x")
    remove_snapshot_from_profile(base_dir, "dev", "snap-x")
    assert get_profile_snapshots(base_dir, "dev") == []


def test_remove_snapshot_unknown_label_raises(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "snap-x")
    with pytest.raises(ProfileError, match="not found"):
        remove_snapshot_from_profile(base_dir, "dev", "missing")


def test_remove_snapshot_unknown_profile_raises(base_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        remove_snapshot_from_profile(base_dir, "nope", "snap-x")


def test_delete_profile(base_dir):
    add_snapshot_to_profile(base_dir, "dev", "s1")
    delete_profile(base_dir, "dev")
    assert "dev" not in list_profiles(base_dir)


def test_delete_unknown_profile_raises(base_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        delete_profile(base_dir, "phantom")


def test_profiles_persist_across_calls(base_dir):
    add_snapshot_to_profile(base_dir, "ci", "snap-ci-1")
    # Simulate a fresh load
    profiles = load_profiles(base_dir)
    assert "ci" in profiles
    assert "snap-ci-1" in profiles["ci"]
