from __future__ import annotations

from pathlib import Path
import sqlite3

from core.data.db import get_connection


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def run_migration(db_path: str | Path = "aphde.db") -> None:
    with get_connection(db_path) as conn:
        if not _column_exists(conn, "decision_runs", "input_signature_hash"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN input_signature_hash TEXT")
        if not _column_exists(conn, "decision_runs", "output_hash"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN output_hash TEXT")
        if not _column_exists(conn, "decision_runs", "determinism_verified"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN determinism_verified INTEGER")
        if not _column_exists(conn, "decision_runs", "governance_json"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN governance_json TEXT")
        conn.commit()


if __name__ == "__main__":
    run_migration()
    print("Applied V5 governance migration.")
