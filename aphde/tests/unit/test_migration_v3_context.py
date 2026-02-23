from core.data.db import get_connection
from core.data.migrations.migrate_v3_context import run_migration


def test_migration_adds_context_columns_and_table_to_legacy_db(tmp_path) -> None:
    db_path = tmp_path / "legacy_v3.db"
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
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

    assert "context_applied" in cols
    assert "context_version" in cols
    assert "context_json" in cols
    assert "context_inputs" in tables
