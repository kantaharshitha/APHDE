# Product Requirements Document (PRD)
## Adaptive Personal Health Decision Engine (APHDE) — Behavioral Guidance Layer

## 1. Executive Summary
APHDE is evolving from a deterministic evaluation engine into a deterministic behavioral guidance system with clearer user-facing decision support.
This release introduces a **layered UX and architecture split** across three pages:

1. **Decision Dashboard** (operational snapshot)
2. **Action Center** (what to do next)
3. **Insights & Trends** (pattern analysis)

The objective is to increase practical user usefulness while preserving APHDE’s core principles:
- deterministic logic
- explainability
- modular separation of concerns
- no ML / no prediction / no black-box reasoning

---

## 2. Problem Statement
Current APHDE provides high-quality deterministic evaluation and recommendations, but user guidance and pattern interpretation are not sufficiently separated in the UI/architecture.

Current friction:
- operational status and analytical reasoning are mixed conceptually
- users need a direct next-step action, not only ranked recommendation lists
- trend and stagnation interpretation is not isolated into a dedicated analysis layer

Need:
- an immediate “tomorrow action”
- deterministic stagnation alerts
- weekly deterministic insights
- dedicated analysis page to avoid dashboard overload

---

## 3. Goals and Non-Goals

### Goals
- Add deterministic **Tomorrow Plan Engine**
- Add deterministic **Stagnation Detection Engine**
- Add deterministic **Weekly Insight Generator**
- Add **Insights visualization layer** for key trends
- Preserve modular architecture and page separation
- Keep Dashboard clean and operational

### Non-Goals
- No ML models
- No predictive analytics
- No LLM-generated narrative
- No scoring formula rewrite
- No backend governance/versioning regression
- No single-page feature overload

---

## 4. Architectural Impact

### Existing (V1–V5) remains intact
- scoring
- confidence
- context modulation
- domain abstraction
- governance/versioning/history

### New logical modules (suggested)
- `core/guidance/tomorrow_plan.py`
- `core/insights/stagnation.py`
- `core/insights/weekly_summary.py`
- `core/insights/trend_views.py` (data shaping only)
- `app/services/action_center_service.py`
- `app/services/insights_service.py`

### Separation rule
- **Core modules** compute deterministic outputs
- **Service layer** adapts persisted data for UI consumption
- **UI pages** render only; no business logic duplication

---

## 5. Page Structure (Final UX Contract)

## Page 1: Decision Dashboard (Operational)
Purpose: “What is my current state?”

Includes:
- Alignment score
- Alignment confidence
- Risk score
- Top recommendation
- Signals table (with tooltips)
- Context summary

Excludes:
- stagnation detection
- weekly summary
- heavy trend analytics

---

## Page 2: Action Center (Guidance)
Purpose: “What should I do next?”

Includes:
- **Tomorrow Plan card** (single prioritized action)
- Reasoning trace (compact)
- Confidence
- Severity
- Impact explanation
- Optional risk alert card (if active risk rules are triggered)

---

## Page 3: Insights & Trends (Analysis)
Purpose: “What patterns are emerging?”

Includes:
- Weekly Insight summary
- Stagnation alerts
- Drift detection status
- Trend charts:
  - weight trend (+ slope)
  - recovery trend
  - compliance trend
  - overload trend (optional)

---

## 6. Feature Definitions

## 6.1 Tomorrow Plan Engine
Input:
- latest computed signals
- goal strategy output
- triggered rules
- confidence components
- context modulation metadata

Output schema:
```json
{
  "action_id": "tomorrow_recovery_focus",
  "action": "Increase recovery allocation by 20 minutes.",
  "reason": "Recovery index below strategy floor for 3 consecutive runs.",
  "confidence": 0.89,
  "severity": "high",
  "expected_impact": "Stabilizes readiness and lowers short-term risk."
}
```

Deterministic ranking logic:
- Evaluate candidate actions from current recommendation set + risk conditions
- Priority score = weighted deterministic function of:
  - risk severity
  - confidence
  - strategy relevance
  - persistence of deviation
- Select single max-priority action
- Stable tie-break rule (lexicographic `action_id`)

---

## 6.2 Stagnation Detection Engine
Detect conditions:
- **Weight stagnation**: near-zero slope over X-day window
- **Overload stagnation**: overload score flat over Y-week window
- **Compliance drift**: compliance declines below threshold trend
- **Recovery suppression**: recovery persistently below floor

Output schema:
```json
{
  "alerts": [
    {
      "type": "weight_stagnation",
      "severity": "medium",
      "recommendation": "Adjust calorie adherence and monitor next 5 days.",
      "confidence": 0.83
    }
  ]
}
```

All thresholds are deterministic and configurable by constants/versioned settings.

---

## 6.3 Weekly Insight Generator
Cadence:
- computed from trailing 7-day windows when data sufficiency exists

Output fields:
- sessions planned vs completed
- compliance %
- recovery shift vs prior week
- volatility direction
- overload progression summary

Output schema:
```json
{
  "week_start": "YYYY-MM-DD",
  "week_end": "YYYY-MM-DD",
  "planned_sessions": 5,
  "completed_sessions": 4,
  "compliance_pct": 80.0,
  "recovery_shift": "down",
  "volatility_direction": "improving",
  "overload_progress": "flat"
}
```

---

## 6.4 Visual Trend Layer
Charts on Insights page:
- Weight series + displayed slope metric
- Recovery line
- Compliance line
- Optional overload line

Charting constraints:
- deterministic source data
- no forecasting lines
- no inferred future predictions

---

## 7. Deterministic Logic Rules

### Tomorrow Plan scoring (example)
`plan_score = 0.35*risk_component + 0.30*persistence_component + 0.20*strategy_component + 0.15*confidence_component`

### Stagnation thresholds (example, versioned constants)
- weight slope absolute value < epsilon for N days
- overload delta < epsilon for M windows
- compliance rolling mean drop > threshold
- recovery below floor in K of last L runs

### Confidence handling
- Reuse existing confidence layer outputs; do not introduce new model families.

---

## 8. Alert Model Schema (Canonical)
```json
{
  "alert_id": "string",
  "type": "string",
  "severity": "low|medium|high",
  "message": "string",
  "recommendation": "string",
  "confidence": 0.0,
  "triggered_at": "ISO-8601",
  "version": "string"
}
```

---

## 9. Risk Scoring Logic (Guidance Context)
Risk context for guidance uses existing deterministic risk artifacts:
- triggered rules
- risk_score
- persistence
- context modulation flags

No new independent risk engine required; guidance consumes existing signals and rule outputs.

---

## 10. Data Flow

1. Logs persisted (existing flow)
2. Evaluation run persisted (existing flow)
3. Action/insight services read persisted runs
4. Deterministic guidance/insight modules produce structured payloads
5. UI pages render payloads with no business logic branching beyond display rules

---

## 11. UI Wireframe Structure (Text)

### Dashboard
- Header
- KPI row
- Top recommendation card
- Signals table (tooltip-enabled)
- Context summary card

### Action Center
- Header
- Tomorrow Plan hero card
- Confidence + severity chips
- Why-this-action section
- Optional risk alert

### Insights & Trends
- Header
- Weekly insight summary cards
- Stagnation alerts list
- Trend charts row(s)
- Technical trace expander

---

## 12. Session State Handling
Use `st.session_state` only for:
- selected run/filter window
- selected chart horizon
- dismissed alert UI state (optional)
- view-level cached payloads

Do not persist business state in session_state beyond UI interaction.

---

## 13. Testing Plan

### Unit tests
- Tomorrow plan deterministic selection and tie-breaking
- Stagnation detector threshold boundaries
- Weekly summary calculations and sufficiency handling

### Integration tests
- Service layer payload contract for Action Center and Insights pages
- End-to-end evaluation + guidance retrieval parity

### Determinism tests
- same input history => identical tomorrow plan/alerts/weekly summary
- output hash reproducibility maintained

### UI tests (lightweight)
- page renders with empty data
- no raw JSON visible by default
- correct page-specific feature separation

---

## 14. Risks and Mitigations

- **Risk:** Feature creep into dashboard  
  **Mitigation:** strict page contract and review checklist.

- **Risk:** Hidden business logic in UI  
  **Mitigation:** enforce service-layer shaping and module tests.

- **Risk:** Overly sensitive stagnation alerts  
  **Mitigation:** conservative thresholds + minimum data sufficiency rules.

- **Risk:** User confusion from too many alert types  
  **Mitigation:** severity normalization and capped visible alerts.

---

## 15. Definition of Done
- Dashboard remains operational and uncluttered.
- Action Center shows one deterministic tomorrow action with rationale.
- Insights page shows deterministic weekly insights + stagnation + trends.
- No ML/prediction introduced.
- Determinism/versioning behavior remains intact.
- Tests added for new guidance/insight modules and service contracts.
- Documentation updated for page responsibilities and module boundaries.

---

## 16. Portfolio Positioning Narrative
This evolution positions APHDE as a **deterministic decision intelligence platform** rather than a tracker UI.  
The design demonstrates:
- architecture maturity (layered pages + modular engines)
- product thinking (operational vs guidance vs analytics separation)
- governance rigor (determinism preserved while expanding user value)
