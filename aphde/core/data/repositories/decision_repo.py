from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime


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
        alignment_confidence: float = 0.0,
        recommendation_confidence: list[dict] | None = None,
        confidence_breakdown: dict | None = None,
        confidence_version: str = "conf_v1",
        engine_version: str = "v1",
    ) -> int:
        recommendation_confidence = recommendation_confidence or []
        confidence_breakdown = confidence_breakdown or {}
        cursor = self.conn.execute(
            """
            INSERT INTO decision_runs (
                user_id, goal_id, run_date, alignment_score, risk_score, alignment_confidence,
                recommendations_json, recommendation_confidence_json, confidence_breakdown_json,
                confidence_version, trace_json, engine_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                goal_id,
                datetime.now(UTC).isoformat(),
                alignment_score,
                risk_score,
                alignment_confidence,
                json.dumps(recommendations),
                json.dumps(recommendation_confidence),
                json.dumps(confidence_breakdown),
                confidence_version,
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
