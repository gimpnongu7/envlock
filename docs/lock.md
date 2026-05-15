# Env File Locking

envlock supports locking `.env` files to prevent accidental modifications during deploys, CI runs, or shared development sessions.

## Overview

A lock is a small JSON sidecar file (`.env.lock` placed next to your `.env`) that records who locked the file and when. It is advisory — envlock commands respect the lock, but the file system itself is not made read-only.

## Commands

### Lock a file

```bash
envlock lock .env
envlock lock .env --reason "deploying to production"
```

Outputs a confirmation with the locking user, timestamp, and optional reason.

### Unlock a file

```bash
envlock unlock .env
```

Removes the lock file. Prints who originally held the lock.

### Check lock status

```bash
envlock lock-status .env
```

Shows whether the file is locked, and if so, by whom and when.

## Python API

```python
from envlock.lock import lock_env, unlock_env, is_locked, get_lock_info

# Lock with an optional reason
info = lock_env(".env", reason="ci pipeline")
print(info.locked_by, info.locked_at)

# Check programmatically
if is_locked(".env"):
    info = get_lock_info(".env")
    print(f"Locked by {info.locked_by}")

# Unlock
unlock_env(".env")
```

## Lock File Format

The lock file is stored as `.env.lock` (or `.your-file.lock`) next to the env file:

```json
{
  "env_path": "/project/.env",
  "locked_by": "alice",
  "locked_at": "2024-06-01T12:00:00+00:00",
  "reason": "deploying to production"
}
```

## Notes

- Lock files should be added to `.gitignore` unless you want to share lock state via version control.
- Attempting to lock an already-locked file raises a `LockError` with details about the existing lock.
