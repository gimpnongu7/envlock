"""Git hook helpers — install/uninstall envlock hooks into a repo."""

from __future__ import annotations

import os
import stat
from pathlib import Path

HOOK_NAMES = ("post-checkout", "post-merge")

_HOOK_BODY = """\
#!/bin/sh
# envlock auto-snapshot hook
envlock snapshot --label auto-{hook_name} "$@" || true
"""


class HookError(Exception):
    pass


def _hooks_dir(repo_root: Path) -> Path:
    git_dir = repo_root / ".git"
    if not git_dir.is_dir():
        raise HookError(f"No .git directory found in {repo_root}")
    return git_dir / "hooks"


def install_hooks(repo_root: Path, hook_names: tuple[str, ...] = HOOK_NAMES) -> list[Path]:
    """Install envlock snapshot hooks. Returns list of installed hook paths."""
    hooks_dir = _hooks_dir(repo_root)
    hooks_dir.mkdir(exist_ok=True)
    installed: list[Path] = []

    for name in hook_names:
        hook_path = hooks_dir / name
        body = _HOOK_BODY.format(hook_name=name)

        if hook_path.exists():
            existing = hook_path.read_text()
            if "envlock" in existing:
                # already managed by us — overwrite cleanly
                pass
            else:
                raise HookError(
                    f"Hook {hook_path} already exists and is not managed by envlock. "
                    "Remove it manually first."
                )

        hook_path.write_text(body)
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        installed.append(hook_path)

    return installed


def uninstall_hooks(repo_root: Path, hook_names: tuple[str, ...] = HOOK_NAMES) -> list[Path]:
    """Remove envlock-managed hooks. Returns list of removed hook paths."""
    hooks_dir = _hooks_dir(repo_root)
    removed: list[Path] = []

    for name in hook_names:
        hook_path = hooks_dir / name
        if not hook_path.exists():
            continue
        content = hook_path.read_text()
        if "envlock" not in content:
            raise HookError(
                f"Hook {hook_path} is not managed by envlock — refusing to remove it."
            )
        hook_path.unlink()
        removed.append(hook_path)

    return removed


def hooks_status(repo_root: Path, hook_names: tuple[str, ...] = HOOK_NAMES) -> dict[str, bool]:
    """Return a dict mapping hook name -> True if envlock hook is installed."""
    hooks_dir = _hooks_dir(repo_root)
    status: dict[str, bool] = {}
    for name in hook_names:
        hook_path = hooks_dir / name
        status[name] = hook_path.exists() and "envlock" in hook_path.read_text()
    return status
