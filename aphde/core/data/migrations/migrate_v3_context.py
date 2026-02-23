from __future__ import annotations

from pathlib import Path
import sqlite3

from core.data.db import get_connection


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def run_migration(db_path: str | Path = "aphde.db") -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS context_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                context_type TEXT NOT NULL,
                context_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        if not _column_exists(conn, "decision_runs", "context_applied"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN context_applied INTEGER NOT NULL DEFAULT 0")
        if not _column_exists(conn, "decision_runs", "context_version"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN context_version TEXT NOT NULL DEFAULT 'ctx_v1'")
        if not _column_exists(conn, "decision_runs", "context_json"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN context_json TEXT NOT NULL DEFAULT '{}'")
        conn.commit()


if __name__ == "__main__":
    run_migration()
    print("Applied V3 context migration.")
