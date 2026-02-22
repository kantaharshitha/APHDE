from datetime import date

from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType


if __name__ == "__main__":
    init_db()
    with get_connection() as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {"target_weight_kg": 72})

        today = date.today()
        weight_repo.add(user_id, today, 78.5)
        calorie_repo.add(user_id, today, 2200, 130)
        workout_repo.add(user_id, today, "upper", 60, 5500.0, 7.5)

        print(f"Seeded demo data for user_id={user_id}")
