from __future__ import annotations

import json
from typing import Any

from core.data.db import get_connection
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.decision.engine import run_decision_engine
from core.models.enums import GoalType
from core.signals.aggregator import build_signal_bundle
from core.strategies.factory import StrategyFactory


def _row_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def run_evaluation(user_id: int, db_path: str = "aphde.db") -> int:
    with get_connection(db_path) as conn:
        goal_repo = GoalRepository(conn)
        decision_repo = DecisionRunRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        goal = goal_repo.get_active_goal(user_id)
        if goal is None:
            raise ValueError("No active goal found for user")

        goal_type = GoalType(goal["goal_type"])
        target = json.loads(goal["target_json"]) if goal["target_json"] else {}

        weight_logs = _row_to_dicts(weight_repo.list_recent(user_id, days=28))
        calorie_logs = _row_to_dicts(calorie_repo.list_recent(user_id, days=28))
        workout_logs = _row_to_dicts(workout_repo.list_recent(user_id, days=28))

        weight_values = [float(row["weight_kg"]) for row in weight_logs]
        signals = build_signal_bundle(
            weight_values=weight_values,
            workout_logs=workout_logs,
            window_days=7,
        )

        strategy = StrategyFactory.create(goal_type)
        result = run_decision_engine(
            strategy=strategy,
            signals=signals,
            target=target,
            input_summary={
                "user_id": user_id,
                "goal_id": int(goal["id"]),
                "goal_type": goal["goal_type"],
                "weight_log_count": len(weight_logs),
                "calorie_log_count": len(calorie_logs),
                "workout_log_count": len(workout_logs),
            },
        )

        return decision_repo.create(
            user_id=user_id,
            goal_id=int(goal["id"]),
            alignment_score=result.alignment_score,
            risk_score=result.risk_score,
            recommendations=result.recommendations,
            trace=result.trace,
            engine_version=result.engine_version,
        )
