"""Verify snapshot integrity by recomputing and comparing content hashes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


class VerifyError(Exception):
    """Raised when verification cannot be performed."""


@dataclass
class VerifyResult:
    snapshot_id: str
    path: Path
    expected_hash: Optional[str]
    actual_hash: str
    passed: bool

    def __str__(self) -> str:
        status = "OK" if self.passed else "FAIL"
        return f"[{status}] {self.snapshot_id}  expected={self.expected_hash}  actual={self.actual_hash}"


def _compute_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _meta_path(snapshot_path: Path) -> Path:
    return snapshot_path.with_suffix(".meta.json")


def _load_expected_hash(snapshot_path: Path) -> Optional[str]:
    meta = _meta_path(snapshot_path)
    if not meta.exists():
        return None
    try:
        data = json.loads(meta.read_text())
        return data.get("hash")
    except (json.JSONDecodeError, OSError):
        return None


def verify_snapshot(snapshot_path: Path) -> VerifyResult:
    """Verify a single snapshot file against its stored hash."""
    if not snapshot_path.exists():
        raise VerifyError(f"Snapshot not found: {snapshot_path}")

    actual = _compute_hash(snapshot_path)
    expected = _load_expected_hash(snapshot_path)
    passed = expected is not None and actual == expected

    return VerifyResult(
        snapshot_id=snapshot_path.stem,
        path=snapshot_path,
        expected_hash=expected,
        actual_hash=actual,
        passed=passed,
    )


def verify_all(snapshot_dir: Path) -> List[VerifyResult]:
    """Verify all .env snapshots in a directory."""
    if not snapshot_dir.exists():
        raise VerifyError(f"Snapshot directory not found: {snapshot_dir}")

    results = []
    for p in sorted(snapshot_dir.glob("*.env")):
        results.append(verify_snapshot(p))
    return results


def format_verify_results(results: List[VerifyResult]) -> str:
    if not results:
        return "No snapshots found."
    lines = [str(r) for r in results]
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    lines.append(f"\n{passed}/{total} snapshots passed verification.")
    return "\n".join(lines)
