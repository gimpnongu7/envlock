"""Tests for envlock.schema."""

import json
import pytest
from pathlib import Path

from envlock.schema import (
    SchemaError,
    SchemaResult,
    load_schema,
    validate_against_schema,
)


@pytest.fixture
def schema_file(tmp_path: Path) -> Path:
    path = tmp_path / "schema.json"
    path.write_text(
        json.dumps(
            {
                "required": ["DATABASE_URL", "SECRET_KEY"],
                "properties": {
                    "PORT": {"type": "integer"},
                    "DEBUG": {"type": "boolean"},
                    "APP_ENV": {"pattern": "^(development|staging|production)$"},
                },
            }
        )
    )
    return path


def test_load_schema_returns_dict(schema_file: Path):
    schema = load_schema(schema_file)
    assert "required" in schema
    assert "properties" in schema


def test_load_schema_missing_file(tmp_path: Path):
    with pytest.raises(SchemaError, match="not found"):
        load_schema(tmp_path / "nope.json")


def test_load_schema_invalid_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    with pytest.raises(SchemaError, match="Invalid JSON"):
        load_schema(bad)


def test_load_schema_non_object(tmp_path: Path):
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]")
    with pytest.raises(SchemaError, match="root must be"):
        load_schema(arr)


def test_valid_env_passes(schema_file: Path):
    schema = load_schema(schema_file)
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "abc123",
        "PORT": "8080",
        "APP_ENV": "production",
    }
    result = validate_against_schema(env, schema)
    assert result.valid is True
    assert "passed" in result.summary()


def test_missing_required_key(schema_file: Path):
    schema = load_schema(schema_file)
    env = {"DATABASE_URL": "postgres://localhost/db"}
    result = validate_against_schema(env, schema)
    assert result.valid is False
    assert "SECRET_KEY" in result.missing
    assert "missing required key" in result.summary()


def test_type_error_integer(schema_file: Path):
    schema = load_schema(schema_file)
    env = {
        "DATABASE_URL": "x",
        "SECRET_KEY": "y",
        "PORT": "not_a_number",
    }
    result = validate_against_schema(env, schema)
    assert result.valid is False
    assert any("PORT" in e for e in result.type_errors)


def test_type_error_boolean(schema_file: Path):
    schema = load_schema(schema_file)
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "DEBUG": "maybe"}
    result = validate_against_schema(env, schema)
    assert result.valid is False
    assert any("DEBUG" in e for e in result.type_errors)


def test_pattern_error(schema_file: Path):
    schema = load_schema(schema_file)
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "APP_ENV": "local"}
    result = validate_against_schema(env, schema)
    assert result.valid is False
    assert any("APP_ENV" in e for e in result.pattern_errors)


def test_boolean_valid_values(schema_file: Path):
    schema = load_schema(schema_file)
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "DEBUG": val}
        result = validate_against_schema(env, schema)
        assert result.type_errors == [], f"Expected no type error for DEBUG={val!r}"
