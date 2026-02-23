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

alignment_confidence = float(latest["alignment_confidence"]) if "alignment_confidence" in latest.keys() else 0.0
confidence_version = latest["confidence_version"] if "confidence_version" in latest.keys() else "conf_v1"

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Alignment Score", f"{latest['alignment_score']:.2f}")
metric2.metric("Risk Score", f"{latest['risk_score']:.2f}")
metric3.metric("Alignment Confidence", f"{alignment_confidence:.2f}")

st.caption(f"Engine version: {latest['engine_version']} | Confidence version: {confidence_version}")

rec_conf_list = []
if "recommendation_confidence_json" in latest.keys() and latest["recommendation_confidence_json"]:
    rec_conf_list = json.loads(latest["recommendation_confidence_json"])
rec_conf_map = {item.get("id"): item.get("confidence") for item in rec_conf_list}

st.subheader("Ranked Recommendations")
if recommendations:
    for rec in recommendations:
        computed_conf = rec_conf_map.get(rec["id"])
        conf_text = f"{computed_conf:.2f}" if isinstance(computed_conf, (int, float)) else "N/A"
        st.markdown(
            f"**#{rec['priority']} [{rec['category']}]** {rec['action']}  \n"
            f"Expected effect: {rec['expected_effect']}  \n"
            f"Base confidence: {rec['confidence']:.2f} | Model confidence: {conf_text}  \n"
            f"Reasons: {', '.join(rec['reason_codes']) if rec['reason_codes'] else 'N/A'}"
        )
else:
    st.write("No recommendations for the current run.")

st.subheader("Confidence Breakdown")
confidence_breakdown = {}
if "confidence_breakdown_json" in latest.keys() and latest["confidence_breakdown_json"]:
    confidence_breakdown = json.loads(latest["confidence_breakdown_json"])
if confidence_breakdown:
    st.json(confidence_breakdown)
else:
    st.info("No confidence breakdown available for this decision row.")

notes = trace.get("confidence_notes", []) if isinstance(trace, dict) else []
if notes:
    st.subheader("Confidence Notes")
    for note in notes:
        st.write(f"- {note}")

st.subheader("Explanation Trace")
st.json(trace)
