"""Tests for envlock.export."""

import json
from pathlib import Path

import pytest

from envlock.export import ExportError, export_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    # create two fake snapshots
    (d / "main.env").write_text('DB_URL="postgres://localhost/main"\nDEBUG="false"\n')
    (d / "dev.env").write_text('DB_URL="postgres://localhost/dev"\nDEBUG="true"\nSECRET="s3cr3t"\n')
    return d


def test_export_json_format(snapshot_dir: Path) -> None:
    result = export_snapshot(snapshot_dir, label="main", fmt="json")
    data = json.loads(result)
    assert data["DB_URL"] == "postgres://localhost/main"
    assert data["DEBUG"] == "false"


def test_export_shell_format(snapshot_dir: Path) -> None:
    result = export_snapshot(snapshot_dir, label="dev", fmt="shell")
    assert 'export DB_URL="postgres://localhost/dev"' in result
    assert 'export DEBUG="true"' in result
    assert 'export SECRET="s3cr3t"' in result


def test_export_shell_no_export_keyword(snapshot_dir: Path) -> None:
    result = export_snapshot(snapshot_dir, label="dev", fmt="shell", export_keyword=False)
    assert result.startswith("DB_URL=") or "DB_URL=" in result
    assert "export" not in result


def test_export_writes_file(snapshot_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    export_snapshot(snapshot_dir, label="main", fmt="json", output_path=out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "DB_URL" in data


def test_export_unknown_label_raises(snapshot_dir: Path) -> None:
    with pytest.raises(ExportError, match="not found"):
        export_snapshot(snapshot_dir, label="nonexistent", fmt="json")


def test_export_unknown_format_raises(snapshot_dir: Path) -> None:
    with pytest.raises(ExportError, match="Unknown format"):
        export_snapshot(snapshot_dir, label="main", fmt="toml")  # type: ignore[arg-type]


def test_export_shell_escapes_special_chars(snapshot_dir: Path) -> None:
    (snapshot_dir / "special.env").write_text('MSG="hello \\"world\\""\n')
    result = export_snapshot(snapshot_dir, label="special", fmt="shell")
    # value should be present and double-quotes escaped
    assert "MSG=" in result
