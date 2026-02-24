from __future__ import annotations

import streamlit as st

from app.components.dashboard_sections import (
    render_dashboard_operational_insights,
    inject_dashboard_css,
    render_metric_row,
    render_operational_view,
)
from app.ui.layout import render_page_header, render_sidebar_navigation
from app.services.dashboard_service import (
    trigger_evaluation,
)
from app.services.ui_data_service import load_dashboard_view
from app.utils import DB_PATH, bootstrap_db_and_user


user_id = bootstrap_db_and_user()
render_sidebar_navigation(current_page="decision_dashboard", db_path=str(DB_PATH), user_id=user_id)
inject_dashboard_css()
render_page_header(
    title="Decision Dashboard",
    subtitle="Operational snapshot of current alignment, recommendation, and context.",
)

left, right = st.columns([1, 3])
with left:
    run_button = st.button("Run Evaluation", type="primary", use_container_width=True)
with right:
    st.caption("Run evaluation and review current-state operational outputs.")

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

render_dashboard_operational_insights(
    trace=trace,
    context_json=context_json,
    context_version=context_version,
)

with st.expander("Technical Trace (Advanced)"):
    st.write("Confidence breakdown payload")
    st.json(confidence_breakdown or {})
    st.write("Context notes")
    st.json(context_notes or [])
