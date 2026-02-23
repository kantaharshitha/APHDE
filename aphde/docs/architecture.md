# APHDE Architecture

## Layered Design

1. Data Layer (`core/data`)
- SQLite schema and migrations.
- Repository classes isolate persistence.
- Decision artifacts persist score, confidence, context, and trace payloads.

2. Signal Engine (`core/signals`)
- Deterministic calculators for trend, volatility, compliance, recovery, muscle balance, overload.
- `SignalBundle` is the normalized signal contract.
- Sufficiency map tracks missing-signal uncertainty.

3. Goal Strategy Layer (`core/strategies`)
- Strategy pattern with one class per goal type.
- `evaluate` computes deviations and risk cues.
- `recommend` emits goal-specific recommendation candidates.

4. Context Engine Layer (`core/context`)
- Context plugin contract in `base.py`.
- Registry dispatch in `registry.py`.
- First plugin: `cycle_context.py`.
- Modulates interpretation parameters only:
  - threshold bands (`max_volatility`, `min_recovery`)
  - penalty scalars (`priority_score_scale`)
- Does not mutate raw signals and does not suppress decision rules.

5. Decision Engine (`core/decision`)
- Merges strategy output and cross-cutting risks.
- Applies context-modulated interpretation.
- Ranks recommendations and builds deterministic output.

6. Scoring and Confidence (`core/scoring`)
- `breakdown.py` + `alignment.py` compute alignment/risk.
- `confidence.py` computes deterministic reliability outputs:
  - alignment confidence
  - recommendation confidence
  - confidence breakdown and notes

7. Explanation Layer (`core/explain`)
- Serializes recommendations.
- Produces structured trace payload with version markers.
- Trace includes confidence and context metadata.

8. Application Layer (`app`)
- Streamlit pages for goal setup, log input, and decision dashboard.
- Service orchestration in `core/services/run_evaluation.py`.

## Runtime Flow (V3)

1. User sets active goal and threshold preferences.
2. User logs weight/calorie/workout entries and optional cycle context.
3. Service loads logs, builds `SignalBundle`, and resolves goal strategy.
4. Context engine computes modulation parameters from latest context input.
5. Decision engine evaluates deviations/rules, ranks recommendations, computes score.
6. Confidence model computes reliability outputs.
7. Service persists `decision_runs` with:
- `engine_version`
- `confidence_version`
- `context_version`
- trace JSON and context JSON
8. Dashboard renders score/confidence/context diagnostics.

## Determinism and Extensibility

- No ML and no external API dependency.
- Context and confidence remain deterministic and bounded.
- Version triad supports reproducibility:
- `engine_version`
- `confidence_version`
- `context_version`
- Context plugins are extensible for future domains (sleep, illness, injury, travel).
