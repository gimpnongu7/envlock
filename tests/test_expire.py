"""Tests for envlock.expire."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envlock.expire import (
    ExpireError,
    ExpiryRecord,
    clear_expiry,
    get_expiry,
    list_expired,
    set_expiry,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _make_meta(snapshot_dir: Path, snapshot_id: str, extra: dict | None = None) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    meta = snapshot_dir / f"{snapshot_id}.meta.json"
    data = {"id": snapshot_id, "created_at": "2024-01-01T00:00:00+00:00"}
    if extra:
        data.update(extra)
    meta.write_text(json.dumps(data))
    return meta


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)


# --- set_expiry ---

def test_set_expiry_writes_to_meta(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "snap1")
    exp = _future()
    record = set_expiry(snapshot_dir, "snap1", exp)
    assert record.snapshot_id == "snap1"
    assert not record.expired


def test_set_expiry_marks_already_past_as_expired(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "snap2")
    record = set_expiry(snapshot_dir, "snap2", _past())
    assert record.expired


def test_set_expiry_missing_meta_raises(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir()
    with pytest.raises(ExpireError, match="No metadata"):
        set_expiry(snapshot_dir, "ghost", _future())


# --- get_expiry ---

def test_get_expiry_returns_none_when_not_set(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "snap3")
    assert get_expiry(snapshot_dir, "snap3") is None


def test_get_expiry_returns_record(snapshot_dir: Path) -> None:
    exp = _future()
    _make_meta(snapshot_dir, "snap4", {"expires_at": exp.isoformat()})
    record = get_expiry(snapshot_dir, "snap4")
    assert isinstance(record, ExpiryRecord)
    assert not record.expired


def test_get_expiry_missing_meta_raises(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir()
    with pytest.raises(ExpireError):
        get_expiry(snapshot_dir, "nope")


# --- list_expired ---

def test_list_expired_returns_only_expired(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "old", {"expires_at": _past().isoformat()})
    _make_meta(snapshot_dir, "fresh", {"expires_at": _future().isoformat()})
    _make_meta(snapshot_dir, "noexp")
    results = list_expired(snapshot_dir)
    ids = [r.snapshot_id for r in results]
    assert "old" in ids
    assert "fresh" not in ids
    assert "noexp" not in ids


def test_list_expired_missing_dir_raises(snapshot_dir: Path) -> None:
    with pytest.raises(ExpireError, match="not found"):
        list_expired(snapshot_dir)


# --- clear_expiry ---

def test_clear_expiry_removes_field(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "snap5", {"expires_at": _past().isoformat()})
    clear_expiry(snapshot_dir, "snap5")
    assert get_expiry(snapshot_dir, "snap5") is None


def test_clear_expiry_missing_meta_raises(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir()
    with pytest.raises(ExpireError):
        clear_expiry(snapshot_dir, "nobody")


def test_expiry_record_str_contains_state(snapshot_dir: Path) -> None:
    _make_meta(snapshot_dir, "snap6", {"expires_at": _past().isoformat()})
    record = get_expiry(snapshot_dir, "snap6")
    assert "EXPIRED" in str(record)
