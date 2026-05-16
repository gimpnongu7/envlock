"""Tests for envlock.badge."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envlock.badge import BadgeError, generate_badge, write_badge
from envlock.remind import ReminderStatus
from envlock.verify import VerifyResult


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    return p


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _patch_state(state: str, label: str):
    return patch("envlock.badge._badge_state", return_value=(state, label))


def test_generate_badge_svg_ok(env_file, snapshot_dir):
    with _patch_state("ok", "up to date"):
        svg = generate_badge(env_file, snapshot_dir, fmt="svg")
    assert "<svg" in svg
    assert "up to date" in svg
    assert "#4c9e3f" in svg


def test_generate_badge_svg_stale(env_file, snapshot_dir):
    with _patch_state("stale", "stale"):
        svg = generate_badge(env_file, snapshot_dir, fmt="svg")
    assert "stale" in svg
    assert "#e6a817" in svg


def test_generate_badge_svg_missing(env_file, snapshot_dir):
    with _patch_state("missing", "no snapshot"):
        svg = generate_badge(env_file, snapshot_dir, fmt="svg")
    assert "no snapshot" in svg
    assert "#cc3c2f" in svg


def test_generate_badge_json_format(env_file, snapshot_dir):
    with _patch_state("ok", "up to date"):
        raw = generate_badge(env_file, snapshot_dir, fmt="json")
    data = json.loads(raw)
    assert data["state"] == "ok"
    assert data["label"] == "up to date"
    assert "color" in data


def test_generate_badge_invalid_format_raises(env_file, snapshot_dir):
    with pytest.raises(BadgeError, match="Unsupported"):
        generate_badge(env_file, snapshot_dir, fmt="xml")  # type: ignore[arg-type]


def test_write_badge_creates_file(env_file, snapshot_dir, tmp_path):
    out = tmp_path / "badges" / "envlock.svg"
    with _patch_state("ok", "up to date"):
        result = write_badge(env_file, snapshot_dir, out, fmt="svg")
    assert result == out
    assert out.exists()
    assert "<svg" in out.read_text()


def test_write_badge_json(env_file, snapshot_dir, tmp_path):
    out = tmp_path / "envlock-badge.json"
    with _patch_state("stale", "stale"):
        write_badge(env_file, snapshot_dir, out, fmt="json")
    data = json.loads(out.read_text())
    assert data["state"] == "stale"


def test_badge_error_state_reflected(env_file, snapshot_dir):
    with _patch_state("error", "tampered"):
        svg = generate_badge(env_file, snapshot_dir, fmt="svg")
    assert "tampered" in svg
    assert "#9b59b6" in svg
