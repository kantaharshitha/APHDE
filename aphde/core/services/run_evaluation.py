from __future__ import annotations

import json
from typing import Any

from core.data.db import get_connection
from core.data.migrations.migrate_v2_confidence import run_migration
from core.data.migrations.migrate_v3_context import run_migration as run_context_migration
from core.data.migrations.migrate_v5_governance import run_migration as run_governance_migration
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.context_repo import ContextInputRepository
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.engine.contracts import DomainDefinition, DomainLogs, validate_domain_definition
from core.decision.engine import run_decision_engine
from core.governance.determinism import verify_determinism
from core.governance.hashing import canonical_sha256


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


def _build_input_signature_payload(
    *,
    user_id: int,
    goal_id: int,
    goal_type: str,
    target: dict[str, Any],
    domain_name: str,
    domain_version: str,
    context_input: dict[str, Any] | None,
    weight_logs: list[dict[str, Any]],
    calorie_logs: list[dict[str, Any]],
    workout_logs: list[dict[str, Any]],
    previous_alignment_confidence: float | None,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "goal_id": goal_id,
        "goal_type": goal_type,
        "target": target,
        "domain_name": domain_name,
        "domain_version": domain_version,
        "context_input": context_input,
        "weight_logs": weight_logs,
        "calorie_logs": calorie_logs,
        "workout_logs": workout_logs,
        "previous_alignment_confidence": previous_alignment_confidence,
        "history": history,
    }


def _build_output_payload(result: Any) -> dict[str, Any]:
    return {
        "alignment_score": result.alignment_score,
        "risk_score": result.risk_score,
        "alignment_confidence": result.alignment_confidence,
        "recommendations": result.recommendations,
        "recommendation_confidence": result.recommendation_confidence,
        "confidence_breakdown": result.confidence_breakdown,
        "confidence_version": result.confidence_version,
        "context_applied": result.context_applied,
        "context_version": result.context_version,
        "context_json": result.context_json,
        "trace": result.trace,
        "engine_version": result.engine_version,
    }


def _output_payload_from_row(row: Any) -> dict[str, Any]:
    trace_payload = json.loads(row["trace_json"]) if row["trace_json"] else {}
    # Governance block is generated after scoring and should not influence
    # deterministic comparison of core evaluation outputs.
    if isinstance(trace_payload, dict):
        trace_payload.pop("governance", None)
    return {
        "alignment_score": float(row["alignment_score"]),
        "risk_score": float(row["risk_score"]),
        "alignment_confidence": float(row["alignment_confidence"]) if "alignment_confidence" in row.keys() else 0.0,
        "recommendations": json.loads(row["recommendations_json"]) if row["recommendations_json"] else [],
        "recommendation_confidence": (
            json.loads(row["recommendation_confidence_json"])
            if "recommendation_confidence_json" in row.keys() and row["recommendation_confidence_json"]
            else []
        ),
        "confidence_breakdown": (
            json.loads(row["confidence_breakdown_json"])
            if "confidence_breakdown_json" in row.keys() and row["confidence_breakdown_json"]
            else {}
        ),
        "confidence_version": row["confidence_version"] if "confidence_version" in row.keys() else "conf_v1",
        "context_applied": bool(row["context_applied"]) if "context_applied" in row.keys() else False,
        "context_version": row["context_version"] if "context_version" in row.keys() else "ctx_v1",
        "context_json": json.loads(row["context_json"]) if "context_json" in row.keys() and row["context_json"] else {},
        "trace": trace_payload,
        "engine_version": row["engine_version"],
    }


def run_evaluation(
    user_id: int,
    db_path: str = "aphde.db",
    domain_definition: DomainDefinition | None = None,
) -> int:
    # Ensure older local databases are upgraded before accessing V2 confidence fields.
    run_migration(db_path)
    run_context_migration(db_path)
    run_governance_migration(db_path)
    if domain_definition is None:
        raise ValueError("domain_definition is required")
    domain = validate_domain_definition(domain_definition)
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

        input_signature_payload = _build_input_signature_payload(
            user_id=user_id,
            goal_id=int(goal["id"]),
            goal_type=normalized_goal_type,
            target=target,
            domain_name=domain.domain_name(),
            domain_version=domain.domain_version(),
            context_input=context_input,
            weight_logs=weight_logs,
            calorie_logs=calorie_logs,
            workout_logs=workout_logs,
            previous_alignment_confidence=previous_alignment_confidence,
            history=history,
        )
        output_payload = _build_output_payload(result)
        input_signature_hash = canonical_sha256(input_signature_payload)

        comparable_row = next(
            (
                row
                for row in recent_decisions
                if "input_signature_hash" in row.keys()
                and row["input_signature_hash"] == input_signature_hash
                and "output_hash" in row.keys()
                and row["output_hash"]
            ),
            None,
        )
        baseline_payload = _output_payload_from_row(comparable_row) if comparable_row is not None else None
        determinism = verify_determinism(
            input_signature_payload=input_signature_payload,
            output_payload=output_payload,
            baseline_output_payload=baseline_payload,
        )
        governance_json = {
            "determinism_reason": determinism.determinism_reason,
            "baseline_decision_id": int(comparable_row["id"]) if comparable_row is not None else None,
        }
        result.trace["governance"] = {
            "input_signature_hash": determinism.input_signature_hash,
            "output_hash": determinism.output_hash,
            "determinism_verified": determinism.determinism_verified,
            "determinism_reason": determinism.determinism_reason,
            "baseline_decision_id": governance_json["baseline_decision_id"],
        }

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
            input_signature_hash=determinism.input_signature_hash,
            output_hash=determinism.output_hash,
            determinism_verified=determinism.determinism_verified,
            governance_json=governance_json,
            trace=result.trace,
            engine_version=result.engine_version,
        )
