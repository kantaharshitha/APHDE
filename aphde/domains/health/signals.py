from __future__ import annotations

from typing import Any

from core.signals.aggregator import SignalBundle, build_signal_bundle
from domains.health.thresholds import DEFAULT_SIGNAL_WINDOW_DAYS


def compute_health_signals(logs: dict[str, list[dict[str, Any]]], config: dict[str, Any] | None = None) -> SignalBundle:
    config = config or {}
    window_days = int(config.get("window_days", DEFAULT_SIGNAL_WINDOW_DAYS))

    weight_logs = logs.get("weight_logs", [])
    workout_logs = logs.get("workout_logs", [])
    weight_values = [float(row["weight_kg"]) for row in weight_logs if "weight_kg" in row]

    return build_signal_bundle(
        weight_values=weight_values,
        workout_logs=workout_logs,
        window_days=window_days,
    )
