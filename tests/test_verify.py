"""Tests for envlock.verify."""

import hashlib
import json
from pathlib import Path

import pytest

from envlock.verify import (
    VerifyError,
    VerifyResult,
    format_verify_results,
    verify_all,
    verify_snapshot,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def _make_snapshot(snapshot_dir: Path, name: str, content: str, store_hash: bool = True) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    p = snapshot_dir / f"{name}.env"
    p.write_text(content)
    if store_hash:
        h = hashlib.sha256(content.encode()).hexdigest()
        meta = p.with_suffix(".meta.json")
        meta.write_text(json.dumps({"hash": h, "label": name}))
    return p


def test_verify_snapshot_passes(snapshot_dir):
    p = _make_snapshot(snapshot_dir, "snap1", "KEY=value\n")
    result = verify_snapshot(p)
    assert result.passed is True
    assert result.snapshot_id == "snap1"


def test_verify_snapshot_fails_on_tamper(snapshot_dir):
    p = _make_snapshot(snapshot_dir, "snap2", "KEY=value\n")
    p.write_text("KEY=tampered\n")  # tamper after hash stored
    result = verify_snapshot(p)
    assert result.passed is False
    assert result.actual_hash != result.expected_hash


def test_verify_snapshot_no_meta(snapshot_dir):
    p = _make_snapshot(snapshot_dir, "snap3", "KEY=value\n", store_hash=False)
    result = verify_snapshot(p)
    assert result.passed is False
    assert result.expected_hash is None


def test_verify_snapshot_missing_file(snapshot_dir):
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(VerifyError, match="not found"):
        verify_snapshot(snapshot_dir / "ghost.env")


def test_verify_all_returns_results(snapshot_dir):
    _make_snapshot(snapshot_dir, "a", "A=1\n")
    _make_snapshot(snapshot_dir, "b", "B=2\n")
    results = verify_all(snapshot_dir)
    assert len(results) == 2
    assert all(isinstance(r, VerifyResult) for r in results)
    assert all(r.passed for r in results)


def test_verify_all_empty_dir(snapshot_dir):
    snapshot_dir.mkdir()
    results = verify_all(snapshot_dir)
    assert results == []


def test_verify_all_missing_dir(snapshot_dir):
    with pytest.raises(VerifyError, match="not found"):
        verify_all(snapshot_dir)


def test_format_verify_results_all_pass(snapshot_dir):
    _make_snapshot(snapshot_dir, "x", "X=1\n")
    results = verify_all(snapshot_dir)
    out = format_verify_results(results)
    assert "OK" in out
    assert "1/1" in out


def test_format_verify_results_empty():
    out = format_verify_results([])
    assert "No snapshots" in out


def test_str_result_ok(snapshot_dir):
    p = _make_snapshot(snapshot_dir, "s", "K=v\n")
    r = verify_snapshot(p)
    assert str(r).startswith("[OK]")


def test_str_result_fail(snapshot_dir):
    p = _make_snapshot(snapshot_dir, "s2", "K=v\n")
    p.write_text("K=changed\n")
    r = verify_snapshot(p)
    assert str(r).startswith("[FAIL]")
