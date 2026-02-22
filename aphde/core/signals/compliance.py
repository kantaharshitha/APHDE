from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def compliance_ratio(completed_planned: int, total_planned: int) -> float | None:
    if total_planned <= 0:
        return None
    ratio = completed_planned / total_planned
    return max(0.0, min(1.0, ratio))


def compliance_from_workout_logs(workout_logs: Iterable[dict[str, Any]]) -> float | None:
    planned = 0
    completed = 0
    for row in workout_logs:
        planned_flag = bool(row.get("planned_flag", False))
        completed_flag = bool(row.get("completed_flag", False))
        if planned_flag:
            planned += 1
            if completed_flag:
                completed += 1
    return compliance_ratio(completed, planned)
