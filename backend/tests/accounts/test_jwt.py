import pytest

from app.accounts.jwt import InvalidTokenError, create_access_token, decode_access_token


def test_round_trip():
    token = create_access_token(user_id=42)
    assert decode_access_token(token) == 42


def test_tampered_token_rejected():
    token = create_access_token(user_id=42)
    # Flip a character inside the signature segment (after the last '.'),
    # but not the very last character of the token: the final base64
    # character of a 256-bit HMAC encodes some unused padding bits that
    # decoders ignore, so changing only that character can leave the
    # decoded signature bytes unchanged and make this test flaky.
    signature_start = token.rindex(".") + 1
    target_index = signature_start + (len(token) - signature_start) // 2
    flipped_char = "a" if token[target_index] != "a" else "b"
    tampered = token[:target_index] + flipped_char + token[target_index + 1 :]
    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered)


def test_garbage_token_rejected():
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-real-token")
