"""Tests for envlock.secure_snapshot module."""

import json
import pytest
from pathlib import Path

pytest.importorskip("cryptography", reason="cryptography not installed")

from envlock.secure_snapshot import (
    create_encrypted_snapshot,
    restore_encrypted_snapshot,
    list_encrypted_snapshots,
    ENCRYPTED_EXT,
)
from envlock.encrypt import decrypt_content


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=supersecret\nDEBUG=true\n")
    return p


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def test_create_encrypted_snapshot_creates_file(env_file, snapshot_dir):
    path = create_encrypted_snapshot(str(env_file), str(snapshot_dir), "pass123")
    assert Path(path).exists()
    assert path.endswith(ENCRYPTED_EXT)


def test_create_encrypted_snapshot_with_label(env_file, snapshot_dir):
    path = create_encrypted_snapshot(str(env_file), str(snapshot_dir), "pass", label="prod")
    assert "_prod" in Path(path).name


def test_restore_encrypted_snapshot(env_file, snapshot_dir, tmp_path):
    snap_path = create_encrypted_snapshot(str(env_file), str(snapshot_dir), "mypass")
    restore_target = tmp_path / "restored.env"
    meta = restore_encrypted_snapshot(str(snap_path), str(restore_target), "mypass")
    assert restore_target.read_text() == env_file.read_text()
    assert "created_at" in meta
    assert "hash" in meta


def test_restore_wrong_passphrase(env_file, snapshot_dir, tmp_path):
    from envlock.encrypt import DecryptionError
    snap_path = create_encrypted_snapshot(str(env_file), str(snapshot_dir), "correct")
    with pytest.raises(DecryptionError):
        restore_encrypted_snapshot(str(snap_path), str(tmp_path / "out.env"), "wrong")


def test_list_encrypted_snapshots(env_file, snapshot_dir):
    create_encrypted_snapshot(str(env_file), str(snapshot_dir), "p")
    create_encrypted_snapshot(str(env_file), str(snapshot_dir), "p")
    snaps = list_encrypted_snapshots(str(snapshot_dir))
    assert len(snaps) == 2
    assert all(s["filename"].endswith(ENCRYPTED_EXT) for s in snaps)


def test_list_encrypted_snapshots_empty(tmp_path):
    result = list_encrypted_snapshots(str(tmp_path / "nonexistent"))
    assert result == []
