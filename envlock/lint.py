"""Lint .env files for common issues and style violations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class LintError(Exception):
    """Raised when linting cannot be performed."""


@dataclass
class LintIssue:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"L{self.line} [{self.code}] {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "No issues found."
        lines = [f"{len(self.issues)} issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


def lint_env_file(path: Path) -> LintResult:
    """Lint an .env file and return a LintResult with any issues."""
    if not path.exists():
        raise LintError(f"File not found: {path}")

    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.rstrip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(lineno, "E001", f"Missing '=' separator: {line!r}"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(LintIssue(lineno, "E002", "Empty key"))
            continue

        if key != key.upper():
            result.issues.append(LintIssue(lineno, "W001", f"Key {key!r} is not uppercase"))

        if " " in key:
            result.issues.append(LintIssue(lineno, "E003", f"Key {key!r} contains whitespace"))

        if key in seen_keys:
            result.issues.append(
                LintIssue(lineno, "W002", f"Duplicate key {key!r} (first seen at L{seen_keys[key]})")
            )
        else:
            seen_keys[key] = lineno

        if value.startswith(("'", '"')) and not (value.endswith(value[0]) and len(value) > 1):
            result.issues.append(LintIssue(lineno, "W003", f"Possibly unclosed quote for key {key!r}"))

    return result
