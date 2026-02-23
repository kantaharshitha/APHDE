from __future__ import annotations

import json
from typing import Any

from core.data.db import get_connection
from core.data.repositories.decision_repo import DecisionRunRepository
from core.governance.history_analyzer import summarize_history
from core.governance.version_diff import diff_runs
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition


def trigger_evaluation(*, user_id: int, db_path: str) -> int:
    return run_evaluation(
        user_id=user_id,
        db_path=db_path,
        domain_definition=HealthDomainDefinition(),
    )


def _safe_json_load(raw: str | None, fallback: Any) -> Any:
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return fallback


def _row_to_run_snapshot(row: Any) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "alignment_score": float(row["alignment_score"]),
        "risk_score": float(row["risk_score"]),
        "alignment_confidence": float(row["alignment_confidence"]) if "alignment_confidence" in row.keys() else 0.0,
        "recommendations": _safe_json_load(row["recommendations_json"], []),
        "recommendation_confidence": (
            _safe_json_load(row["recommendation_confidence_json"], [])
            if "recommendation_confidence_json" in row.keys()
            else []
        ),
        "confidence_breakdown": (
            _safe_json_load(row["confidence_breakdown_json"], {})
            if "confidence_breakdown_json" in row.keys()
            else {}
        ),
        "confidence_version": row["confidence_version"] if "confidence_version" in row.keys() else "conf_v1",
        "context_applied": bool(row["context_applied"]) if "context_applied" in row.keys() else False,
        "context_version": row["context_version"] if "context_version" in row.keys() else "ctx_v1",
        "context_json": _safe_json_load(row["context_json"], {}) if "context_json" in row.keys() else {},
        "trace": _safe_json_load(row["trace_json"], {}),
        "engine_version": row["engine_version"],
        "input_signature_hash": row["input_signature_hash"] if "input_signature_hash" in row.keys() else None,
        "output_hash": row["output_hash"] if "output_hash" in row.keys() else None,
        "determinism_verified": row["determinism_verified"] if "determinism_verified" in row.keys() else None,
    }


def load_dashboard_data(*, user_id: int, db_path: str, recent_limit: int = 25) -> dict[str, Any]:
    with get_connection(db_path) as conn:
        repo = DecisionRunRepository(conn)
        latest = repo.latest(user_id)
        rows = repo.list_recent(user_id=user_id, limit=recent_limit)

    if latest is None:
        return {"latest": None, "recent_runs": []}
    return {"latest": _row_to_run_snapshot(latest), "recent_runs": [_row_to_run_snapshot(r) for r in rows]}


def build_recommendation_table(run: dict[str, Any]) -> list[dict[str, Any]]:
    conf_map = {item.get("id"): item.get("confidence") for item in run.get("recommendation_confidence", [])}
    rows: list[dict[str, Any]] = []
    for rec in run.get("recommendations", []):
        rows.append(
            {
                "Priority": rec.get("priority"),
                "Category": rec.get("category"),
                "Action": rec.get("action"),
                "Expected Effect": rec.get("expected_effect"),
                "Base Conf": rec.get("confidence"),
                "Model Conf": conf_map.get(rec.get("id")),
                "Reasons": ", ".join(rec.get("reason_codes", [])),
            }
        )
    return rows


def build_governance_view(run: dict[str, Any]) -> dict[str, Any]:
    trace = run.get("trace", {})
    governance = trace.get("governance", {}) if isinstance(trace, dict) else {}
    determinism_verified = run.get("determinism_verified")
    if determinism_verified is None:
        determinism_status = "Unknown (No baseline)"
    elif int(determinism_verified) == 1:
        determinism_status = "Verified"
    else:
        determinism_status = "Mismatch"

    return {
        "determinism_status": determinism_status,
        "output_hash": run.get("output_hash") or governance.get("output_hash"),
        "input_signature_hash": run.get("input_signature_hash") or governance.get("input_signature_hash"),
        "determinism_reason": governance.get("determinism_reason"),
        "baseline_decision_id": governance.get("baseline_decision_id"),
        "domain_name": trace.get("domain_name", "unknown") if isinstance(trace, dict) else "unknown",
        "domain_version": trace.get("domain_version", "unknown") if isinstance(trace, dict) else "unknown",
    }


def build_diff_payload(*, recent_runs: list[dict[str, Any]], run_a_id: int, run_b_id: int) -> dict[str, Any]:
    row_map = {int(row["id"]): row for row in recent_runs}
    return diff_runs(row_map[run_a_id], row_map[run_b_id])


def build_history_payload(*, recent_runs: list[dict[str, Any]]) -> dict[str, Any]:
    runs = []
    for run in recent_runs:
        trace = run.get("trace", {})
        runs.append(
            {
                "alignment_score": run.get("alignment_score"),
                "alignment_confidence": run.get("alignment_confidence"),
                "context_applied": run.get("context_applied"),
                "triggered_rules": trace.get("triggered_rules", []) if isinstance(trace, dict) else [],
                "determinism_verified": run.get("determinism_verified"),
            }
        )
    return summarize_history(runs)
