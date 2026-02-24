from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def _extract_signal_series(recent_runs: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for run in reversed(recent_runs):
        trace = run.get("trace", {})
        if not isinstance(trace, dict):
            continue
        signals = trace.get("computed_signals", {})
        if not isinstance(signals, dict):
            continue
        raw = signals.get(key)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def _direction(start: float, end: float, epsilon: float = 0.01) -> str:
    if (end - start) > epsilon:
        return "up"
    if (start - end) > epsilon:
        return "down"
    return "flat"


def build_weekly_insight(*, recent_runs: list[dict[str, Any]]) -> dict[str, Any]:
    window = list(reversed(recent_runs[-7:])) if recent_runs else []
    today = date.today()
    week_start = today - timedelta(days=6)

    compliance_series = _extract_signal_series(window, "compliance_ratio")
    recovery_series = _extract_signal_series(window, "recovery_index")
    volatility_series = _extract_signal_series(window, "volatility_index")
    overload_series = _extract_signal_series(window, "progressive_overload_score")

    compliance_last = compliance_series[-1] if compliance_series else 0.0
    compliance_avg = (sum(compliance_series) / len(compliance_series)) if compliance_series else 0.0
    planned_sessions = 7
    completed_sessions = int(round(planned_sessions * compliance_last))

    recovery_shift = _direction(recovery_series[0], recovery_series[-1]) if len(recovery_series) >= 2 else "flat"
    if len(volatility_series) >= 2:
        volatility_direction = "improving" if volatility_series[-1] < volatility_series[0] else "worsening"
    else:
        volatility_direction = "flat"
    overload_progress = _direction(overload_series[0], overload_series[-1]) if len(overload_series) >= 2 else "flat"

    return {
        "week_start": week_start.isoformat(),
        "week_end": today.isoformat(),
        "planned_sessions": planned_sessions,
        "completed_sessions": completed_sessions,
        "compliance_pct": round(compliance_last * 100.0, 2),
        "compliance_avg_pct": round(compliance_avg * 100.0, 2),
        "recovery_shift": recovery_shift,
        "volatility_direction": volatility_direction,
        "overload_progress": overload_progress,
        "data_sufficient": len(window) >= 3,
    }
