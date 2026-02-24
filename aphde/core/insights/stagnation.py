from __future__ import annotations

from datetime import date
from typing import Any


def _severity_rank(level: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(level, 3)


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


def detect_stagnation_alerts(
    *,
    recent_runs: list[dict[str, Any]],
    min_points: int = 5,
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []

    trend_values = _extract_signal_series(recent_runs, "trend_slope")
    if len(trend_values) >= min_points:
        avg_abs = sum(abs(v) for v in trend_values[-min_points:]) / min_points
        if avg_abs <= 0.01:
            alerts.append(
                {
                    "alert_id": "stagnation_weight_trend",
                    "type": "weight_trend_stagnation",
                    "severity": "medium",
                    "message": "Weight trend slope has remained near-flat over the configured window.",
                    "recommendation": "Adjust adherence or calorie consistency and re-check in 5 days.",
                    "confidence": 0.82,
                    "triggered_at": date.today().isoformat(),
                    "version": "stg_v1",
                }
            )

    overload_values = _extract_signal_series(recent_runs, "progressive_overload_score")
    if len(overload_values) >= 4:
        spread = max(overload_values[-4:]) - min(overload_values[-4:])
        if spread <= 0.04:
            alerts.append(
                {
                    "alert_id": "stagnation_overload_flat",
                    "type": "overload_flatline",
                    "severity": "medium",
                    "message": "Progressive overload score has remained flat across recent windows.",
                    "recommendation": "Introduce a controlled overload progression adjustment next cycle.",
                    "confidence": 0.79,
                    "triggered_at": date.today().isoformat(),
                    "version": "stg_v1",
                }
            )

    compliance_values = _extract_signal_series(recent_runs, "compliance_ratio")
    if len(compliance_values) >= min_points:
        if (compliance_values[0] - compliance_values[-1]) >= 0.08:
            alerts.append(
                {
                    "alert_id": "stagnation_compliance_drift",
                    "type": "compliance_drift",
                    "severity": "high",
                    "message": "Compliance ratio shows a persistent negative drift.",
                    "recommendation": "Prioritize habit stabilization before raising threshold strictness.",
                    "confidence": 0.86,
                    "triggered_at": date.today().isoformat(),
                    "version": "stg_v1",
                }
            )

    recovery_values = _extract_signal_series(recent_runs, "recovery_index")
    if len(recovery_values) >= 3:
        last_three = recovery_values[-3:]
        if all(v < 0.50 for v in last_three):
            alerts.append(
                {
                    "alert_id": "stagnation_low_recovery_persistent",
                    "type": "persistent_low_recovery",
                    "severity": "high",
                    "message": "Recovery index remains below floor for three consecutive windows.",
                    "recommendation": "Reduce training stress and improve recovery inputs before progression.",
                    "confidence": 0.88,
                    "triggered_at": date.today().isoformat(),
                    "version": "stg_v1",
                }
            )

    alerts.sort(key=lambda item: (_severity_rank(str(item.get("severity"))), str(item.get("type"))))
    return alerts
