from __future__ import annotations

import json
from typing import Any

from core.data.db import get_connection
from core.data.migrations.migrate_v2_confidence import run_migration
from core.data.migrations.migrate_v3_context import run_migration as run_context_migration
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.context_repo import ContextInputRepository
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.engine.contracts import DomainDefinition, DomainLogs, validate_domain_definition
from core.decision.engine import run_decision_engine
from domains.health.domain_definition import HealthDomainDefinition


def _row_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _history_from_decision_rows(rows: list[Any]) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    for row in rows:
        trace_raw = row["trace_json"] if "trace_json" in row.keys() else None
        if not trace_raw:
            continue
        try:
            trace = json.loads(trace_raw)
        except (TypeError, json.JSONDecodeError):
            continue
        history.append(
            {
                "deviations": trace.get("deviations", trace.get("computed_signals", {}).get("deviations", {})),
                "triggered_rules": trace.get("triggered_rules", []),
            }
        )
    return history


def run_evaluation(
    user_id: int,
    db_path: str = "aphde.db",
    domain_definition: DomainDefinition | None = None,
) -> int:
    # Ensure older local databases are upgraded before accessing V2 confidence fields.
    run_migration(db_path)
    run_context_migration(db_path)
    domain = validate_domain_definition(domain_definition or HealthDomainDefinition())
    with get_connection(db_path) as conn:
        goal_repo = GoalRepository(conn)
        decision_repo = DecisionRunRepository(conn)
        context_repo = ContextInputRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        goal = goal_repo.get_active_goal(user_id)
        if goal is None:
            raise ValueError("No active goal found for user")

        normalized_goal_type = domain.normalize_goal_type(str(goal["goal_type"]))
        target = json.loads(goal["target_json"]) if goal["target_json"] else {}
        context_input = None
        latest_context = context_repo.latest_for_user(user_id=user_id, context_type="cycle")
        if latest_context is not None:
            try:
                context_input = json.loads(latest_context["context_payload_json"])
            except (TypeError, json.JSONDecodeError):
                context_input = None

        weight_logs = _row_to_dicts(weight_repo.list_recent(user_id, days=28))
        calorie_logs = _row_to_dicts(calorie_repo.list_recent(user_id, days=28))
        workout_logs = _row_to_dicts(workout_repo.list_recent(user_id, days=28))

        signals = domain.compute_signals(
            DomainLogs(
                items={
                    "weight_logs": weight_logs,
                    "calorie_logs": calorie_logs,
                    "workout_logs": workout_logs,
                },
                metadata={"user_id": user_id},
            ),
            config=domain.get_domain_config(),
        )

        strategy = domain.get_strategy(normalized_goal_type)
        recent_decisions = decision_repo.list_recent(user_id=user_id, limit=10)
        history = _history_from_decision_rows(recent_decisions)
        previous_alignment_confidence = None
        if recent_decisions:
            first_row = recent_decisions[0]
            if "alignment_confidence" in first_row.keys():
                previous_alignment_confidence = float(first_row["alignment_confidence"])

        result = run_decision_engine(
            strategy=strategy,
            signals=signals,
            target=target,
            input_summary={
                "user_id": user_id,
                "goal_id": int(goal["id"]),
                "goal_type": normalized_goal_type,
                "weight_log_count": len(weight_logs),
                "calorie_log_count": len(calorie_logs),
                "workout_log_count": len(workout_logs),
            },
            history=history,
            previous_alignment_confidence=previous_alignment_confidence,
            context_input=context_input,
        )
        result.trace["domain_name"] = domain.domain_name()
        result.trace["domain_version"] = domain.domain_version()

        return decision_repo.create(
            user_id=user_id,
            goal_id=int(goal["id"]),
            alignment_score=result.alignment_score,
            risk_score=result.risk_score,
            alignment_confidence=result.alignment_confidence,
            recommendations=result.recommendations,
            recommendation_confidence=result.recommendation_confidence,
            confidence_breakdown=result.confidence_breakdown,
            confidence_version=result.confidence_version,
            context_applied=result.context_applied,
            context_version=result.context_version,
            context_json=result.context_json,
            trace=result.trace,
            engine_version=result.engine_version,
        )
