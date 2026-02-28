from __future__ import annotations

import streamlit as st

from ..auth_ui import require_authenticated_user
from ..services.action_center_service import load_action_center_view
from ..ui.layout import render_page_header, render_sidebar_navigation
from ..utils import DB_PATH

st.set_page_config(page_title="Action Center", layout="wide")


def inject_action_center_css() -> None:
    st.markdown(
        """
        <style>
        .ac-head {
            color: #0f172a;
            font-size: 1.28rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.8rem;
        }
        .ac-main-action {
            color: #0f172a;
            font-size: 1.42rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 0.45rem;
        }
        .ac-body {
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.45;
        }
        .ac-chip {
            display: inline-block;
            padding: 0.19rem 0.62rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.35rem;
            margin-bottom: 0.3rem;
        }
        .ac-chip-info { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
        .ac-chip-impact-low { background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; }
        .ac-chip-impact-med { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
        .ac-chip-impact-high { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
        .ac-muted {
            color: #64748b;
            font-size: 0.86rem;
            margin-top: 0.45rem;
        }
        .ac-risk-title {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _impact_chip(severity: str) -> str:
    sev = str(severity).lower().strip()
    if sev == "high":
        return '<span class="ac-chip ac-chip-impact-high">High Impact</span>'
    if sev == "medium":
        return '<span class="ac-chip ac-chip-impact-med">Moderate Impact</span>'
    return '<span class="ac-chip ac-chip-impact-low">Low Impact</span>'


def _risk_explanation(level: str) -> str:
    level_norm = str(level).lower().strip()
    if level_norm == "high":
        return "Training fatigue is accumulating faster than recovery."
    if level_norm == "moderate":
        return "Multiple stress signals detected."
    if level_norm == "low":
        return "Minor stress signals are present but currently manageable."
    return "System stable. No elevated stress signals detected."


def render_tomorrows_plan(plan: dict | None) -> None:
    with st.container(border=True):
        st.markdown('<div class="ac-head">Tomorrow\'s Plan</div>', unsafe_allow_html=True)
        if not plan:
            st.info("No action plan available yet. Run an evaluation first.")
            return

        st.markdown(
            f'<div class="ac-main-action">{plan.get("action", "No action available.")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="ac-body">{plan.get("reason", "No explanation available.")}</div>',
            unsafe_allow_html=True,
        )

        confidence = float(plan.get("confidence", 0.0))
        severity = str(plan.get("severity", "low"))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<span class="ac-chip ac-chip-info">Confidence {confidence * 100:.0f}%</span>{_impact_chip(severity)}',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ac-muted">Apply for 7 days, then reassess.</div>', unsafe_allow_html=True)


def render_current_risk(alert: dict | None) -> None:
    with st.container(border=True):
        st.markdown('<div class="ac-risk-title">Current Risk Level</div>', unsafe_allow_html=True)
        if not alert:
            level = "Stable"
            explanation = _risk_explanation(level)
        else:
            level = str(alert.get("level", "Moderate"))
            explanation = str(alert.get("message") or _risk_explanation(level))
        st.markdown(f"Current Risk Level: **{level}**")
        st.caption(explanation)


def render_why_this_action(summary: dict | None) -> None:
    with st.expander("Why this action?"):
        if not summary:
            st.caption("No additional rationale available.")
            return
        st.markdown(f"- {summary.get('recovery_summary', 'Recovery trend unavailable.')}")
        st.markdown(f"- {summary.get('rpe_summary', 'RPE trend unavailable.')}")
        st.markdown(f"- {summary.get('compliance_summary', 'Compliance trend unavailable.')}")


def render_technical_trace(view: dict) -> None:
    plan = view.get("tomorrow_plan") or {}
    latest = view.get("latest") or {}
    trace = latest.get("trace", {}) if isinstance(latest.get("trace"), dict) else {}
    with st.expander("Technical Trace (Advanced)", expanded=False):
        st.markdown(f"- Action ID: `{plan.get('action_id', 'n/a')}`")
        st.markdown(f"- Priority Score: `{float(plan.get('priority_score', 0.0)):.4f}`")
        st.markdown(f"- Internal rule codes: `{', '.join(trace.get('triggered_rules', [])) if trace else 'none'}`")
        st.write("Raw signal values")
        st.json(trace.get("computed_signals", {}) if trace else {})


def main() -> None:
    user_id = require_authenticated_user()
    render_sidebar_navigation(current_page="action_center", db_path=str(DB_PATH), user_id=user_id)
    inject_action_center_css()
    render_page_header(
        title="Action Center",
        subtitle="Clear, deterministic guidance for what to do next.",
    )

    try:
        view = load_action_center_view(user_id=user_id, db_path=str(DB_PATH), recent_limit=28)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load action center view: {exc}")
        st.stop()

    if view.get("latest") is None:
        st.info("No evaluation runs found. Add logs and run evaluation to generate guidance.")
        render_technical_trace(view)
        return

    # Required hierarchy:
    # 1) Tomorrow's plan
    # 2) Current risk level
    # 3) Why this action? (expandable)
    # 4) Technical trace (collapsed)
    render_tomorrows_plan(view.get("tomorrow_plan"))
    render_current_risk(view.get("risk_alert"))
    render_why_this_action(view.get("why_this_action"))
    render_technical_trace(view)


main()


