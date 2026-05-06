"""Archive multiple snapshots into a single zip bundle for sharing or backup."""

import zipfile
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional


class ArchiveError(Exception):
    pass


def _snapshot_files(snapshot_dir: Path) -> List[Path]:
    return sorted(snapshot_dir.glob("*.env"))


def create_archive(
    snapshot_dir: Path,
    output_path: Path,
    label: Optional[str] = None,
    snapshot_ids: Optional[List[str]] = None,
) -> Path:
    """Bundle snapshots into a zip archive.

    Args:
        snapshot_dir: Directory containing snapshot files.
        output_path: Destination path for the .zip file.
        label: Optional human-readable label stored in archive metadata.
        snapshot_ids: If provided, only archive these snapshot filenames.

    Returns:
        Path to the created archive.
    """
    if not snapshot_dir.exists():
        raise ArchiveError(f"Snapshot directory not found: {snapshot_dir}")

    all_files = _snapshot_files(snapshot_dir)
    if snapshot_ids is not None:
        wanted = set(snapshot_ids)
        all_files = [f for f in all_files if f.name in wanted]
        missing = wanted - {f.name for f in all_files}
        if missing:
            raise ArchiveError(f"Snapshots not found: {', '.join(sorted(missing))}")

    if not all_files:
        raise ArchiveError("No snapshots to archive.")

    meta = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label or "",
        "snapshots": [f.name for f in all_files],
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for snap in all_files:
            zf.write(snap, arcname=snap.name)
        zf.writestr("_envlock_meta.json", json.dumps(meta, indent=2))

    return output_path


def extract_archive(archive_path: Path, snapshot_dir: Path, overwrite: bool = False) -> List[str]:
    """Extract snapshots from an archive into snapshot_dir.

    Returns:
        List of extracted snapshot filenames.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise ArchiveError(f"Archive not found: {archive_path}")

    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    extracted = []
    with zipfile.ZipFile(archive_path, "r") as zf:
        for name in zf.namelist():
            if name == "_envlock_meta.json":
                continue
            dest = snapshot_dir / name
            if dest.exists() and not overwrite:
                raise ArchiveError(
                    f"Snapshot already exists: {name}. Use overwrite=True to replace."
                )
            zf.extract(name, path=snapshot_dir)
            extracted.append(name)

    return extracted


def archive_info(archive_path: Path) -> dict:
    """Return metadata stored inside an archive."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise ArchiveError(f"Archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path, "r") as zf:
        if "_envlock_meta.json" not in zf.namelist():
            raise ArchiveError("Archive is missing envlock metadata.")
        raw = zf.read("_envlock_meta.json")

    return json.loads(raw)
