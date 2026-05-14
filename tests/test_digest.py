"""Tests for envlock.digest."""

import pytest
from pathlib import Path

from envlock.digest import (
    DigestError,
    DigestRecord,
    compute_digest,
    record_digest,
    verify_digest,
    get_digest,
    list_digests,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_compute_digest_sha256():
    result = compute_digest("KEY=value\n")
    assert len(result) == 64
    assert result == compute_digest("KEY=value\n")


def test_compute_digest_md5():
    result = compute_digest("KEY=value\n", algorithm="md5")
    assert len(result) == 32


def test_compute_digest_bad_algorithm():
    with pytest.raises(DigestError, match="Unsupported"):
        compute_digest("data", algorithm="notreal")


def test_record_digest_creates_file(snapshot_dir):
    record_digest(snapshot_dir, "snap-001", "A=1\n")
    assert (snapshot_dir / "digests.json").exists()


def test_record_digest_returns_record(snapshot_dir):
    rec = record_digest(snapshot_dir, "snap-001", "A=1\n")
    assert isinstance(rec, DigestRecord)
    assert rec.snapshot_id == "snap-001"
    assert rec.algorithm == "sha256"
    assert len(rec.hex_digest) == 64


def test_record_digest_str(snapshot_dir):
    rec = record_digest(snapshot_dir, "snap-001", "A=1\n")
    assert "snap-001" in str(rec)
    assert "sha256" in str(rec)


def test_verify_digest_correct(snapshot_dir):
    content = "DB_HOST=localhost\nDB_PORT=5432\n"
    record_digest(snapshot_dir, "snap-002", content)
    assert verify_digest(snapshot_dir, "snap-002", content) is True


def test_verify_digest_tampered(snapshot_dir):
    record_digest(snapshot_dir, "snap-002", "ORIGINAL=1\n")
    assert verify_digest(snapshot_dir, "snap-002", "TAMPERED=1\n") is False


def test_verify_digest_missing_raises(snapshot_dir):
    with pytest.raises(DigestError, match="No digest recorded"):
        verify_digest(snapshot_dir, "ghost-snap", "X=1\n")


def test_get_digest_returns_record(snapshot_dir):
    record_digest(snapshot_dir, "snap-003", "Z=99\n", algorithm="md5")
    rec = get_digest(snapshot_dir, "snap-003")
    assert rec.algorithm == "md5"
    assert rec.snapshot_id == "snap-003"


def test_get_digest_missing_raises(snapshot_dir):
    with pytest.raises(DigestError):
        get_digest(snapshot_dir, "nonexistent")


def test_list_digests_empty(snapshot_dir):
    assert list_digests(snapshot_dir) == []


def test_list_digests_returns_all(snapshot_dir):
    record_digest(snapshot_dir, "snap-b", "B=2\n")
    record_digest(snapshot_dir, "snap-a", "A=1\n")
    records = list_digests(snapshot_dir)
    assert len(records) == 2
    assert records[0].snapshot_id == "snap-a"  # sorted
    assert records[1].snapshot_id == "snap-b"
