"""Tests for envlock.hooks."""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from envlock.hooks import (
    HookError,
    HOOK_NAMES,
    install_hooks,
    uninstall_hooks,
    hooks_status,
)


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    return tmp_path


def test_install_creates_hook_files(fake_repo):
    installed = install_hooks(fake_repo)
    assert len(installed) == len(HOOK_NAMES)
    for path in installed:
        assert path.exists()


def test_installed_hooks_are_executable(fake_repo):
    install_hooks(fake_repo)
    for name in HOOK_NAMES:
        hook = fake_repo / ".git" / "hooks" / name
        assert hook.stat().st_mode & stat.S_IEXEC


def test_installed_hook_contains_envlock(fake_repo):
    install_hooks(fake_repo)
    for name in HOOK_NAMES:
        content = (fake_repo / ".git" / "hooks" / name).read_text()
        assert "envlock" in content
        assert name in content


def test_install_idempotent_for_managed_hooks(fake_repo):
    install_hooks(fake_repo)
    # second call should succeed without error
    install_hooks(fake_repo)


def test_install_raises_if_foreign_hook_exists(fake_repo):
    hook_path = fake_repo / ".git" / "hooks" / "post-checkout"
    hook_path.write_text("#!/bin/sh\necho hello\n")
    with pytest.raises(HookError, match="not managed by envlock"):
        install_hooks(fake_repo, hook_names=("post-checkout",))


def test_uninstall_removes_hooks(fake_repo):
    install_hooks(fake_repo)
    removed = uninstall_hooks(fake_repo)
    assert len(removed) == len(HOOK_NAMES)
    for path in removed:
        assert not path.exists()


def test_uninstall_skips_missing_hooks(fake_repo):
    # nothing installed — should return empty list
    removed = uninstall_hooks(fake_repo)
    assert removed == []


def test_uninstall_raises_if_foreign_hook(fake_repo):
    hook_path = fake_repo / ".git" / "hooks" / "post-merge"
    hook_path.write_text("#!/bin/sh\nsome other tool\n")
    with pytest.raises(HookError, match="not managed by envlock"):
        uninstall_hooks(fake_repo, hook_names=("post-merge",))


def test_hooks_status_all_installed(fake_repo):
    install_hooks(fake_repo)
    status = hooks_status(fake_repo)
    assert all(status.values())


def test_hooks_status_none_installed(fake_repo):
    status = hooks_status(fake_repo)
    assert not any(status.values())


def test_no_git_dir_raises(tmp_path):
    with pytest.raises(HookError, match="No .git directory"):
        install_hooks(tmp_path)
