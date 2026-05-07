"""Search snapshots by key, value, or label."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envlock.snapshot import parse_env_file


class SearchError(Exception):
    pass


@dataclass
class SearchHit:
    snapshot_id: str
    label: Optional[str]
    key: str
    value: str

    def __str__(self) -> str:
        tag = f" [{self.label}]" if self.label else ""
        return f"{self.snapshot_id}{tag}  {self.key}={self.value}"


@dataclass
class SearchResult:
    hits: List[SearchHit] = field(default_factory=list)

    def found(self) -> bool:
        return len(self.hits) > 0

    def summary(self) -> str:
        if not self.hits:
            return "No matches found."
        lines = [str(h) for h in self.hits]
        return "\n".join(lines)


def _load_meta(snapshot_path: Path) -> dict:
    meta_path = snapshot_path.with_suffix(".meta.json")
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text())
        except Exception:
            pass
    return {}


def search_snapshots(
    snapshot_dir: Path,
    *,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    label_pattern: Optional[str] = None,
) -> SearchResult:
    """Search all snapshots in *snapshot_dir* for matching keys/values/labels."""
    if not snapshot_dir.exists():
        raise SearchError(f"Snapshot directory not found: {snapshot_dir}")

    if key_pattern is None and value_pattern is None and label_pattern is None:
        raise SearchError("At least one of key_pattern, value_pattern, or label_pattern must be provided.")

    result = SearchResult()

    for snap_path in sorted(snapshot_dir.glob("*.env")):
        meta = _load_meta(snap_path)
        label: Optional[str] = meta.get("label")
        snapshot_id = snap_path.stem

        if label_pattern is not None:
            if label is None or label_pattern.lower() not in label.lower():
                continue

        try:
            env = parse_env_file(snap_path)
        except Exception:
            continue

        for k, v in env.items():
            if key_pattern is not None and key_pattern.lower() not in k.lower():
                continue
            if value_pattern is not None and value_pattern.lower() not in v.lower():
                continue
            result.hits.append(SearchHit(snapshot_id=snapshot_id, label=label, key=k, value=v))

    return result
