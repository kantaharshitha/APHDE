## Implementation Plan: APHDE V3 (Context Engine + UI Redesign)

### 1. Objective
Deliver V3 with:
1. Deterministic modular Context Engine.
2. Cycle context as first plugin.
3. UI flow redesign for clear context visibility.
4. Full persistence + trace + versioning support.
5. No ML, no external APIs, no scoring-rule bypass.

---

### 2. Delivery Principles
1. Keep raw signal computation unchanged.
2. Context only modulates interpretation parameters.
3. Preserve V1/V2 behavior when no context is provided.
4. Version everything independently: `engine_version`, `confidence_version`, `context_version`.
5. Ship in vertical slices with tests at each step.

---

### 3. Workstreams

### Workstream A: Data Layer and Migration
Tasks:
1. Add `context_inputs` table.
2. Ensure `decision_runs` has:
- `context_applied`
- `context_version`
- `context_json`
3. Add/verify migration script for legacy DBs.
4. Add repository for context input CRUD (at least `add`, `latest_for_user`).

Acceptance criteria:
1. New DB initializes with context tables/fields.
2. Legacy DB migrates without data loss.
3. Context input can be read deterministically for evaluation.

---

### Workstream B: Context Engine Core
Tasks:
1. Implement `core/context/base.py` (`BaseContext`/result contract).
2. Implement `core/context/cycle_context.py` with bounded rules:
- luteal: widen volatility tolerance
- menstrual/luteal: soften recovery expectation/penalty
3. Implement `core/context/registry.py` for plugin dispatch.
4. Add explicit clamping and deterministic defaults.

Acceptance criteria:
1. Supported phases: menstrual, follicular, ovulatory, luteal.
2. No raw signal mutation.
3. No rule suppression.
4. Deterministic output for identical input.

---

### Workstream C: Decision Engine Integration
Tasks:
1. Integrate context modulation into decision flow after strategy eval and before scoring/confidence.
2. Apply modulated thresholds/scalers to interpretation only.
3. Extend `DecisionResult` with context fields:
- `context_applied`
- `context_notes`
- `context_version`
- `context_json`
4. Preserve behavior when context is absent.

Acceptance criteria:
1. Decision output includes context metadata.
2. Context-off path equals prior V2 behavior.
3. Score/confidence remain bounded and deterministic.

---

### Workstream D: Service and Trace Wiring
Tasks:
1. Update `run_evaluation` to load latest context input from `context_inputs`.
2. Pass context payload into decision engine.
3. Persist context fields in `decision_runs`.
4. Extend trace with:
- `context_applied`
- `context_notes`
- `context_version`
- modulation metadata

Acceptance criteria:
1. Context logged in input appears in persisted decision row/trace.
2. Missing context handled cleanly.
3. Versioning fields present and auditable.

---

### Workstream E: UI Redesign
Tasks:
1. Keep Goal Setup first page (goal + thresholds only).
2. Move cycle context capture to Log Input page.
3. Replace workout dropdown with tile/card selector.
4. Update dashboard with Context Engine diagnostics:
- applied yes/no
- phase/type
- context notes
- modulated thresholds/scalers
- context version

Acceptance criteria:
1. User can test context end-to-end from UI.
2. Context effects are visible without opening raw trace.
3. UX remains demo-friendly and simple.

---

### Workstream F: Testing
Tasks:
1. Unit tests:
- cycle modulation rules
- boundary clamps
- no signal mutation
- registry behavior
2. Integration tests:
- context input persisted and consumed by evaluation
- decision row persists context fields
- trace contains context details
3. Snapshot tests:
- stable deterministic output with/without context

Acceptance criteria:
1. Full suite passes.
2. Determinism guaranteed by repeated-run equality.
3. No regressions in V1/V2 core tests.

---

### Workstream G: Documentation and Demo
Tasks:
1. Update:
- `docs/architecture.md`
- `docs/decision-rules.md`
- `README.md`
2. Add `docs/context-engine.md`.
3. Update demo scenario docs/script to show context behavior.

Acceptance criteria:
1. Docs match implementation exactly.
2. Clear technical interview narrative (V1->V2->V3).
3. Demo output visibly includes context effects.

---

### 4. Milestone Sequence
1. M1: Data/migration/repository.
2. M2: Context engine module.
3. M3: Decision integration.
4. M4: Service + persistence + trace.
5. M5: UI redesign.
6. M6: Test hardening + snapshots.
7. M7: Docs/demo finalization.

---

### 5. Definition of Done (V3)
1. Context engine is modular and deterministic.
2. Cycle context is input-driven (not goal-config-driven).
3. Context metadata persisted in DB and trace.
4. Dashboard clearly shows context application and effects.
5. All tests pass.
6. Version triad present per run:
- `engine_version`
- `confidence_version`
- `context_version`
