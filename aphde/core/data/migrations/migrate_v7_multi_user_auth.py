from __future__ import annotations

from pathlib import Path
import sqlite3

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


DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "aphde.db"


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def _ensure_users_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            display_name TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    if not _column_exists(conn, "users", "email"):
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if not _column_exists(conn, "users", "password_hash"):
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if not _column_exists(conn, "users", "display_name"):
        conn.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
    if not _column_exists(conn, "users", "last_login_at"):
        conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT")
    if not _column_exists(conn, "users", "is_active"):
        conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")

    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email) WHERE email IS NOT NULL"
    )


def _ensure_default_user(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
    if row is not None:
        return int(row["id"])

    cur = conn.execute(
        """
        INSERT INTO users (email, password_hash, display_name, created_at, is_active)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        """,
        ("default@stratify.local", None, "Default Migrated User"),
    )
    return int(cur.lastrowid)


def _backfill_user_profiles(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT id, email, display_name, is_active FROM users").fetchall()
    for row in rows:
        user_id = int(row["id"])
        email = row["email"]
        display_name = row["display_name"]
        is_active = row["is_active"]

        if email is None or str(email).strip() == "":
            conn.execute(
                "UPDATE users SET email = ? WHERE id = ?",
                (f"migrated_user_{user_id}@stratify.local", user_id),
            )
        if display_name is None or str(display_name).strip() == "":
            conn.execute(
                "UPDATE users SET display_name = ? WHERE id = ?",
                (f"User {user_id}", user_id),
            )
        if is_active is None:
            conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))


def _ensure_user_scope_columns(conn: sqlite3.Connection, default_user_id: int) -> None:
    for table_name, date_column in USER_SCOPED_TABLES:
        if not _table_exists(conn, table_name):
            continue

        if not _column_exists(conn, table_name, "user_id"):
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id INTEGER")

        conn.execute(
            f"UPDATE {table_name} SET user_id = ? WHERE user_id IS NULL",
            (default_user_id,),
        )

        conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_user_{date_column} ON {table_name}(user_id, {date_column})"
        )


def run_migration(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        _ensure_users_table(conn)
        default_user_id = _ensure_default_user(conn)
        _backfill_user_profiles(conn)
        _ensure_user_scope_columns(conn, default_user_id=default_user_id)
        conn.commit()


if __name__ == "__main__":
    run_migration()
    print("Applied V7 multi-user auth migration.")
