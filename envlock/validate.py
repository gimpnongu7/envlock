"""Validate .env files against a template, reporting missing or extra keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envlock.snapshot import parse_env_file


@dataclass
class ValidationResult:
    missing: List[str] = field(default_factory=list)   # in template, not in env
    extra: List[str] = field(default_factory=list)     # in env, not in template
    empty: List[str] = field(default_factory=list)     # key present but value is blank

    @property
    def is_valid(self) -> bool:
        return not (self.missing or self.extra or self.empty)

    def summary(self) -> str:
        lines: List[str] = []
        if self.missing:
            lines.append("Missing keys: " + ", ".join(sorted(self.missing)))
        if self.extra:
            lines.append("Extra keys:   " + ", ".join(sorted(self.extra)))
        if self.empty:
            lines.append("Empty keys:   " + ", ".join(sorted(self.empty)))
        if not lines:
            return "OK — env file matches template."
        return "\n".join(lines)


class ValidationError(Exception):
    """Raised when a required file is missing or unreadable."""


def validate_env(
    env_path: Path | str,
    template_path: Path | str,
    *,
    allow_extra: bool = False,
    check_empty: bool = True,
) -> ValidationResult:
    """Compare *env_path* against *template_path* and return a ValidationResult.

    Parameters
    ----------
    env_path:
        The .env file to validate.
    template_path:
        A template file whose keys act as the required set (values are ignored).
    allow_extra:
        When *True*, keys present in the env but absent from the template are
        not reported as extra.
    check_empty:
        When *True*, keys whose value is an empty string are flagged.
    """
    env_path = Path(env_path)
    template_path = Path(template_path)

    for p in (env_path, template_path):
        if not p.exists():
            raise ValidationError(f"File not found: {p}")

    env: Dict[str, str] = parse_env_file(env_path)
    template: Dict[str, str] = parse_env_file(template_path)

    required = set(template.keys())
    present = set(env.keys())

    result = ValidationResult(
        missing=sorted(required - present),
        extra=[] if allow_extra else sorted(present - required),
    )

    if check_empty:
        result.empty = sorted(
            k for k in present if env[k] == ""
        )

    return result
