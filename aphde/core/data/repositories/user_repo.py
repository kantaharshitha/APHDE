from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class UserRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self) -> int:
        cursor = self.conn.execute(
            "INSERT INTO users (created_at) VALUES (?)",
            (datetime.now(UTC).isoformat(),),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def exists(self, user_id: int) -> bool:
        row = self.conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        return row is not None
