from __future__ import annotations

from typing import Any

from app.services.dashboard_service import load_dashboard_data
from core.data.db import get_connection
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.guidance.tomorrow_plan import build_tomorrow_plan


def _signal_series(recent_runs: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for run in reversed(recent_runs):
        trace = run.get("trace", {})
        if not isinstance(trace, dict):
            continue
        computed = trace.get("computed_signals", {})
        if not isinstance(computed, dict):
            continue
        raw = computed.get(key)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def _risk_level_and_message(*, rules: list[str]) -> tuple[str, str]:
    count = len(rules)
    if count >= 4:
        return "High", "Training fatigue is accumulating faster than recovery."
    if count >= 2:
        return "Moderate", "Multiple stress signals detected. Recovery support is recommended."
    if count == 1:
        return "Low", "A single stress signal is present. Monitor closely during next sessions."
    return "Stable", "System stable. No elevated stress signals detected."


def _high_rpe_streak(*, user_id: int, db_path: str, days: int = 28, threshold: float = 8.0) -> int:
    with get_connection(db_path) as conn:
        workouts = WorkoutLogRepository(conn).list_recent(user_id=user_id, days=days)
    streak = 0
    for row in reversed(workouts):
        avg_rpe = row["avg_rpe"]
        if avg_rpe is None:
            break
        if float(avg_rpe) >= threshold:
            streak += 1
        else:
            break
    return streak


def _build_action_explainability(*, latest: dict[str, Any], recent_runs: list[dict[str, Any]], user_id: int, db_path: str) -> dict[str, Any]:
    recovery = _signal_series(recent_runs, "recovery_index")
    compliance = _signal_series(recent_runs, "compliance_ratio")
    recovery_summary = "Recovery trend unavailable."
    compliance_summary = "Compliance trend unavailable."

    if len(recovery) >= 2:
        recovery_summary = f"Recovery index declined from {recovery[0]:.2f} -> {recovery[-1]:.2f}" if recovery[-1] < recovery[0] else f"Recovery index remained stable around {recovery[-1]:.2f}"
    if len(compliance) >= 2:
        drop_pct = (compliance[0] - compliance[-1]) * 100.0
        if drop_pct > 0:
            compliance_summary = f"Compliance dropped by {drop_pct:.0f}% over recent runs."
        else:
            compliance_summary = f"Compliance remained stable near {compliance[-1] * 100:.0f}%."

    rpe_streak = _high_rpe_streak(user_id=user_id, db_path=db_path)
    if rpe_streak > 0:
        rpe_summary = f"High RPE recorded for {rpe_streak} consecutive sessions."
    else:
        rpe_summary = "No high-RPE streak detected in recent sessions."

    return {
        "recovery_summary": recovery_summary,
        "rpe_summary": rpe_summary,
        "compliance_summary": compliance_summary,
    }


def load_action_center_view(*, user_id: int, db_path: str, recent_limit: int = 28) -> dict[str, Any]:
    data = load_dashboard_data(user_id=user_id, db_path=db_path, recent_limit=recent_limit)
    latest = data.get("latest")
    recent_runs = data.get("recent_runs", [])

    if latest is None:
        return {
            "latest": None,
            "tomorrow_plan": None,
            "risk_alert": None,
            "recent_runs": recent_runs,
        }

    plan = build_tomorrow_plan(latest_run=latest, recent_runs=recent_runs)
    trace = latest.get("trace", {}) if isinstance(latest.get("trace"), dict) else {}
    rules = trace.get("triggered_rules", [])
    risk_level, risk_message = _risk_level_and_message(rules=rules)
    risk_alert = {
        "level": risk_level,
        "message": risk_message,
        "rules": rules,
    }
    explainability = _build_action_explainability(
        latest=latest,
        recent_runs=recent_runs,
        user_id=user_id,
        db_path=db_path,
    )

    return {
        "latest": latest,
        "tomorrow_plan": plan,
        "risk_alert": risk_alert,
        "why_this_action": explainability,
        "recent_runs": recent_runs,
    }
