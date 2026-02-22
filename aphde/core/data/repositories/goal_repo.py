from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime

from core.models.enums import GoalType


class GoalRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def set_active_goal(self, user_id: int, goal_type: GoalType, target: dict) -> int:
        today = date.today().isoformat()
        self.conn.execute("UPDATE goals SET is_active = 0, active_to = ? WHERE user_id = ? AND is_active = 1", (today, user_id))
        cursor = self.conn.execute(
            """
            INSERT INTO goals (user_id, goal_type, target_json, active_from, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (user_id, goal_type.value, json.dumps(target), today, datetime.now(UTC).isoformat()),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def get_active_goal(self, user_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM goals WHERE user_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
