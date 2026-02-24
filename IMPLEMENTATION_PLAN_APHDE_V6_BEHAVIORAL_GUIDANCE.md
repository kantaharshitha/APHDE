# IMPLEMENTATION PLAN — APHDE V6 Behavioral Guidance Layer

## Objective
Implement a deterministic Behavioral Guidance Layer in APHDE by introducing two new UI pages and supporting deterministic engines/services, while preserving current backend scoring/confidence/context/governance behavior.

## Guiding Constraints
- No ML, no prediction, no black-box logic.
- No rewrite of existing scoring formulas.
- Preserve domain abstraction and governance boundaries.
- Keep Decision Dashboard operational and lightweight.
- Do not collapse new features into a single page.

## Delivery Summary
V6 will be delivered through six workstreams:
- A. Contracts + module scaffolding
- B. Tomorrow Plan engine + Action Center page
- C. Stagnation + weekly insights engines
- D. Insights & Trends page
- E. Dashboard boundary cleanup + integration wiring
- F. Test hardening, docs, release handoff

---

## Workstream A — Contracts and Scaffolding

### Scope
Create deterministic contracts and module skeletons for guidance/insight outputs.

### Tasks
1. Add new core modules:
   - `core/guidance/tomorrow_plan.py`
   - `core/insights/stagnation.py`
   - `core/insights/weekly_summary.py`
   - `core/insights/trend_views.py`
2. Add app service adapters:
   - `app/services/action_center_service.py`
   - `app/services/insights_service.py`
3. Define canonical payload contracts for:
   - tomorrow plan
   - alert model
   - weekly summary
   - trend chart payloads
4. Add docs contract file:
   - `docs/v6_behavioral_guidance_contracts.md`

### Exit Criteria
- All payload schemas defined and importable.
- No business logic in page files.

---

## Workstream B — Tomorrow Plan Engine + Action Center Page

### Scope
Deliver deterministic single-priority “Tomorrow Plan” and expose on new Action Center page.

### Tasks
1. Implement deterministic plan ranking in `core/guidance/tomorrow_plan.py`:
   - candidate extraction
   - weighted scoring
   - deterministic tie-break
2. Implement service adapter in `app/services/action_center_service.py`.
3. Add new Streamlit page:
   - `app/pages/04_action_center.py`
4. Render:
   - primary action
   - reason
   - confidence
   - severity
   - expected impact
   - optional risk alert card
5. Add technical trace expander for payload debug.

### Exit Criteria
- One deterministic top action returned for same input.
- Page renders cleanly with empty and populated histories.

---

## Workstream C — Stagnation + Weekly Insight Engines

### Scope
Implement deterministic detection/summarization modules.

### Tasks
1. Implement stagnation detector in `core/insights/stagnation.py`:
   - weight stagnation
   - overload flatline
   - compliance drift
   - persistent low recovery
2. Implement weekly summary in `core/insights/weekly_summary.py`:
   - planned vs completed
   - compliance percent
   - recovery shift
   - volatility direction
   - overload progress
3. Keep thresholds centralized as constants and versioned.
4. Add service integration in `app/services/insights_service.py`.

### Exit Criteria
- Deterministic alert objects produced with confidence + severity.
- Weekly summary produced when data sufficiency conditions are met.

---

## Workstream D — Insights & Trends Page

### Scope
Add analysis-dedicated page consuming insights service payloads.

### Tasks
1. Add page:
   - `app/pages/05_insights_trends.py`
2. Render sections:
   - weekly summary cards
   - stagnation alert list
   - drift overview
   - trend charts (weight/recovery/compliance/overload)
3. Add technical trace expander for raw payload.
4. Use neutral palette and consistency with global header/theme.

### Exit Criteria
- Analysis content fully isolated from dashboard.
- Charts render from deterministic historical data only.

---

## Workstream E — Dashboard Boundary Cleanup + Routing Integration

### Scope
Enforce page-responsibility boundaries.

### Tasks
1. Keep dashboard focused on operational snapshot only.
2. Ensure no stagnation/weekly heavy analytics on dashboard.
3. Add quick navigation from homepage to new pages.
4. Ensure consistent headers and spacing across all pages.

### Exit Criteria
- Dashboard remains concise and operational.
- Guidance and analysis live exclusively on dedicated pages.

---

## Workstream F — Testing, Documentation, Release

### Scope
Stabilize and document V6.

### Tasks
1. Unit tests:
   - `tests/unit/test_tomorrow_plan.py`
   - `tests/unit/test_stagnation.py`
   - `tests/unit/test_weekly_summary.py`
2. Integration tests:
   - `tests/integration/test_action_center_service.py`
   - `tests/integration/test_insights_service.py`
3. Determinism tests for repeated identical input histories.
4. Update docs:
   - `README.md` (or `aphde/README.md` section updates)
   - release notes file: `docs/release-notes-v6-behavioral-guidance.md`
5. QA checklist for page separation and no-JSON default rendering.

### Exit Criteria
- New tests pass and determinism checks hold.
- Documentation complete and release-ready.

---

## Suggested File Additions

### Core
- `core/guidance/tomorrow_plan.py`
- `core/insights/stagnation.py`
- `core/insights/weekly_summary.py`
- `core/insights/trend_views.py`

### App Services
- `app/services/action_center_service.py`
- `app/services/insights_service.py`

### UI Pages
- `app/pages/04_action_center.py`
- `app/pages/05_insights_trends.py`

### Tests
- `tests/unit/test_tomorrow_plan.py`
- `tests/unit/test_stagnation.py`
- `tests/unit/test_weekly_summary.py`
- `tests/integration/test_action_center_service.py`
- `tests/integration/test_insights_service.py`

### Docs
- `docs/v6_behavioral_guidance_contracts.md`
- `docs/release-notes-v6-behavioral-guidance.md`

---

## Milestones

1. **M1 (A+B):** Tomorrow Plan functional and Action Center page live.
2. **M2 (C+D):** Stagnation + weekly insights and Insights page live.
3. **M3 (E+F):** Dashboard boundary enforcement, tests/docs complete, release handoff.

---

## Validation Checklist

- Same input history yields identical tomorrow plan output.
- Stagnation alerts deterministic and threshold-bounded.
- Weekly summary generated only under sufficient data.
- Dashboard does not contain insights-heavy features.
- Action Center contains only guidance-oriented content.
- Insights page contains only analysis-oriented content.
- No default-visible raw JSON blocks outside technical expanders.

---

## Rollout Plan

1. Merge M1 behind branch.
2. Manual UI walkthrough with seeded scenarios.
3. Merge M2 with regression checks.
4. Finalize M3 with full test suite and release notes.
5. Tag release candidate (e.g., `v6.0.0-rc1`) then stable release.
