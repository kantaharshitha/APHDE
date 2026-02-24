# APHDE UI Modernization PRD

## Executive Summary
This PRD defines a Streamlit UI modernization for APHDE that exposes the system's deterministic architecture and governance maturity without changing backend logic. The redesigned UI will present Operational, Diagnostic, and Governance views with clear data bindings to existing services.

## Problem Statement
The backend architecture is mature (decision engine, confidence, context, governance), but the current UI does not make these layers visible enough for testing, demos, and portfolio presentation. Users cannot easily inspect determinism status, version triad, confidence internals, or run-to-run differences.

## Scope
- Redesign Streamlit dashboard layout and interaction flow.
- Surface architecture-level telemetry and governance artifacts.
- Replace placeholder/demo UI fragments with dynamic backend bindings.

Out of scope:
- Any backend formula or decision logic changes.
- ML/predictive features.
- New domain behavior.

## UI Architecture Overview
UI follows strict separation of concerns:
- Presentation layer: Streamlit pages/components only.
- UI service layer: fetches and shapes backend payloads for rendering.
- Backend/core: unchanged deterministic logic.

## Layout Structure
- Top bar: run controls, goal/context selectors, run trigger.
- KPI strip: alignment score, confidence, risk score, determinism status, context applied.
- Main body with tabs:
  - Operational View
  - Diagnostic View
  - Governance View

## Component Design
- `RunControls`: user id, goal, context inputs, run button.
- `KpiCards`: metric cards for primary values.
- `RecommendationsTable`: ranked recommendations with confidence.
- `SignalsPanel`: key derived signals.
- `ConfidencePanel`: confidence factors/breakdown.
- `ContextPanel`: context metadata, modulation notes.
- `GovernancePanel`: version triad, output hash, determinism badge.
- `VersionDiffPanel`: compare two runs and show deltas.
- `HistoryPanel`: trend and frequency analytics.

## Data Binding Requirements
Bind directly to existing backend outputs:
- `alignment_score`
- `alignment_confidence`
- `risk_score`
- `recommendations`
- `context_applied`, `context_version`, `context_json`
- `confidence_breakdown`
- `engine_version`, `confidence_version`, `context_version`, `domain_version`
- `determinism_verified`, `output_hash`
- `version_diff_payload`
- `history_analytics_payload`

## Interaction Patterns
- Use tile/card-style selection where practical to reduce dropdown-heavy UX.
- Keep forms explicit and deterministic (no hidden auto-updates that could confuse evaluation provenance).
- Show loading, empty, and error states for every data block.

## Governance Panel Requirements
Governance section must visibly include:
- Version triad (+ domain version when present)
- Determinism status badge
- Canonical output hash
- Run-to-run diff viewer (score/confidence/recommendation/context deltas)

## Charting Strategy
Use Streamlit-native charts for:
- Alignment trend over time
- Confidence trend over time
- Context application frequency
- Rule trigger distribution

## Styling
- Wide layout.
- Minimal CSS for card borders, spacing, type hierarchy, and section separation.
- Visual distinction for governance blocks without heavy animation.

## State Management
Use `st.session_state` for:
- Selected run ids for comparison
- Current filters
- Last evaluation payload
- Page-level loading/error flags

## Accessibility and Usability
- High-contrast metric labels and status badges.
- Deterministic, readable ordering of sections.
- Avoid deep nested UI patterns; keep inspection paths shallow.

## Testing Strategy
- UI render smoke tests for key pages.
- Contract checks for required payload keys.
- Regression checks for governance display fields.
- Manual QA checklist for loading/error/empty states.

## Risks and Mitigations
- Risk: UI drift from backend schema.
  - Mitigation: centralized UI service adapters with strict key mapping.
- Risk: Governance data overwhelming main flow.
  - Mitigation: split views and clear section priorities.
- Risk: Figma parity conflicts with Streamlit constraints.
  - Mitigation: preserve structure and hierarchy over pixel-perfect parity.

## Definition of Done
- All required data points are rendered dynamically.
- Governance panel is complete and visually distinct.
- Diagnostic tabs surface signals/confidence/context clearly.
- No backend logic/formula changes.
- UI docs and integration instructions updated.

## Portfolio Positioning
The UI should demonstrate APHDE as a deterministic, explainable architecture system with production-minded governance and reproducibility visibility, not as a basic wellness dashboard.
