# Git Hooks Integration

envlock can automatically snapshot your `.env` file whenever you switch branches
or pull changes, using standard Git hooks.

## Supported Hooks

| Hook | Trigger |
|---|---|
| `post-checkout` | After `git checkout` or `git switch` |
| `post-merge` | After `git merge` or `git pull` |

## Installing Hooks

From the root of your repository:

```bash
envlock hooks install
```

This writes executable shell scripts into `.git/hooks/`. Each script calls
`envlock snapshot --label auto-<hook-name>` so you get a timestamped snapshot
before your working tree changes.

## Uninstalling Hooks

```bash
envlock hooks uninstall
```

envlock will **only** remove hooks it created. If a hook was placed there by
another tool the command will exit with an error rather than silently deleting
foreign scripts.

## Checking Status

```bash
envlock hooks status
```

Prints which hooks are currently managed by envlock:

```
post-checkout  installed
post-merge     not installed
```

## Safety Notes

- Hooks are stored inside `.git/` and are **not** committed to version control.
- If a hook file already exists and was not created by envlock, installation
  will fail loudly. Remove or rename the existing hook first.
- The generated hook calls envlock with `|| true` so a snapshot failure will
  never block your Git workflow.

## Python API

```python
from pathlib import Path
from envlock.hooks import install_hooks, uninstall_hooks, hooks_status

repo = Path(".")
install_hooks(repo)
print(hooks_status(repo))  # {'post-checkout': True, 'post-merge': True}
uninstall_hooks(repo)
```

### Installing individual hooks

If you only want a specific hook, pass a list of hook names:

```python
install_hooks(repo, hooks=["post-checkout"])
```

This is useful when, for example, you only care about branch switches and not
merges.
