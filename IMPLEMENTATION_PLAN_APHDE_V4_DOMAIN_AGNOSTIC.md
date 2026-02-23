## Implementation Plan: APHDE V4 (Domain-Agnostic Core Refactor)

### 1. Objective
Refactor APHDE from a health-coupled deterministic engine into a reusable deterministic framework with pluggable domains, while preserving V3 behavior.

Primary goals:
1. Separate core generic engine from health-specific logic.
2. Introduce `DomainDefinition` contract and dependency inversion.
3. Preserve determinism, explainability, and version triad.
4. Maintain output parity with V3.

Non-goals:
1. No ML integration.
2. No predictive models.
3. No user-facing feature expansion.
4. No scoring formula changes.

---

### 2. Delivery Principles
1. Parity-first refactor (no behavioral drift).
2. Contract-driven architecture.
3. Incremental migration with compatibility adapters.
4. Deterministic test gates before each milestone close.
5. Keep traces and persistence schema backward-compatible.

---

### 3. Workstreams

### Workstream A: Contract Layer and Core Boundaries
Tasks:
1. Create `core/engine/contracts.py`.
2. Define `DomainDefinition`, `StrategyLike`, `SignalBundleLike` contracts.
3. Add simple contract validation helpers.
4. Ban direct health imports inside `core/engine/*`.

Acceptance criteria:
1. Core compiles with interfaces only.
2. Domain contract is testable in isolation.
3. No health term references in core engine package.

---

### Workstream B: Core Engine Refactor
Tasks:
1. Introduce `core/engine/pipeline.py` and `core/engine/runner.py`.
2. Move orchestration from current decision flow into domain-agnostic runner.
3. Keep scoring/confidence/context invocation points unchanged.
4. Preserve trace assembly and version fields.

Acceptance criteria:
1. Runner executes entirely via injected domain contract.
2. Existing V3 outputs are reproducible.
3. `engine_version`, `confidence_version`, `context_version` still persisted.

---

### Workstream C: Health Domain Extraction
Tasks:
1. Create `domains/health/domain_definition.py`.
2. Move health signal computation under `domains/health/signals.py`.
3. Move strategy factory/goal mapping under `domains/health/strategy.py`.
4. Move domain thresholds/config under `domains/health/thresholds.py`.
5. Add compatibility adapters to avoid breakage during migration.

Acceptance criteria:
1. Health-specific code no longer required by core.
2. Health domain fulfills contract.
3. Legacy behavior remains unchanged.

---

### Workstream D: Service Wiring and Dependency Inversion
Tasks:
1. Update `core/services/run_evaluation.py` to use `DomainDefinition` injection.
2. Build health-domain provider in app/service bootstrap.
3. Ensure persistence repositories remain unchanged where possible.
4. Add domain metadata (`domain_name`, `domain_version`) to trace as additive fields.

Acceptance criteria:
1. End-to-end run works with injected health domain.
2. Existing DB schema remains compatible.
3. Additive metadata does not break existing readers.

---

### Workstream E: Test Parity and Determinism Gates
Tasks:
1. Add unit tests for contract conformance.
2. Add core runner tests with mocked domain.
3. Add integration tests for injected health domain.
4. Add parity tests comparing V3 fixtures vs V4 outputs.
5. Run repeated-run determinism checks with fixed context.

Acceptance criteria:
1. All existing V3 tests pass.
2. New V4 contract/parity tests pass.
3. No score/recommendation/trace regressions.

---

### Workstream F: Cleanup and De-coupling Hardening
Tasks:
1. Remove deprecated import paths once parity is confirmed.
2. Remove duplicate logic left from migration phase.
3. Add lint/check script to detect forbidden health terms in core.
4. Validate package layout and import graph.

Acceptance criteria:
1. Core has zero domain-coupled dependencies.
2. CI checks fail on forbidden core-domain coupling.
3. Project tree reflects target architecture.

---

### Workstream G: Documentation and Release
Tasks:
1. Update `aphde/docs/architecture.md` for V4 boundaries.
2. Add `aphde/docs/domain-definition.md` contract spec.
3. Update `aphde/README.md` with V4 structure and extension narrative.
4. Add migration notes: V3 -> V4 compatibility.
5. Prepare release notes and tag strategy.

Acceptance criteria:
1. Docs match implementation exactly.
2. Clear portfolio narrative for senior-level interviews.
3. V4 release is reproducible from docs.

---

### 4. Milestone Sequence
1. M1: Contract layer complete.
2. M2: Core runner refactor complete.
3. M3: Health domain extraction complete.
4. M4: Service inversion wiring complete.
5. M5: Parity and determinism tests complete.
6. M6: Cleanup and coupling hardening complete.
7. M7: Documentation and release packaging complete.

---

### 5. Execution Checklist
1. Baseline capture: freeze V3 fixtures and integration outputs.
2. Implement contracts and scaffold new folders.
3. Migrate core orchestration to runner.
4. Plug in health domain via interface.
5. Run parity test suite after each migration step.
6. Remove temporary compatibility code.
7. Finalize docs and tag release candidate.

---

### 6. Risks and Mitigations
1. Risk: output drift during extraction.
Mitigation: fixture parity tests as release gate.

2. Risk: over-abstracted contract.
Mitigation: keep interface minimal and behavior-driven.

3. Risk: migration complexity and import churn.
Mitigation: phased adapters with clear deprecation checkpoints.

4. Risk: hidden health coupling in core.
Mitigation: static checks + code review checklist.

---

### 7. Definition of Done (V4)
1. Core engine is fully domain-agnostic.
2. Health logic exists only in `domains/health`.
3. V3 behavior parity is proven via automated tests.
4. Determinism remains intact.
5. Version triad is preserved in persisted runs.
6. V4 architecture and contracts are fully documented.
