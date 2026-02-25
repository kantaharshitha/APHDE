## Product Requirements Document (PRD) V3
### Stratify

## 1. Executive Summary
Stratify V3 adds a **Modular Context Engine Layer** and a **UI flow redesign** while preserving deterministic, explainable, versioned architecture.

V3 goals:
1. Add context-aware interpretation without changing raw signals.
2. Keep scoring/rules active; context only modulates thresholds/penalty multipliers.
3. Persist context metadata and versioning in trace/output.
4. Improve demo usability via clearer page flow and context visibility.

---

## 2. Problem Statement
V1 and V2 evaluate behavior and reliability deterministically, but they treat interpretation as mostly static. In reality, contextual states (e.g., cycle phase) can temporarily alter expected ranges, causing avoidable false-positive penalties if context is ignored.

Need:
1. Context-aware interpretation with strict determinism.
2. No black-box adaptation.
3. Explicit audit trail for every context effect.

---

## 3. Architectural Evolution (V1 -> V2 -> V3)
1. **V1**: Deterministic decision and scoring engine with explainable trace.
2. **V2**: Deterministic confidence layer (`alignment_confidence`, per-recommendation confidence).
3. **V3**: Deterministic context modulation layer + UI flow redesign.

Identity progression:
1. V1: state evaluation engine.
2. V2: reliability modeling layer.
3. V3: context-aware deterministic interpretation framework.

---

## 4. V3 Scope
In scope:
1. `core/context/` plugin architecture.
2. `CycleContext` as first plugin.
3. Context metadata persistence (`context_applied`, `context_version`, context payload).
4. Context-integrated trace.
5. UI flow changes:
- Goal first page
- Workout tiles
- Cycle context input
- Context diagnostics on dashboard

Out of scope:
1. ML/prediction
2. external APIs
3. probabilistic inference

---

## 5. Context Engine Design
### 5.1 New Module Structure
```text
core/context/
  base.py
  cycle_context.py
  registry.py
```

### 5.2 Placement in Pipeline
Logs -> Signals -> Strategy -> Context Modulation -> Scoring -> Confidence -> Decision/Trace

### 5.3 Design Rule
Context must:
1. Adjust interpretation parameters only.
2. Never mutate raw signal values.
3. Never bypass scoring/rule execution.

---

## 6. BaseContext Interface
`BaseContext` contract (conceptual):
1. Input:
- goal type
- base thresholds
- score inputs
- context input payload
2. Output:
- modulated thresholds
- penalty scalars
- tolerance adjustments
- context_applied flag
- context_notes
- context_version
- context metadata blob

Determinism requirements:
1. Pure function behavior.
2. Bounded outputs.
3. Fixed plugin execution order via registry.

---

## 7. CycleContext Specification
Supported phases:
1. menstrual
2. follicular
3. ovulatory
4. luteal

Behavior requirements:
1. Luteal:
- widen volatility tolerance
- slightly soften recovery penalty/expectation
2. Menstrual:
- slightly soften recovery penalty/expectation
3. Follicular/Ovulatory:
- baseline behavior (no aggressive modulation)

Must always:
1. Keep evaluation active.
2. Keep changes bounded.
3. Emit context notes.

---

## 8. Context Modulation Rules (Deterministic)
Let:
1. `T_base` = original thresholds
2. `P_base` = original penalty multipliers
3. `phase` = cycle phase

Then:
1. `T_mod = clamp(T_base + delta_threshold(phase), min, max)`
2. `P_mod = clamp(P_base * scale_penalty(phase), min_scale, max_scale)`

Illustrative bounded rules:
1. Luteal volatility tolerance: `max_volatility *= 1.15` (bounded upper cap)
2. Menstrual/Luteal recovery softening: `min_recovery -= small_delta` (bounded floor)
3. Priority/penalty scaling: slight reduction, never zero

---

## 9. Data Model Changes
Add context input persistence:
1. `context_inputs` table (recommended):
- `id`
- `user_id`
- `log_date`
- `context_type`
- `context_payload_json`
- `created_at`

Decision run persistence:
1. `context_applied` (boolean/int)
2. `context_version` (text)
3. `context_json` (serialized modulation metadata)

---

## 10. Trace and Versioning Strategy
Trace additions:
1. `context_applied`
2. `context_notes`
3. `context_version`
4. `context_json` (modulated thresholds/scalers/metadata)

Version fields per run:
1. `engine_version`
2. `confidence_version`
3. `context_version`

Rule:
1. Any context formula change increments `context_version`.

---

## 11. UI Redesign Specification
1. **Goal Setup** (first page):
- select goal
- strategy thresholds
2. **Log Input**:
- weight + calories + workout logs
- workout type via tiles/cards
- cycle context input section
3. **Decision Dashboard**:
- alignment/risk/confidence
- context_applied, context_version
- context notes + context diagnostics

UI objective:
1. Demo clarity
2. Traceability
3. No extra complexity beyond architecture intent

---

## 12. Determinism Guarantees
1. No randomization.
2. No external real-time dependencies.
3. Context modulation is bounded and formula-based.
4. Fixed ordering in context registry.
5. Same persisted inputs + same versions => same outputs.

---

## 13. Testing Strategy
Unit tests:
1. Cycle phase modulation rules
2. bounds/clamp checks
3. no raw signal mutation
4. registry dispatch behavior

Integration tests:
1. context input saved and loaded into evaluation
2. context fields persisted in decision runs
3. trace includes context metadata

Snapshot tests:
1. deterministic outputs per phase
2. stable trace payload with context + confidence + score

Regression tests:
1. context cannot disable scoring pipeline
2. recommendation-confidence ID alignment preserved

---

## 14. Risks and Tradeoffs
1. Overfitting rules to one context domain.
- Mitigation: plugin architecture + conservative bounded deltas.
2. Increased logic complexity.
- Mitigation: strict separation and versioned contracts.
3. User confusion around context effects.
- Mitigation: dashboard diagnostics + explicit context notes.

---

## 15. Future Context Extensions
Next plugins under same interface:
1. sleep disruption context
2. illness context
3. travel stress context
4. injury context

Each extension must:
1. remain deterministic
2. be independently versioned
3. preserve non-mutation of signals

---

## 16. Definition of Done (V3)
1. `core/context` implemented with base interface + cycle plugin + registry.
2. Context modulation integrated into decision flow before scoring/confidence.
3. Context metadata persisted in DB and trace.
4. UI supports context input and context diagnostics.
5. Unit/integration/snapshot tests pass.
6. Version triad (`engine_version`, `confidence_version`, `context_version`) present and auditable.
7. No ML, no prediction, no external APIs introduced.
