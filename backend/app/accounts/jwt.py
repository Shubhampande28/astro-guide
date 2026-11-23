"""JWT access tokens, issued after OTP verification."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    pass


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_minutes)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError) as e:
        raise InvalidTokenError("Invalid or expired token") from e
