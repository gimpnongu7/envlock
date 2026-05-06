"""Schema validation for .env files against a JSON schema definition."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class SchemaError(Exception):
    """Raised when schema loading or structure is invalid."""


@dataclass
class SchemaResult:
    valid: bool
    missing: List[str] = field(default_factory=list)
    type_errors: List[str] = field(default_factory=list)
    pattern_errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.valid:
            return "Schema validation passed."
        lines = ["Schema validation failed:"]
        for k in self.missing:
            lines.append(f"  missing required key: {k}")
        for e in self.type_errors:
            lines.append(f"  type error: {e}")
        for e in self.pattern_errors:
            lines.append(f"  pattern error: {e}")
        return "\n".join(lines)


def load_schema(schema_path: Path) -> Dict:
    """Load and minimally validate a JSON schema file."""
    if not schema_path.exists():
        raise SchemaError(f"Schema file not found: {schema_path}")
    try:
        data = json.loads(schema_path.read_text())
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON in schema: {exc}") from exc
    if not isinstance(data, dict):
        raise SchemaError("Schema root must be a JSON object.")
    return data


def validate_against_schema(
    env: Dict[str, str],
    schema: Dict,
) -> SchemaResult:
    """Validate a parsed env dict against a schema definition.

    Schema format example::

        {
          "required": ["DATABASE_URL", "SECRET_KEY"],
          "properties": {
            "PORT": {"type": "integer"},
            "DEBUG": {"type": "boolean"},
            "APP_ENV": {"pattern": "^(development|staging|production)$"}
          }
        }
    """
    import re

    missing: List[str] = []
    type_errors: List[str] = []
    pattern_errors: List[str] = []

    for key in schema.get("required", []):
        if key not in env:
            missing.append(key)

    for key, rules in schema.get("properties", {}).items():
        if key not in env:
            continue
        value = env[key]

        expected_type: Optional[str] = rules.get("type")
        if expected_type == "integer":
            try:
                int(value)
            except ValueError:
                type_errors.append(f"{key}={value!r} is not an integer")
        elif expected_type == "boolean":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                type_errors.append(f"{key}={value!r} is not a boolean")

        pattern: Optional[str] = rules.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            pattern_errors.append(f"{key}={value!r} does not match pattern {pattern!r}")

    valid = not (missing or type_errors or pattern_errors)
    return SchemaResult(
        valid=valid,
        missing=missing,
        type_errors=type_errors,
        pattern_errors=pattern_errors,
    )
