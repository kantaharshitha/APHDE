from __future__ import annotations

from typing import Any

from aphde.app.services.dashboard_service import load_dashboard_data
from core.data.db import get_connection
from core.data.repositories.weight_repo import WeightLogRepository
from core.insights.stagnation import detect_stagnation_alerts
from core.insights.trend_views import build_series_with_slope
from core.insights.weekly_summary import build_weekly_insight


def _signal_series(recent_runs: list[dict[str, Any]], signal_key: str) -> list[float]:
    values: list[float] = []
    for run in reversed(recent_runs):
        trace = run.get("trace", {})
        if not isinstance(trace, dict):
            continue
        computed = trace.get("computed_signals", {})
        if not isinstance(computed, dict):
            continue
        raw = computed.get(signal_key)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def _drift_detection(*, compliance_series: list[float], recovery_series: list[float], alerts: list[dict[str, Any]]) -> dict[str, Any]:
    compliance_drift = False
    if len(compliance_series) >= 5:
        compliance_drift = (compliance_series[0] - compliance_series[-1]) >= 0.08

    recovery_drift = False
    if len(recovery_series) >= 4:
        recent = recovery_series[-4:]
        recovery_drift = all(v < 0.5 for v in recent)

    return {
        "compliance_drift": compliance_drift,
        "recovery_drift": recovery_drift,
        "active_alert_count": len(alerts),
        "has_high_severity_alert": any(str(a.get("severity", "")).lower() == "high" for a in alerts),
    }


def load_insights_view(*, user_id: int, db_path: str, recent_limit: int = 42) -> dict[str, Any]:
    data = load_dashboard_data(user_id=user_id, db_path=db_path, recent_limit=recent_limit)
    recent_runs = data.get("recent_runs", [])
    alerts = detect_stagnation_alerts(recent_runs=recent_runs)
    weekly = build_weekly_insight(recent_runs=recent_runs)

    compliance_series = _signal_series(recent_runs, "compliance_ratio")
    recovery_series = _signal_series(recent_runs, "recovery_index")
    overload_series = _signal_series(recent_runs, "progressive_overload_score")

    with get_connection(db_path) as conn:
        weight_rows = WeightLogRepository(conn).list_recent(user_id=user_id, days=42)
    weight_values = [float(row["weight_kg"]) for row in weight_rows]

    trends = {
        "weight": build_series_with_slope(weight_values),
        "recovery": build_series_with_slope(recovery_series),
        "compliance": build_series_with_slope(compliance_series),
        "overload": build_series_with_slope(overload_series),
    }
    drift = _drift_detection(
        compliance_series=compliance_series,
        recovery_series=recovery_series,
        alerts=alerts,
    )

    return {
        "latest": data.get("latest"),
        "weekly_insight": weekly,
        "stagnation_alerts": alerts,
        "drift_detection": drift,
        "trends": trends,
        "recent_runs": recent_runs,
    }

