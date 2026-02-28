from __future__ import annotations

from typing import Any

from aphde.app.services.dashboard_service import (
    build_diff_payload,
    build_governance_view,
    build_history_payload,
    build_recommendation_table,
    load_dashboard_data,
)


def load_dashboard_view(*, user_id: int, db_path: str, recent_limit: int = 25) -> dict[str, Any]:
    data = load_dashboard_data(user_id=user_id, db_path=db_path, recent_limit=recent_limit)
    latest = data.get("latest")
    recent_runs = data.get("recent_runs", [])

    if latest is None:
        return {
            "latest": None,
            "recent_runs": recent_runs,
            "recommendation_rows": [],
            "governance": {},
            "history_payload": {},
            "trace": {},
            "confidence_breakdown": {},
            "context_json": {},
            "context_notes": [],
            "confidence_version": "conf_v1",
            "context_version": "ctx_v1",
        }

    trace = latest.get("trace", {})
    context_notes = trace.get("context_notes", []) if isinstance(trace, dict) else []

    return {
        "latest": latest,
        "recent_runs": recent_runs,
        "recommendation_rows": build_recommendation_table(latest),
        "governance": build_governance_view(latest),
        "history_payload": build_history_payload(recent_runs=recent_runs),
        "trace": trace,
        "confidence_breakdown": latest.get("confidence_breakdown", {}),
        "context_json": latest.get("context_json", {}),
        "context_notes": context_notes,
        "confidence_version": latest.get("confidence_version", "conf_v1"),
        "context_version": latest.get("context_version", "ctx_v1"),
    }


def load_run_diff(*, recent_runs: list[dict[str, Any]], run_a_id: int, run_b_id: int) -> dict[str, Any]:
    return build_diff_payload(recent_runs=recent_runs, run_a_id=run_a_id, run_b_id=run_b_id)

