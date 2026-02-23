# APHDE Architecture

## Layered Design

1. Data Layer (`core/data`)
- SQLite schema and connection utilities.
- Repository classes isolate persistence concerns.
- Decision artifacts store scores, confidence payloads, recommendations, and traces.

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
- `breakdown.py` and `alignment.py` compute alignment/risk scores.
- `confidence.py` computes deterministic reliability metrics:
  - alignment confidence
  - per-recommendation confidence
  - component breakdown
  - confidence notes

6. Explanation Layer (`core/explain`)
- Serializes recommendations.
- Produces structured trace payload for auditability and replay.
- Trace includes confidence blocks and versioning fields.

7. Application Layer (`app`)
- Streamlit pages for goal setup, log input, and decision dashboard.
- Uses service orchestration (`core/services/run_evaluation.py`).

## Runtime Flow

1. User enters logs and sets active goal.
2. Service loads latest logs and computes `SignalBundle`.
3. Strategy factory resolves active goal strategy.
4. Decision engine computes risks, ranking, score, and confidence.
5. Service persists decision row with confidence JSON fields.
6. Dashboard renders score + confidence + ranked actions + trace.

## Determinism and Extensibility

- No ML; all outputs are deterministic formulas.
- Strategy classes are isolated and pluggable.
- Confidence model is independently versioned (`confidence_version`).
- Trace schema includes both `engine_version` and `confidence_version` for replay stability.
