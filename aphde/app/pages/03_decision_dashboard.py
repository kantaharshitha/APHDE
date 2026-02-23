from __future__ import annotations

import streamlit as st

from app.components.dashboard_sections import (
    inject_dashboard_css,
    render_diagnostics_tabs,
    render_governance_panel,
    render_metric_row,
    render_recommendations_section,
)
from app.services.dashboard_service import (
    build_diff_payload,
    build_governance_view,
    build_history_payload,
    build_recommendation_table,
    load_dashboard_data,
    trigger_evaluation,
)
from app.utils import DB_PATH, bootstrap_db_and_user


st.title("Decision Dashboard")
user_id = bootstrap_db_and_user()
inject_dashboard_css()

left, right = st.columns([1, 3])
with left:
    run_button = st.button("Run Evaluation", type="primary", use_container_width=True)
with right:
    st.caption("Deterministic decision outputs with governance observability.")

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
    data = load_dashboard_data(user_id=user_id, db_path=str(DB_PATH), recent_limit=25)
except Exception as exc:  # noqa: BLE001
    st.error(f"Failed to load dashboard data: {exc}")
    st.stop()

latest = data["latest"]
recent_runs = data["recent_runs"]
if latest is None:
    st.info("No decision runs found. Set a goal and add logs, then run evaluation.")
    st.stop()

trace = latest.get("trace", {})
confidence_breakdown = latest.get("confidence_breakdown", {})
context_json = latest.get("context_json", {})
context_notes = trace.get("context_notes", []) if isinstance(trace, dict) else []
confidence_version = latest.get("confidence_version", "conf_v1")
context_version = latest.get("context_version", "ctx_v1")

governance = build_governance_view(latest)
recommendation_rows = build_recommendation_table(latest)
history_payload = build_history_payload(recent_runs=recent_runs)

render_metric_row(
    latest=latest,
    governance=governance,
    confidence_version=confidence_version,
    context_version=context_version,
)

render_recommendations_section(recommendation_rows)

diff_payload = None
st.markdown("### Run Comparison")
if len(recent_runs) >= 2:
    options = [int(item["id"]) for item in recent_runs]
    c1, c2 = st.columns(2)
    with c1:
        run_a_id = st.selectbox("Base run", options=options, index=min(1, len(options) - 1))
    with c2:
        run_b_id = st.selectbox("Compare run", options=options, index=0)
    if run_a_id != run_b_id:
        diff_payload = build_diff_payload(recent_runs=recent_runs, run_a_id=run_a_id, run_b_id=run_b_id)
else:
    st.info("Need at least two runs for version comparison.")

render_governance_panel(governance=governance, diff_payload=diff_payload, history_payload=history_payload)

render_diagnostics_tabs(
    confidence_breakdown=confidence_breakdown,
    context_json=context_json,
    context_notes=context_notes,
    trace=trace,
)
