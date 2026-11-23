from datetime import UTC, datetime

from app.accounts.otp import (
    OTP_LENGTH,
    expiry_time,
    generate_code,
    hash_code,
    verify_code,
)


def test_generate_code_is_correct_length_and_digits():
    code = generate_code()
    assert len(code) == OTP_LENGTH
    assert code.isdigit()


def test_verify_code_accepts_correct_code():
    code = generate_code()
    assert verify_code(code, hash_code(code)) is True


def test_verify_code_rejects_wrong_code():
    code = generate_code()
    wrong = "000000" if code != "000000" else "111111"
    assert verify_code(wrong, hash_code(code)) is False


def test_expiry_time_is_in_the_future():
    assert expiry_time() > datetime.now(UTC)
