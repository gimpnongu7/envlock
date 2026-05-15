"""Tests for envlock.import_env."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envlock.import_env import (
    ImportError,
    import_and_snapshot,
    import_from_json,
    import_from_shell_env,
    _parse_dotenv_text,
)


# ---------------------------------------------------------------------------
# _parse_dotenv_text
# ---------------------------------------------------------------------------

def test_parse_dotenv_text_basic():
    text = "KEY=value\nOTHER=123\n"
    assert _parse_dotenv_text(text) == {"KEY": "value", "OTHER": "123"}


def test_parse_dotenv_text_skips_comments():
    text = "# comment\nKEY=val\n"
    assert _parse_dotenv_text(text) == {"KEY": "val"}


def test_parse_dotenv_text_skips_blank_lines():
    text = "\nKEY=val\n\n"
    assert _parse_dotenv_text(text) == {"KEY": "val"}


def test_parse_dotenv_text_skips_no_equals():
    text = "BADLINE\nGOOD=ok\n"
    assert _parse_dotenv_text(text) == {"GOOD": "ok"}


# ---------------------------------------------------------------------------
# import_from_json
# ---------------------------------------------------------------------------

def test_import_from_json_valid(tmp_path):
    src = tmp_path / "vars.json"
    src.write_text(json.dumps({"A": "1", "B": "2"}), encoding="utf-8")
    result = import_from_json(src)
    assert result == {"A": "1", "B": "2"}


def test_import_from_json_missing_file(tmp_path):
    with pytest.raises(ImportError, match="not found"):
        import_from_json(tmp_path / "nope.json")


def test_import_from_json_invalid_json(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("not-json", encoding="utf-8")
    with pytest.raises(ImportError, match="Invalid JSON"):
        import_from_json(src)


def test_import_from_json_non_object(tmp_path):
    src = tmp_path / "arr.json"
    src.write_text(json.dumps(["a", "b"]), encoding="utf-8")
    with pytest.raises(ImportError, match="Expected a JSON object"):
        import_from_json(src)


def test_import_from_json_non_string_values(tmp_path):
    src = tmp_path / "mixed.json"
    src.write_text(json.dumps({"KEY": 42}), encoding="utf-8")
    with pytest.raises(ImportError, match="Non-string values"):
        import_from_json(src)


# ---------------------------------------------------------------------------
# import_from_shell_env
# ---------------------------------------------------------------------------

def test_import_from_shell_env_all():
    result = import_from_shell_env()
    assert isinstance(result, dict)
    assert len(result) > 0


def test_import_from_shell_env_specific_keys(monkeypatch):
    monkeypatch.setenv("ENVLOCK_TEST_VAR", "hello")
    result = import_from_shell_env(keys=["ENVLOCK_TEST_VAR"])
    assert result == {"ENVLOCK_TEST_VAR": "hello"}


def test_import_from_shell_env_missing_key():
    with pytest.raises(ImportError, match="not found in environment"):
        import_from_shell_env(keys=["__ENVLOCK_DEFINITELY_MISSING__"])


# ---------------------------------------------------------------------------
# import_and_snapshot
# ---------------------------------------------------------------------------

def test_import_and_snapshot_creates_file(tmp_path):
    env_vars = {"FOO": "bar", "BAZ": "qux"}
    snap = import_and_snapshot(env_vars, tmp_path)
    assert snap.exists()
    assert snap.suffix == ".env"


def test_import_and_snapshot_no_tmp_leftover(tmp_path):
    import_and_snapshot({"X": "1"}, tmp_path)
    assert not (tmp_path / "_import_tmp.env").exists()


def test_import_and_snapshot_content(tmp_path):
    env_vars = {"HELLO": "world"}
    snap = import_and_snapshot(env_vars, tmp_path)
    content = snap.read_text(encoding="utf-8")
    assert "HELLO=world" in content
