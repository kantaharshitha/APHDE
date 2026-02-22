from __future__ import annotations

import json

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.decision_repo import DecisionRunRepository
from core.services.run_evaluation import run_evaluation

st.title("Decision Dashboard")
user_id = bootstrap_db_and_user()

col1, col2 = st.columns([1, 2])
with col1:
    run_button = st.button("Run Evaluation", type="primary", use_container_width=True)

if run_button:
    try:
        decision_id = run_evaluation(user_id=user_id, db_path=str(DB_PATH))
        st.success(f"Evaluation complete. decision_id={decision_id}")
    except ValueError as exc:
        st.error(str(exc))

with get_connection(DB_PATH) as conn:
    latest = DecisionRunRepository(conn).latest(user_id)

if latest is None:
    st.info("No decision runs found. Set a goal and add logs, then run evaluation.")
    st.stop()

recommendations = json.loads(latest["recommendations_json"])
trace = json.loads(latest["trace_json"])

metric1, metric2 = st.columns(2)
metric1.metric("Alignment Score", f"{latest['alignment_score']:.2f}")
metric2.metric("Risk Score", f"{latest['risk_score']:.2f}")

st.subheader("Ranked Recommendations")
if recommendations:
    for rec in recommendations:
        st.markdown(
            f"**#{rec['priority']} [{rec['category']}]** {rec['action']}  \n"
            f"Expected effect: {rec['expected_effect']}  \n"
            f"Confidence: {rec['confidence']:.2f} | Reasons: {', '.join(rec['reason_codes']) if rec['reason_codes'] else 'N/A'}"
        )
else:
    st.write("No recommendations for the current run.")

st.subheader("Explanation Trace")
st.json(trace)
