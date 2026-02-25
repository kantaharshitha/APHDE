from core.auth.passwords import hash_password, verify_password


def test_hash_and_verify_roundtrip() -> None:
    pw = "StrongPass123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)


def test_verify_password_rejects_invalid() -> None:
    hashed = hash_password("StrongPass123")
    assert not verify_password("WrongPass123", hashed)
