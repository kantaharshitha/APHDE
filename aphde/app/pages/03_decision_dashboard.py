from __future__ import annotations

import json

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.decision_repo import DecisionRunRepository
from core.governance.history_analyzer import summarize_history
from core.governance.version_diff import diff_runs
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
    decision_repo = DecisionRunRepository(conn)
    latest = decision_repo.latest(user_id)
    recent_rows = decision_repo.list_recent(user_id=user_id, limit=25)

if latest is None:
    st.info("No decision runs found. Set a goal and add logs, then run evaluation.")
    st.stop()

recommendations = json.loads(latest["recommendations_json"])
trace = json.loads(latest["trace_json"])
governance_block = trace.get("governance", {}) if isinstance(trace, dict) else {}

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

st.subheader("Governance")
governance_col1, governance_col2, governance_col3 = st.columns(3)

determinism_verified = latest["determinism_verified"] if "determinism_verified" in latest.keys() else None
if determinism_verified is None:
    determinism_text = "Unknown (no baseline)"
elif int(determinism_verified) == 1:
    determinism_text = "Verified"
else:
    determinism_text = "Mismatch"

output_hash = latest["output_hash"] if "output_hash" in latest.keys() else governance_block.get("output_hash", "")
input_signature_hash = (
    latest["input_signature_hash"] if "input_signature_hash" in latest.keys() else governance_block.get("input_signature_hash", "")
)
domain_name = trace.get("domain_name", "unknown") if isinstance(trace, dict) else "unknown"
domain_version = trace.get("domain_version", "unknown") if isinstance(trace, dict) else "unknown"

governance_col1.metric("Determinism", determinism_text)
governance_col2.metric("Domain", domain_name)
governance_col3.metric("Domain Version", domain_version)
st.caption(f"Output Hash: `{output_hash}`")
st.caption(f"Input Signature Hash: `{input_signature_hash}`")

st.markdown("**Version Diff Viewer**")
if len(recent_rows) >= 2:
    run_options = [int(row["id"]) for row in recent_rows]
    diff_col1, diff_col2 = st.columns(2)
    with diff_col1:
        run_a_id = st.selectbox("Base run", options=run_options, index=min(1, len(run_options) - 1))
    with diff_col2:
        run_b_id = st.selectbox("Compare run", options=run_options, index=0)

    if run_a_id == run_b_id:
        st.info("Select two different runs to compare.")
    else:
        row_map = {int(row["id"]): row for row in recent_rows}
        row_a = row_map[run_a_id]
        row_b = row_map[run_b_id]
        run_a = {
            "alignment_score": float(row_a["alignment_score"]),
            "risk_score": float(row_a["risk_score"]),
            "alignment_confidence": float(row_a["alignment_confidence"]) if "alignment_confidence" in row_a.keys() else 0.0,
            "recommendations": json.loads(row_a["recommendations_json"]) if row_a["recommendations_json"] else [],
            "context_applied": bool(row_a["context_applied"]) if "context_applied" in row_a.keys() else False,
            "context_version": row_a["context_version"] if "context_version" in row_a.keys() else "ctx_v1",
        }
        run_b = {
            "alignment_score": float(row_b["alignment_score"]),
            "risk_score": float(row_b["risk_score"]),
            "alignment_confidence": float(row_b["alignment_confidence"]) if "alignment_confidence" in row_b.keys() else 0.0,
            "recommendations": json.loads(row_b["recommendations_json"]) if row_b["recommendations_json"] else [],
            "context_applied": bool(row_b["context_applied"]) if "context_applied" in row_b.keys() else False,
            "context_version": row_b["context_version"] if "context_version" in row_b.keys() else "ctx_v1",
        }
        st.json(diff_runs(run_a, run_b))
else:
    st.info("Need at least 2 runs for version diff.")

st.markdown("**Evaluation History Analytics**")
history_runs = []
for row in recent_rows:
    trace_json = json.loads(row["trace_json"]) if row["trace_json"] else {}
    governance = trace_json.get("governance", {}) if isinstance(trace_json, dict) else {}
    history_runs.append(
        {
            "alignment_score": float(row["alignment_score"]),
            "alignment_confidence": float(row["alignment_confidence"]) if "alignment_confidence" in row.keys() else 0.0,
            "context_applied": bool(row["context_applied"]) if "context_applied" in row.keys() else False,
            "triggered_rules": trace_json.get("triggered_rules", []) if isinstance(trace_json, dict) else [],
            "determinism_verified": (
                bool(row["determinism_verified"]) if "determinism_verified" in row.keys() and row["determinism_verified"] is not None else None
            ),
            "determinism_reason": governance.get("determinism_reason"),
        }
    )
history_summary = summarize_history(history_runs)
st.json(history_summary)

st.subheader("Explanation Trace")
st.json(trace)
