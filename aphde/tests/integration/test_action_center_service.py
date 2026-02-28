from __future__ import annotations

from datetime import date

from aphde.app.services.action_center_service import load_action_center_view
from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition


def _seed_user_with_data(db_path) -> int:
    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})
        today = date.today()
        for i in range(7):
            weight_repo.add(user_id, today, 78.0 + (0.03 * i))
            calorie_repo.add(user_id, today, 2400, 120)
            workout_repo.add(user_id, today, "upper", 50, 5000 + (50 * i), 8.1, True, True)
    return user_id


def test_action_center_returns_empty_contract_without_runs(tmp_path) -> None:
    db_path = tmp_path / "action_empty.db"
    init_db(db_path)
    with get_connection(db_path) as conn:
        user_id = UserRepository(conn).create()

    payload = load_action_center_view(user_id=user_id, db_path=str(db_path), recent_limit=10)
    assert payload["latest"] is None
    assert payload["tomorrow_plan"] is None
    assert payload["risk_alert"] is None
    assert payload["recent_runs"] == []


def test_action_center_builds_tomorrow_plan_after_evaluation(tmp_path) -> None:
    db_path = tmp_path / "action_populated.db"
    init_db(db_path)
    user_id = _seed_user_with_data(db_path)

    run_evaluation(
        user_id=user_id,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )

    payload = load_action_center_view(user_id=user_id, db_path=str(db_path), recent_limit=10)
    plan = payload["tomorrow_plan"]
    assert payload["latest"] is not None
    assert plan is not None
    assert "action_id" in plan
    assert "action" in plan
    assert "reason" in plan
    assert "confidence" in plan
    assert "severity" in plan
    assert "expected_impact" in plan

