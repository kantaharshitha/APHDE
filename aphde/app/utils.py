from __future__ import annotations

from pathlib import Path

from core.data.db import get_connection, init_db
from core.data.migrations.migrate_v2_confidence import run_migration as run_v2_migration
from core.data.migrations.migrate_v3_context import run_migration as run_v3_migration
from core.data.migrations.migrate_v5_governance import run_migration as run_v5_migration
from core.data.migrations.migrate_v7_multi_user_auth import run_migration as run_v7_migration
from core.data.repositories.user_repo import UserRepository

DB_PATH = Path(__file__).resolve().parents[1] / "aphde.db"


def bootstrap_db() -> None:
    init_db(DB_PATH)
    run_v2_migration(DB_PATH)
    run_v3_migration(DB_PATH)
    run_v5_migration(DB_PATH)
    run_v7_migration(DB_PATH)


def bootstrap_db_and_user(default_user_id: int = 1) -> int:
    bootstrap_db()
    with get_connection(DB_PATH) as conn:
        user_repo = UserRepository(conn)
        if user_repo.exists(default_user_id):
            return default_user_id

        existing = conn.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1").fetchone()
        if existing is not None:
            return int(existing["id"])

        return user_repo.create()
