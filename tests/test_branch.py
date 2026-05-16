"""Tests for envlock.branch."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envlock.branch import (
    BranchError,
    bind_snapshot,
    resolve_branch,
    unbind_branch,
    list_bindings,
    current_branch,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _mock_branch(name: str):
    return patch("envlock.branch.current_branch", return_value=name)


def test_current_branch_calls_git():
    import subprocess
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "main\n"
        mock_run.return_value.returncode = 0
        result = current_branch()
    assert result == "main"


def test_current_branch_raises_on_failure():
    import subprocess
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(128, "git")):
        with pytest.raises(BranchError, match="could not determine"):
            current_branch()


def test_bind_snapshot_creates_binding(snapshot_dir):
    with _mock_branch("feature/x"):
        branch = bind_snapshot(snapshot_dir, "snap-001")
    assert branch == "feature/x"
    data = json.loads((snapshot_dir / ".branch_bindings.json").read_text())
    assert data["feature/x"] == "snap-001"


def test_bind_snapshot_explicit_branch(snapshot_dir):
    bind_snapshot(snapshot_dir, "snap-002", branch="release")
    data = json.loads((snapshot_dir / ".branch_bindings.json").read_text())
    assert data["release"] == "snap-002"


def test_bind_snapshot_missing_dir(tmp_path):
    with pytest.raises(BranchError, match="snapshot directory not found"):
        bind_snapshot(tmp_path / "nope", "snap-001", branch="main")


def test_resolve_branch_returns_snapshot_id(snapshot_dir):
    bind_snapshot(snapshot_dir, "snap-abc", branch="dev")
    sid = resolve_branch(snapshot_dir, branch="dev")
    assert sid == "snap-abc"


def test_resolve_branch_missing_raises(snapshot_dir):
    with pytest.raises(BranchError, match="no snapshot bound to branch"):
        resolve_branch(snapshot_dir, branch="nonexistent")


def test_unbind_branch_removes_entry(snapshot_dir):
    bind_snapshot(snapshot_dir, "snap-xyz", branch="hotfix")
    unbind_branch(snapshot_dir, branch="hotfix")
    data = json.loads((snapshot_dir / ".branch_bindings.json").read_text())
    assert "hotfix" not in data


def test_unbind_missing_branch_raises(snapshot_dir):
    with pytest.raises(BranchError, match="no binding found"):
        unbind_branch(snapshot_dir, branch="ghost")


def test_list_bindings_empty(snapshot_dir):
    assert list_bindings(snapshot_dir) == {}


def test_list_bindings_returns_all(snapshot_dir):
    bind_snapshot(snapshot_dir, "s1", branch="main")
    bind_snapshot(snapshot_dir, "s2", branch="dev")
    result = list_bindings(snapshot_dir)
    assert result == {"main": "s1", "dev": "s2"}
