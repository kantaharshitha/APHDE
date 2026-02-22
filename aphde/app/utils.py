from __future__ import annotations

from pathlib import Path

from core.data.db import get_connection, init_db
from core.data.repositories.user_repo import UserRepository

DB_PATH = Path(__file__).resolve().parents[1] / "aphde.db"


def bootstrap_db_and_user(default_user_id: int = 1) -> int:
    init_db(DB_PATH)
    with get_connection(DB_PATH) as conn:
        user_repo = UserRepository(conn)
        if user_repo.exists(default_user_id):
            return default_user_id

        existing = conn.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1").fetchone()
        if existing is not None:
            return int(existing["id"])

        return user_repo.create()
