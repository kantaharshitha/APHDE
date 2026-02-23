# Product Requirements Document (PRD)
## APHDE V4: Domain-Agnostic Core Refactor

## 1. Executive Summary
APHDE V4 refactors the current deterministic health-oriented implementation into a reusable deterministic decision framework with pluggable domain modules.
No new product features are introduced in V4. The objective is architectural: preserve existing V3 behavior while removing health-specific coupling from core logic.

V4 outcome:
- Core becomes domain-agnostic.
- Health logic moves to `domains/health/`.
- Existing outputs remain behaviorally identical.
- Determinism, explainability, and versioning guarantees are preserved.

---

## 2. Architectural Motivation
V1-V3 validated the deterministic engine in a health domain, but core still includes domain-specific assumptions. This creates reuse friction and weakens portability.

V4 addresses this by:
- Applying dependency inversion.
- Defining explicit domain contracts (`DomainDefinition`).
- Keeping core focused on orchestration, scoring, confidence, context, and persistence.
- Treating health as one concrete domain plugin.

---

## 3. Current State (V1-V3 Recap)
### V1: Deterministic Decision Engine
- Rolling-window signal computation
- Goal strategy abstraction
- Composite alignment score (0-100)
- Ranked recommendations
- Explanation trace
- SQLite persistence
- `engine_version`

### V2: Deterministic Confidence Modeling
- `alignment_confidence` (0-1)
- `recommendation_confidence`
- `confidence_version`
- Confidence from completeness, volatility, threshold distance, persistence

### V3: Context Engine
- Plugin architecture under `core/context`
- `CycleContext` first plugin
- Context modulation without raw signal mutation
- Context metadata persisted + traced
- UI flow redesigned for context visibility
- `context_version`

---

## 4. V4 Objective
Refactor APHDE into:
- Domain-agnostic core framework
- Pluggable domain modules
- Behavior-preserving architecture

Constraints:
- No ML
- No prediction
- No new user-facing features
- No scoring/decision behavior changes

---

## 5. Target Architecture (Domain-Agnostic Core)

```txt
core/
  engine/
    contracts.py
    pipeline.py
    runner.py
  scoring/
    alignment.py
    breakdown.py
  confidence/
    confidence.py
  context/
    base.py
    registry.py
  explain/
    trace_builder.py
  data/
    db.py
    schema.sql
    repositories/

domains/
  health/
    domain_definition.py
    signals.py
    strategy.py
    thresholds.py
    adapters/
```

Core must not reference health-specific terms such as:
- weight
- calorie
- workout
- recovery
- cycle

---

## 6. DomainDefinition Interface Design
A new interface (`core/engine/contracts.py`) defines domain injection boundaries.

### Required contract
- `compute_signals(logs, config) -> SignalBundleLike`
- `get_strategy(goal_type) -> StrategyLike`
- `get_domain_config() -> dict`
- `normalize_goal_type(raw_goal_type) -> str`
- `domain_name() -> str`
- `domain_version() -> str`

### Strategy contract (existing semantics preserved)
- `evaluate(signals, target) -> evaluation_payload`
- `recommend(evaluation_payload) -> recommendations`

Core consumes only contract types, not health modules.

---

## 7. Folder Structure: Before vs After
### Before
- `core/signals/*` (health-specific)
- `core/strategies/*` (health-specific)
- Mixed generic and domain concerns

### After
- Generic runtime in `core/*`
- Domain-specific logic in `domains/health/*`
- Clear separation of concerns and replaceable domain modules

---

## 8. Dependency Inversion Strategy
1. Introduce `DomainDefinition` contract in `core/engine/contracts.py`.
2. Refactor engine/service entrypoint to receive a domain implementation.
3. Implement health domain adapter in `domains/health/domain_definition.py`.
4. Replace direct imports from health modules inside core with contract calls.
5. Keep temporary compatibility adapters during migration.
6. Remove legacy coupling after parity is confirmed.

Rule:
- `domains/*` may depend on `core` contracts.
- `core` may not depend on any `domains/*` implementation.

---

## 9. Refactor Plan (Step-by-Step)
1. Create contract layer (`core/engine/contracts.py`).
2. Extract orchestration into `core/engine/pipeline.py`.
3. Build `domains/health/domain_definition.py`.
4. Move health signals/strategy/threshold mapping under `domains/health/`.
5. Refactor `run_evaluation` to inject domain implementation.
6. Preserve trace schema and persistence behavior.
7. Add parity tests against V3 fixtures.
8. Remove deprecated import paths.
9. Final doc + architecture update.

---

## 10. Determinism Preservation Strategy
- Preserve exact formulas, thresholds, and ordering logic.
- Preserve same context application point in pipeline.
- Preserve ranking tie-break behavior.
- Preserve confidence smoothing semantics.
- Preserve trace payload fields and value semantics.
- Add fixture-based parity assertions (V3 vs V4 outputs).

---

## 11. Versioning Strategy
V4 keeps required triad:
- `engine_version`
- `confidence_version`
- `context_version`

Additive metadata (non-breaking):
- `domain_name`
- `domain_version`

No version reset; V4 is a structural refactor with parity guarantees.

---

## 12. Testing Strategy (Behavior Unchanged)
### Unit tests
- Contract conformance tests for `DomainDefinition`
- Core engine tests with mocked domain
- Health domain unit tests for signals + strategies

### Integration tests
- End-to-end `run_evaluation` using injected health domain
- Persistence and trace integrity
- Context + confidence coexistence checks

### Parity tests
- Compare V3 and V4 outputs for identical inputs:
  - alignment/risk scores
  - recommendations and ranking
  - confidence outputs
  - context outputs
  - trace contents

### Determinism tests
- Repeated-run stability under fixed inputs and fixed context.

---

## 13. Risks and Mitigations
1. Behavior drift during relocation
Mitigation: strict snapshot parity gates in CI.

2. Over-abstracted contracts
Mitigation: keep interface minimal; expand only when needed.

3. Migration complexity / import breakage
Mitigation: phased adapter strategy and deprecation window.

4. Trace/schema inconsistency
Mitigation: schema and trace validation tests.

---

## 14. Definition of Done
V4 is complete when:
1. Core has no health-specific imports/terminology.
2. Health logic runs exclusively via `domains/health`.
3. V3 behavior is preserved (parity tests pass).
4. Determinism tests pass.
5. Version triad remains persisted and traceable.
6. Docs reflect new architecture and dependency flow.

---

## 15. Portfolio Positioning Narrative
V4 positions APHDE as a reusable deterministic decision framework rather than a domain-bound health project.
It demonstrates senior-level architecture skills:
- dependency inversion
- modular domain plugins
- explainable deterministic runtime
- behavior-preserving refactor discipline
- production-grade version and trace governance

This strengthens APHDE for technical interview defense, architecture discussions, and early-stage platform narratives.
