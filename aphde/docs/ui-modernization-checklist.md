# UI Modernization QA Checklist

Use this checklist before merging UI dashboard changes.

## Pre-Run
- Start Streamlit from `aphde/` with `.venv\Scripts\python.exe -m streamlit run app/main.py`.
- Confirm app opens without Python tracebacks.
- Confirm database bootstrap and user seed still work.

## Operational View
- `Run Evaluation` triggers successfully and shows completion message.
- KPI strip updates with:
  - alignment score
  - alignment confidence
  - risk score
  - determinism status
  - context applied
- Recommendations table renders without static placeholder rows.
- Run Snapshot panel shows decision id and top recommendation details.
- Empty-state messaging appears when recommendations are absent.

## Diagnostic View
- `Signals` tab renders computed signal payload as a readable table.
- `Confidence Breakdown` tab renders breakdown JSON and confidence notes.
- `Context Details` tab renders modulation buckets and context notes.
- `Score Breakdown` tab renders score components and triggered rules.
- Raw trace expander opens and displays complete trace JSON.

## Governance View
- Version metrics display:
  - engine version
  - confidence version
  - context version
  - domain version
- Determinism badge text is visible and matches determinism status.
- Output hash and input signature hash are visible and non-empty when available.
- Run comparison works for two different runs and shows structured diff blocks.
- History section renders:
  - run count
  - context frequency
  - determinism pass rate
  - alignment trend chart
  - confidence trend chart
  - rule trigger distribution table

## Error/Resilience Checks
- Loading spinner appears during dashboard data load.
- Dashboard shows clear error message when data load fails.
- Dashboard shows clear empty-state message when no decision runs exist.

## Test Suite
- Run `.venv\Scripts\python.exe -m pytest tests/integration/test_run_evaluation.py -q`.
- Run `.venv\Scripts\python.exe -m pytest tests/integration/test_ui_dashboard_contracts.py -q`.
