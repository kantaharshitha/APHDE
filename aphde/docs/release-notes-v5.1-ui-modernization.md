# Release Notes: v5.1.0 UI Modernization

## Summary
This release modernizes the Streamlit dashboard to expose APHDE architecture depth across Operational, Diagnostic, and Governance views while preserving deterministic backend behavior.

## Highlights
- Added UI data contract adapter layer:
  - `app/services/ui_data_service.py`
- Refactored dashboard into structured tabs:
  - Operational View
  - Diagnostic View
  - Governance View
- Expanded governance observability display:
  - version triad + domain version
  - determinism status badge
  - output hash and input signature hash
  - structured run diff and history analytics
- Added UI contract documentation:
  - `docs/ui_data_contracts.md`
- Added UI QA checklist:
  - `docs/ui-modernization-checklist.md`
- Added integration coverage for UI service contracts:
  - `tests/integration/test_ui_dashboard_contracts.py`

## Validation
- Full test suite pass: `57 passed`
- Streamlit startup smoke check pass on local host (`app/main.py`)

## Compatibility
- No backend decision logic changes.
- No scoring/confidence/context formula changes.
- No ML or predictive behavior introduced.
