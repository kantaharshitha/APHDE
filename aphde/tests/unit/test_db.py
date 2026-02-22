from core.data.db import get_connection, init_db


def test_init_db_creates_tables(tmp_path) -> None:
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()

    assert row is not None
