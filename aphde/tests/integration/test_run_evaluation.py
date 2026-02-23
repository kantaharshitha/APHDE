from datetime import date
import json

from core.data.db import get_connection, init_db
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.context_repo import ContextInputRepository
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
    recs = json.loads(latest["recommendations_json"])
    rec_ids = {item["id"] for item in recs}
    rec_conf_ids = {item["id"] for item in rec_conf}
    assert rec_ids == rec_conf_ids


def test_run_evaluation_uses_previous_confidence_for_smoothing(tmp_path) -> None:
    db_path = tmp_path / "eval_smooth.db"
    init_db(db_path)

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
            workout_repo.add(user_id, today, "upper", 50, 5000 + 50 * i, 8.1, True, True)

    first_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    second_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    assert second_id > first_id

    with get_connection(db_path) as conn:
        rows = DecisionRunRepository(conn).list_recent(user_id=user_id, limit=2)
        latest = rows[0]
        latest_trace = json.loads(latest["trace_json"])

    assert latest_trace["confidence_breakdown"]["smoothing"]["previous_used"] is True


def test_run_evaluation_persists_and_traces_cycle_context(tmp_path) -> None:
    db_path = tmp_path / "eval_context.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)
        context_repo = ContextInputRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})

        today = date.today()
        for i in range(7):
            weight_repo.add(user_id, today, 78.0 + (0.03 * i))
            calorie_repo.add(user_id, today, 2400, 120)
            workout_repo.add(user_id, today, "upper", 50, 5000 + 50 * i, 8.1, True, True)

        context_repo.add(
            user_id=user_id,
            log_date=today,
            context_type="cycle",
            payload={"phase": "luteal", "source": "integration_test"},
        )

    decision_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    assert decision_id > 0

    with get_connection(db_path) as conn:
        latest = DecisionRunRepository(conn).latest(user_id)

    assert latest is not None
    assert "context_applied" in latest.keys()
    assert "context_version" in latest.keys()
    assert "context_json" in latest.keys()
    assert int(latest["context_applied"]) == 1
    assert latest["context_version"] == "ctx_v1"

    context_json = json.loads(latest["context_json"])
    assert context_json["metadata"]["context_type"] == "cycle"
    assert context_json["metadata"]["phase"] == "luteal"
    assert "modulated_thresholds" in context_json

    trace = json.loads(latest["trace_json"])
    assert trace["context_applied"] is True
    assert trace["context_version"] == "ctx_v1"
    assert isinstance(trace["context_notes"], list)
    assert len(trace["context_notes"]) > 0


def test_run_evaluation_is_stable_across_repeated_runs_with_same_context(tmp_path) -> None:
    db_path = tmp_path / "eval_context_determinism.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)
        context_repo = ContextInputRepository(conn)

        user_id = user_repo.create()
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})

        today = date.today()
        for i in range(7):
            weight_repo.add(user_id, today, 78.0 + (0.03 * i))
            calorie_repo.add(user_id, today, 2400, 120)
            workout_repo.add(user_id, today, "upper", 50, 5000 + 50 * i, 8.1, True, True)

        context_repo.add(
            user_id=user_id,
            log_date=today,
            context_type="cycle",
            payload={"phase": "luteal", "source": "integration_test"},
        )

    first_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    second_id = run_evaluation(user_id=user_id, db_path=str(db_path))
    assert second_id > first_id

    with get_connection(db_path) as conn:
        rows = DecisionRunRepository(conn).list_recent(user_id=user_id, limit=2)
        latest = rows[0]
        previous = rows[1]

    # Stable deterministic outputs (excluding run metadata and smoothing trace internals).
    assert latest["alignment_score"] == previous["alignment_score"]
    assert latest["risk_score"] == previous["risk_score"]
    assert latest["recommendations_json"] == previous["recommendations_json"]
    assert latest["context_applied"] == previous["context_applied"]
    assert latest["context_version"] == previous["context_version"]
    assert latest["context_json"] == previous["context_json"]

    latest_trace = json.loads(latest["trace_json"])
    previous_trace = json.loads(previous["trace_json"])
    assert latest_trace["confidence_breakdown"]["smoothing"]["previous_used"] is True
    assert previous_trace["confidence_breakdown"]["smoothing"]["previous_used"] is False
    assert latest["alignment_confidence"] >= previous["alignment_confidence"]
