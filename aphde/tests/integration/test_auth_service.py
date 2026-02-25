from __future__ import annotations

from pathlib import Path

from core.auth.service import AuthError, AuthService
from core.data.db import get_connection, init_db
from core.data.migrations.migrate_v7_multi_user_auth import run_migration as run_v7_migration
from core.data.repositories.user_repo import UserRepository


def test_signup_and_login_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "auth.db"
    init_db(db_path)
    run_v7_migration(db_path)

    with get_connection(db_path) as conn:
        repo = UserRepository(conn)
        service = AuthService(repo)

        created = service.signup(email="user@example.com", password="StrongPass123", display_name="User")
        assert created.email == "user@example.com"
        assert created.display_name == "User"

        logged_in = service.login(email="user@example.com", password="StrongPass123")
        assert logged_in.id == created.id
        assert logged_in.email == created.email


def test_signup_rejects_duplicate_email(tmp_path: Path) -> None:
    db_path = tmp_path / "auth.db"
    init_db(db_path)
    run_v7_migration(db_path)

    with get_connection(db_path) as conn:
        repo = UserRepository(conn)
        service = AuthService(repo)
        service.signup(email="user@example.com", password="StrongPass123")

        try:
            service.signup(email="user@example.com", password="StrongPass123")
            assert False, "Expected duplicate signup failure"
        except AuthError as exc:
            assert "already" in str(exc).lower()


def test_login_rejects_wrong_password(tmp_path: Path) -> None:
    db_path = tmp_path / "auth.db"
    init_db(db_path)
    run_v7_migration(db_path)

    with get_connection(db_path) as conn:
        repo = UserRepository(conn)
        service = AuthService(repo)
        service.signup(email="user@example.com", password="StrongPass123")

        try:
            service.login(email="user@example.com", password="WrongPass123")
            assert False, "Expected invalid login"
        except AuthError as exc:
            assert "invalid" in str(exc).lower()
