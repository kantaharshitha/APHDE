# Stratify Architecture (V5)

## Overview

Stratify V5 separates a domain-agnostic deterministic core from domain-specific implementations and adds governance observability around evaluation lifecycle.

Core responsibilities:
- orchestration pipeline
- scoring
- confidence
- context modulation
- explanation trace assembly
- persistence
- governance observability (hashing, determinism verification, run diff, history analytics)

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
  governance/
    hashing.py
    determinism.py
    version_diff.py
    history_analyzer.py
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

## Runtime Flow (V5)

1. Caller injects `DomainDefinition` into `run_evaluation`.
2. Service loads logs and context entries from repositories.
3. Service builds `DomainLogs` and delegates signal computation to domain.
4. Service resolves strategy via domain contract.
5. Core runner executes deterministic decision pipeline.
6. Score/confidence/context outputs are persisted.
7. Governance layer computes:
- input signature hash
- output hash
- determinism verification metadata
8. Trace includes version triad + additive metadata:
- `domain_name`
- `domain_version`
- `governance` block

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
- governance fields (`output_hash`, determinism status/reason)

## Backward Behavior Compatibility

V5 is an engineering maturity expansion, not a domain feature expansion.
Core decision behavior is guarded through snapshot, parity, determinism, and integration tests.
