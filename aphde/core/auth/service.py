from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.data.repositories.user_repo import UserRepository

from .passwords import hash_password, verify_password


class AuthError(ValueError):
    pass


@dataclass(frozen=True)
class AuthIdentity:
    id: int
    email: str
    display_name: str | None

    def to_session_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
        }


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def signup(self, *, email: str, password: str, display_name: str | None = None) -> AuthIdentity:
        normalized_email = _normalize_email(email)
        _validate_password(password)

        if self.user_repo.email_exists(normalized_email):
            raise AuthError("Email already registered.")

        hashed = hash_password(password)
        user_id = self.user_repo.create(
            email=normalized_email,
            password_hash=hashed,
            display_name=(display_name.strip() if display_name else None),
            is_active=True,
        )

        row = self.user_repo.get_by_id(user_id)
        if row is None:
            raise AuthError("Failed to create account.")
        return _row_to_identity(row)

    def login(self, *, email: str, password: str) -> AuthIdentity:
        normalized_email = _normalize_email(email)
        row = self.user_repo.get_by_email(normalized_email)

        if row is None:
            raise AuthError("Invalid email or password.")
        if int(row["is_active"]) != 1:
            raise AuthError("Account is inactive.")

        password_hash = row["password_hash"]
        if not isinstance(password_hash, str) or not verify_password(password, password_hash):
            raise AuthError("Invalid email or password.")

        user_id = int(row["id"])
        self.user_repo.touch_last_login(user_id)
        refreshed = self.user_repo.get_by_id(user_id)
        if refreshed is None:
            raise AuthError("Account lookup failed.")
        return _row_to_identity(refreshed)


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not normalized or "@" not in normalized:
        raise AuthError("Enter a valid email address.")
    return normalized


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters.")


def _row_to_identity(row: Any) -> AuthIdentity:
    email_val = row["email"]
    if not isinstance(email_val, str) or not email_val:
        raise AuthError("Account email is missing.")
    display_name = row["display_name"] if row["display_name"] is not None else None
    return AuthIdentity(
        id=int(row["id"]),
        email=email_val,
        display_name=(str(display_name) if display_name else None),
    )
