# V4 Release Notes

## Release

Stratify V4 introduces a domain-agnostic core refactor with behavior parity to V3.

## What Changed

1. Core contract layer introduced:
- `core/engine/contracts.py`

2. Generic orchestration layer introduced:
- `core/engine/pipeline.py`
- `core/engine/runner.py`

3. Health domain extracted to:
- `domains/health/domain_definition.py`
- `domains/health/signals.py`
- `domains/health/strategy.py`
- `domains/health/thresholds.py`

4. Service inversion completed:
- `run_evaluation(...)` now requires explicit `domain_definition` injection.
- Trace includes additive:
  - `domain_name`
  - `domain_version`

5. Architecture hardening:
- `scripts/check_architecture_boundaries.py`
- `tests/unit/test_architecture_boundaries.py`

## Compatibility

- No ML or prediction added.
- No new user feature surface introduced.
- Existing decision/scoring/confidence/context behavior preserved.
- Version triad preserved:
  - `engine_version`
  - `confidence_version`
  - `context_version`

## Validation Summary

- Unit + integration + snapshot + parity tests pass.
- Deterministic repeatability checks added.
- Default-vs-explicit domain injection parity verified.

## Upgrade Notes

If you call `run_evaluation` directly, you must now pass a domain implementation:

```python
run_evaluation(user_id=1, db_path="aphde.db", domain_definition=HealthDomainDefinition())
```

App pages and demo scripts are already updated.
