from __future__ import annotations

from datetime import date

from aphde.app.services.insights_service import load_insights_view
from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition


def _seed_user_with_logs(db_path) -> int:
    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})

        today = date.today()
        for i in range(10):
            weight_repo.add(user_id, today, 78.0 + (0.02 * i))
            calorie_repo.add(user_id, today, 2400, 120)
            workout_repo.add(user_id, today, "upper", 50, 5000 + (40 * i), 8.0, True, True)
    return user_id


def test_insights_service_returns_expected_contract(tmp_path) -> None:
    db_path = tmp_path / "insights.db"
    init_db(db_path)
    user_id = _seed_user_with_logs(db_path)

    run_evaluation(
        user_id=user_id,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )
    run_evaluation(
        user_id=user_id,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )

    payload = load_insights_view(user_id=user_id, db_path=str(db_path), recent_limit=20)
    assert "latest" in payload
    assert "weekly_insight" in payload
    assert "stagnation_alerts" in payload
    assert "drift_detection" in payload
    assert "trends" in payload
    assert "recent_runs" in payload

    trends = payload["trends"]
    assert "weight" in trends
    assert "recovery" in trends
    assert "compliance" in trends
    assert "overload" in trends

