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
        context_applied: bool = False,
        context_version: str = "ctx_v1",
        context_json: dict | None = None,
        input_signature_hash: str | None = None,
        output_hash: str | None = None,
        determinism_verified: bool | None = None,
        governance_json: dict | None = None,
        engine_version: str = "v1",
    ) -> int:
        recommendation_confidence = recommendation_confidence or []
        confidence_breakdown = confidence_breakdown or {}
        context_json = context_json or {}
        governance_json = governance_json or {}
        cursor = self.conn.execute(
            """
            INSERT INTO decision_runs (
                user_id, goal_id, run_date, alignment_score, risk_score, alignment_confidence,
                recommendations_json, recommendation_confidence_json, confidence_breakdown_json,
                confidence_version, context_applied, context_version, context_json,
                input_signature_hash, output_hash, determinism_verified, governance_json,
                trace_json, engine_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                int(context_applied),
                context_version,
                json.dumps(context_json),
                input_signature_hash,
                output_hash,
                int(determinism_verified) if determinism_verified is not None else None,
                json.dumps(governance_json),
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

    def get_by_id(self, user_id: int, decision_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM decision_runs WHERE user_id = ? AND id = ? LIMIT 1",
            (user_id, decision_id),
        ).fetchone()

    def list_recent(self, user_id: int, limit: int = 10) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT * FROM decision_runs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
