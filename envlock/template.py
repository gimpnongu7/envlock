"""Template generation from .env files — strip values, keep keys with optional comments."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


class TemplateError(Exception):
    pass


def _is_comment_or_blank(line: str) -> bool:
    stripped = line.strip()
    return stripped == "" or stripped.startswith("#")


def generate_template(
    env_path: Path,
    *,
    include_comments: bool = True,
    placeholder: str = "",
) -> str:
    """Read an .env file and return a template string with values stripped.

    Args:
        env_path: Path to the source .env file.
        include_comments: Whether to preserve comment lines.
        placeholder: Value to use instead of the original (default: empty string).

    Returns:
        Template content as a string.
    """
    if not env_path.exists():
        raise TemplateError(f"env file not found: {env_path}")

    lines: list[str] = []
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        if _is_comment_or_blank(raw):
            if include_comments:
                lines.append(raw)
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=.*$", raw)
        if match:
            lines.append(f"{match.group(1)}={placeholder}")
        else:
            # preserve unrecognised lines as-is
            lines.append(raw)

    return "\n".join(lines) + "\n"


def write_template(
    env_path: Path,
    output_path: Path,
    *,
    include_comments: bool = True,
    placeholder: str = "",
    overwrite: bool = False,
) -> Path:
    """Generate a template from *env_path* and write it to *output_path*."""
    if output_path.exists() and not overwrite:
        raise TemplateError(
            f"output file already exists: {output_path}. Pass overwrite=True to replace."
        )
    content = generate_template(
        env_path, include_comments=include_comments, placeholder=placeholder
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
