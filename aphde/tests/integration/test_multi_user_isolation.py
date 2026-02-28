from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from aphde.app.services.dashboard_service import load_dashboard_data
from core.data.db import get_connection, init_db
from core.data.migrations.migrate_v2_confidence import run_migration as run_v2_migration
from core.data.migrations.migrate_v3_context import run_migration as run_v3_migration
from core.data.migrations.migrate_v5_governance import run_migration as run_v5_migration
from core.data.migrations.migrate_v7_multi_user_auth import run_migration as run_v7_migration
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.decision_repo import DecisionRunRepository
from core.data.repositories.goal_repo import GoalRepository
from core.data.repositories.user_repo import UserRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository
from core.models.enums import GoalType
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition


def _bootstrap_db(db_path: Path) -> None:
    init_db(db_path)
    run_v2_migration(db_path)
    run_v3_migration(db_path)
    run_v5_migration(db_path)
    run_v7_migration(db_path)


def _seed_user_with_decision(db_path: Path, weight_base: float) -> tuple[int, int]:
    with get_connection(db_path) as conn:
        user_id = UserRepository(conn).create()
        GoalRepository(conn).set_active_goal(user_id, GoalType.WEIGHT_LOSS, {})
        today = date(2026, 2, 25)
        for i in range(12):
            WeightLogRepository(conn).add(user_id, today, weight_base + (0.03 * i))
            CalorieLogRepository(conn).add(user_id, today, 2400, 120)
            WorkoutLogRepository(conn).add(user_id, today, "upper", 50, 5000 + (40 * i), 8.0, True, True)

    decision_id = run_evaluation(
        user_id=user_id,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )
    return user_id, decision_id


def test_dashboard_data_is_user_scoped(tmp_path: Path) -> None:
    db_path = tmp_path / "isolation.db"
    _bootstrap_db(db_path)

    user_a, _ = _seed_user_with_decision(db_path, 78.0)
    user_b, _ = _seed_user_with_decision(db_path, 88.0)

    payload_a = load_dashboard_data(user_id=user_a, db_path=str(db_path), recent_limit=10)
    payload_b = load_dashboard_data(user_id=user_b, db_path=str(db_path), recent_limit=10)

    assert payload_a["latest"] is not None
    assert payload_b["latest"] is not None
    assert payload_a["latest"]["id"] != payload_b["latest"]["id"]

    ids_a = {row["id"] for row in payload_a["recent_runs"]}
    ids_b = {row["id"] for row in payload_b["recent_runs"]}
    assert ids_a.isdisjoint(ids_b)


def test_decision_get_by_id_is_user_scoped(tmp_path: Path) -> None:
    db_path = tmp_path / "isolation.db"
    _bootstrap_db(db_path)

    user_a, decision_a = _seed_user_with_decision(db_path, 78.0)
    user_b, _ = _seed_user_with_decision(db_path, 88.0)

    with get_connection(db_path) as conn:
        repo = DecisionRunRepository(conn)
        own = repo.get_by_id(user_id=user_a, decision_id=decision_a)
        leaked = repo.get_by_id(user_id=user_b, decision_id=decision_a)

    assert own is not None
    assert leaked is None

def test_determinism_baseline_is_isolated_per_user(tmp_path: Path) -> None:
    db_path = tmp_path / "isolation_determinism.db"
    _bootstrap_db(db_path)

    user_a, decision_a1 = _seed_user_with_decision(db_path, 78.0)
    user_b, decision_b1 = _seed_user_with_decision(db_path, 78.0)

    decision_a2 = run_evaluation(
        user_id=user_a,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )
    decision_b2 = run_evaluation(
        user_id=user_b,
        db_path=str(db_path),
        domain_definition=HealthDomainDefinition(),
    )

    with get_connection(db_path) as conn:
        repo = DecisionRunRepository(conn)
        a1 = repo.get_by_id(user_id=user_a, decision_id=decision_a1)
        b1 = repo.get_by_id(user_id=user_b, decision_id=decision_b1)
        a2 = repo.get_by_id(user_id=user_a, decision_id=decision_a2)
        b2 = repo.get_by_id(user_id=user_b, decision_id=decision_b2)

    assert a1 is not None and b1 is not None and a2 is not None and b2 is not None

    a1_trace = json.loads(a1["trace_json"])
    b1_trace = json.loads(b1["trace_json"])
    a2_trace = json.loads(a2["trace_json"])
    b2_trace = json.loads(b2["trace_json"])

    assert a1_trace["governance"]["determinism_reason"] == "NO_BASELINE"
    assert b1_trace["governance"]["determinism_reason"] == "NO_BASELINE"
    assert a1_trace["governance"]["baseline_decision_id"] is None
    assert b1_trace["governance"]["baseline_decision_id"] is None

    # Current deterministic input signature includes rolling history and
    # previous confidence, so each new run produces a fresh signature and no
    # baseline match for replay comparison.
    assert a2_trace["governance"]["determinism_reason"] == "NO_BASELINE"
    assert b2_trace["governance"]["determinism_reason"] == "NO_BASELINE"
    assert a2_trace["governance"]["baseline_decision_id"] is None
    assert b2_trace["governance"]["baseline_decision_id"] is None

    # User scoping guarantee: even with identical logs, input signature differs
    # per user identity and never resolves to another user's baseline.
    assert a1["input_signature_hash"] != b1["input_signature_hash"]

