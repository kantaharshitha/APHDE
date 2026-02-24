# APHDE UI Data Contracts

This document defines the data bindings used by Streamlit pages. It keeps UI rendering separate from deterministic backend logic.

## Source Layers
- `core/*`: deterministic engine, scoring, confidence, context, governance.
- `app/services/dashboard_service.py`: backend-facing read model assembly.
- `app/services/ui_data_service.py`: UI-facing adapter and normalization.

## Dashboard View Contract
`load_dashboard_view(user_id, db_path, recent_limit)` returns:

- `latest: dict | None`
- `recent_runs: list[dict]`
- `recommendation_rows: list[dict]`
- `governance: dict`
- `history_payload: dict`
- `trace: dict`
- `confidence_breakdown: dict`
- `context_json: dict`
- `context_notes: list[str]`
- `confidence_version: str`
- `context_version: str`

## Required Render Keys

### KPI / Summary
- `latest.alignment_score`
- `latest.alignment_confidence`
- `latest.risk_score`
- `latest.context_applied`
- `latest.engine_version`
- `governance.determinism_status`

### Recommendations
- `latest.recommendations`
- `latest.recommendation_confidence`

### Context and Confidence
- `confidence_breakdown`
- `context_json`
- `context_notes`
- `trace.confidence_notes`

### Governance
- `governance.output_hash`
- `governance.input_signature_hash`
- `governance.determinism_reason`
- `governance.baseline_decision_id`
- `governance.domain_name`
- `governance.domain_version`

### Diff / History
- `load_run_diff(recent_runs, run_a_id, run_b_id)` payload
- `history_payload` from governance history analyzer

## Contract Rules
- UI must only render payloads; no scoring or confidence math in UI.
- Missing optional keys must degrade gracefully to empty/default values.
- Changes to backend schema should be normalized in `ui_data_service.py`, not in pages/components.
