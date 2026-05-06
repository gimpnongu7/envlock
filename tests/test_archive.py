"""Tests for envlock.archive."""

import pytest
from pathlib import Path
from envlock.archive import (
    create_archive,
    extract_archive,
    archive_info,
    ArchiveError,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _make_snapshots(snapshot_dir, names):
    for name in names:
        (snapshot_dir / name).write_text(f"KEY=value_{name}\n")


def test_create_archive_produces_zip(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env", "snap2.env"])
    out = tmp_path / "bundle.zip"
    result = create_archive(snapshot_dir, out)
    assert result == out
    assert out.exists()


def test_archive_contains_metadata(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env"])
    out = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, out, label="my-backup")
    info = archive_info(out)
    assert info["label"] == "my-backup"
    assert "snap1.env" in info["snapshots"]
    assert "created_at" in info


def test_create_archive_selective(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env", "snap2.env", "snap3.env"])
    out = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, out, snapshot_ids=["snap1.env", "snap3.env"])
    info = archive_info(out)
    assert set(info["snapshots"]) == {"snap1.env", "snap3.env"}


def test_create_archive_missing_snapshot_raises(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env"])
    out = tmp_path / "bundle.zip"
    with pytest.raises(ArchiveError, match="ghost.env"):
        create_archive(snapshot_dir, out, snapshot_ids=["ghost.env"])


def test_create_archive_empty_dir_raises(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ArchiveError, match="No snapshots"):
        create_archive(empty, tmp_path / "out.zip")


def test_create_archive_missing_dir_raises(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        create_archive(tmp_path / "nope", tmp_path / "out.zip")


def test_extract_archive_restores_files(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env", "snap2.env"])
    out = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, out)

    restore_dir = tmp_path / "restored"
    extracted = extract_archive(out, restore_dir)
    assert set(extracted) == {"snap1.env", "snap2.env"}
    assert (restore_dir / "snap1.env").exists()


def test_extract_archive_no_overwrite_raises(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env"])
    out = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, out)

    restore_dir = tmp_path / "restored"
    extract_archive(out, restore_dir)
    with pytest.raises(ArchiveError, match="already exists"):
        extract_archive(out, restore_dir, overwrite=False)


def test_extract_archive_overwrite_succeeds(snapshot_dir, tmp_path):
    _make_snapshots(snapshot_dir, ["snap1.env"])
    out = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, out)

    restore_dir = tmp_path / "restored"
    extract_archive(out, restore_dir)
    extracted = extract_archive(out, restore_dir, overwrite=True)
    assert "snap1.env" in extracted


def test_archive_info_missing_file_raises(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        archive_info(tmp_path / "nope.zip")
