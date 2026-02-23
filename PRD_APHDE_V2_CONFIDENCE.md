# Product Requirements Document (PRD) V2
## Adaptive Personal Health Decision Engine (APHDE)
## Deterministic Confidence Modeling Engine

## 1. Executive Summary
APHDE V2 extends the existing deterministic decision framework by adding a **Deterministic Confidence Modeling Engine** that quantifies reliability of outputs without introducing ML.

V2 adds:
1. `alignment_confidence (0-1)` for composite score reliability.
2. `recommendation_confidence (0-1)` for each recommendation.
3. `confidence_breakdown` with explicit factor-level contributions.
4. Versioned, persisted, explainable confidence traces.

V2 does **not** add prediction, probabilistic ML, external APIs, or black-box logic.

---

## 2. Problem Statement
V1 provides deterministic decisions and explanations, but it does not explicitly quantify how trustworthy a decision is under varying data quality and signal stability.

Current gap:
1. Same score format is shown whether data is dense or sparse.
2. Recommendation confidence is heuristic-only and not standardized.
3. Users cannot audit uncertainty sources (volatility, threshold proximity, persistence).
4. Governance/defensibility is weaker without explicit reliability modeling.

V2 resolves this by introducing deterministic, bounded confidence formulas with transparent breakdowns.

---

## 3. V2 Goals and Non-Goals
### Goals
1. Add deterministic confidence outputs at alignment and recommendation level.
2. Encode reliability drivers explicitly:
- data completeness ratio
- volatility effects
- threshold breach distance
- historical persistence of deviation
- window sufficiency
3. Persist confidence artifacts in DB and explanation trace.
4. Version confidence logic independently from core scoring.

### Non-Goals
1. No machine learning.
2. No predictive forecasting.
3. No external data integrations.
4. No stochastic/probabilistic sampling.

---

## 4. Architectural Changes
### New Module
- `core/scoring/confidence.py`

### Supporting Additions
1. `core/scoring/confidence_components.py` (optional helper)
2. `core/explain/confidence_notes.py` (optional helper)
3. Decision engine integration points:
- `core/decision/engine.py` updated to call confidence engine.
4. Persistence updates:
- `decision_runs` schema extended for confidence payloads.

### Separation of Concerns
1. `alignment score` remains in existing scoring engine.
2. `confidence` calculated in confidence engine only.
3. Decision engine orchestrates both; neither layer mutates the other.

---

## 5. New Modules and Interfaces
### Confidence Engine Interface
```python
def compute_confidence(
    *,
    signals: SignalBundle,
    deviations: dict,
    score_breakdown: dict,
    recommendations: list[dict],
    history: dict,
    model_version: str = "conf_v1"
) -> dict:
    """
    Returns:
    {
      "alignment_confidence": float,  # 0..1
      "recommendation_confidence": list[dict],  # per rec
      "confidence_breakdown": dict,
      "confidence_notes": list[str],
      "confidence_version": str
    }
    """
```

### Historical Input Contract
`history` should include rolling runs (e.g., last 7/14 decisions):
1. prior deviations by type
2. prior triggered risks
3. prior signal sufficiency flags

---

## 6. Confidence Model Definition
Confidence is deterministic composition of 5 normalized components:

1. `C_data` Data Completeness  
2. `C_stability` Signal Stability (inverse volatility effect)  
3. `C_distance` Threshold Distance Strength  
4. `C_persistence` Historical Persistence Consistency  
5. `C_window` Window Sufficiency

All components are in `[0,1]`.  
Final confidence is bounded and smoothed.

---

## 7. Mathematical Formulation
### 7.1 Component Definitions

1. **Data Completeness**
- `C_data = observed_required_points / required_points`
- clamp to `[0,1]`.

2. **Stability**
- Let `V` be normalized volatility aggregate.
- `C_stability = 1 - clamp(V, 0, 1)`.

3. **Threshold Distance**
- For each evaluated threshold `i`, compute normalized distance `d_i`:
- `d_i = clamp(abs(actual_i - threshold_i) / scale_i, 0, 1)`
- `C_distance = mean(d_i)` for active deviations (or neutral fallback if none).

4. **Historical Persistence**
- Let `p = proportion of recent runs with same deviation direction`.
- `C_persistence = clamp(p, 0, 1)`.

5. **Window Sufficiency**
- If min required lookback unmet, penalize:
- `C_window = min(available_days / required_days, 1)`.

### 7.2 Alignment Confidence
Weighted sum:
- `C_align_raw = w1*C_data + w2*C_stability + w3*C_distance + w4*C_persistence + w5*C_window`
- default weights:
  - `w1=0.30, w2=0.20, w3=0.20, w4=0.20, w5=0.10`

Smoothing:
- `C_align = clamp(alpha*C_prev + (1-alpha)*C_align_raw, 0, 1)`  
- if no prior run, `C_prev = C_align_raw`; default `alpha=0.2`.

### 7.3 Recommendation Confidence
For recommendation `r`:
- `C_rec(r) = clamp( b0 + b1*C_align + b2*evidence_strength(r) + b3*rule_specificity(r) - b4*conflict_penalty(r), 0, 1 )`

All terms deterministic from trace and reason-codes.

---

## 8. Confidence Breakdown Structure
Example persisted JSON:
```json
{
  "alignment_confidence": 0.78,
  "components": {
    "data_completeness": 0.86,
    "signal_stability": 0.71,
    "threshold_distance": 0.74,
    "historical_persistence": 0.80,
    "window_sufficiency": 0.90
  },
  "weights": {
    "data_completeness": 0.30,
    "signal_stability": 0.20,
    "threshold_distance": 0.20,
    "historical_persistence": 0.20,
    "window_sufficiency": 0.10
  },
  "recommendation_confidence": [
    {"id": "wl_nutrition_01", "confidence": 0.81},
    {"id": "wl_habit_01", "confidence": 0.75}
  ],
  "smoothing": {"alpha": 0.2, "previous_used": true},
  "confidence_version": "conf_v1"
}
```

---

## 9. Data Model Changes
### `decision_runs` table additions
1. `alignment_confidence REAL NOT NULL DEFAULT 0.0`
2. `recommendation_confidence_json TEXT NOT NULL DEFAULT '[]'`
3. `confidence_breakdown_json TEXT NOT NULL DEFAULT '{}'`
4. `confidence_version TEXT NOT NULL DEFAULT 'conf_v1'`

Migration required with backward-compatible defaults.

---

## 10. API / Service Changes
### Service Layer (`run_evaluation`)
Add confidence computation after score/recommendation generation:
1. load recent historical decisions
2. compute confidence payload
3. persist new confidence columns
4. include confidence in response DTO

### Decision Engine Output Contract
Extend `DecisionResult`:
1. `alignment_confidence: float`
2. `recommendation_confidence: list[dict]`
3. `confidence_breakdown: dict`
4. `confidence_version: str`

---

## 11. Explanation Trace Updates
Trace adds:
1. `confidence_breakdown`
2. `confidence_notes`
3. `alignment_confidence`
4. `recommendation_confidence`
5. `confidence_version`

Example note:
- `"Low confidence due to sparse 7-day logs and high volatility spike."`

---

## 12. Determinism Guarantees
1. No random seeds or stochastic branches.
2. Pure formula-based transforms from persisted inputs.
3. Fixed ordering for recommendation scoring.
4. Version-locked coefficients/weights.
5. Same inputs + same versions => same confidence outputs.

---

## 13. Testing Strategy
### Unit Tests
1. Component-level confidence calculations.
2. Boundary clamping (`0` and `1`).
3. Missing-data behavior and fallback defaults.
4. Smoothing behavior with/without previous runs.

### Integration Tests
1. End-to-end run persists confidence fields.
2. Trace includes confidence payload.
3. Recommendation confidence aligns with recommendation IDs.

### Determinism / Golden Tests
1. Snapshot tests for fixed inputs across versions.
2. Regression tests for component weights and final confidence.

---

## 14. Risks and Tradeoffs
1. **Perceived precision risk**: numeric confidence may appear over-authoritative.
- Mitigation: confidence notes + component transparency.
2. **Complexity creep**: too many modifiers can reduce maintainability.
- Mitigation: strict component cap, explicit formulas, versioning.
3. **Cold-start instability**: weak history early on.
- Mitigation: bounded defaults and historical fallback rules.

---

## 15. Versioning Strategy
Two independent versions:
1. `engine_version` for decision/scoring logic.
2. `confidence_version` for confidence model logic.

Rules:
1. Any coefficient/weight/formula change increments `confidence_version`.
2. Store both versions on each decision run.
3. Golden fixtures maintained per version.

---

## 16. MVP V2 Scope
In scope:
1. Confidence engine module + formulas.
2. DB migration and persistence.
3. Trace updates and dashboard display.
4. Unit/integration/golden tests.
5. Docs updates (`decision-rules`, architecture, confidence spec).

Out of scope:
1. ML confidence calibration.
2. External reliability signals.
3. probabilistic forecasting.

---

## 17. Future Expansion Hooks (Post-V2)
1. Optional calibrated probabilistic confidence layer (still explainable).
2. Per-user confidence personalization profiles.
3. Drift monitoring for confidence-health mismatch.
4. Optional ML augmentation behind strict governance flags.

---

## 18. Success Metrics (V2)
1. 100% of decision runs persist confidence payload.
2. Determinism pass rate for confidence snapshots: 100%.
3. Reduced ambiguous recommendations in low-sufficiency scenarios.
4. Reviewer/interviewer clarity on “why confidence is high/low”.
