"""Tests for envlock.pin"""

import pytest
from pathlib import Path
from envlock.pin import (
    PinError,
    pin_snapshot,
    unpin,
    resolve_pin,
    list_pins,
)


@pytest.fixture
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_pin_and_resolve(pin_dir):
    pin_snapshot(pin_dir, "stable", "snap_001")
    assert resolve_pin(pin_dir, "stable") == "snap_001"


def test_pin_duplicate_raises(pin_dir):
    pin_snapshot(pin_dir, "stable", "snap_001")
    with pytest.raises(PinError, match="already points to"):
        pin_snapshot(pin_dir, "stable", "snap_002")


def test_pin_overwrite(pin_dir):
    pin_snapshot(pin_dir, "stable", "snap_001")
    pin_snapshot(pin_dir, "stable", "snap_002", overwrite=True)
    assert resolve_pin(pin_dir, "stable") == "snap_002"


def test_unpin_removes_alias(pin_dir):
    pin_snapshot(pin_dir, "release", "snap_003")
    unpin(pin_dir, "release")
    with pytest.raises(PinError, match="not found"):
        resolve_pin(pin_dir, "release")


def test_unpin_missing_raises(pin_dir):
    with pytest.raises(PinError, match="not found"):
        unpin(pin_dir, "ghost")


def test_resolve_missing_raises(pin_dir):
    with pytest.raises(PinError, match="not found"):
        resolve_pin(pin_dir, "nope")


def test_list_pins_empty(pin_dir):
    assert list_pins(pin_dir) == {}


def test_list_pins_returns_all(pin_dir):
    pin_snapshot(pin_dir, "stable", "snap_001")
    pin_snapshot(pin_dir, "canary", "snap_002")
    pins = list_pins(pin_dir)
    assert pins == {"stable": "snap_001", "canary": "snap_002"}


def test_pin_creates_directory(tmp_path):
    deep_dir = tmp_path / "a" / "b" / "c"
    pin_snapshot(deep_dir, "x", "snap_x")
    assert resolve_pin(deep_dir, "x") == "snap_x"
