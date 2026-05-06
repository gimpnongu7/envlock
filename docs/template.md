# Template Generation

`envlock` can generate a `.env.template` file from any existing `.env` file.
The template preserves all key names (and optionally comments) while stripping
sensitive values, making it safe to commit to version control.

## Usage

### Python API

```python
from pathlib import Path
from envlock.template import generate_template, write_template

# Get template as a string
content = generate_template(Path(".env"))
print(content)

# Write template to disk
write_template(
    Path(".env"),
    Path(".env.template"),
    placeholder="CHANGEME",  # optional default fill-in
    overwrite=True,
)
```

### Options

| Parameter | Type | Default | Description |
|---|---|---|---|
| `include_comments` | `bool` | `True` | Preserve `#` comment lines |
| `placeholder` | `str` | `""` | Value written after `=` for every key |
| `overwrite` | `bool` | `False` | Replace output file if it already exists |

## Example

Given `.env`:

```
# database
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=supersecret
```

Running `generate_template` produces:

```
# database
DB_HOST=
DB_PORT=
SECRET_KEY=
```

With `placeholder="CHANGEME"`:

```
# database
DB_HOST=CHANGEME
DB_PORT=CHANGEME
SECRET_KEY=CHANGEME
```

## Notes

- Lines that do not match the `KEY=value` pattern are preserved verbatim.
- A `TemplateError` is raised if the source file does not exist or if the
  output file already exists and `overwrite=False`.
