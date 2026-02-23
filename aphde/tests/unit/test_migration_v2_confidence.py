from core.data.db import get_connection
from core.data.migrations.migrate_v2_confidence import run_migration


def test_migration_adds_confidence_columns_to_existing_decision_runs_table(tmp_path) -> None:
    db_path = tmp_path / "legacy.db"
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE decision_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                run_date TEXT NOT NULL,
                alignment_score REAL NOT NULL,
                risk_score REAL NOT NULL,
                recommendations_json TEXT NOT NULL,
                trace_json TEXT NOT NULL,
                engine_version TEXT NOT NULL
            )
            """
        )
        conn.commit()

    run_migration(db_path)

    with get_connection(db_path) as conn:
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(decision_runs)").fetchall()]

    assert "alignment_confidence" in cols
    assert "recommendation_confidence_json" in cols
    assert "confidence_breakdown_json" in cols
    assert "confidence_version" in cols
