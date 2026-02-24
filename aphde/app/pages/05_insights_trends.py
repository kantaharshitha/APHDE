from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.insights_service import load_insights_view
from app.ui.layout import render_page_header, render_sidebar_navigation
from app.utils import DB_PATH, bootstrap_db_and_user

st.set_page_config(page_title="Insights & Trends", layout="wide")


def inject_insights_css() -> None:
    st.markdown(
        """
        <style>
        .it-summary {
            color: #1F2937;
            font-size: 1rem;
            line-height: 1.5;
        }
        .it-card {
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            background: #FBFCFD;
            padding: 0.85rem 0.95rem;
            min-height: 120px;
        }
        .it-label {
            color: #6B7280;
            font-size: 0.82rem;
            margin-bottom: 0.32rem;
        }
        .it-value {
            color: #1F2937;
            font-size: 1.15rem;
            font-weight: 700;
        }
        .it-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.15rem 0.58rem;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .it-chip-good { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .it-chip-monitor { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .it-chip-elevated { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
        .it-section-note {
            color: #6B7280;
            font-size: 0.82rem;
            margin-top: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _status_chip(status: str) -> str:
    status = status.strip().lower()
    if status in {"stable", "improving"}:
        cls = "it-chip-good"
    elif status in {"monitor", "moderate", "decreasing", "trending down"}:
        cls = "it-chip-monitor"
    else:
        cls = "it-chip-elevated"
    return f'<span class="it-chip {cls}">{status.title()}</span>'


def _trend_direction(values: list[float]) -> str:
    if len(values) < 2:
        return "stable"
    start = values[0]
    end = values[-1]
    delta = end - start
    if delta > 0.02:
        return "increasing"
    if delta < -0.02:
        return "decreasing"
    return "stable"


def build_weekly_summary_text(*, summary: dict, drift: dict, alerts: list[dict]) -> str:
    compliance = float(summary.get("compliance_pct", 0.0))
    recovery_shift = str(summary.get("recovery_shift", "flat"))
    overload = str(summary.get("overload_progress", "flat"))
    high_alert = bool(drift.get("has_high_severity_alert", False))

    if compliance >= 80.0 and recovery_shift != "down" and overload == "up":
        return "Strong adherence this week. Recovery remained stable while overload progressed in a controlled manner."
    if compliance >= 70.0 and recovery_shift == "down":
        return "Adherence remained solid this week, but recovery trended down. Monitor fatigue before increasing load."
    if high_alert or alerts:
        return "Multiple stress signals were detected this week. Keep progression conservative and prioritize recovery support."
    return "Stable week with moderate adherence and no major stress escalation."


def render_weekly_summary(summary: dict, drift: dict, alerts: list[dict]) -> None:
    with st.container():
        st.markdown("### Weekly Summary")
        text = build_weekly_summary_text(summary=summary, drift=drift, alerts=alerts)
        st.markdown(f'<div class="it-summary">{text}</div>', unsafe_allow_html=True)


def render_weekly_snapshot(summary: dict) -> None:
    with st.container():
        st.markdown("### Weekly Snapshot")
        recovery_shift = str(summary.get("recovery_shift", "flat"))
        overload_progress = str(summary.get("overload_progress", "flat"))
        recovery_label = "↓ Decreasing" if recovery_shift == "down" else ("↑ Increasing" if recovery_shift == "up" else "→ Stable")
        overload_label = "↑ Increasing" if overload_progress == "up" else ("↓ Decreasing" if overload_progress == "down" else "→ Stable")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(
            f'<div class="it-card"><div class="it-label">Sessions</div><div class="it-value">{summary.get("completed_sessions", 0)} / {summary.get("planned_sessions", 0)}</div></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="it-card"><div class="it-label">Compliance</div><div class="it-value">{float(summary.get("compliance_pct", 0.0)):.1f}%</div></div>',
            unsafe_allow_html=True,
        )
        c3.markdown(
            f'<div class="it-card"><div class="it-label">Recovery</div><div class="it-value">{recovery_label}</div></div>',
            unsafe_allow_html=True,
        )
        c4.markdown(
            f'<div class="it-card"><div class="it-label">Overload</div><div class="it-value">{overload_label}</div></div>',
            unsafe_allow_html=True,
        )


def render_drift_status(drift: dict) -> None:
    with st.container():
        st.markdown("### Drift Status")
        compliance = "Stable" if not drift.get("compliance_drift") else "Monitor"
        recovery = "Stable" if not drift.get("recovery_drift") else "Trending Down"
        if drift.get("has_high_severity_alert"):
            severity = "Elevated"
        elif drift.get("active_alert_count", 0) > 0:
            severity = "Monitor"
        else:
            severity = "Stable"

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'Compliance: {_status_chip(compliance)}', unsafe_allow_html=True)
        c2.markdown(f'Recovery: {_status_chip(recovery)}', unsafe_allow_html=True)
        c3.markdown(f'Severity Level: {_status_chip(severity)}', unsafe_allow_html=True)


def _alert_title(alert_type: str) -> str:
    mapping = {
        "persistent_low_recovery": "Persistent Low Recovery",
        "weight_trend_stagnation": "Weight Trend Plateau",
        "overload_flatline": "Overload Plateau",
        "compliance_drift": "Compliance Drift",
    }
    return mapping.get(alert_type, "Behavioral Stagnation Signal")


def render_stagnation_alerts(alerts: list[dict]) -> None:
    with st.container():
        st.markdown("### Stagnation Alert")
        if not alerts:
            st.caption("No plateau or stagnation signals detected this week.")
            return

        for alert in alerts:
            st.markdown(f"**{_alert_title(str(alert.get('type', '')))}**")
            st.markdown(alert.get("message", "Sustained pattern indicates potential stagnation."))
            recommendation = alert.get("recommendation")
            if recommendation:
                st.caption(recommendation)
            st.markdown('<div class="it-section-note">Monitor this pattern in the next evaluation window.</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


def _trend_interpretation(name: str, values: list[float]) -> str:
    direction = _trend_direction(values)
    if name == "weight":
        if direction == "decreasing":
            return "Weight stable with slight downward drift."
        if direction == "increasing":
            return "Weight trending upward over the current window."
        return "Weight trend appears stable."
    if name == "recovery":
        if direction == "decreasing":
            return "Recovery has declined and requires closer monitoring."
        if direction == "increasing":
            return "Recovery trend is improving gradually."
        return "Recovery trend is stable."
    if name == "compliance":
        if direction == "decreasing":
            return "Compliance is drifting down and may affect progress consistency."
        if direction == "increasing":
            return "Compliance is improving across recent entries."
        return "Compliance remains steady."
    if name == "overload":
        if direction == "increasing":
            return "Progressive increase in training load is visible."
        if direction == "decreasing":
            return "Training load has reduced during this window."
        return "Overload trend is flat."
    return "Trend interpretation unavailable."


def render_signal_trends(trends: dict) -> None:
    with st.container():
        st.markdown("### Signal Trends (Last 28 Days)")
        c1, c2 = st.columns(2)
        charts = [
            ("Weight Trend", "weight", "weight"),
            ("Recovery Trend", "recovery", "recovery"),
            ("Compliance Trend", "compliance", "compliance"),
            ("Overload Trend", "overload", "overload"),
        ]
        for idx, (title, key, col_name) in enumerate(charts):
            target_col = c1 if idx % 2 == 0 else c2
            with target_col:
                st.markdown(f"**{title}**")
                payload = trends.get(key, {})
                values = payload.get("values", [])
                if values:
                    st.line_chart(pd.DataFrame({col_name: values}))
                    st.caption(_trend_interpretation(key, values))
                else:
                    st.info("No data available.")


def render_technical_trace(view: dict) -> None:
    with st.expander("Technical Trace (Advanced)", expanded=False):
        st.write("Weekly insight payload")
        st.json(view.get("weekly_insight") or {})
        st.write("Stagnation alerts payload")
        st.json(view.get("stagnation_alerts") or [])
        st.write("Drift detection payload")
        st.json(view.get("drift_detection") or {})
        st.write("Trend slope payloads")
        st.json(view.get("trends") or {})


def main() -> None:
    user_id = bootstrap_db_and_user()
    render_sidebar_navigation(current_page="insights_trends", db_path=str(DB_PATH), user_id=user_id)
    inject_insights_css()
    render_page_header(
        title="Insights & Trends",
        subtitle="Interpretive weekly view of progress, drift, and caution signals.",
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

    summary = view.get("weekly_insight", {})
    drift = view.get("drift_detection", {})
    alerts = view.get("stagnation_alerts", [])
    trends = view.get("trends", {})

    render_weekly_summary(summary, drift, alerts)
    st.markdown("<br>", unsafe_allow_html=True)
    render_weekly_snapshot(summary)
    st.markdown("<br>", unsafe_allow_html=True)
    render_drift_status(drift)
    st.markdown("<br>", unsafe_allow_html=True)
    render_stagnation_alerts(alerts)
    st.markdown("<br>", unsafe_allow_html=True)
    render_signal_trends(trends)
    st.markdown("<br>", unsafe_allow_html=True)
    render_technical_trace(view)


main()

