"""Pin a snapshot to a named alias (e.g. 'stable', 'release') for quick reference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

PIN_FILE = ".envlock_pins.json"


class PinError(Exception):
    pass


def _pin_path(base_dir: Path) -> Path:
    return base_dir / PIN_FILE


def _load_pins(base_dir: Path) -> Dict[str, str]:
    path = _pin_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_pins(base_dir: Path, pins: Dict[str, str]) -> None:
    path = _pin_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(pins, f, indent=2)


def pin_snapshot(base_dir: Path, alias: str, snapshot_id: str, overwrite: bool = False) -> None:
    """Pin *snapshot_id* under *alias*. Raises PinError if alias exists and overwrite is False."""
    pins = _load_pins(base_dir)
    if alias in pins and not overwrite:
        raise PinError(
            f"Alias '{alias}' already points to '{pins[alias]}'. Use overwrite=True to replace."
        )
    pins[alias] = snapshot_id
    _save_pins(base_dir, pins)


def unpin(base_dir: Path, alias: str) -> None:
    """Remove a pin alias. Raises PinError if it does not exist."""
    pins = _load_pins(base_dir)
    if alias not in pins:
        raise PinError(f"Alias '{alias}' not found.")
    del pins[alias]
    _save_pins(base_dir, pins)


def resolve_pin(base_dir: Path, alias: str) -> str:
    """Return the snapshot_id for *alias*, or raise PinError."""
    pins = _load_pins(base_dir)
    if alias not in pins:
        raise PinError(f"Alias '{alias}' not found.")
    return pins[alias]


def list_pins(base_dir: Path) -> Dict[str, str]:
    """Return all alias -> snapshot_id mappings."""
    return _load_pins(base_dir)
