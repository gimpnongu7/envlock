"""Tests for envlock.cli_lock module."""

import sys
import pytest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from envlock.cli_lock import cmd_lock, cmd_unlock, cmd_lock_status
from envlock.lock import lock_env


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def _ns(**kwargs):
    return Namespace(**kwargs)


def test_cmd_lock_prints_confirmation(env_file, capsys):
    cmd_lock(_ns(env_file=str(env_file), reason=None))
    out = capsys.readouterr().out
    assert "Locked" in out
    assert env_file.name in out


def test_cmd_lock_with_reason(env_file, capsys):
    cmd_lock(_ns(env_file=str(env_file), reason="deploy"))
    out = capsys.readouterr().out
    assert "deploy" in out


def test_cmd_lock_missing_env_exits(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_lock(_ns(env_file=str(tmp_path / "missing.env"), reason=None))
    assert exc_info.value.code == 1


def test_cmd_lock_already_locked_exits(env_file):
    lock_env(env_file)
    with pytest.raises(SystemExit) as exc_info:
        cmd_lock(_ns(env_file=str(env_file), reason=None))
    assert exc_info.value.code == 1


def test_cmd_unlock_prints_confirmation(env_file, capsys):
    lock_env(env_file)
    cmd_unlock(_ns(env_file=str(env_file)))
    out = capsys.readouterr().out
    assert "Unlocked" in out


def test_cmd_unlock_not_locked_exits(env_file):
    with pytest.raises(SystemExit) as exc_info:
        cmd_unlock(_ns(env_file=str(env_file)))
    assert exc_info.value.code == 1


def test_cmd_lock_status_unlocked(env_file, capsys):
    cmd_lock_status(_ns(env_file=str(env_file)))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_cmd_lock_status_locked(env_file, capsys):
    lock_env(env_file, reason="freeze")
    cmd_lock_status(_ns(env_file=str(env_file)))
    out = capsys.readouterr().out
    assert "locked" in out
    assert "freeze" in out


def test_cmd_lock_status_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_lock_status(_ns(env_file=str(tmp_path / "ghost.env")))
    assert exc_info.value.code == 1
