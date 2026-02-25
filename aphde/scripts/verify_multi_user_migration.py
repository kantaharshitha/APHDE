from __future__ import annotations

from pathlib import Path

from core.data.db import get_connection


USER_SCOPED_TABLES: tuple[tuple[str, str], ...] = (
    ("goals", "active_from"),
    ("weight_logs", "log_date"),
    ("calorie_logs", "log_date"),
    ("workout_logs", "log_date"),
    ("signal_snapshots", "snapshot_date"),
    ("context_inputs", "log_date"),
    ("decision_runs", "run_date"),
)


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "aphde.db"


def _table_exists(conn, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def verify(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        users_count = int(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        print(f"users.count={users_count}")

        for table_name, _ in USER_SCOPED_TABLES:
            if not _table_exists(conn, table_name):
                print(f"{table_name}.exists=false")
                continue

            null_count = int(conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE user_id IS NULL").fetchone()[0])
            orphan_count = int(
                conn.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table_name} t
                    LEFT JOIN users u ON u.id = t.user_id
                    WHERE t.user_id IS NOT NULL AND u.id IS NULL
                    """
                ).fetchone()[0]
            )

            print(f"{table_name}.null_user_id={null_count}")
            print(f"{table_name}.orphan_user_id={orphan_count}")


if __name__ == "__main__":
    verify()
