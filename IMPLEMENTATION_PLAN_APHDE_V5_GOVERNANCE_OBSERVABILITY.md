## Implementation Plan: APHDE V5 (Governance, Reproducibility, Observability)

### 1. Objective
Deliver V5 as an engineering-maturity release that adds governance and observability around the existing deterministic evaluation lifecycle.

Primary outcomes:
1. Determinism verification artifacts persisted per run.
2. Structured version-to-version diff capability.
3. Historical analytics for confidence/context/rule behavior.
4. Governance-first dashboard surfaces.
5. Zero behavior change to decision, scoring, confidence, context logic.

Non-goals:
1. No ML.
2. No prediction.
3. No domain feature expansion.
4. No scoring formula changes.

---

### 2. Delivery Principles
1. Wrapper-only governance: never mutate core outputs.
2. Deterministic hashing with canonical payload normalization.
3. Additive schema and trace changes only.
4. Full backward compatibility for existing DB and UI consumers.
5. Parity gates before and after each milestone.

---

### 3. Workstreams

### Workstream A: Governance Module Scaffold
Tasks:
1. Create `core/governance/` package.
2. Add files:
- `hashing.py`
- `determinism.py`
- `version_diff.py`
- `history_analyzer.py`
3. Define public interfaces and typed payload contracts.

Acceptance criteria:
1. Governance modules import cleanly.
2. Modules are pure (no side effects by default).
3. Unit test scaffolds added.

---

### Workstream B: Determinism Verifier
Tasks:
1. Implement canonical serialization + SHA-256 hashing in `hashing.py`.
2. Implement input signature + output hash generation in `determinism.py`.
3. Add comparer for baseline run matching (same input signature + version triad).
4. Return deterministic verdict:
- `determinism_verified`
- `determinism_reason`

Acceptance criteria:
1. Same normalized output => same hash.
2. Non-deterministic fields excluded from hash payload.
3. Determinism verdict is reproducible.

---

### Workstream C: Data Model and Persistence
Tasks:
1. Add migration for governance fields in `decision_runs`:
- `input_signature_hash`
- `output_hash`
- `determinism_verified`
- `governance_json`
2. Optional: create `decision_run_diffs` table.
3. Extend repository create/read APIs safely.

Acceptance criteria:
1. Legacy DBs migrate without data loss.
2. New runs persist governance metadata.
3. Existing read paths remain compatible.

---

### Workstream D: Evaluation Lifecycle Integration
Tasks:
1. Integrate governance verifier into `run_evaluation` post-decision computation.
2. Compare against most recent comparable run.
3. Persist governance outputs in same transaction boundary.
4. Add governance block to trace JSON.

Acceptance criteria:
1. Core decision outputs unchanged.
2. Governance metadata persisted every run.
3. Trace includes governance fields for UI access.

---

### Workstream E: Version Diff Engine
Tasks:
1. Implement deterministic run diff in `version_diff.py`.
2. Compute deltas for:
- alignment/risk/confidence
- recommendations (add/remove/rank shifts/confidence shifts)
- context application/modulation deltas
- triggered rule deltas
3. Expose service method for dashboard consumption.

Acceptance criteria:
1. Diff output schema is stable and deterministic.
2. Deltas are correct and test-covered.
3. No impact on evaluation runtime outputs.

---

### Workstream F: History Analyzer
Tasks:
1. Implement trend + distribution analytics in `history_analyzer.py`:
- alignment trend
- confidence trend
- context frequency
- rule trigger frequency
- determinism pass rate
2. Add service aggregation API for latest N runs.

Acceptance criteria:
1. Analytics are descriptive only.
2. No predictive inference/forecasting.
3. Output deterministic for identical DB state.

---

### Workstream G: UI Governance Panel
Tasks:
1. Extend `03_decision_dashboard.py` with governance section:
- version triad + domain version
- output hash
- determinism status
2. Add diff viewer controls (select two run ids, render structured diff).
3. Add history analytics visuals (simple chart/table blocks).
4. Keep context + confidence panels intact and visible.

Acceptance criteria:
1. Governance info visible without opening raw trace.
2. Diff and history views are usable and deterministic.
3. UI still runs in Streamlit with minimal friction.

---

### Workstream H: Testing and Release Hardening
Tasks:
1. Unit tests:
- hash canonicalization
- determinism verdict logic
- diff correctness
- history aggregation correctness
2. Integration tests:
- governance fields persisted during evaluation
- determinism flag behavior across repeated runs
- diff service output from seeded runs
3. Parity tests:
- V4 vs V5 decision outputs unchanged (excluding governance additions)
4. Update boundary checks and docs.

Acceptance criteria:
1. Full suite passes.
2. Parity confirmed.
3. Governance outputs reproducible.

---

### 4. Milestone Sequence
1. M1: Governance scaffold + interfaces.
2. M2: Determinism hashing/verifier.
3. M3: DB migration + repository updates.
4. M4: Lifecycle integration in `run_evaluation`.
5. M5: Version diff engine.
6. M6: History analyzer.
7. M7: UI governance panel.
8. M8: Test hardening + docs + release notes.

---

### 5. Execution Checklist
1. Freeze V4 baseline outputs and fixtures.
2. Implement governance module skeleton.
3. Add migrations and persistence fields.
4. Wire determinism verifier post-evaluation.
5. Add diff and history services.
6. Extend dashboard governance panel.
7. Run full tests + parity checks + boundary checks.
8. Tag V5 release candidate.

---

### 6. Risks and Mitigations
1. Risk: Hash instability from serialization differences.
Mitigation: central canonical serializer + fixture tests.

2. Risk: Governance logic accidentally changes runtime outputs.
Mitigation: strict parity tests around decision payloads.

3. Risk: UI complexity overload.
Mitigation: collapsible sections and summary-first design.

4. Risk: Legacy DB migration regressions.
Mitigation: migration tests on synthetic legacy schemas.

---

### 7. Definition of Done (V5)
1. Governance modules fully implemented and integrated.
2. `output_hash` and `determinism_verified` persisted for new runs.
3. Version diff output available and validated.
4. History analytics available in dashboard.
5. Version triad and domain metadata visible in governance panel.
6. V4 behavior parity preserved.
7. All tests and boundary checks pass.
