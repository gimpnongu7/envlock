# Linting `.env` Files

`envlock lint` checks your `.env` file for common issues and style violations before you snapshot or commit.

## Usage

```bash
envlock lint                  # lint default .env
envlock lint --file .env.prod # lint a specific file
```

## Issue Codes

| Code  | Severity | Description                              |
|-------|----------|------------------------------------------|
| E001  | Error    | Line is missing an `=` separator         |
| E002  | Error    | Key is empty                             |
| E003  | Error    | Key contains whitespace                  |
| W001  | Warning  | Key is not uppercase                     |
| W002  | Warning  | Duplicate key defined in the same file   |
| W003  | Warning  | Possibly unclosed quote around value     |

## Example Output

```
3 issue(s) found:
  L2 [W001] Key 'my_secret' is not uppercase
  L5 [W002] Duplicate key 'API_KEY' (first seen at L3)
  L7 [E001] Missing '=' separator: 'INVALID LINE'
```

## Python API

```python
from pathlib import Path
from envlock.lint import lint_env_file

result = lint_env_file(Path(".env"))
if not result.ok:
    print(result.summary())
```

The `LintResult` object exposes:

- `result.ok` — `True` when no issues were found
- `result.issues` — list of `LintIssue(line, code, message)`
- `result.summary()` — human-readable report string

## Exit Codes

When used via the CLI, `envlock lint` exits with:

- `0` — no issues
- `1` — one or more issues found
- `2` — file not found or unreadable
