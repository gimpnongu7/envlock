"""Tests for envlock.watch module."""

import time
import pytest
from pathlib import Path

from envlock.watch import watch_env_file, WatchError


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value1\n")
    return f


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_watch_raises_if_env_missing(tmp_path, snapshot_dir):
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(WatchError, match="not found"):
        watch_env_file(missing, snapshot_dir, max_snapshots=1)


def test_watch_creates_snapshot_on_change(env_file, snapshot_dir):
    """Modify the file mid-watch and confirm a snapshot is created."""
    snapshots_created = []

    def _modify_after_first_tick():
        time.sleep(0.05)
        env_file.write_text("KEY=value2\n")

    import threading
    t = threading.Thread(target=_modify_after_first_tick, daemon=True)
    t.start()

    watch_env_file(
        env_file,
        snapshot_dir,
        interval=0.03,
        label_prefix="test",
        on_snapshot=snapshots_created.append,
        max_snapshots=1,
    )
    t.join()

    assert len(snapshots_created) == 1
    assert (snapshot_dir / snapshots_created[0]).exists()


def test_watch_no_snapshot_without_change(env_file, snapshot_dir):
    """If the file never changes no snapshot should be written."""
    snapshots_created = []

    import threading

    def _stop_after_delay():
        time.sleep(0.12)
        # Simulate KeyboardInterrupt by patching time.sleep won't work easily,
        # so we rely on max_snapshots=0 + the file never changing.
        # We use a side-channel: write the same content (hash unchanged).
        pass

    # Run with max_snapshots=0 but force-stop via a thread raising in main
    # Instead, just call with max_snapshots=1 and never change the file;
    # the watch loop won't reach max_snapshots so we cap via interval count.
    # Simplest: use a subclass-friendly approach with a short timeout.
    import signal

    def _raise_keyboard(*_):
        raise KeyboardInterrupt

    old = signal.signal(signal.SIGALRM, _raise_keyboard)
    signal.alarm(1)
    try:
        watch_env_file(
            env_file,
            snapshot_dir,
            interval=0.1,
            on_snapshot=snapshots_created.append,
            max_snapshots=0,
        )
    except KeyboardInterrupt:
        pass
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)

    assert snapshots_created == []
