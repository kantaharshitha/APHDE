# APHDE

Adaptive Personal Health Decision Engine (APHDE) is a modular, deterministic health decision framework.

V3 adds a Context Engine layer (cycle-aware first plugin) while preserving deterministic scoring and explainability.

## Quickstart

```bash
cd aphde
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .[dev]
.venv\Scripts\python.exe -m streamlit run app/main.py
```

## Tests

```bash
cd aphde
.venv\Scripts\python.exe -m pytest
```

## Demo Script

```bash
cd aphde
.venv\Scripts\python.exe scripts\run_demo_scenarios.py
```

## Docs

- Architecture: `docs/architecture.md`
- Decision framework: `docs/decision-rules.md`
- Confidence model: `docs/confidence-model.md`
- Context engine: `docs/context-engine.md`
- Demo walkthroughs: `docs/demo-scenarios.md`

## Current Scope

- SQLite-backed log ingestion for weight, calories, workouts
- Deterministic signal engine
- Goal-adaptive strategy layer (4 strategies)
- Context engine (cycle context in V3)
- Decision engine with ranked recommendations
- Composite scoring (`alignment_score`, `risk_score`)
- Deterministic confidence modeling (`alignment_confidence`, per-rec confidence)
- Deterministic context modulation (`context_applied`, `context_version`, `context_json`)
- Explanation trace persistence (versioned)
- Streamlit workflow pages for goal setup, logging, and dashboard

## V3 UI Flow

1. `Goal Setup` page
- Choose optimization goal and target thresholds.
2. `Log Input` page
- Add weight, calories, and workouts (tile/card selector for workout type).
- Add optional cycle context input (phase, cycle day, symptom load).
3. `Decision Dashboard` page
- Run evaluation.
- Inspect alignment/risk/confidence plus context diagnostics and modulation details.

## Run V3 Quickly

```bash
cd aphde
.venv\Scripts\python.exe -m streamlit run app/main.py
```

In the app:
1. Set a goal.
2. Log at least 7 days of workouts/weight.
3. Save cycle context with phase `luteal`.
4. Run evaluation and compare dashboard output with and without context.
