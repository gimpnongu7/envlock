"""Tests for envlock.lint module."""

import pytest
from pathlib import Path
from envlock.lint import lint_env_file, LintError, LintResult, LintIssue


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    yield f


def _write(env_file, content):
    env_file.write_text(content)


def test_lint_clean_file(env_file):
    _write(env_file, "APP_NAME=myapp\nDEBUG=false\n")
    result = lint_env_file(env_file)
    assert result.ok
    assert result.issues == []


def test_lint_missing_equals(env_file):
    _write(env_file, "BADLINE\n")
    result = lint_env_file(env_file)
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_lint_lowercase_key(env_file):
    _write(env_file, "my_key=value\n")
    result = lint_env_file(env_file)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_lint_duplicate_key(env_file):
    _write(env_file, "FOO=1\nFOO=2\n")
    result = lint_env_file(env_file)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_lint_key_with_space(env_file):
    _write(env_file, "MY KEY=value\n")
    result = lint_env_file(env_file)
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_lint_unclosed_quote(env_file):
    _write(env_file, 'TOKEN="abc\n')
    result = lint_env_file(env_file)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_lint_comments_and_blanks_ignored(env_file):
    _write(env_file, "# comment\n\nAPP=ok\n")
    result = lint_env_file(env_file)
    assert result.ok


def test_lint_file_not_found(tmp_path):
    with pytest.raises(LintError, match="not found"):
        lint_env_file(tmp_path / "missing.env")


def test_lint_summary_no_issues(env_file):
    _write(env_file, "KEY=value\n")
    result = lint_env_file(env_file)
    assert result.summary() == "No issues found."


def test_lint_summary_with_issues(env_file):
    _write(env_file, "bad line\n")
    result = lint_env_file(env_file)
    summary = result.summary()
    assert "issue(s)" in summary
    assert "E001" in summary


def test_lint_issue_str():
    issue = LintIssue(line=3, code="W001", message="Key is not uppercase")
    assert str(issue) == "L3 [W001] Key is not uppercase"
