# Adaptive Personal Health Decision Engine (APHDE)

APHDE is a deterministic, explainable, versioned optimization framework demonstrated in the health domain.

This is **not** a fitness tracker and **not** an ML system.  
It is a layered decision architecture focused on:

- signal computation
- goal-based strategy evaluation
- composite scoring
- confidence modeling
- context modulation
- governance and reproducibility

## What APHDE Does

Given structured behavioral logs (weight, calories, workouts, optional context), APHDE:

1. Computes domain signals over rolling windows.
2. Applies goal strategy rules.
3. Scores alignment and risk deterministically.
4. Computes deterministic confidence.
5. Produces ranked recommendations and explanation trace.
6. Persists run outputs with governance metadata.

## Architecture Summary

- `core/engine/`: domain-agnostic orchestration
- `core/scoring/`: alignment, score breakdown, confidence
- `core/context/`: deterministic context adapters (cycle-aware plugin included)
- `core/governance/`: hashing, determinism verification, run diff, history analytics
- `domains/health/`: health-specific domain implementation (`DomainDefinition`)
- `core/data/`: SQLite schema, migrations, repositories
- `app/`: Streamlit UI (homepage, goal setup, log input, decision dashboard)

Version triad is persisted per run:

- `engine_version`
- `confidence_version`
- `context_version`

## Project Layout

```text
aphde/
  app/
    main.py
    pages/
      01_goal_setup.py
      02_log_input.py
      03_decision_dashboard.py
  core/
  domains/
  tests/
  docs/
```

## Quickstart (Windows PowerShell)

```bash
cd aphde
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .[dev]
.venv\Scripts\python.exe -m streamlit run app/main.py
```

Open: `http://localhost:8501`

## Core Commands

Run tests:

```bash
cd aphde
.venv\Scripts\python.exe -m pytest -q
```

Run architecture boundary check:

```bash
cd aphde
.venv\Scripts\python.exe scripts\check_architecture_boundaries.py
```

Run demo scenarios:

```bash
cd aphde
.venv\Scripts\python.exe -m scripts.run_demo_scenarios
```

## UI Workflow

1. **Homepage**: quick navigation and active-goal overview.
2. **Goal Configuration**: select strategy and configure thresholds.
3. **Log Input**: stage biometrics/training/context and commit once.
4. **Decision Dashboard**: inspect scoring, recommendations, diagnostics, and governance.

## Determinism and Governance

The system includes:

- canonical output hashing
- determinism verification metadata
- run-to-run version diff tooling
- historical trend analysis for alignment/confidence/context/rules

No scoring or confidence logic is performed in the UI layer.

## Domain Injection Contract

`core/services/run_evaluation.py` accepts an injected `DomainDefinition`.

```python
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition

decision_id = run_evaluation(
    user_id=1,
    db_path="aphde.db",
    domain_definition=HealthDomainDefinition(),
)
```

## Documentation Index

- `docs/architecture.md`
- `docs/domain-definition.md`
- `docs/decision-rules.md`
- `docs/confidence-model.md`
- `docs/context-engine.md`
- `docs/ui_data_contracts.md`
- `docs/ui-modernization-checklist.md`
- `docs/demo-scenarios.md`
- `docs/release-notes-v4.md`
- `docs/release-notes-v5.md`
- `docs/release-notes-v5.1-ui-modernization.md`
