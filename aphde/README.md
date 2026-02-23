# APHDE

Adaptive Personal Health Decision Engine (APHDE) is a modular, deterministic health decision framework.

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
- Demo walkthroughs: `docs/demo-scenarios.md`

## Current Scope

- SQLite-backed log ingestion for weight, calories, workouts
- Deterministic signal engine
- Goal-adaptive strategy layer (4 strategies)
- Decision engine with ranked recommendations
- Composite scoring (`alignment_score`, `risk_score`)
- Deterministic confidence modeling (`alignment_confidence`, per-rec confidence)
- Explanation trace persistence (versioned)
- Streamlit workflow pages for goal setup, logging, and dashboard
