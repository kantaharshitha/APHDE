## Implementation Plan: APHDE (V1)

### 1) Delivery Strategy
1. Build vertical slices, not isolated components.
2. Keep all core engines deterministic and pure where possible.
3. Lock interfaces early (`signals`, `strategy`, `decision`, `explanation`) to avoid churn.
4. Ship a portfolio-ready demo with reproducible test scenarios.

---

### 2) Project Structure (Python, modular)
```text
aphde/
  app/
    main.py                  # Streamlit entry
    pages/
      01_log_input.py
      02_goal_setup.py
      03_decision_dashboard.py
  core/
    models/
      entities.py            # dataclasses / pydantic models
      enums.py               # GoalType, RiskCode, etc.
    data/
      db.py                  # sqlite connection/session
      schema.sql
      migrations/
      repositories/
        user_repo.py
        goal_repo.py
        weight_repo.py
        calorie_repo.py
        workout_repo.py
        decision_repo.py
    signals/
      trend.py
      volatility.py
      compliance.py
      muscle_balance.py
      recovery.py
      overload.py
      aggregator.py
    strategies/
      base.py
      weight_loss.py
      recomposition.py
      strength_gain.py
      general_health.py
      factory.py
    decision/
      rules.py
      ranker.py
      engine.py
    scoring/
      alignment.py
      breakdown.py
    explain/
      trace_builder.py
      serializers.py
    services/
      run_evaluation.py      # orchestration service
  tests/
    unit/
    integration/
    fixtures/
  scripts/
    seed_demo_data.py
  docs/
    architecture.md
    decision-rules.md
```

---

### 3) Phase Plan (Execution Order)

### Phase 0: Foundation (Day 1)
1. Initialize Python project, dependency management, lint/test tooling.
2. Create folder structure and module stubs.
3. Add ADR-style architecture notes.

Acceptance criteria:
1. `pytest` runs.
2. Basic import graph is clean.
3. `README` has local run steps.

---

### Phase 1: Data Layer + Schema (Days 1-2)
1. Create SQLite schema from PRD entities.
2. Implement repositories with CRUD for logs/goals/decisions.
3. Add migration/version table.
4. Add seed script with realistic 4-week sample data.

Acceptance criteria:
1. Can create and retrieve logs for all three input types.
2. Active goal retrieval works.
3. Decision run persistence works with JSON fields.

---

### Phase 2: Signal Engine (Days 2-4)
1. Implement rolling-window extraction (`7/14/28`).
2. Implement deterministic signal calculators:
   - trend slope
   - volatility
   - compliance
   - muscle balance
   - recovery
   - progressive overload
3. Implement `signals/aggregator.py` to produce typed signal bundle.

Acceptance criteria:
1. All signal functions are pure and unit tested.
2. Signal output schema is stable.
3. Handles missing/sparse data with explicit status flags.

---

### Phase 3: Goal Strategy Layer (Days 4-6)
1. Define `GoalStrategy` interface in `strategies/base.py`.
2. Implement four strategies with:
   - optimization priorities
   - thresholds
   - deviation rules
   - recommendation candidates
   - score component contributions
3. Add strategy factory and validation.

Acceptance criteria:
1. Strategy selection by goal type works.
2. Same signal input yields different outputs per goal (as expected).
3. Unit tests assert strategy-specific behavior.

---

### Phase 4: Decision + Scoring + Explanation (Days 6-8)
1. Implement decision rule engine (`rules.py`).
2. Implement deterministic recommendation ranker.
3. Implement composite alignment scoring (`0-100`) with breakdown.
4. Implement explanation trace model and serializer.
5. Persist full decision artifact (`recommendations_json`, `trace_json`).

Acceptance criteria:
1. End-to-end evaluation works from logs -> decision output.
2. Score always clamped `0-100`.
3. Every recommendation has reason codes and supporting evidence signals.

---

### Phase 5: UI Layer (Streamlit) (Days 8-9)
1. Log input pages for weight/calorie/workouts.
2. Goal setup page with strategy parameter inputs.
3. Decision dashboard:
   - alignment score
   - signal panel
   - ranked recommendations
   - explanation trace viewer
4. Minimal visual quality for demo readability.

Acceptance criteria:
1. Full manual workflow works without terminal commands.
2. User can inspect why score changed.
3. Latest decision run is reproducible from persisted data.

---

### Phase 6: Hardening + Portfolio Readiness (Days 9-10)
1. Integration tests for full orchestration.
2. Golden tests for explanation trace stability.
3. Document architecture, tradeoffs, extensibility hooks.
4. Prepare demo script with 2-3 scenario walkthroughs.

Acceptance criteria:
1. All tests pass locally.
2. Demo scenarios produce expected recommendations.
3. Documentation supports interview deep-dive.

---

### 4) Backlog by Epic

### Epic A: Platform & Quality
1. Set up `pyproject.toml`, formatting/linting, `pytest`.
2. CI command set (local-friendly even without cloud CI).
3. Logging + error handling conventions.

### Epic B: Data & Persistence
1. Schema + migrations.
2. Repositories + transaction boundaries.
3. Seed and fixture generation.

### Epic C: Signal Intelligence
1. Signal definitions + math validation.
2. Rolling windows and null-handling policies.
3. Snapshot persistence.

### Epic D: Adaptive Strategy Logic
1. Strategy abstraction.
2. Four concrete goal strategies.
3. Parameterized thresholds.

### Epic E: Decisioning & Explainability
1. Risk rule catalog.
2. Ranking model.
3. Explanation trace + confidence notes.

### Epic F: Experience Layer
1. Input forms.
2. Evaluation trigger flow.
3. Results and explainability dashboard.

---

### 5) Testing Plan
1. Unit tests:
   - each signal calculator
   - each strategy
   - scoring formula and clamps
2. Integration tests:
   - seed data -> evaluation -> persisted decision
3. Determinism tests:
   - same input and version => same recommendations/score
4. Edge-case tests:
   - sparse logs
   - contradictory behavior patterns
   - inactive/no goal selected

Target:
1. High coverage on `core/signals`, `core/strategies`, `core/decision`, `core/scoring`.
2. Golden snapshots for explanation trace JSON.

---

### 6) Key Technical Decisions
1. Streamlit for fast, interview-ready UI.
2. SQLite JSON columns for trace/recommendation persistence.
3. Pure-function core for testability and deterministic behavior.
4. Versioned scoring/strategy rules for reproducibility.

---

### 7) Risks and Mitigations (Implementation)
1. Risk: rule complexity explosion.
   - Mitigation: keep rule registry centralized and versioned.
2. Risk: sparse data causes noisy decisions.
   - Mitigation: data sufficiency checks + confidence degradation.
3. Risk: strategy drift during expansion.
   - Mitigation: strict base interface + contract tests.

---

### 8) Definition of Done (MVP)
1. User can log inputs, choose goal, run evaluation, and view results.
2. System returns ranked recommendations with reasons.
3. Composite score is calculated with visible component breakdown.
4. Decision trace is stored and auditable.
5. Tests pass and docs explain architecture decisions clearly.
