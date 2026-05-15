# Stash

The **stash** feature lets you temporarily shelve the current state of your `.env` file without creating a named snapshot. This is useful when you need to quickly switch context or experiment without polluting your snapshot history.

## Concepts

- The stash is a **stack** — you can push multiple times and pop them back in LIFO order.
- Each stash entry has an auto-generated id like `stash@{0}`, `stash@{1}`, etc.
- Stash entries are stored inside a `.stash/` subdirectory of your snapshot directory.

## API

### `stash_push(env_file, base_dir, message=None) -> str`

Saves the current `.env` to the stash stack. Returns the new entry id.

```python
from envlock.stash import stash_push

entry_id = stash_push(Path(".env"), Path(".envlock"), message="before refactor")
print(entry_id)  # stash@{0}
```

### `stash_pop(env_file, base_dir) -> str`

Restores the most recent stash entry to the `.env` file and removes it from the stack.

```python
from envlock.stash import stash_pop

stash_pop(Path(".env"), Path(".envlock"))
```

### `stash_list(base_dir) -> list[dict]`

Returns all stash entries, newest first. Each entry contains `id`, `message`, and `file`.

```python
from envlock.stash import stash_list

for entry in stash_list(Path(".envlock")):
    print(entry["id"], entry["message"])
```

### `stash_drop(base_dir, index_pos=0) -> str`

Discards a stash entry by position (0 = most recent) without restoring it.

```python
from envlock.stash import stash_drop

stash_drop(Path(".envlock"), index_pos=0)
```

## Errors

- `StashError` is raised when the stash is empty, the env file is missing, or an invalid index is given.

## Notes

- Stash entries are not encrypted even if you use `secure_snapshot`. Avoid stashing files with highly sensitive values in shared environments.
- Stash state is local only and not included in archives created by `envlock.archive`.
