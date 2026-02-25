from core.data.db import init_db
from core.data.migrations.migrate_v2_confidence import run_migration as run_v2_migration
from core.data.migrations.migrate_v3_context import run_migration as run_v3_migration
from core.data.migrations.migrate_v5_governance import run_migration as run_v5_migration
from core.data.migrations.migrate_v7_multi_user_auth import run_migration as run_v7_migration


if __name__ == "__main__":
    init_db()
    run_v2_migration()
    run_v3_migration()
    run_v5_migration()
    run_v7_migration()
    print("Initialized Stratify SQLite schema and applied migrations.")
