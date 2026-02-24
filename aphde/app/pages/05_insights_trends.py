from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.insights_service import load_insights_view
from app.ui.layout import render_page_header
from app.utils import DB_PATH, bootstrap_db_and_user

st.set_page_config(page_title="Insights & Trends", layout="wide")


def inject_insights_css() -> None:
    st.markdown(
        """
        <style>
        .it-card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 0.95rem 1rem;
            margin-bottom: 1rem;
        }
        .it-label {
            color: #6B7280;
            font-size: 0.82rem;
            margin-bottom: 0.32rem;
        }
        .it-value {
            color: #1F2937;
            font-size: 1.35rem;
            font-weight: 700;
        }
        .it-sub {
            color: #4B5563;
            font-size: 0.88rem;
            margin-top: 0.3rem;
        }
        .it-alert {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
        }
        .it-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.15rem 0.62rem;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .it-chip-low { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .it-chip-medium { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .it-chip-high { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _severity_chip(severity: str) -> str:
    sev = str(severity).lower().strip()
    if sev == "high":
        cls = "it-chip-high"
    elif sev == "medium":
        cls = "it-chip-medium"
    else:
        cls = "it-chip-low"
    return f'<span class="it-chip {cls}">{sev.title()}</span>'


def render_weekly_summary(summary: dict) -> None:
    st.markdown("### Weekly Insights")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(
        f'<div class="it-card"><div class="it-label">Planned Sessions</div><div class="it-value">{summary.get("planned_sessions", 0)}</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="it-card"><div class="it-label">Completed Sessions</div><div class="it-value">{summary.get("completed_sessions", 0)}</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="it-card"><div class="it-label">Compliance %</div><div class="it-value">{float(summary.get("compliance_pct", 0.0)):.1f}%</div></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div class="it-card"><div class="it-label">Recovery Shift</div><div class="it-value">{summary.get("recovery_shift", "flat")}</div></div>',
        unsafe_allow_html=True,
    )
    c5.markdown(
        f'<div class="it-card"><div class="it-label">Overload Progress</div><div class="it-value">{summary.get("overload_progress", "flat")}</div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Window: {summary.get('week_start', 'n/a')} to {summary.get('week_end', 'n/a')}")


def render_stagnation_alerts(alerts: list[dict]) -> None:
    st.markdown("### Stagnation Alerts")
    if not alerts:
        st.info("No stagnation alerts detected in the current analysis window.")
        return
    for alert in alerts:
        st.markdown('<div class="it-alert">', unsafe_allow_html=True)
        st.markdown(
            f"{_severity_chip(alert.get('severity', 'low'))} &nbsp; **{alert.get('type', 'unknown')}**",
            unsafe_allow_html=True,
        )
        st.write(alert.get("message", ""))
        st.caption(alert.get("recommendation", ""))
        st.markdown("</div>", unsafe_allow_html=True)


def render_drift_detection(drift: dict) -> None:
    st.markdown("### Drift Detection")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Compliance Drift", "Yes" if drift.get("compliance_drift") else "No")
    c2.metric("Recovery Drift", "Yes" if drift.get("recovery_drift") else "No")
    c3.metric("Active Alerts", int(drift.get("active_alert_count", 0)))
    c4.metric("High Severity", "Yes" if drift.get("has_high_severity_alert") else "No")


def render_trends(trends: dict) -> None:
    st.markdown("### Trend Charts")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Weight Trend**")
        weight = trends.get("weight", {})
        values = weight.get("values", [])
        if values:
            st.line_chart(pd.DataFrame({"weight": values}))
            st.caption(f"Slope: {weight.get('slope')}")
        else:
            st.info("No weight data.")
        st.markdown("**Recovery Trend**")
        recovery = trends.get("recovery", {})
        rvals = recovery.get("values", [])
        if rvals:
            st.line_chart(pd.DataFrame({"recovery": rvals}))
            st.caption(f"Slope: {recovery.get('slope')}")
        else:
            st.info("No recovery data.")
    with c2:
        st.markdown("**Compliance Trend**")
        compliance = trends.get("compliance", {})
        cvals = compliance.get("values", [])
        if cvals:
            st.line_chart(pd.DataFrame({"compliance": cvals}))
            st.caption(f"Slope: {compliance.get('slope')}")
        else:
            st.info("No compliance data.")
        st.markdown("**Overload Trend**")
        overload = trends.get("overload", {})
        ovals = overload.get("values", [])
        if ovals:
            st.line_chart(pd.DataFrame({"overload": ovals}))
            st.caption(f"Slope: {overload.get('slope')}")
        else:
            st.info("No overload data.")


def render_technical_trace(view: dict) -> None:
    with st.expander("Technical Trace (Advanced)"):
        st.write("Weekly insight payload")
        st.json(view.get("weekly_insight") or {})
        st.write("Stagnation alerts payload")
        st.json(view.get("stagnation_alerts") or [])
        st.write("Drift detection payload")
        st.json(view.get("drift_detection") or {})


def main() -> None:
    user_id = bootstrap_db_and_user()
    inject_insights_css()
    render_page_header(
        title="Insights & Trends",
        subtitle="Deterministic pattern analysis across recent behavioral signals.",
    )

    try:
        view = load_insights_view(user_id=user_id, db_path=str(DB_PATH), recent_limit=42)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load insights view: {exc}")
        st.stop()

    if view.get("latest") is None:
        st.info("No evaluation runs found. Run evaluation to unlock insights.")
        render_technical_trace(view)
        return

    render_weekly_summary(view.get("weekly_insight", {}))
    render_drift_detection(view.get("drift_detection", {}))
    render_stagnation_alerts(view.get("stagnation_alerts", []))
    render_trends(view.get("trends", {}))
    render_technical_trace(view)


main()
