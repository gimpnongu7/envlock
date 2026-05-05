"""Tests for envlock.encrypt module."""

import pytest

try:
    from envlock.encrypt import (
        derive_key,
        encrypt_content,
        decrypt_content,
        DecryptionError,
        CRYPTO_AVAILABLE,
    )
except ImportError:
    CRYPTO_AVAILABLE = False

pytest.importorskip("cryptography", reason="cryptography not installed")


def test_derive_key_deterministic():
    key1, salt = derive_key("secret")
    key2, _ = derive_key("secret", salt)
    assert key1 == key2


def test_derive_key_different_salt():
    key1, salt1 = derive_key("secret")
    key2, salt2 = derive_key("secret")
    assert salt1 != salt2
    assert key1 != key2


def test_encrypt_decrypt_roundtrip():
    original = "DB_HOST=localhost\nDB_PORT=5432\n"
    encrypted = encrypt_content(original, "mypassphrase")
    assert isinstance(encrypted, bytes)
    assert original.encode() not in encrypted
    decrypted = decrypt_content(encrypted, "mypassphrase")
    assert decrypted == original


def test_decrypt_wrong_passphrase():
    encrypted = encrypt_content("SECRET=abc", "correct")
    with pytest.raises(DecryptionError):
        decrypt_content(encrypted, "wrong")


def test_encrypt_produces_different_ciphertext():
    text = "KEY=value"
    enc1 = encrypt_content(text, "pass")
    enc2 = encrypt_content(text, "pass")
    # different salts each time
    assert enc1 != enc2


def test_decrypt_corrupted_data():
    encrypted = encrypt_content("KEY=val", "pass")
    corrupted = encrypted[:16] + b"\x00" * (len(encrypted) - 16)
    with pytest.raises(DecryptionError):
        decrypt_content(corrupted, "pass")
