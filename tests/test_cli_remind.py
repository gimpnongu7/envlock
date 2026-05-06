"""Tests for envlock.cli_remind."""

import argparse
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from envlock.cli_remind import add_remind_subparser, cmd_remind
from envlock.remind import ReminderStatus


def _ns(**kwargs):
    defaults = dict(
        env_file=".env",
        snapshot_dir=".envlock",
        max_age=86400,
        exit_code=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _stale_status(env_file):
    return ReminderStatus(
        env_path=Path(env_file),
        last_snapshot_ts=None,
        env_mtime=0.0,
        stale=True,
        message="No snapshot found — consider running `envlock snapshot`.",
    )


def _fresh_status(env_file):
    return ReminderStatus(
        env_path=Path(env_file),
        last_snapshot_ts=1000.0,
        env_mtime=900.0,
        stale=False,
        message="Snapshot is up to date.",
    )


def test_cmd_remind_prints_message(capsys):
    with patch("envlock.cli_remind.check_reminder", return_value=_fresh_status(".env")):
        cmd_remind(_ns())
    out = capsys.readouterr().out
    assert "up to date" in out


def test_cmd_remind_stale_prints_warning(capsys):
    with patch("envlock.cli_remind.check_reminder", return_value=_stale_status(".env")):
        cmd_remind(_ns())
    out = capsys.readouterr().out
    assert "No snapshot" in out


def test_cmd_remind_exit_code_on_stale():
    with patch("envlock.cli_remind.check_reminder", return_value=_stale_status(".env")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_remind(_ns(exit_code=True))
    assert exc_info.value.code == 2


def test_cmd_remind_no_exit_code_when_fresh():
    with patch("envlock.cli_remind.check_reminder", return_value=_fresh_status(".env")):
        cmd_remind(_ns(exit_code=True))  # should NOT raise


def test_cmd_remind_error_exits(capsys):
    from envlock.remind import RemindError
    with patch("envlock.cli_remind.check_reminder", side_effect=RemindError("oops")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_remind(_ns())
    assert exc_info.value.code == 1
    assert "oops" in capsys.readouterr().err


def test_add_remind_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_remind_subparser(subs)
    args = parser.parse_args(["remind", "--max-age", "3600", "--exit-code"])
    assert args.max_age == 3600
    assert args.exit_code is True
