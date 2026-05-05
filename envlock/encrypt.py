"""Optional encryption support for snapshot files."""

import base64
import hashlib
import os
from typing import Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class EncryptionError(Exception):
    pass


class DecryptionError(Exception):
    pass


def _require_crypto() -> None:
    if not CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package is required for encryption support. "
            "Install it with: pip install cryptography"
        )


def derive_key(passphrase: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """Derive a Fernet key from a passphrase. Returns (key, salt)."""
    _require_crypto()
    if salt is None:
        salt = os.urandom(16)
    key_bytes = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=200_000)
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return fernet_key, salt


def encrypt_content(content: str, passphrase: str) -> bytes:
    """Encrypt a string and return raw bytes (salt + token)."""
    _require_crypto()
    key, salt = derive_key(passphrase)
    f = Fernet(key)
    token = f.encrypt(content.encode())
    return salt + token


def decrypt_content(data: bytes, passphrase: str) -> str:
    """Decrypt bytes produced by encrypt_content."""
    _require_crypto()
    salt, token = data[:16], data[16:]
    key, _ = derive_key(passphrase, salt)
    f = Fernet(key)
    try:
        return f.decrypt(token).decode()
    except InvalidToken as exc:
        raise DecryptionError("Invalid passphrase or corrupted snapshot.") from exc
