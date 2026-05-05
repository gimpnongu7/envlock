"""Encrypted snapshot helpers built on top of snapshot.py and encrypt.py."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from envlock.encrypt import encrypt_content, decrypt_content
from envlock.snapshot import parse_env_file, _hash_content

ENCRYPTED_EXT = ".envlock.enc"


def create_encrypted_snapshot(
    env_path: str,
    snapshot_dir: str,
    passphrase: str,
    label: str = "",
) -> str:
    """Create an encrypted snapshot. Returns the snapshot file path."""
    env_path = Path(env_path)
    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    raw_content = env_path.read_text()
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(env_path),
        "label": label,
        "hash": _hash_content(raw_content),
    }
    payload = json.dumps({"metadata": metadata, "content": raw_content})
    encrypted = encrypt_content(payload, passphrase)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    slug = f"_{label}" if label else ""
    filename = f"{ts}{slug}{ENCRYPTED_EXT}"
    out_path = snapshot_dir / filename
    out_path.write_bytes(encrypted)
    return str(out_path)


def restore_encrypted_snapshot(
    snapshot_path: str,
    env_path: str,
    passphrase: str,
) -> dict:
    """Restore an encrypted snapshot. Returns metadata dict."""
    data = Path(snapshot_path).read_bytes()
    payload_str = decrypt_content(data, passphrase)
    payload = json.loads(payload_str)
    Path(env_path).write_text(payload["content"])
    return payload["metadata"]


def list_encrypted_snapshots(snapshot_dir: str) -> list[dict]:
    """List encrypted snapshots in a directory (metadata only, no decryption)."""
    snapshot_dir = Path(snapshot_dir)
    if not snapshot_dir.exists():
        return []
    files = sorted(snapshot_dir.glob(f"*{ENCRYPTED_EXT}"))
    return [{"path": str(f), "filename": f.name, "size": f.stat().st_size} for f in files]
