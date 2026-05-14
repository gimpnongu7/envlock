"""envlock.redact — Redact sensitive values from snapshots before sharing."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Keys matching these patterns are considered sensitive by default
_DEFAULT_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

REDACT_PLACEHOLDER = "<redacted>"


class RedactError(Exception):
    """Raised when redaction cannot be completed."""


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def _is_sensitive(key: str, compiled: List[re.Pattern]) -> bool:
    return any(p.fullmatch(key) for p in compiled)


def redact_env(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by placeholder."""
    patterns = _DEFAULT_PATTERNS + (extra_patterns or [])
    compiled = _compile_patterns(patterns)
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key, compiled):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(original=dict(env), redacted=redacted, redacted_keys=sorted(redacted_keys))


def redact_file(
    env_path: Path,
    output_path: Path,
    extra_patterns: Optional[List[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    """Read *env_path*, redact it, and write the result to *output_path*."""
    if not env_path.exists():
        raise RedactError(f"env file not found: {env_path}")

    from envlock.snapshot import parse_env_file  # avoid circular at module level

    env = parse_env_file(env_path)
    result = redact_env(env, extra_patterns=extra_patterns, placeholder=placeholder)

    lines = [f"{k}={v}\n" for k, v in result.redacted.items()]
    output_path.write_text("".join(lines), encoding="utf-8")
    return result
