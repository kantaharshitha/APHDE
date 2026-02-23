# APHDE

Adaptive Personal Health Decision Engine (APHDE) is a deterministic, modular, explainable decision framework.

As of V5, APHDE is structured as a domain-agnostic core with pluggable domain implementations and a governance/observability layer.
The health domain is the reference implementation under `domains/health/`.

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

## Architecture Boundary Check

```bash
cd aphde
.venv\Scripts\python.exe scripts\check_architecture_boundaries.py
```

## Demo Script

```bash
cd aphde
.venv\Scripts\python.exe -m scripts.run_demo_scenarios
```

## Docs

- Architecture: `docs/architecture.md`
- Domain contract: `docs/domain-definition.md`
- Decision framework: `docs/decision-rules.md`
- Confidence model: `docs/confidence-model.md`
- Context engine: `docs/context-engine.md`
- Demo walkthroughs: `docs/demo-scenarios.md`
- V4 release notes: `docs/release-notes-v4.md`
- V5 release notes: `docs/release-notes-v5.md`

## Current Scope

- Deterministic core engine orchestration (`core/engine`)
- Deterministic scoring + confidence + context pipelines
- SQLite-backed persistence + traceability
- Version triad per run:
  - `engine_version`
  - `confidence_version`
  - `context_version`
- Health domain implementation via `DomainDefinition`:
  - `domains/health/domain_definition.py`
  - health signals + strategies + thresholds
- Streamlit UI for goal setup, logging, and dashboard
- Governance layer:
  - output hashing
  - determinism verification metadata
  - run diff utilities
  - history analytics summaries

## V5 Governance Highlights

`core/services/run_evaluation.py` requires an injected `DomainDefinition`.

Example:

```python
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition

run_evaluation(
    user_id=1,
    db_path="aphde.db",
    domain_definition=HealthDomainDefinition(),
)
```

This keeps core runtime decoupled from domain-specific behavior.

The dashboard now also surfaces:
1. Version triad + domain metadata.
2. Determinism status and output hash.
3. Run-to-run diff viewer.
4. History analytics (alignment/confidence/context/rules).
