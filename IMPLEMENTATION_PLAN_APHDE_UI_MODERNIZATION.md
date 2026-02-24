# APHDE UI Modernization Implementation Plan

## Objective
Implement the Streamlit UI modernization for APHDE so the interface clearly exposes Operational, Diagnostic, and Governance architecture layers while preserving backend determinism and logic.

## Non-Negotiable Constraints
- No backend formula changes.
- No scoring/confidence/context logic changes.
- No ML or predictive additions.
- UI layer must remain presentation-only.

## Delivery Strategy
Use six sequential workstreams with tight validation at each step.

## Workstream A: Baseline and Contracts
### Tasks
- Inventory existing Streamlit pages and reusable UI utilities.
- Document payload contracts required by UI:
  - Decision summary
  - Recommendations
  - Confidence/context/governance payloads
  - Version diff payload
  - History analytics payload
- Add a UI adapter/service module for payload normalization only.

### Output
- `docs/ui_data_contracts.md`
- `app/services/ui_data_service.py` (or equivalent)

### Exit Criteria
- All required keys mapped in one place.
- Missing-key handling is explicit and testable.

## Workstream B: Layout Foundation
### Tasks
- Set Streamlit `wide` layout and page skeleton.
- Implement base sections:
  - Header controls
  - KPI strip
  - Tab scaffold (Operational/Diagnostic/Governance)
- Add minimal global CSS for cards, spacing, and typography hierarchy.

### Output
- Updated dashboard page layout.
- Shared render helpers for card/metric blocks.

### Exit Criteria
- Layout structure complete with static placeholders.
- Responsive behavior acceptable on common laptop widths.

## Workstream C: Operational View Integration
### Tasks
- Bind KPI cards to live data (`alignment_score`, `alignment_confidence`, `risk_score`, `context_applied`, `determinism_verified`).
- Replace static recommendation placeholders with ranked table/cards.
- Add loading, empty, and error states.

### Output
- Fully dynamic Operational tab.

### Exit Criteria
- Running evaluation updates KPIs and recommendations without manual refresh hacks.

## Workstream D: Diagnostic View Integration
### Tasks
- Add Diagnostic subtabs:
  - Signals
  - Confidence Breakdown
  - Context Details
  - Score Breakdown
- Render structured payloads using `st.dataframe`, `st.json`, and concise summary cards.
- Ensure no business logic calculations happen in UI.

### Output
- Dynamic diagnostic inspection surface.

### Exit Criteria
- Every diagnostic panel displays live payload data or explicit empty-state messaging.

## Workstream E: Governance View Integration
### Tasks
- Build governance panel with:
  - Version triad (+ domain version if present)
  - Determinism badge
  - Output hash
- Build run comparison UI for version diff payload.
- Add history analytics section:
  - Alignment trend
  - Confidence trend
  - Context frequency
  - Rule trigger distribution

### Output
- Full governance and observability UI.

### Exit Criteria
- Governance panel is visually distinct and complete.
- Version diff and trend sections are functional with real run data.

## Workstream F: Hardening and Documentation
### Tasks
- Add UI-focused tests (render smoke + payload key contract checks).
- Perform deterministic UI regression pass across multiple runs.
- Update README with run instructions and architecture section mapping.
- Capture before/after screenshots for portfolio use.

### Output
- Stable release-ready UI modernization.

### Exit Criteria
- No critical rendering errors.
- All required architecture signals are visible from UI.
- Documentation updated.

## Suggested File Plan
- `app/pages/03_decision_dashboard.py` (or split into multiple pages)
- `app/components/kpi_cards.py`
- `app/components/recommendations_panel.py`
- `app/components/diagnostic_panels.py`
- `app/components/governance_panel.py`
- `app/services/ui_data_service.py`
- `app/styles/ui_theme.css`
- `docs/ui_data_contracts.md`

## Milestones
1. M1: Contracts + layout skeleton complete.
2. M2: Operational + Diagnostic tabs fully dynamic.
3. M3: Governance + history + diff complete.
4. M4: Tests/docs polish and release handoff.

## Validation Checklist
- KPI values match backend run output.
- Recommendations display rank and confidence correctly.
- Context metadata appears with version/notes.
- Version triad, determinism status, and output hash are visible.
- Diff output correctly reflects selected run pair.
- History charts render from stored decision runs.

## Rollout
- Merge behind a feature branch first.
- Run integration tests + manual Streamlit validation.
- Promote to main after governance view verification.
