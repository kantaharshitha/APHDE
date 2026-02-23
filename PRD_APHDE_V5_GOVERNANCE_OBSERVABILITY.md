# Product Requirements Document (PRD)
## APHDE V5: Governance, Reproducibility, and Observability

## 1. Executive Summary
APHDE V5 introduces a governance and observability layer that validates deterministic integrity, improves reproducibility, and exposes architectural depth in the UI.
V5 does not change domain behavior, scoring formulas, confidence formulas, context modulation logic, or recommendation logic.
It is an engineering maturity release focused on verification, traceability, and explainable system operations.

---

## 2. Architectural Motivation
V1-V4 established deterministic decisioning, confidence modeling, context modulation, and domain-agnostic architecture.
V5 addresses the next senior-level gap: proving and operationalizing determinism over time.

Current gaps:
- No first-class deterministic output verification artifact
- No structured run-to-run version diff tooling
- Limited historical governance analytics in product UI
- Limited visibility of architectural mechanics for interview/demo storytelling

V5 closes these gaps with a pure wrapper layer around evaluation lifecycle.

---

## 3. V5 Scope and Non-Goals
### In Scope
- Determinism verifier with output hashing and replay equality checks
- Version diff engine between decision runs
- History analyzer for non-predictive trend analytics
- Governance/observability panel in UI
- Persistent governance metadata in decision runs and trace

### Out of Scope
- No ML
- No predictive analytics
- No domain logic changes
- No scoring/confidence/context formula changes
- No recommendation generation changes

---

## 4. Governance Layer Design
New module:
```txt
core/governance/
  determinism.py
  version_diff.py
  history_analyzer.py
  hashing.py
```

Layer responsibilities:
- Consume evaluation artifacts post-run
- Compute governance metadata
- Persist verification outputs
- Produce analytics/diff payloads for UI and API surfaces

Design rule:
- Governance is observational and comparative only.
- Governance must not mutate runtime decision artifacts.

---

## 5. Determinism Verification Design
## Objective
Prove that identical inputs produce identical normalized outputs under same version triad.

## Flow
1. Capture evaluation input envelope (domain logs summary, goal config, context input, version triad).
2. Build canonical output payload from current run.
3. Generate deterministic hash (`output_hash`) from canonical payload.
4. Compare against nearest comparable baseline run (same normalized input signature and same version triad).
5. Set `determinism_verified`:
- `true` if canonical hashes match
- `false` if mismatch
- `null` when no comparable baseline exists

## Determinism Artifacts
- `input_signature_hash`
- `output_hash`
- `determinism_verified`
- `determinism_reason` (optional: `NO_BASELINE`, `MATCH`, `MISMATCH`)

---

## 6. Version Diff Engine Design
## Objective
Provide structured run-to-run explainable diffs without recomputation changes.

## Inputs
- `decision_run_id_a`
- `decision_run_id_b`

## Diff Output Contract
- metadata:
  - run ids
  - timestamps
  - version triad per run
- score deltas:
  - `alignment_score_delta`
  - `risk_score_delta`
  - `alignment_confidence_delta`
- recommendation delta:
  - added ids
  - removed ids
  - rank shifts
  - confidence deltas
- context delta:
  - applied flag changes
  - context version changes
  - modulation payload differences
- rule delta:
  - triggered rules added/removed

Output must be deterministic and stable in ordering.

---

## 7. Evaluation History Analyzer Design
## Objective
Expose governance-grade descriptive analytics (not predictive).

## Metrics
- Alignment trend (run-index/time series)
- Confidence trend
- Context application frequency
- Triggered rule distribution
- Determinism verification pass rate
- Version triad distribution over time

## Output Format
- Structured JSON blocks suitable for Streamlit charts/tables
- Aggregations computed from persisted decision_runs + trace only

---

## 8. Data Model Changes
`decision_runs` additive fields:
- `input_signature_hash TEXT NULL`
- `output_hash TEXT NULL`
- `determinism_verified INTEGER NULL` (0/1/null)
- `governance_json TEXT NULL` (optional summary payload)

Optional new table:
- `decision_run_diffs`
  - `id`
  - `run_a_id`
  - `run_b_id`
  - `diff_json`
  - `created_at`

Migration requirements:
- Backward compatible with V1-V4 databases
- Defaults do not break existing readers

---

## 9. Hashing Strategy
Use canonical JSON hashing:
1. Normalize payload (sorted keys, stable numeric rounding policy aligned to persisted precision).
2. Exclude non-deterministic fields:
- database row ids
- timestamps
- runtime-only metadata
3. Hash algorithm: SHA-256
4. Hash inputs:
- alignment/risk/confidence outputs
- recommendations (ordered)
- context payload
- trace deterministic sub-structure
- version triad and domain version metadata

Canonicalization must be centrally implemented in `core/governance/hashing.py`.

---

## 10. Determinism Guarantees
V5 preserves and proves determinism by:
- Non-invasive governance wrapper
- Canonical payload hashing
- Explicit exclusion of non-deterministic fields
- Version-locked comparison policy
- Determinism tests across repeated runs and replayed fixtures

No governance step may alter evaluation output.

---

## 11. UI Redesign Specification (Governance Panel)
Enhance Decision Dashboard with a new Governance section showing:

1. Version Triad + Domain metadata
- `engine_version`
- `confidence_version`
- `context_version`
- `domain_name`
- `domain_version`

2. Determinism Status
- `determinism_verified` badge
- `output_hash`
- comparable baseline run id (if any)

3. Version Diff Viewer
- select two decision runs
- render structured deltas:
  - score/confidence
  - recommendation changes
  - context changes
  - rule changes

4. History Analytics
- alignment trend chart
- confidence trend chart
- context applied ratio
- rule frequency table

UI principle:
- reveal architecture transparently, not just end-user advice.

---

## 12. Testing Strategy
### Parity Tests
- V4 vs V5 decision outputs must match for same inputs (excluding new governance fields)

### Determinism Tests
- identical inputs across repeated runs must produce identical `output_hash`
- mismatch test with intentional input change must produce different hash

### Diff Correctness Tests
- fixtures for expected structured diff payloads
- stable ordering and deterministic deltas

### History Analyzer Tests
- trend and frequency aggregates from seeded runs
- no predictive outputs introduced

### Migration Tests
- legacy DB upgrade adds governance fields without corruption

---

## 13. Risks and Mitigations
1. Risk: False determinism mismatches due to non-canonical payloads
Mitigation: strict canonical serializer + explicit excluded fields list.

2. Risk: Governance logic accidentally mutates decision artifacts
Mitigation: pure-function governance modules + immutability tests.

3. Risk: UI complexity reduces clarity
Mitigation: progressive disclosure (collapsed panels, concise summary cards).

4. Risk: Diff noise across version changes
Mitigation: version-aware comparison and clear diff metadata headers.

---

## 14. Definition of Done
V5 is complete when:
1. Governance modules exist and are integrated post-evaluation.
2. `output_hash` and `determinism_verified` persist for new runs.
3. Determinism checks are reproducible and tested.
4. Version diff output is structured and validated.
5. History analytics are available and deterministic.
6. Dashboard exposes governance, diff, context, and confidence panels.
7. V4 behavior parity is preserved.
8. Full test suite (including new governance tests) passes.

---

## 15. Portfolio Positioning Narrative
V5 elevates APHDE from deterministic decision engine to deterministic governance-grade platform.
It demonstrates:
- reproducibility engineering
- architectural observability
- explainability under change
- version-aware analytical tooling
- senior-level system hardening without scope creep

This positions APHDE strongly for senior technical interviews, architecture reviews, and early-stage platform credibility discussions.
