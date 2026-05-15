"""Tests for envlock.classify."""

import pytest
from pathlib import Path
from envlock.classify import (
    classify_snapshot,
    get_class,
    list_by_class,
    remove_class,
    ClassifyError,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_classify_assigns_label(snapshot_dir):
    result = classify_snapshot(snapshot_dir, "snap-001", "production")
    assert result.snapshot_id == "snap-001"
    assert result.env_class == "production"


def test_classify_normalises_to_lowercase(snapshot_dir):
    result = classify_snapshot(snapshot_dir, "snap-002", "  Staging  ")
    assert result.env_class == "staging"


def test_classify_str_representation(snapshot_dir):
    result = classify_snapshot(snapshot_dir, "snap-003", "dev")
    assert str(result) == "snap-003 -> dev"


def test_get_class_returns_label(snapshot_dir):
    classify_snapshot(snapshot_dir, "snap-010", "dev")
    assert get_class(snapshot_dir, "snap-010") == "dev"


def test_get_class_returns_none_when_unclassified(snapshot_dir):
    assert get_class(snapshot_dir, "nonexistent") is None


def test_list_by_class_returns_matching(snapshot_dir):
    classify_snapshot(snapshot_dir, "snap-a", "dev")
    classify_snapshot(snapshot_dir, "snap-b", "prod")
    classify_snapshot(snapshot_dir, "snap-c", "dev")
    result = list_by_class(snapshot_dir, "dev")
    assert sorted(result) == ["snap-a", "snap-c"]


def test_list_by_class_empty_when_none_match(snapshot_dir):
    classify_snapshot(snapshot_dir, "snap-x", "staging")
    assert list_by_class(snapshot_dir, "prod") == []


def test_remove_class_deletes_label(snapshot_dir):
    classify_snapshot(snapshot_dir, "snap-del", "dev")
    remove_class(snapshot_dir, "snap-del")
    assert get_class(snapshot_dir, "snap-del") is None


def test_remove_class_missing_raises(snapshot_dir):
    with pytest.raises(ClassifyError, match="no classification"):
        remove_class(snapshot_dir, "ghost")


def test_classify_missing_dir_raises(tmp_path):
    missing = tmp_path / "no_such_dir"
    with pytest.raises(ClassifyError, match="not found"):
        classify_snapshot(missing, "snap-x", "dev")


def test_classify_blank_class_raises(snapshot_dir):
    with pytest.raises(ClassifyError, match="blank"):
        classify_snapshot(snapshot_dir, "snap-y", "   ")


def test_overwrite_classification(snapshot_dir):
    classify_snapshot(snapshot_dir, "snap-z", "dev")
    classify_snapshot(snapshot_dir, "snap-z", "prod")
    assert get_class(snapshot_dir, "snap-z") == "prod"
