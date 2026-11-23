"""Phone OTP generation/verification (F1 onboarding, Phase 4 auth).

No real SMS gateway is wired up yet -- CLAUDE.md doesn't name one, so
sending is a pluggable function that defaults to logging the code (dev
only). Swap `send_otp` for a real provider (e.g. MSG91, which is common
for Indian phone OTP) when the founder picks one. See DECISIONS.md.
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

OTP_LENGTH = 6
OTP_TTL_MINUTES = 5
MAX_VERIFY_ATTEMPTS = 5


def generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def expiry_time() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=OTP_TTL_MINUTES)


def send_otp(phone_number: str, code: str) -> None:
    """Dev-only: prints the code instead of sending an SMS. Uses print()
    rather than the logging module so it's reliably visible in
    `docker compose logs backend` regardless of uvicorn's log
    configuration -- this is a temporary stand-in, not production
    behaviour."""
    print(f"OTP for {phone_number}: {code} (dev mode, not actually sent)", flush=True)


def verify_code(submitted_code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_code(submitted_code), code_hash)
