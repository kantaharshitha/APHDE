from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def recovery_index(
    density_ratio: float,
    high_rpe_streak_norm: float,
    rest_gap_penalty_norm: float,
) -> float:
    risk = (
        0.5 * _clamp01(density_ratio)
        + 0.3 * _clamp01(high_rpe_streak_norm)
        + 0.2 * _clamp01(rest_gap_penalty_norm)
    )
    return _clamp01(1.0 - risk)


def recovery_from_workout_logs(
    workout_logs: Iterable[dict[str, Any]],
    window_days: int = 7,
    high_rpe_threshold: float = 8.0,
) -> float | None:
    logs = list(workout_logs)
    if not logs:
        return None

    sessions = len(logs)
    density_ratio = sessions / max(1, window_days)

    longest_high_rpe_streak = 0
    current_high_rpe_streak = 0
    longest_training_streak = 0
    current_training_streak = 0

    for row in logs:
        avg_rpe = row.get("avg_rpe")
        if avg_rpe is not None and float(avg_rpe) >= high_rpe_threshold:
            current_high_rpe_streak += 1
        else:
            current_high_rpe_streak = 0
        longest_high_rpe_streak = max(longest_high_rpe_streak, current_high_rpe_streak)

        current_training_streak += 1
        longest_training_streak = max(longest_training_streak, current_training_streak)

    high_rpe_streak_norm = min(1.0, longest_high_rpe_streak / 3.0)
    rest_gap_penalty_norm = min(1.0, max(0.0, longest_training_streak - 2.0) / 5.0)

    return recovery_index(density_ratio, high_rpe_streak_norm, rest_gap_penalty_norm)
