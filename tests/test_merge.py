"""Tests for envlock.merge."""

import pytest

from envlock.merge import (
    MergeConflictError,
    MergeResult,
    merge_env_files,
    merge_envs,
)


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
OTHER = {"DB_HOST": "remotehost", "DB_PORT": "5432", "API_KEY": "xyz"}


def test_merge_no_conflict_same_values():
    result = merge_envs({"A": "1"}, {"A": "1"})
    assert result.merged == {"A": "1"}
    assert result.conflicts == []
    assert result.has_conflicts is False


def test_merge_added_key():
    result = merge_envs({"A": "1"}, {"A": "1", "B": "2"})
    assert result.merged["B"] == "2"
    assert "B" in result.added


def test_merge_removed_key():
    result = merge_envs({"A": "1", "B": "2"}, {"A": "1"})
    assert "B" in result.merged  # base wins, key preserved
    assert "B" in result.removed


def test_merge_conflict_strategy_ours():
    result = merge_envs(BASE, OTHER, strategy="ours")
    assert result.merged["DB_HOST"] == "localhost"
    assert result.has_conflicts is True
    assert any(k == "DB_HOST" for k, _, _ in result.conflicts)


def test_merge_conflict_strategy_theirs():
    result = merge_envs(BASE, OTHER, strategy="theirs")
    assert result.merged["DB_HOST"] == "remotehost"


def test_merge_conflict_strategy_error():
    with pytest.raises(MergeConflictError, match="DB_HOST"):
        merge_envs(BASE, OTHER, strategy="error")


def test_merge_invalid_strategy():
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge_envs(BASE, OTHER, strategy="magic")


def test_merge_summary_no_changes():
    result = merge_envs({"A": "1"}, {"A": "1"})
    assert result.summary() == "No changes."


def test_merge_summary_with_changes():
    result = merge_envs(BASE, OTHER, strategy="ours")
    summary = result.summary()
    assert "API_KEY" in summary
    assert "SECRET" in summary
    assert "DB_HOST" in summary


def test_merge_env_files(tmp_path):
    base_file = tmp_path / ".env.base"
    other_file = tmp_path / ".env.other"
    base_file.write_text("HOST=localhost\nPORT=5432\n")
    other_file.write_text("HOST=remotehost\nPORT=5432\nDEBUG=true\n")

    result = merge_env_files(str(base_file), str(other_file), strategy="theirs")
    assert result.merged["HOST"] == "remotehost"
    assert result.merged["DEBUG"] == "true"
    assert result.merged["PORT"] == "5432"


def test_merge_env_files_not_found(tmp_path):
    from envlock.snapshot import parse_env_file
    with pytest.raises(FileNotFoundError):
        merge_env_files(str(tmp_path / "missing.env"), str(tmp_path / "other.env"))
