# APHDE Architecture

## Layered Design

1. Data Layer (`core/data`)
- SQLite schema and connection utilities.
- Repository classes isolate persistence concerns.
- Decision artifacts are stored with serialized recommendations and traces.

2. Signal Engine (`core/signals`)
- Deterministic calculators for trend, volatility, compliance, recovery, muscle balance, overload.
- `SignalBundle` acts as normalized signal contract.
- Sufficiency map tracks missing-signal uncertainty.

3. Goal Strategy Layer (`core/strategies`)
- Strategy pattern with one class per goal type.
- `evaluate` computes deviations and risk cues.
- `recommend` returns goal-specific recommendation candidates.

4. Decision Engine (`core/decision`)
- Merges strategy and cross-cutting rule detections.
- Ranks recommendations by impact/urgency/confidence/effort.
- Produces deterministic result for same inputs.

5. Scoring Engine (`core/scoring`)
- Builds component penalties.
- Computes final alignment score and complementary risk score.

6. Explanation Layer (`core/explain`)
- Serializes recommendations.
- Produces structured trace payload for auditability and replay.

7. Application Layer (`app`)
- Streamlit pages for goal setup, log input, and decision dashboard.
- Uses service orchestration (`core/services/run_evaluation.py`).

## Runtime Flow

1. User enters logs and sets active goal.
2. Service loads latest logs and computes `SignalBundle`.
3. Strategy factory resolves active goal strategy.
4. Decision engine computes risks, ranking, and scores.
5. Explanation trace and recommendations are persisted.
6. Dashboard renders latest run (score + reasons + ranked actions).

## Determinism and Extensibility

- No ML in V1; all outputs are deterministic.
- Strategy classes are isolated and pluggable.
- Trace schema is versioned (`engine_version`) to support future evolution.
