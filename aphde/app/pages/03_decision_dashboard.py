from __future__ import annotations

import streamlit as st

from app.components.dashboard_sections import (
    inject_dashboard_css,
    render_diagnostics_tabs,
    render_governance_panel,
    render_metric_row,
    render_operational_view,
)
from app.ui.layout import render_page_header
from app.services.dashboard_service import (
    trigger_evaluation,
)
from app.services.ui_data_service import load_dashboard_view, load_run_diff
from app.utils import DB_PATH, bootstrap_db_and_user


user_id = bootstrap_db_and_user()
inject_dashboard_css()
render_page_header(
    title="Decision Dashboard",
    subtitle="Review deterministic evaluation outputs, diagnostics, and governance state.",
)

left, right = st.columns([1, 3])
with left:
    run_button = st.button("Run Evaluation", type="primary", use_container_width=True)
with right:
    st.caption("Run and inspect deterministic outputs across recommendations, diagnostics, and governance.")

if run_button:
    with st.spinner("Running evaluation..."):
        try:
            decision_id = trigger_evaluation(user_id=user_id, db_path=str(DB_PATH))
            st.success(f"Evaluation complete. decision_id={decision_id}")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001
            st.error(f"Evaluation failed: {exc}")

try:
    with st.spinner("Loading dashboard data..."):
        view = load_dashboard_view(user_id=user_id, db_path=str(DB_PATH), recent_limit=25)
except Exception as exc:  # noqa: BLE001
    st.error(f"Failed to load dashboard data: {exc}")
    st.stop()

latest = view["latest"]
recent_runs = view["recent_runs"]
if latest is None:
    st.info("No decision runs found. Set a goal and add logs, then run evaluation.")
    st.stop()

trace = view["trace"]
confidence_breakdown = view["confidence_breakdown"]
context_json = view["context_json"]
context_notes = view["context_notes"]
confidence_version = view["confidence_version"]
context_version = view["context_version"]
governance = view["governance"]
recommendation_rows = view["recommendation_rows"]
history_payload = view["history_payload"]

render_metric_row(
    latest=latest,
    governance=governance,
    confidence_version=confidence_version,
    context_version=context_version,
)

render_operational_view(
    latest=latest,
    governance=governance,
    recommendation_rows=recommendation_rows,
)

render_diagnostics_tabs(
    confidence_breakdown=confidence_breakdown,
    context_json=context_json,
    context_notes=context_notes,
    trace=trace,
)

diff_payload = None
st.markdown("### Run Comparison")
if len(recent_runs) >= 2:
    options = [int(item["id"]) for item in recent_runs]
    c1, c2 = st.columns(2)
    with c1:
        run_a_id = st.selectbox("Base run", options=options, index=min(1, len(options) - 1), key="run_a_id")
    with c2:
        run_b_id = st.selectbox("Compare run", options=options, index=0, key="run_b_id")
    if run_a_id != run_b_id:
        diff_payload = load_run_diff(recent_runs=recent_runs, run_a_id=run_a_id, run_b_id=run_b_id)
else:
    st.info("Need at least two runs for version comparison.")

render_governance_panel(
    governance=governance,
    latest=latest,
    confidence_version=confidence_version,
    context_version=context_version,
    diff_payload=diff_payload,
    history_payload=history_payload,
)
