from __future__ import annotations

from core.data.db import get_connection
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository


def run_evaluation(user_id: int, db_path: str = "aphde.db") -> int:
    """Placeholder orchestration path for upcoming engine integration."""
    with get_connection(db_path) as conn:
        goal_repo = GoalRepository(conn)
        decision_repo = DecisionRunRepository(conn)

        goal = goal_repo.get_active_goal(user_id)
        if goal is None:
            raise ValueError("No active goal found for user")

        placeholder_trace = {
            "status": "placeholder",
            "message": "Decision engine not yet wired",
            "goal_id": goal["id"],
        }
        return decision_repo.create(
            user_id=user_id,
            goal_id=int(goal["id"]),
            alignment_score=50.0,
            risk_score=50.0,
            recommendations=[],
            trace=placeholder_trace,
        )
