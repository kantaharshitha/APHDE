## Implementation Plan: APHDE V2 (Deterministic Confidence Modeling)

### 1. V2 Delivery Strategy
1. Preserve V1 behavior first, then layer confidence incrementally.
2. Keep confidence logic isolated in `core/scoring/confidence.py`.
3. Add DB/schema support early so all later stages persist confidence artifacts.
4. Gate rollout with deterministic/golden tests before UI exposure.
5. Version confidence independently (`confidence_version`) from `engine_version`.

---

### 2. Scope of V2
1. Add `alignment_confidence (0-1)`.
2. Add `recommendation_confidence` per recommendation.
3. Add `confidence_breakdown` + `confidence_notes`.
4. Persist all confidence artifacts in `decision_runs`.
5. Extend trace and dashboard to display confidence transparently.
6. Add deterministic and snapshot tests for confidence stability.

---

### 3. Workstream Breakdown

### Workstream A: Data Model and Persistence
Tasks:
1. Update `core/data/schema.sql`:
- `alignment_confidence REAL NOT NULL DEFAULT 0.0`
- `recommendation_confidence_json TEXT NOT NULL DEFAULT '[]'`
- `confidence_breakdown_json TEXT NOT NULL DEFAULT '{}'`
- `confidence_version TEXT NOT NULL DEFAULT 'conf_v1'`
2. Add migration script for existing DBs in `core/data/migrations/`.
3. Update `DecisionRunRepository.create(...)` signature and insert SQL.
4. Update `DecisionRunRepository.latest(...)` consumer paths (dashboard/service) to parse new fields.

Acceptance criteria:
1. New columns exist for fresh DB init.
2. Migration upgrades old DB without data loss.
3. Decision runs persist confidence payloads with defaults.

---

### Workstream B: Confidence Engine (Core)
Tasks:
1. Create `core/scoring/confidence.py`.
2. Implement component calculators:
- data completeness ratio
- signal stability (volatility inverse)
- threshold distance strength
- historical persistence
- window sufficiency
3. Implement bounded weighting and smoothing:
- clamp all outputs to `[0,1]`
- optional prior-confidence smoothing with deterministic alpha
4. Implement recommendation-level confidence calculation.
5. Return standardized payload:
- `alignment_confidence`
- `recommendation_confidence[]`
- `confidence_breakdown`
- `confidence_notes`
- `confidence_version`

Acceptance criteria:
1. Same inputs produce same confidence outputs.
2. All confidence values strictly bounded `[0,1]`.
3. Component breakdown sums and weighting are transparent.

---

### Workstream C: Decision Engine Integration
Tasks:
1. Update `core/decision/engine.py`:
- keep current scoring path unchanged
- call confidence engine after score/recommendation generation
- merge confidence outputs into `DecisionResult`
2. Add helper to gather historical context from prior runs.
3. Ensure recommendation IDs align with `recommendation_confidence`.
4. Keep confidence and alignment logic separated (no leakage).

Acceptance criteria:
1. `DecisionResult` contains confidence fields.
2. Confidence generation does not alter recommendation ordering logic unexpectedly.
3. Runs remain deterministic and reproducible.

---

### Workstream D: Service + Trace + Serialization
Tasks:
1. Update `core/services/run_evaluation.py`:
- load recent decisions as history input
- pass history/deviations/signals to confidence engine
- persist confidence fields via repository
2. Update `core/explain/trace_builder.py`:
- include `alignment_confidence`
- include `recommendation_confidence`
- include `confidence_breakdown`
- include `confidence_notes`
- include `confidence_version`
3. Update serializers for recommendation confidence mapping.

Acceptance criteria:
1. Persisted `trace_json` always includes confidence block.
2. Persisted `decision_runs` always includes confidence columns.
3. Missing-history case handled deterministically.

---

### Workstream E: UI Updates (Streamlit)
Tasks:
1. Update `app/pages/03_decision_dashboard.py`:
- show `alignment_confidence` metric
- show confidence badge/value per recommendation
- render confidence breakdown section
- render confidence notes
2. Add safe fallback UI if confidence fields missing (older rows).
3. Keep layout readable and interview-demo friendly.

Acceptance criteria:
1. Confidence values visible after each run.
2. No page crash on legacy decision rows.
3. Dashboard clearly distinguishes “score” vs “confidence”.

---

### Workstream F: Testing and Determinism Hardening
Tasks:
1. Unit tests for `core/scoring/confidence.py`:
- boundary tests (`0`, `1`)
- sparse data penalties
- volatility/stability effects
- threshold distance behavior
- smoothing behavior with/without prior runs
2. Update unit tests for decision engine to assert confidence fields exist.
3. Update integration tests for `run_evaluation` to assert DB persistence of confidence columns.
4. Add/refresh golden snapshot fixture with confidence payload.
5. Add regression test to ensure confidence version is present and stable.

Acceptance criteria:
1. All tests pass.
2. Snapshot tests stable for fixed inputs.
3. Confidence determinism validated in CI/local.

---

### Workstream G: Documentation and Versioning
Tasks:
1. Update:
- `docs/decision-rules.md` (confidence formulas and weights)
- `docs/architecture.md` (new confidence layer)
- `README.md` (confidence outputs and test coverage)
2. Add `docs/confidence-model.md` (detailed formulas, rationale, examples).
3. Define confidence version policy:
- `conf_v1`, `conf_v2`, etc.
4. Note migration and backward compatibility strategy.

Acceptance criteria:
1. Documentation matches implemented formulas exactly.
2. Versioning policy is explicit and enforceable.
3. Demo script output includes confidence highlights.

---

### 4. File-by-File Change Map

1. `aphde/core/data/schema.sql`
2. `aphde/core/data/repositories/decision_repo.py`
3. `aphde/core/scoring/confidence.py` (new)
4. `aphde/core/decision/engine.py`
5. `aphde/core/services/run_evaluation.py`
6. `aphde/core/explain/trace_builder.py`
7. `aphde/core/explain/serializers.py` (if needed)
8. `aphde/app/pages/03_decision_dashboard.py`
9. `aphde/tests/unit/test_confidence.py` (new)
10. `aphde/tests/unit/test_decision_engine.py` (update)
11. `aphde/tests/integration/test_run_evaluation.py` (update)
12. `aphde/tests/unit/test_decision_snapshot.py` + fixture update
13. `aphde/docs/confidence-model.md` (new)
14. `aphde/docs/decision-rules.md` (update)
15. `aphde/docs/architecture.md` (update)
16. `aphde/README.md` (update)

---

### 5. Implementation Sequence (Recommended)
1. Data model + repository updates.
2. Confidence engine module (isolated).
3. Decision/service integration.
4. Trace serialization updates.
5. UI dashboard confidence display.
6. Tests (unit -> integration -> snapshot).
7. Docs + demo updates.
8. Commit and push.

---

### 6. Definition of Done (V2)
1. Every decision run outputs and persists:
- `alignment_confidence`
- per-recommendation confidence
- confidence breakdown
- confidence notes
- confidence version
2. All outputs deterministic and bounded.
3. Full test suite (including snapshot/determinism) passes.
4. Streamlit dashboard shows score and confidence clearly.
5. Docs explain formulas and tradeoffs for interview-grade defense.

---

### 7. Estimated Effort
1. Workstream A-B: 0.5-1 day
2. Workstream C-D: 0.5-1 day
3. Workstream E-F: 0.5-1 day
4. Workstream G: 0.5 day

Total: ~2-3 focused days.
