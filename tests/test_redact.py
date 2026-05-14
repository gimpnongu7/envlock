"""Tests for envlock.redact."""

from pathlib import Path

import pytest

from envlock.redact import (
    REDACT_PLACEHOLDER,
    RedactError,
    RedactResult,
    redact_env,
    redact_file,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PASSWORD=s3cr3t\nAPI_KEY=abc123\nDEBUG=true\n")
    return p


def test_redact_env_masks_password():
    env = {"DB_PASSWORD": "hunter2", "HOST": "localhost"}
    result = redact_env(env)
    assert result.redacted["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result.redacted["HOST"] == "localhost"


def test_redact_env_masks_api_key():
    env = {"API_KEY": "xyz", "PORT": "8080"}
    result = redact_env(env)
    assert result.redacted["API_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["PORT"] == "8080"


def test_redact_env_masks_token():
    env = {"AUTH_TOKEN": "tok_abc", "NAME": "app"}
    result = redact_env(env)
    assert result.redacted["AUTH_TOKEN"] == REDACT_PLACEHOLDER


def test_redact_env_redacted_keys_sorted():
    env = {"SECRET_B": "1", "SECRET_A": "2", "PLAIN": "3"}
    result = redact_env(env)
    assert result.redacted_keys == ["SECRET_A", "SECRET_B"]


def test_redact_env_count():
    env = {"DB_PASSWORD": "x", "API_KEY": "y", "HOST": "z"}
    result = redact_env(env)
    assert result.redact_count == 2


def test_redact_env_custom_placeholder():
    env = {"SECRET_KEY": "val"}
    result = redact_env(env, placeholder="***")
    assert result.redacted["SECRET_KEY"] == "***"


def test_redact_env_extra_patterns():
    env = {"INTERNAL_CODE": "42", "PLAIN": "ok"}
    result = redact_env(env, extra_patterns=[r"INTERNAL_CODE"])
    assert result.redacted["INTERNAL_CODE"] == REDACT_PLACEHOLDER
    assert result.redacted["PLAIN"] == "ok"


def test_redact_env_preserves_original():
    env = {"DB_PASSWORD": "secret", "HOST": "localhost"}
    result = redact_env(env)
    assert result.original["DB_PASSWORD"] == "secret"


def test_redact_file_writes_output(env_file: Path, tmp_path: Path):
    out = tmp_path / "redacted.env"
    result = redact_file(env_file, out)
    assert out.exists()
    content = out.read_text()
    assert REDACT_PLACEHOLDER in content
    assert "s3cr3t" not in content
    assert "localhost" in content


def test_redact_file_returns_result(env_file: Path, tmp_path: Path):
    out = tmp_path / "redacted.env"
    result = redact_file(env_file, out)
    assert isinstance(result, RedactResult)
    assert result.redact_count >= 2


def test_redact_file_missing_raises(tmp_path: Path):
    with pytest.raises(RedactError, match="not found"):
        redact_file(tmp_path / "missing.env", tmp_path / "out.env")


def test_redact_env_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = redact_env(env)
    assert result.redact_count == 0
    assert result.redacted == env
