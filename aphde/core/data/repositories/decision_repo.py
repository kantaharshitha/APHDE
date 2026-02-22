from __future__ import annotations

import json
import sqlite3
from datetime import datetime


class DecisionRunRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(
        self,
        user_id: int,
        goal_id: int,
        alignment_score: float,
        risk_score: float,
        recommendations: list[dict],
        trace: dict,
        engine_version: str = "v1",
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO decision_runs (
                user_id, goal_id, run_date, alignment_score, risk_score, recommendations_json, trace_json, engine_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                goal_id,
                datetime.utcnow().isoformat(),
                alignment_score,
                risk_score,
                json.dumps(recommendations),
                json.dumps(trace),
                engine_version,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def latest(self, user_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM decision_runs WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
