"""Profile support: named sets of .env snapshots for different environments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

PROFILE_FILE = ".envlock_profiles.json"


class ProfileError(Exception):
    """Raised when a profile operation fails."""


def _profile_path(base_dir: Path) -> Path:
    return base_dir / PROFILE_FILE


def load_profiles(base_dir: Path) -> Dict[str, List[str]]:
    """Load profile -> snapshot-label list mapping from disk."""
    path = _profile_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_profiles(base_dir: Path, profiles: Dict[str, List[str]]) -> None:
    """Persist profiles mapping to disk."""
    path = _profile_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(profiles, fh, indent=2)


def add_snapshot_to_profile(
    base_dir: Path, profile: str, label: str
) -> Dict[str, List[str]]:
    """Associate a snapshot label with a named profile."""
    profiles = load_profiles(base_dir)
    profiles.setdefault(profile, [])
    if label not in profiles[profile]:
        profiles[profile].append(label)
    save_profiles(base_dir, profiles)
    return profiles


def remove_snapshot_from_profile(
    base_dir: Path, profile: str, label: str
) -> Dict[str, List[str]]:
    """Remove a snapshot label from a named profile."""
    profiles = load_profiles(base_dir)
    if profile not in profiles:
        raise ProfileError(f"Profile '{profile}' does not exist.")
    try:
        profiles[profile].remove(label)
    except ValueError:
        raise ProfileError(f"Label '{label}' not found in profile '{profile}'.")
    save_profiles(base_dir, profiles)
    return profiles


def list_profiles(base_dir: Path) -> List[str]:
    """Return all known profile names."""
    return list(load_profiles(base_dir).keys())


def get_profile_snapshots(base_dir: Path, profile: str) -> List[str]:
    """Return snapshot labels belonging to a profile."""
    profiles = load_profiles(base_dir)
    if profile not in profiles:
        raise ProfileError(f"Profile '{profile}' does not exist.")
    return profiles[profile]


def delete_profile(base_dir: Path, profile: str) -> None:
    """Remove a profile entirely."""
    profiles = load_profiles(base_dir)
    if profile not in profiles:
        raise ProfileError(f"Profile '{profile}' does not exist.")
    del profiles[profile]
    save_profiles(base_dir, profiles)
