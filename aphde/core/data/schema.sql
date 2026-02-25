CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
    display_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_type TEXT NOT NULL,
    target_json TEXT NOT NULL,
    active_from TEXT NOT NULL,
    active_to TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    weight_kg REAL NOT NULL,
    source TEXT DEFAULT 'manual',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS calorie_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    calories_kcal INTEGER NOT NULL,
    protein_g INTEGER,
    source TEXT DEFAULT 'manual',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    session_type TEXT NOT NULL,
    duration_min INTEGER NOT NULL,
    volume_load REAL,
    avg_rpe REAL,
    planned_flag INTEGER NOT NULL DEFAULT 1,
    completed_flag INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS signal_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    window_days INTEGER NOT NULL,
    signal_json TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS context_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS decision_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_id INTEGER NOT NULL,
    run_date TEXT NOT NULL,
    alignment_score REAL NOT NULL,
    risk_score REAL NOT NULL,
    alignment_confidence REAL NOT NULL DEFAULT 0.0,
    recommendations_json TEXT NOT NULL,
    recommendation_confidence_json TEXT NOT NULL DEFAULT '[]',
    confidence_breakdown_json TEXT NOT NULL DEFAULT '{}',
    confidence_version TEXT NOT NULL DEFAULT 'conf_v1',
    context_applied INTEGER NOT NULL DEFAULT 0,
    context_version TEXT NOT NULL DEFAULT 'ctx_v1',
    context_json TEXT NOT NULL DEFAULT '{}',
    input_signature_hash TEXT,
    output_hash TEXT,
    determinism_verified INTEGER,
    governance_json TEXT,
    trace_json TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE INDEX IF NOT EXISTS idx_goals_user_active_from ON goals(user_id, active_from);
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_log_date ON weight_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_calorie_logs_user_log_date ON calorie_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_workout_logs_user_log_date ON workout_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_signal_snapshots_user_snapshot_date ON signal_snapshots(user_id, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_context_inputs_user_log_date ON context_inputs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_decision_runs_user_run_date ON decision_runs(user_id, run_date);

