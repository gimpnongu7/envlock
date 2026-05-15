"""Tests for envlock.namespace."""

from __future__ import annotations

import pytest
from pathlib import Path

from envlock.namespace import (
    NamespaceError,
    assign_namespace,
    remove_from_namespace,
    list_namespaces,
    get_namespace_members,
    find_namespace,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_assign_creates_namespace(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "production")
    assert "production" in list_namespaces(snapshot_dir)


def test_assign_adds_member(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "staging")
    assert "snap-001" in get_namespace_members(snapshot_dir, "staging")


def test_assign_no_duplicates(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "staging")
    assign_namespace(snapshot_dir, "snap-001", "staging")
    assert get_namespace_members(snapshot_dir, "staging").count("snap-001") == 1


def test_assign_blank_namespace_raises(snapshot_dir):
    with pytest.raises(NamespaceError, match="blank"):
        assign_namespace(snapshot_dir, "snap-001", "   ")


def test_assign_multiple_members(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "dev")
    assign_namespace(snapshot_dir, "snap-002", "dev")
    members = get_namespace_members(snapshot_dir, "dev")
    assert "snap-001" in members
    assert "snap-002" in members


def test_remove_from_namespace(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "dev")
    remove_from_namespace(snapshot_dir, "snap-001", "dev")
    assert "dev" not in list_namespaces(snapshot_dir)


def test_remove_missing_namespace_raises(snapshot_dir):
    with pytest.raises(NamespaceError, match="does not exist"):
        remove_from_namespace(snapshot_dir, "snap-001", "ghost")


def test_remove_missing_member_raises(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "dev")
    with pytest.raises(NamespaceError, match="not in namespace"):
        remove_from_namespace(snapshot_dir, "snap-999", "dev")


def test_list_namespaces_empty(snapshot_dir):
    assert list_namespaces(snapshot_dir) == []


def test_list_namespaces_sorted(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-001", "zebra")
    assign_namespace(snapshot_dir, "snap-002", "alpha")
    assert list_namespaces(snapshot_dir) == ["alpha", "zebra"]


def test_get_members_missing_namespace_raises(snapshot_dir):
    with pytest.raises(NamespaceError, match="does not exist"):
        get_namespace_members(snapshot_dir, "nope")


def test_find_namespace_returns_name(snapshot_dir):
    assign_namespace(snapshot_dir, "snap-007", "ci")
    assert find_namespace(snapshot_dir, "snap-007") == "ci"


def test_find_namespace_returns_none_when_unassigned(snapshot_dir):
    assert find_namespace(snapshot_dir, "snap-999") is None
