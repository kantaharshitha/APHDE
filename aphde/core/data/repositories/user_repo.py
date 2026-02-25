from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any


class UserRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(
        self,
        *,
        email: str | None = None,
        password_hash: str | None = None,
        display_name: str | None = None,
        is_active: bool = True,
    ) -> int:
        created_at = datetime.now(UTC).isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO users (email, password_hash, display_name, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                email,
                password_hash,
                display_name,
                created_at,
                1 if is_active else 0,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def exists(self, user_id: int) -> bool:
        row = self.conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        return row is not None

    def get_by_id(self, user_id: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def get_by_email(self, email: str) -> sqlite3.Row | None:
        normalized = email.strip().lower()
        return self.conn.execute(
            "SELECT * FROM users WHERE lower(email) = ? LIMIT 1",
            (normalized,),
        ).fetchone()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def touch_last_login(self, user_id: int) -> None:
        self.conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now(UTC).isoformat(), user_id),
        )
        self.conn.commit()

    def set_password_hash(self, user_id: int, password_hash: str) -> None:
        self.conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )
        self.conn.commit()

    def list_all(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()

    @staticmethod
    def row_to_identity(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": int(row["id"]),
            "email": str(row["email"]) if row["email"] is not None else None,
            "display_name": str(row["display_name"]) if row["display_name"] is not None else None,
            "is_active": bool(row["is_active"]) if row["is_active"] is not None else True,
        }
