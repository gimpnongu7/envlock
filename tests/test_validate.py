"""Tests for envlock.validate."""

import pytest
from pathlib import Path

from envlock.validate import validate_env, ValidationError


@pytest.fixture
def tmp_env(tmp_path: Path):
    """Write a helper that creates a named file and returns its path."""
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def test_valid_env_matches_template(tmp_env):
    template = tmp_env("template.env", "DB_HOST=\nDB_PORT=\nSECRET_KEY=\n")
    env = tmp_env(".env", "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    result = validate_env(env, template)
    assert result.is_valid
    assert result.summary() == "OK — env file matches template."


def test_missing_key_detected(tmp_env):
    template = tmp_env("template.env", "DB_HOST=\nDB_PORT=\nSECRET_KEY=\n")
    env = tmp_env(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = validate_env(env, template)
    assert not result.is_valid
    assert "SECRET_KEY" in result.missing


def test_extra_key_detected(tmp_env):
    template = tmp_env("template.env", "DB_HOST=\n")
    env = tmp_env(".env", "DB_HOST=localhost\nUNKNOWN=oops\n")
    result = validate_env(env, template)
    assert "UNKNOWN" in result.extra


def test_extra_key_allowed(tmp_env):
    template = tmp_env("template.env", "DB_HOST=\n")
    env = tmp_env(".env", "DB_HOST=localhost\nUNKNOWN=oops\n")
    result = validate_env(env, template, allow_extra=True)
    assert result.extra == []


def test_empty_value_flagged(tmp_env):
    template = tmp_env("template.env", "API_KEY=\n")
    env = tmp_env(".env", "API_KEY=\n")
    result = validate_env(env, template, check_empty=True)
    assert "API_KEY" in result.empty
    assert not result.is_valid


def test_empty_value_not_flagged_when_disabled(tmp_env):
    template = tmp_env("template.env", "API_KEY=\n")
    env = tmp_env(".env", "API_KEY=\n")
    result = validate_env(env, template, check_empty=False)
    assert result.empty == []


def test_missing_env_file_raises(tmp_env):
    template = tmp_env("template.env", "DB_HOST=\n")
    with pytest.raises(ValidationError, match="File not found"):
        validate_env(Path("/no/such/.env"), template)


def test_missing_template_file_raises(tmp_env):
    env = tmp_env(".env", "DB_HOST=localhost\n")
    with pytest.raises(ValidationError, match="File not found"):
        validate_env(env, Path("/no/such/template.env"))


def test_summary_lists_all_issues(tmp_env):
    template = tmp_env("template.env", "A=\nB=\n")
    env = tmp_env(".env", "B=\nC=value\n")
    result = validate_env(env, template)
    summary = result.summary()
    assert "Missing" in summary
    assert "A" in summary
    assert "Extra" in summary
    assert "C" in summary
