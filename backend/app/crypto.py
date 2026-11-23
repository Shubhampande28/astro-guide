"""Encrypts birth data at rest (CLAUDE.md principle 4: DPDP compliance).

Fernet (AES-128-CBC + HMAC, via the `cryptography` package) rather than a
hand-rolled scheme. The key comes from `ENCRYPTION_KEY`; .env.example ships
a dev-only key -- production must set its own (see README/.env.example).
"""

from functools import lru_cache

from cryptography.fernet import Fernet

from app.config import get_settings


@lru_cache
def _fernet() -> Fernet:
    return Fernet(get_settings().encryption_key.encode())


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
