from __future__ import annotations

import streamlit as st

from app.services.action_center_service import load_action_center_view
from app.ui.layout import render_page_header
from app.utils import DB_PATH, bootstrap_db_and_user

st.set_page_config(page_title="Action Center", layout="wide")


def inject_action_center_css() -> None:
    st.markdown(
        """
        <style>
        .ac-section {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 1rem 1rem 0.9rem 1rem;
            margin-bottom: 1rem;
        }
        .ac-hero-title {
            color: #1F2937;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .ac-text {
            color: #374151;
            font-size: 0.95rem;
        }
        .ac-chip {
            display: inline-block;
            padding: 0.2rem 0.62rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }
        .ac-chip-info { background: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .ac-chip-ok { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .ac-chip-warn { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .ac-chip-high { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _severity_chip(severity: str) -> str:
    severity = severity.lower().strip()
    if severity == "high":
        return '<span class="ac-chip ac-chip-high">High Severity</span>'
    if severity == "medium":
        return '<span class="ac-chip ac-chip-warn">Medium Severity</span>'
    return '<span class="ac-chip ac-chip-ok">Low Severity</span>'


def render_tomorrow_plan(plan: dict | None) -> None:
    st.markdown('<div class="ac-section">', unsafe_allow_html=True)
    st.markdown("### Tomorrow Plan")
    if not plan:
        st.info("No action plan available yet. Run an evaluation first.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(f'<div class="ac-hero-title">{plan.get("action", "No action available")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ac-text">{plan.get("expected_impact", "")}</div>', unsafe_allow_html=True)
    st.markdown(" ")

    confidence = float(plan.get("confidence", 0.0))
    severity = str(plan.get("severity", "low"))
    st.markdown(
        f"""
        <span class="ac-chip ac-chip-info">Confidence: {confidence * 100:.0f}%</span>
        {_severity_chip(severity)}
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Priority Reasoning")
    st.write(plan.get("reason", "No reason available."))
    st.caption(f"Action ID: {plan.get('action_id', 'n/a')} | Priority Score: {float(plan.get('priority_score', 0.0)):.4f}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_risk_alert(alert: dict | None) -> None:
    if not alert:
        return
    chip = "ac-chip-high" if alert.get("severity") == "high" else "ac-chip-warn"
    st.markdown('<div class="ac-section">', unsafe_allow_html=True)
    st.markdown("### Active Risk Alert")
    st.markdown(f'<span class="ac-chip {chip}">{str(alert.get("severity", "")).title()} Risk</span>', unsafe_allow_html=True)
    st.write(alert.get("message", "Risk condition present."))
    rules = alert.get("rules", [])
    if rules:
        st.caption("Triggered rules: " + ", ".join(str(r) for r in rules))
    st.markdown("</div>", unsafe_allow_html=True)


def render_technical_trace(view: dict) -> None:
    with st.expander("Technical Trace (Advanced)"):
        st.write("Latest run snapshot")
        st.json(view.get("latest") or {})
        st.write("Tomorrow plan payload")
        st.json(view.get("tomorrow_plan") or {})
        st.write("Risk alert payload")
        st.json(view.get("risk_alert") or {})


def main() -> None:
    user_id = bootstrap_db_and_user()
    inject_action_center_css()
    render_page_header(
        title="Action Center",
        subtitle="Deterministic guidance for the next best action.",
    )

    try:
        view = load_action_center_view(user_id=user_id, db_path=str(DB_PATH), recent_limit=28)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load action center view: {exc}")
        st.stop()

    if view.get("latest") is None:
        st.info("No evaluation runs found. Add logs and run evaluation to generate tomorrow guidance.")
        render_technical_trace(view)
        return

    render_tomorrow_plan(view.get("tomorrow_plan"))
    render_risk_alert(view.get("risk_alert"))
    render_technical_trace(view)


main()
