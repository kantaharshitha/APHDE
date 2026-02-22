from __future__ import annotations

import sqlite3
from datetime import date


class WorkoutLogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(
        self,
        user_id: int,
        log_date: date,
        session_type: str,
        duration_min: int,
        volume_load: float | None = None,
        avg_rpe: float | None = None,
        planned_flag: bool = True,
        completed_flag: bool = True,
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO workout_logs (
                user_id, log_date, session_type, duration_min, volume_load, avg_rpe, planned_flag, completed_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                log_date.isoformat(),
                session_type,
                duration_min,
                volume_load,
                avg_rpe,
                int(planned_flag),
                int(completed_flag),
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def list_recent(self, user_id: int, days: int = 28) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT * FROM workout_logs
            WHERE user_id = ?
              AND log_date >= date('now', ?)
            ORDER BY log_date ASC
            """,
            (user_id, f"-{days} day"),
        ).fetchall()
