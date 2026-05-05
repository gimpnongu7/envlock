# envlock

> Utility to snapshot and restore `.env` file states across project branches

---

## Installation

```bash
pip install envlock
```

Or with pipx:

```bash
pipx install envlock
```

---

## Usage

**Save a snapshot of your current `.env`:**

```bash
envlock save my-feature-branch
```

**Restore a previously saved snapshot:**

```bash
envlock restore my-feature-branch
```

**List all saved snapshots:**

```bash
envlock list
```

**Delete a snapshot:**

```bash
envlock delete my-feature-branch
```

Snapshots are stored locally in a `.envlock/` directory at the project root. Add `.envlock/` to your `.gitignore` to keep secrets out of version control.

```bash
echo ".envlock/" >> .gitignore
```

---

## Why envlock?

Switching branches often means manually swapping out `.env` values. `envlock` automates that workflow — snapshot your environment before switching, restore it when you come back.

---

## License

[MIT](LICENSE)