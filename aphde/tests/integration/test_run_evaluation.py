from datetime import date
import json

from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType
from core.services.run_evaluation import run_evaluation


def test_run_evaluation_persists_decision_with_trace(tmp_path) -> None:
    db_path = tmp_path / "eval.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.STRENGTH_GAIN, {})

        today = date.today()
        weight_repo.add(user_id, today, 79.0)
        weight_repo.add(user_id, today, 79.2)
        calorie_repo.add(user_id, today, 2500, 150)
        workout_repo.add(user_id, today, "upper", 55, 5100.0, 8.2)
        workout_repo.add(user_id, today, "lower", 60, 5300.0, 8.4)

    decision_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    assert decision_id > 0

    with get_connection(db_path) as conn:
        decision_repo = DecisionRunRepository(conn)
        latest = decision_repo.latest(user_id)

    assert latest is not None
    assert latest["alignment_score"] >= 0
    assert latest["risk_score"] >= 0
    assert "alignment_confidence" in latest.keys()
    assert "recommendation_confidence_json" in latest.keys()
    assert "confidence_breakdown_json" in latest.keys()
    assert "confidence_version" in latest.keys()
    assert 0.0 <= latest["alignment_confidence"] <= 1.0
    assert latest["confidence_version"] == "conf_v1"

    rec_conf = json.loads(latest["recommendation_confidence_json"])
    conf_breakdown = json.loads(latest["confidence_breakdown_json"])
    trace = json.loads(latest["trace_json"])
    assert isinstance(rec_conf, list)
    assert "components" in conf_breakdown
    assert "alignment_confidence" in trace
    assert "recommendation_confidence" in trace
    assert "confidence_breakdown" in trace
    assert "confidence_version" in trace
