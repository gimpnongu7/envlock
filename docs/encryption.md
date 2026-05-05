# Snapshot Encryption

envlock supports optional AES-based encryption for snapshot files, keeping sensitive credentials safe at rest.

## Requirements

Install the extra dependency:

```bash
pip install cryptography
```

## How It Works

1. A random 16-byte salt is generated per snapshot.
2. Your passphrase is stretched via **PBKDF2-HMAC-SHA256** (200 000 iterations) into a 32-byte key.
3. The key is used with **Fernet** (AES-128-CBC + HMAC-SHA256) to encrypt the snapshot payload.
4. The output file contains `salt (16 bytes) || fernet_token` and is saved with the `.envlock.enc` extension.

Because a fresh salt is generated every time, two snapshots of identical content produce different ciphertext.

## CLI Usage (planned)

```bash
# Create an encrypted snapshot
envlock snapshot --encrypt --label prod

# Restore an encrypted snapshot
envlock restore snapshots/20240101T120000_prod.envlock.enc --decrypt
```

You will be prompted for your passphrase interactively, or you can set the `ENVLOCK_PASSPHRASE` environment variable.

## Security Notes

- Never commit your passphrase or the `ENVLOCK_PASSPHRASE` variable to version control.
- Encrypted snapshots (`.envlock.enc`) are excluded from git via `.gitignore` by default.
- The hash stored inside the encrypted metadata allows you to verify integrity after decryption.
