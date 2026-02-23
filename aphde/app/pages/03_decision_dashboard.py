from __future__ import annotations

import json

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.decision_repo import DecisionRunRepository
from core.services.run_evaluation import run_evaluation
from domains.health.domain_definition import HealthDomainDefinition


st.title("Decision Dashboard")
user_id = bootstrap_db_and_user()
st.markdown(
    """
    <style>
    .ctx-box {
        border: 1px solid #d9e3f0;
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        background: #f8fbff;
        margin-bottom: 0.75rem;
    }
    .ctx-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
    }
    .ctx-item {
        font-size: 0.85rem;
        color: #2f4b67;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 2])
with col1:
    run_button = st.button("Run Evaluation", type="primary", use_container_width=True)

if run_button:
    try:
        decision_id = run_evaluation(
            user_id=user_id,
            db_path=str(DB_PATH),
            domain_definition=HealthDomainDefinition(),
        )
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
context_applied = bool(latest["context_applied"]) if "context_applied" in latest.keys() else bool(trace.get("context_applied", False))
context_version = latest["context_version"] if "context_version" in latest.keys() else str(trace.get("context_version", "ctx_v1"))
context_json = {}
if "context_json" in latest.keys() and latest["context_json"]:
    context_json = json.loads(latest["context_json"])
elif isinstance(trace, dict):
    context_json = trace.get("context_json", {}) or {}
context_notes = trace.get("context_notes", []) if isinstance(trace, dict) else []
context_meta = context_json.get("metadata", {}) if isinstance(context_json, dict) else {}
context_type = context_meta.get("context_type", "none")
context_phase = context_meta.get("phase", "n/a")

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Alignment Score", f"{latest['alignment_score']:.2f}")
metric2.metric("Risk Score", f"{latest['risk_score']:.2f}")
metric3.metric("Alignment Confidence", f"{alignment_confidence:.2f}")
metric4.metric("Context Applied", "Yes" if context_applied else "No")

st.caption(
    f"Engine version: {latest['engine_version']} | "
    f"Confidence version: {confidence_version} | "
    f"Context version: {context_version}"
)

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

st.subheader("Context Engine")
left, right = st.columns(2)
with left:
    st.markdown(
        f"""
        <div class="ctx-box">
            <div class="ctx-title">Context Summary</div>
            <div class="ctx-item">Type: <b>{context_type}</b></div>
            <div class="ctx-item">Phase: <b>{context_phase}</b></div>
            <div class="ctx-item">Applied: <b>{"yes" if context_applied else "no"}</b></div>
            <div class="ctx-item">Version: <b>{context_version}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    if context_notes:
        st.markdown(
            """
            <div class="ctx-box">
                <div class="ctx-title">Context Notes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for note in context_notes:
            st.write(f"- {note}")
    else:
        st.write("Context notes: none")

if context_json:
    thresholds = context_json.get("modulated_thresholds", {}) if isinstance(context_json, dict) else {}
    scalars = context_json.get("penalty_scalars", {}) if isinstance(context_json, dict) else {}
    adjustments = context_json.get("tolerance_adjustments", {}) if isinstance(context_json, dict) else {}

    st.caption("Context modulation details")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("**Modulated thresholds**")
        st.json(thresholds)
    with t2:
        st.markdown("**Penalty scalars**")
        st.json(scalars)
    with t3:
        st.markdown("**Tolerance adjustments**")
        st.json(adjustments)

st.subheader("Explanation Trace")
st.json(trace)
