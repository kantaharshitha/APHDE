from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

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


def _seed_range(n_days: int) -> list[date]:
    today = date.today()
    return [today - timedelta(days=i) for i in range(n_days)][::-1]


def _print_latest(user_id: int, conn) -> None:
    row = DecisionRunRepository(conn).latest(user_id)
    if row is None:
        print("No decision generated")
        return
    import json

    recs = json.loads(row["recommendations_json"])
    rec_conf = json.loads(row["recommendation_confidence_json"])
    trace = json.loads(row["trace_json"])
    print(
        "alignment="
        f"{row['alignment_score']:.2f} "
        f"risk={row['risk_score']:.2f} "
        f"alignment_conf={row['alignment_confidence']:.2f}"
    )
    print(f"confidence_version={row['confidence_version']}")
    if "context_applied" in row.keys():
        context_version = row["context_version"] if "context_version" in row.keys() else "ctx_v1"
        print(
            f"context_applied={bool(row['context_applied'])} "
            f"context_version={context_version}"
        )
    print(f"triggered_rules={trace.get('triggered_rules', [])}")
    if trace.get("context_notes"):
        print(f"context_notes={trace.get('context_notes')}")
    if recs:
        conf_map = {item["id"]: item["confidence"] for item in rec_conf}
        top_conf = conf_map.get(recs[0]["id"], "N/A")
        print(
            f"top_recommendation={recs[0]['id']} "
            f"(conf={top_conf}) -> {recs[0]['action']}"
        )
    print("---")


def main() -> None:
    db_path = Path(__file__).resolve().parents[1] / "aphde.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        user_repo = UserRepository(conn)
        goal_repo = GoalRepository(conn)
        weight_repo = WeightLogRepository(conn)
        calorie_repo = CalorieLogRepository(conn)
        workout_repo = WorkoutLogRepository(conn)
        context_repo = ContextInputRepository(conn)

        user_id = user_repo.create()

        # Scenario 1: weight loss drift + low compliance
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})
        for idx, d in enumerate(_seed_range(10)):
            weight_repo.add(user_id, d, 78.0 + (0.08 * idx))
            calorie_repo.add(user_id, d, 2600 if idx % 2 == 0 else 2200, 120)
            workout_repo.add(
                user_id,
                d,
                "upper" if idx % 2 == 0 else "lower",
                50,
                5000 + idx * 30,
                8.6 if idx % 3 == 0 else 7.8,
                planned_flag=True,
                completed_flag=False if idx % 4 == 0 else True,
            )
        run_evaluation(user_id, str(db_path))
        print("Scenario 1: Weight Loss Drift + Low Adherence")
        _print_latest(user_id, conn)

        # Scenario 2: recomposition with imbalance
        goal_repo.set_active_goal(user_id, GoalType.RECOMPOSITION, {})
        for idx, d in enumerate(_seed_range(8)):
            weight_repo.add(user_id, d, 78.5 + (0.01 * (-1) ** idx))
            workout_repo.add(user_id, d, "push", 55, 5200 + idx * 20, 7.6, True, True)
        run_evaluation(user_id, str(db_path))
        print("Scenario 2: Recomposition with Imbalance")
        _print_latest(user_id, conn)

        # Scenario 3: strength gain fatigue accumulation
        goal_repo.set_active_goal(user_id, GoalType.STRENGTH_GAIN, {})
        for idx, d in enumerate(_seed_range(9)):
            workout_repo.add(user_id, d, "lower", 70, 6000 + idx * 80, 8.8 if idx > 3 else 8.1, True, True)
            weight_repo.add(user_id, d, 79.0 + 0.02 * idx)
        run_evaluation(user_id, str(db_path))
        print("Scenario 3: Strength Gain Fatigue")
        _print_latest(user_id, conn)

        # Scenario 4: same data, compare no-context vs luteal context
        goal_repo.set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})
        for idx, d in enumerate(_seed_range(7)):
            weight_repo.add(user_id, d, 77.8 + (0.05 * idx))
            calorie_repo.add(user_id, d, 2350, 125)
            workout_repo.add(user_id, d, "upper", 52, 5050 + idx * 40, 8.0, True, True)

        run_evaluation(user_id, str(db_path))
        print("Scenario 4A: Weight Loss without Context")
        _print_latest(user_id, conn)

        context_repo.add(
            user_id=user_id,
            log_date=date.today(),
            context_type="cycle",
            payload={"phase": "luteal", "source": "demo_script"},
        )
        run_evaluation(user_id, str(db_path))
        print("Scenario 4B: Weight Loss with Luteal Context")
        _print_latest(user_id, conn)


if __name__ == "__main__":
    main()
