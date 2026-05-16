"""Import environment variables from external sources into a snapshot."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envlock.snapshot import create_snapshot


class ImportError(Exception):  # noqa: A001
    """Raised when an import operation fails."""


def _parse_dotenv_text(text: str) -> Dict[str, str]:
    """Parse raw .env-style text into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def import_from_dotenv(source: Path) -> Dict[str, str]:
    """Load env vars from a .env-style file.

    Args:
        source: Path to the .env file to parse.

    Returns:
        A dict of key/value pairs parsed from the file.

    Raises:
        ImportError: If the file does not exist.
    """
    if not source.exists():
        raise ImportError(f"Source file not found: {source}")
    return _parse_dotenv_text(source.read_text(encoding="utf-8"))


def import_from_json(source: Path) -> Dict[str, str]:
    """Load env vars from a JSON file (flat key/value object)."""
    if not source.exists():
        raise ImportError(f"Source file not found: {source}")
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ImportError(f"Invalid JSON in {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError(f"Expected a JSON object, got {type(data).__name__}")
    bad = [k for k, v in data.items() if not isinstance(v, str)]
    if bad:
        raise ImportError(f"Non-string values for keys: {bad}")
    return data


def import_from_shell_env(keys: Optional[list] = None) -> Dict[str, str]:
    """Capture variables from the current process environment.

    Args:
        keys: If provided, only capture these specific keys.
    """
    env = dict(os.environ)
    if keys is not None:
        missing = [k for k in keys if k not in env]
        if missing:
            raise ImportError(f"Keys not found in environment: {missing}")
        env = {k: env[k] for k in keys}
    return env


def import_and_snapshot(
    env_vars: Dict[str, str],
    snapshot_dir: Path,
    label: Optional[str] = None,
) -> Path:
    """Write *env_vars* to a temporary .env file and create a snapshot.

    Returns the path to the created snapshot file.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    tmp_env = snapshot_dir / "_import_tmp.env"
    lines = [f"{k}={v}\n" for k, v in sorted(env_vars.items())]
    tmp_env.write_text("".join(lines), encoding="utf-8")
    try:
        snapshot_path = create_snapshot(tmp_env, snapshot_dir, label=label)
    finally:
        tmp_env.unlink(missing_ok=True)
    return snapshot_path
