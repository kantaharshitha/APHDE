# APHDE Architecture (V4)

## Overview

APHDE V4 separates a domain-agnostic deterministic core from domain-specific implementations.

Core responsibilities:
- orchestration pipeline
- scoring
- confidence
- context modulation
- explanation trace assembly
- persistence

Domain responsibilities:
- signal computation from raw logs
- goal strategy resolution
- domain configuration and normalization

## Folder Layout

```txt
core/
  engine/
    contracts.py
    pipeline.py
    runner.py
  decision/
  scoring/
  context/
  explain/
  data/
  services/

domains/
  health/
    domain_definition.py
    signals.py
    strategy.py
    thresholds.py
```

## Dependency Inversion Rules

Allowed:
- `domains/*` can depend on core contracts/utilities.
- app/scripts can wire core services with concrete domain implementations.

Not allowed:
- `core/engine/*` importing domain packages.
- `core/services/run_evaluation.py` importing concrete domain implementations.

These boundaries are enforced by:
- `scripts/check_architecture_boundaries.py`
- `tests/unit/test_architecture_boundaries.py`

## Runtime Flow (V4)

1. Caller injects `DomainDefinition` into `run_evaluation`.
2. Service loads logs and context entries from repositories.
3. Service builds `DomainLogs` and delegates signal computation to domain.
4. Service resolves strategy via domain contract.
5. Core runner executes deterministic decision pipeline.
6. Score/confidence/context outputs are persisted.
7. Trace includes version triad + additive domain metadata:
- `domain_name`
- `domain_version`

## Determinism

Determinism is preserved by:
- pure-function style computations
- bounded clamps in scoring/context/confidence
- versioned output payloads
- parity and repeatability tests

## Versioning

Each run persists:
- `engine_version`
- `confidence_version`
- `context_version`

Trace also includes:
- `domain_name`
- `domain_version`

## Backward Behavior Compatibility

V4 is a structural refactor, not a feature change.
Existing outputs are guarded through snapshot, parity, and integration tests.
