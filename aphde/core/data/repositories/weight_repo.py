from __future__ import annotations

import sqlite3
from datetime import date


class WeightLogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, user_id: int, log_date: date, weight_kg: float) -> int:
        cursor = self.conn.execute(
            "INSERT INTO weight_logs (user_id, log_date, weight_kg) VALUES (?, ?, ?)",
            (user_id, log_date.isoformat(), weight_kg),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def list_recent(self, user_id: int, days: int = 28) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT * FROM weight_logs
            WHERE user_id = ?
              AND log_date >= date('now', ?)
            ORDER BY log_date ASC
            """,
            (user_id, f"-{days} day"),
        ).fetchall()
