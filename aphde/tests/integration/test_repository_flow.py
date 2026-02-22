from datetime import date

from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType


def test_repository_flow(tmp_path) -> None:
    db_path = tmp_path / "flow.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        user_id = user_repo.create()
        goal_id = goal_repo.set_active_goal(user_id, GoalType.GENERAL_HEALTH, {"consistency_target": 0.8})

        today = date.today()
        weight_repo.add(user_id, today, 80.2)
        calorie_repo.add(user_id, today, 2300, 120)
        workout_repo.add(user_id, today, "full_body", 45)

        active_goal = goal_repo.get_active_goal(user_id)
        recent_weights = weight_repo.list_recent(user_id)

    assert goal_id > 0
    assert active_goal is not None
    assert active_goal["goal_type"] == GoalType.GENERAL_HEALTH.value
    assert len(recent_weights) == 1
