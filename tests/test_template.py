"""Tests for envlock.template."""

from pathlib import Path

import pytest

from envlock.template import (
    TemplateError,
    generate_template,
    write_template,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "# database config\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "\n"
        "SECRET_KEY=supersecret\n",
        encoding="utf-8",
    )
    return p


def test_generate_strips_values(env_file: Path) -> None:
    result = generate_template(env_file)
    assert "DB_HOST=" in result
    assert "localhost" not in result
    assert "supersecret" not in result


def test_generate_preserves_keys(env_file: Path) -> None:
    result = generate_template(env_file)
    for key in ("DB_HOST", "DB_PORT", "SECRET_KEY"):
        assert key in result


def test_generate_keeps_comments_by_default(env_file: Path) -> None:
    result = generate_template(env_file)
    assert "# database config" in result


def test_generate_strips_comments_when_disabled(env_file: Path) -> None:
    result = generate_template(env_file, include_comments=False)
    assert "#" not in result


def test_generate_custom_placeholder(env_file: Path) -> None:
    result = generate_template(env_file, placeholder="CHANGEME")
    assert "DB_HOST=CHANGEME" in result


def test_generate_missing_file(tmp_path: Path) -> None:
    with pytest.raises(TemplateError, match="not found"):
        generate_template(tmp_path / "missing.env")


def test_write_template_creates_file(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "subdir" / ".env.template"
    result = write_template(env_file, out)
    assert result == out
    assert out.exists()
    assert "SECRET_KEY=" in out.read_text(encoding="utf-8")


def test_write_template_no_overwrite(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / ".env.template"
    out.write_text("existing", encoding="utf-8")
    with pytest.raises(TemplateError, match="already exists"):
        write_template(env_file, out)


def test_write_template_overwrite_flag(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / ".env.template"
    out.write_text("old content", encoding="utf-8")
    write_template(env_file, out, overwrite=True)
    assert "DB_HOST" in out.read_text(encoding="utf-8")
