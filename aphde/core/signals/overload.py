from __future__ import annotations

from collections.abc import Iterable
from statistics import pstdev
from typing import Any

from core.signals.trend import linear_regression_slope


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def progressive_overload_from_volumes(volumes: list[float]) -> float | None:
    if len(volumes) < 2:
        return None

    improvements = sum(1 for i in range(1, len(volumes)) if volumes[i] > volumes[i - 1])
    improved_sessions_ratio = improvements / (len(volumes) - 1)

    first = volumes[0]
    last = volumes[-1]
    if abs(first) < 1e-9:
        trend_norm = 0.5
    else:
        pct_change = (last - first) / abs(first)
        # Map [-10%, +10%] into [0, 1], then clamp.
        trend_norm = _clamp01((pct_change + 0.10) / 0.20)

    mean = sum(volumes) / len(volumes)
    if abs(mean) < 1e-9:
        consistency = 0.0
    else:
        consistency = _clamp01(1.0 - (pstdev(volumes) / abs(mean)))

    score = 0.5 * improved_sessions_ratio + 0.3 * trend_norm + 0.2 * consistency
    return _clamp01(score)


def progressive_overload_from_workout_logs(workout_logs: Iterable[dict[str, Any]]) -> float | None:
    volumes = [float(row["volume_load"]) for row in workout_logs if row.get("volume_load") is not None]
    # Fall back to trend-only signal when there are at least 2 points but near-flat improvements.
    base = progressive_overload_from_volumes(volumes)
    if base is None:
        return None

    slope = linear_regression_slope(volumes)
    if slope is None:
        return base

    mean = sum(volumes) / len(volumes)
    slope_boost = 0.0 if abs(mean) < 1e-9 else _clamp01(slope / (abs(mean) * 0.02))
    return _clamp01(0.85 * base + 0.15 * slope_boost)
