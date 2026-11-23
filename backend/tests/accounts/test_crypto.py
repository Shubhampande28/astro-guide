from app.crypto import decrypt, encrypt


def test_round_trip():
    assert decrypt(encrypt("1990-05-15")) == "1990-05-15"


def test_ciphertext_does_not_contain_plaintext():
    secret = "1990-05-15"
    assert secret not in encrypt(secret)
