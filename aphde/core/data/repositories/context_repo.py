from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime
from typing import Any


class ContextInputRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, user_id: int, log_date: date, context_type: str, payload: dict[str, Any]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO context_inputs (user_id, log_date, context_type, context_payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                log_date.isoformat(),
                context_type,
                json.dumps(payload),
                datetime.now(UTC).isoformat(),
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def latest_for_user(self, user_id: int, context_type: str = "cycle") -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT * FROM context_inputs
            WHERE user_id = ? AND context_type = ?
            ORDER BY log_date DESC, id DESC
            LIMIT 1
            """,
            (user_id, context_type),
        ).fetchone()
