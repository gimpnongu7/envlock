"""Tests for envlock.cli_digest."""

import argparse
import pytest
from pathlib import Path

from envlock.digest import record_digest
from envlock.cli_digest import (
    cmd_digest_record,
    cmd_digest_verify,
    cmd_digest_show,
    cmd_digest_list,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDEBUG=true\n")
    return p


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"snapshot_dir": "", "env_file": "", "snapshot_id": "", "algorithm": "sha256"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_digest_record_prints_confirmation(snapshot_dir, env_file, capsys):
    ns = _ns(snapshot_dir=str(snapshot_dir), env_file=str(env_file), snapshot_id="snap-1")
    cmd_digest_record(ns)
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "sha256" in out


def test_cmd_digest_record_missing_env_exits(snapshot_dir, tmp_path):
    ns = _ns(snapshot_dir=str(snapshot_dir), env_file=str(tmp_path / "missing.env"), snapshot_id="snap-1")
    with pytest.raises(SystemExit) as exc:
        cmd_digest_record(ns)
    assert exc.value.code == 1


def test_cmd_digest_verify_ok(snapshot_dir, env_file, capsys):
    content = env_file.read_text()
    record_digest(snapshot_dir, "snap-2", content)
    ns = _ns(snapshot_dir=str(snapshot_dir), env_file=str(env_file), snapshot_id="snap-2")
    cmd_digest_verify(ns)
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_digest_verify_tampered_exits(snapshot_dir, env_file):
    record_digest(snapshot_dir, "snap-3", "ORIGINAL=1\n")
    # env_file has different content
    ns = _ns(snapshot_dir=str(snapshot_dir), env_file=str(env_file), snapshot_id="snap-3")
    with pytest.raises(SystemExit) as exc:
        cmd_digest_verify(ns)
    assert exc.value.code == 2


def test_cmd_digest_verify_no_record_exits(snapshot_dir, env_file):
    ns = _ns(snapshot_dir=str(snapshot_dir), env_file=str(env_file), snapshot_id="ghost")
    with pytest.raises(SystemExit) as exc:
        cmd_digest_verify(ns)
    assert exc.value.code == 1


def test_cmd_digest_show_prints_record(snapshot_dir, capsys):
    record_digest(snapshot_dir, "snap-4", "X=1\n")
    ns = _ns(snapshot_dir=str(snapshot_dir), snapshot_id="snap-4")
    cmd_digest_show(ns)
    out = capsys.readouterr().out
    assert "snap-4" in out
    assert "sha256" in out


def test_cmd_digest_show_missing_exits(snapshot_dir):
    ns = _ns(snapshot_dir=str(snapshot_dir), snapshot_id="nobody")
    with pytest.raises(SystemExit) as exc:
        cmd_digest_show(ns)
    assert exc.value.code == 1


def test_cmd_digest_list_empty(snapshot_dir, capsys):
    ns = _ns(snapshot_dir=str(snapshot_dir))
    cmd_digest_list(ns)
    assert "No digests" in capsys.readouterr().out


def test_cmd_digest_list_shows_entries(snapshot_dir, capsys):
    record_digest(snapshot_dir, "snap-a", "A=1\n")
    record_digest(snapshot_dir, "snap-b", "B=2\n")
    ns = _ns(snapshot_dir=str(snapshot_dir))
    cmd_digest_list(ns)
    out = capsys.readouterr().out
    assert "snap-a" in out
    assert "snap-b" in out
