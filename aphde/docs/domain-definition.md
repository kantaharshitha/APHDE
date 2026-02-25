# Domain Definition Contract (V4)

## Purpose

`DomainDefinition` is the injection contract between the domain-agnostic core and domain-specific logic.

It allows Stratify core to operate without knowledge of domain entities such as weight, calories, workouts, or cycle.

## Interface

Defined in `core/engine/contracts.py`.

Required methods:

1. `compute_signals(logs, config) -> SignalBundleLike`
- Converts domain logs into normalized signal bundle consumed by core decision pipeline.

2. `get_strategy(goal_type) -> StrategyLike`
- Resolves deterministic strategy implementation for normalized goal type.

3. `get_domain_config() -> dict`
- Returns domain defaults (e.g., window settings, default targets).

4. `normalize_goal_type(raw_goal_type) -> str`
- Canonicalizes goal identifiers before strategy resolution.

5. `domain_name() -> str`
- Stable domain identifier for trace metadata.

6. `domain_version() -> str`
- Version marker for domain implementation traceability.

## Related Contracts

- `DomainLogs`
- Domain-neutral container with:
  - `items: dict[str, list[dict]]`
  - `metadata: dict[str, Any]`

- `StrategyLike`
- Must provide deterministic:
  - `evaluate(signals, target)`
  - `recommend(evaluation)`

- `SignalBundleLike`
- Must provide `sufficiency: dict[str, bool] | None`

## Health Domain Implementation

Reference implementation:
- `domains/health/domain_definition.py`

Health domain delegates to:
- `domains/health/signals.py`
- `domains/health/strategy.py`
- `domains/health/thresholds.py`

## Service Wiring

`run_evaluation` requires explicit contract injection:

```python
run_evaluation(
    user_id=1,
    db_path="aphde.db",
    domain_definition=HealthDomainDefinition(),
)
```

This keeps core modules free of concrete domain dependencies.

## Validation

Runtime validation:
- `validate_domain_definition(candidate)` in `core/engine/contracts.py`

Test coverage:
- `tests/unit/test_engine_contracts.py`
- `tests/unit/test_health_domain_definition.py`
- integration parity tests in `tests/integration/test_run_evaluation.py`
