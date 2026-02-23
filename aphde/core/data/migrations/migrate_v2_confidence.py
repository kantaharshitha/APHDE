from __future__ import annotations

from pathlib import Path
import sqlite3

from core.data.db import get_connection


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def run_migration(db_path: str | Path = "aphde.db") -> None:
    with get_connection(db_path) as conn:
        if not _column_exists(conn, "decision_runs", "alignment_confidence"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN alignment_confidence REAL NOT NULL DEFAULT 0.0")
        if not _column_exists(conn, "decision_runs", "recommendation_confidence_json"):
            conn.execute(
                "ALTER TABLE decision_runs ADD COLUMN recommendation_confidence_json TEXT NOT NULL DEFAULT '[]'"
            )
        if not _column_exists(conn, "decision_runs", "confidence_breakdown_json"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN confidence_breakdown_json TEXT NOT NULL DEFAULT '{}'")
        if not _column_exists(conn, "decision_runs", "confidence_version"):
            conn.execute("ALTER TABLE decision_runs ADD COLUMN confidence_version TEXT NOT NULL DEFAULT 'conf_v1'")
        conn.commit()


if __name__ == "__main__":
    run_migration()
    print("Applied V2 confidence migration.")
