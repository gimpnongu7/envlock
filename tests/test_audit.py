"""Tests for envlock.audit module."""

import pytest
from pathlib import Path

from envlock.audit import record, read_log, format_log, AuditEntry


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def test_record_creates_file(snapshot_dir):
    record(snapshot_dir, "create", "snap_abc123", ".env")
    audit_file = snapshot_dir / ".envlock_audit.jsonl"
    assert audit_file.exists()


def test_record_returns_entry(snapshot_dir):
    entry = record(snapshot_dir, "create", "snap_abc123", ".env", label="main")
    assert isinstance(entry, AuditEntry)
    assert entry.action == "create"
    assert entry.snapshot_name == "snap_abc123"
    assert entry.label == "main"


def test_read_log_empty_when_no_file(snapshot_dir):
    entries = read_log(snapshot_dir)
    assert entries == []


def test_read_log_returns_all_entries(snapshot_dir):
    record(snapshot_dir, "create", "snap_001", ".env")
    record(snapshot_dir, "restore", "snap_001", ".env")
    record(snapshot_dir, "delete", "snap_001", ".env")
    entries = read_log(snapshot_dir)
    assert len(entries) == 3
    assert entries[0].action == "create"
    assert entries[1].action == "restore"
    assert entries[2].action == "delete"


def test_read_log_preserves_fields(snapshot_dir):
    record(snapshot_dir, "create", "snap_xyz", ".env", label="feature-x", note="before merge")
    entries = read_log(snapshot_dir)
    e = entries[0]
    assert e.label == "feature-x"
    assert e.note == "before merge"
    assert e.env_file == ".env"


def test_entries_have_timestamps(snapshot_dir):
    record(snapshot_dir, "create", "snap_ts", ".env")
    entries = read_log(snapshot_dir)
    assert entries[0].timestamp.endswith("+00:00") or "Z" in entries[0].timestamp or "T" in entries[0].timestamp


def test_format_log_empty():
    result = format_log([])
    assert "no audit" in result


def test_format_log_contains_action(snapshot_dir):
    record(snapshot_dir, "restore", "snap_r1", ".env", label="hotfix")
    entries = read_log(snapshot_dir)
    output = format_log(entries)
    assert "restore" in output
    assert "snap_r1" in output
    assert "[hotfix]" in output


def test_multiple_records_appended(snapshot_dir):
    for i in range(5):
        record(snapshot_dir, "create", f"snap_{i:03d}", ".env")
    entries = read_log(snapshot_dir)
    assert len(entries) == 5
