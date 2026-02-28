from __future__ import annotations

from datetime import date

from aphde.app.services.ui_data_service import load_dashboard_view, load_run_diff
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
        for i in range(7):
            weight_repo.add(user_id, today, 78.0 + (0.03 * i))
            calorie_repo.add(user_id, today, 2400, 120)
            workout_repo.add(user_id, today, "upper", 50, 5000 + (50 * i), 8.1, True, True)

    return user_id


def test_load_dashboard_view_returns_empty_contract_when_no_runs(tmp_path) -> None:
    db_path = tmp_path / "ui_empty.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_id = UserRepository(conn).create()

    payload = load_dashboard_view(user_id=user_id, db_path=str(db_path), recent_limit=10)
    assert payload["latest"] is None
    assert payload["recent_runs"] == []
    assert payload["recommendation_rows"] == []
    assert payload["governance"] == {}
    assert payload["history_payload"] == {}
    assert payload["trace"] == {}
    assert payload["confidence_breakdown"] == {}
    assert payload["context_json"] == {}
    assert payload["context_notes"] == []
    assert payload["confidence_version"] == "conf_v1"
    assert payload["context_version"] == "ctx_v1"


def test_load_dashboard_view_and_diff_have_expected_ui_contract(tmp_path) -> None:
    db_path = tmp_path / "ui_contract.db"
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

    payload = load_dashboard_view(user_id=user_id, db_path=str(db_path), recent_limit=10)
    latest = payload["latest"]
    recent_runs = payload["recent_runs"]
    assert latest is not None
    assert len(recent_runs) >= 2

    assert "alignment_score" in latest
    assert "alignment_confidence" in latest
    assert "risk_score" in latest
    assert "engine_version" in latest
    assert "output_hash" in latest
    assert "determinism_verified" in latest

    assert isinstance(payload["recommendation_rows"], list)
    assert isinstance(payload["governance"], dict)
    assert isinstance(payload["history_payload"], dict)
    assert isinstance(payload["trace"], dict)

    options = [int(item["id"]) for item in recent_runs]
    diff = load_run_diff(recent_runs=recent_runs, run_a_id=options[1], run_b_id=options[0])
    assert "score_delta" in diff
    assert "recommendation_changes" in diff
    assert "context_changes" in diff

