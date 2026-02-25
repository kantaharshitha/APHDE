from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st

SIGNAL_TOOLTIPS: dict[str, str] = {
    "Trend Slope": "Direction and magnitude of recent performance change.",
    "Volatility Index": "Stability measure across recent signals.",
    "Compliance Ratio": "Adherence to planned sessions over rolling window.",
    "Muscle Balance Index": "Distribution balance across trained muscle groups.",
    "Recovery Index": "Estimated recovery readiness level.",
    "Progressive Overload Score": "Consistency of progressive training intensity.",
}


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        .aphde-section {
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1.2rem;
            background: #ffffff;
            margin-bottom: 1.1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }
        .aphde-header {
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            background: #f8fafc;
        }
        .aphde-kpi-strip {
            border: none;
            padding: 0;
            margin-bottom: 1rem;
            background: transparent;
        }
        .aphde-governance {
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1rem 1rem 1.2rem 1rem;
            background: #ffffff;
        }
        .aphde-hash {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            font-size: 0.75rem;
            padding: 0.45rem 0.55rem;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #f8fafc;
            word-break: break-all;
            color: #0f172a;
        }
        .aphde-kpi-card {
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            background: #ffffff;
            padding: 1rem 1rem 0.8rem 1rem;
            min-height: 170px;
        }
        .aphde-kpi-title {
            color: #475569;
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }
        .aphde-kpi-value {
            color: #0f172a;
            font-size: 2.15rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.55rem;
        }
        .aphde-kpi-sub {
            color: #475569;
            font-size: 0.9rem;
        }
        .aphde-pill {
            display: inline-block;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 600;
            padding: 0.22rem 0.7rem;
        }
        .aphde-pill-ok {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        .aphde-pill-info {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #93c5fd;
        }
        .aphde-pill-warn {
            background: #fff7ed;
            color: #c2410c;
            border: 1px solid #fdba74;
        }
        .aphde-rec-card {
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            background: #ffffff;
            padding: 1.1rem;
            margin-top: 0.85rem;
        }
        .aphde-rec-number {
            width: 38px;
            height: 38px;
            border-radius: 999px;
            background: #e2e8f0;
            color: #0f172a;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.8rem;
            flex-shrink: 0;
        }
        .aphde-rec-title {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 700;
        }
        .aphde-rec-text {
            color: #334155;
            font-size: 0.94rem;
            margin-top: 0.45rem;
        }
        .aphde-rule-row {
            padding: 0.6rem 0;
            border-bottom: 1px solid #f1f5f9;
        }
        .aphde-rule-row:last-child {
            border-bottom: 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.1rem;
            background: #f1f5f9;
            border-radius: 999px;
            padding: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            height: 2.2rem;
            padding: 0 1rem;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
        }
        .aphde-signal-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.7rem;
        }
        .aphde-signal-table th, .aphde-signal-table td {
            border-bottom: 1px solid #f1f5f9;
            padding: 0.55rem 0.4rem;
            text-align: left;
            color: #1f2937;
            font-size: 0.9rem;
        }
        .aphde-signal-table th {
            color: #475569;
            font-size: 0.82rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _pill(text: str, cls: str) -> str:
    return f'<span class="aphde-pill {cls}">{html.escape(text)}</span>'


def _kpi_card(title: str, value: str, subline: str, pill: str | None = None) -> str:
    body = f"""
        <div class="aphde-kpi-card">
            <div class="aphde-kpi-title">{html.escape(title)}</div>
            <div class="aphde-kpi-value">{html.escape(value)}</div>
            <div class="aphde-kpi-sub">{html.escape(subline)}</div>
        </div>
    """
    if pill:
        body = body.replace("</div>\n        </div>", f"<div style='margin-top:0.55rem'>{pill}</div></div>")
    return body


def render_metric_row(*, latest: dict[str, Any], governance: dict[str, Any], confidence_version: str, context_version: str) -> None:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            _kpi_card("Alignment Score", f"{latest['alignment_score']:.0f}", "Composite alignment quality"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            _kpi_card("Alignment Confidence", f"{latest['alignment_confidence'] * 100:.0f}%", "Model certainty"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            _kpi_card("Risk Score", f"{latest['risk_score']:.0f}", "Lower is better"),
            unsafe_allow_html=True,
        )
    with c4:
        context_text = "Yes" if latest.get("context_applied") else "No"
        context_cls = "aphde-pill-info" if latest.get("context_applied") else "aphde-pill-warn"
        st.markdown(
            _kpi_card("Context Applied", context_text, "Context modulation status", _pill(context_text, context_cls)),
            unsafe_allow_html=True,
        )
    st.caption(
        f"engine={latest.get('engine_version','v1')} | confidence={confidence_version} | "
        f"context={context_version} | domain={governance.get('domain_name','unknown')}/{governance.get('domain_version','unknown')}"
    )


def render_recommendations_section(rows: list[dict[str, Any]]) -> None:
    with st.container(border=True):
        st.markdown("### Recommendations")
        if rows:
            for idx, row in enumerate(rows[:6], start=1):
                priority = int(row.get("Priority") or idx)
                impact = "High Impact" if priority == 1 else ("Medium Impact" if priority <= 3 else "Low Impact")
                impact_cls = "aphde-pill-warn" if priority == 1 else ("aphde-pill-info" if priority <= 3 else "aphde-pill-ok")
                conf_val = row.get("Model Conf")
                if conf_val is None:
                    conf_val = row.get("Base Conf")
                if isinstance(conf_val, float):
                    conf_label = f"{conf_val * 100:.0f}% conf."
                else:
                    conf_label = "n/a conf."

                action = str(row.get("Action") or "No action specified")
                effect = str(row.get("Expected Effect") or "")
                category = str(row.get("Category") or "")
                reasons = str(row.get("Reasons") or "")

                rec_html = f"""
                <div class="aphde-rec-card">
                  <div style="display:flex; justify-content:space-between; gap:1rem;">
                    <div style="display:flex; align-items:flex-start;">
                      <div class="aphde-rec-number">{idx}</div>
                      <div>
                        <div class="aphde-rec-title">{html.escape(action)}</div>
                        <div class="aphde-rec-text">{html.escape(effect or category or "Recommendation from deterministic rules.")}</div>
                        <div class="aphde-rec-text" style="font-size:0.83rem; color:#64748b;">{html.escape(reasons)}</div>
                      </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.45rem; white-space:nowrap;">
                      {_pill(impact, impact_cls)}
                      {_pill(conf_label, "aphde-pill-info")}
                    </div>
                  </div>
                </div>
                """
                st.markdown(rec_html, unsafe_allow_html=True)
        else:
            st.info("No recommendations for the current run.")


def render_operational_view(
    *,
    latest: dict[str, Any],
    governance: dict[str, Any],
    recommendation_rows: list[dict[str, Any]],
) -> None:
    _ = latest, governance
    render_recommendations_section(recommendation_rows)


def render_dashboard_operational_insights(*, trace: dict[str, Any], context_json: dict[str, Any], context_version: str) -> None:
    with st.container(border=True):
        st.markdown("### Signals")
        computed_signals = trace.get("computed_signals", {}) if isinstance(trace, dict) else {}
        values: dict[str, float] = {}
        if computed_signals:
            for key, value in computed_signals.items():
                if isinstance(value, (int, float)):
                    normalized = float(value)
                    if "volatility" in key:
                        normalized = max(0.0, min(100.0, (1.0 - normalized) * 100.0))
                    elif normalized <= 1.0:
                        normalized = normalized * 100.0
                    values[key.replace("_", " ").title()] = round(normalized, 2)
            if values:
                table_rows = []
                for signal_name, score in values.items():
                    tooltip = SIGNAL_TOOLTIPS.get(signal_name, "Derived deterministic signal.")
                    table_rows.append(
                        f"<tr><td title='{html.escape(tooltip)}'>{html.escape(signal_name)}</td><td>{score:.2f}</td></tr>"
                    )
                st.markdown(
                    """
                    <table class="aphde-signal-table">
                        <thead><tr><th>Signal</th><th>Score</th></tr></thead>
                        <tbody>
                    """
                    + "".join(table_rows)
                    + """
                        </tbody>
                    </table>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption("Hover over each signal name for definition.")
            else:
                st.info("No numeric signal values available in this trace.")
        else:
            st.info("No computed signals available in this trace.")

    with st.container(border=True):
        st.markdown("### Context Summary")
        metadata = context_json.get("metadata", {}) if isinstance(context_json, dict) else {}
        applied = bool(metadata and metadata.get("context_type"))
        st.markdown(f"- Context Applied: {'Yes' if applied else 'No'}")
        st.markdown(f"- Context Version: {context_version}")
        if metadata:
            phase = metadata.get("phase")
            context_type = metadata.get("context_type")
            if context_type is not None:
                st.markdown(f"- Context Type: {context_type}")
            if phase is not None:
                st.markdown(f"- Phase: {phase}")


def render_diagnostics_tabs(*, confidence_breakdown: dict[str, Any], context_json: dict[str, Any], context_notes: list[str], trace: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown("### Diagnostics")
        tab1, tab2, tab3, tab4 = st.tabs(["Signals", "Confidence Breakdown", "Context Details", "Score Breakdown"])

        with tab1:
            st.markdown("#### Signal Snapshot")
            computed_signals = trace.get("computed_signals", {}) if isinstance(trace, dict) else {}
            values: dict[str, float] = {}
            if computed_signals:
                for key, value in computed_signals.items():
                    if isinstance(value, (int, float)):
                        normalized = float(value)
                        if "volatility" in key:
                            normalized = max(0.0, min(100.0, (1.0 - normalized) * 100.0))
                        elif normalized <= 1.0:
                            normalized = normalized * 100.0
                        values[key.replace("_", " ").title()] = round(normalized, 2)
                if values:
                    sig_df = pd.DataFrame([{"Signal": k, "Score": v} for k, v in values.items()]).set_index("Signal")
                    st.bar_chart(sig_df)
                    table_rows = []
                    for signal_name, score in values.items():
                        tooltip = SIGNAL_TOOLTIPS.get(signal_name, "Derived deterministic signal.")
                        table_rows.append(
                            f"<tr><td title='{html.escape(tooltip)}'>{html.escape(signal_name)}</td><td>{score:.2f}</td></tr>"
                        )
                    st.markdown(
                        """
                        <table class="aphde-signal-table">
                            <thead><tr><th>Signal</th><th>Score</th></tr></thead>
                            <tbody>
                        """
                        + "".join(table_rows)
                        + """
                            </tbody>
                        </table>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.caption("Hover over each signal name for definition.")
                else:
                    st.info("No numeric signal values available in this trace.")
            else:
                st.info("No computed signals available in this trace.")

        with tab2:
            st.markdown("#### Confidence Breakdown")
            components = confidence_breakdown.get("components", {}) if isinstance(confidence_breakdown, dict) else {}
            weights = confidence_breakdown.get("weights", {}) if isinstance(confidence_breakdown, dict) else {}
            if components:
                for key, val in components.items():
                    pct = max(0.0, min(100.0, float(val) * 100.0))
                    w = weights.get(key)
                    left, right = st.columns([6, 1])
                    left.markdown(f"**{key.replace('_', ' ').title()}**")
                    right.markdown(f"**{pct:.0f}%**")
                    st.progress(int(round(pct)))
                    if w is not None:
                        st.caption(f"w: {float(w):.2f}")
                weighted = confidence_breakdown.get("confidence")
                if weighted is not None:
                    st.markdown("---")
                    st.markdown(f"### Weighted Average: `{float(weighted) * 100:.0f}%`")
            else:
                st.caption("No confidence component breakdown available.")
            notes = trace.get("confidence_notes", []) if isinstance(trace, dict) else []
            if notes:
                st.markdown("#### Confidence Notes")
                for note in notes:
                    st.write(f"- {note}")

        with tab3:
            st.markdown("#### Context Details")
            metadata = context_json.get("metadata", {}) if isinstance(context_json, dict) else {}
            context_rows = [
                ("Time Window", "7 days", True),
                ("User Profile", "Active Adult", True),
                ("Environmental", metadata.get("source", "Not available"), bool(metadata)),
                ("Seasonal Adjustment", metadata.get("season", "Not applied"), "season" in metadata),
                ("Goal Alignment", metadata.get("phase", "Maintenance"), bool(metadata)),
            ]
            for label, value, applied in context_rows:
                pill = _pill("Applied", "aphde-pill-ok") if applied else _pill("Not Applied", "aphde-pill-info")
                st.markdown(
                    f"""
                    <div class="aphde-rule-row">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                          <div style="font-size:1.05rem; font-weight:600; color:#0f172a;">{html.escape(label)}</div>
                          <div style="font-size:0.95rem; color:#475569;">{html.escape(str(value))}</div>
                        </div>
                        <div>{pill}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with st.expander("Technical Trace"):
                c1, c2, c3 = st.columns(3)
                c1.markdown("#### Modulated Thresholds")
                c2.markdown("#### Penalty Scalars")
                c3.markdown("#### Tolerance Adjustments")
                c1.json(context_json.get("modulated_thresholds", {}))
                c2.json(context_json.get("penalty_scalars", {}))
                c3.json(context_json.get("tolerance_adjustments", {}))
            if context_notes:
                st.markdown("#### Context Notes")
                for note in context_notes:
                    st.write(f"- {note}")

        with tab4:
            st.markdown("#### Score Breakdown")
            score_breakdown = trace.get("score_breakdown", {}) if isinstance(trace, dict) else {}
            if score_breakdown:
                left_col, right_col = st.columns(2)
                score_items = list(score_breakdown.items())
                mid = max(1, len(score_items) // 2)
                with left_col:
                    st.markdown("#### Alignment Components")
                    for key, value in score_items[:mid]:
                        st.markdown(
                            f"""
                            <div class="aphde-rule-row">
                                <span style="color:#475569;">{html.escape(key.replace('_', ' ').title())}</span>
                                <span style="float:right; font-weight:700; color:#0f172a;">{value}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                with right_col:
                    st.markdown("#### Risk Components")
                    for key, value in score_items[mid:]:
                        st.markdown(
                            f"""
                            <div class="aphde-rule-row">
                                <span style="color:#475569;">{html.escape(key.replace('_', ' ').title())}</span>
                                <span style="float:right; font-weight:700; color:#0f172a;">{value}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No score breakdown present in this trace.")

            st.markdown("#### Triggered Rules")
            triggered_rules = trace.get("triggered_rules", []) if isinstance(trace, dict) else []
            if triggered_rules:
                for rule in triggered_rules:
                    st.write(f"- {rule}")
            else:
                st.info("No rules triggered in this run.")

            with st.expander("Technical Trace"):
                st.json(trace or {})


def render_governance_panel(
    *,
    governance: dict[str, Any],
    latest: dict[str, Any],
    confidence_version: str,
    context_version: str,
    diff_payload: dict[str, Any] | None,
    history_payload: dict[str, Any],
) -> None:
    with st.container(border=True):
        st.markdown("### Governance & Versioning")
        status = governance.get("determinism_status", "Unknown")
        if status == "Verified":
            badge = _pill("Determinism Verified", "aphde-pill-ok")
        elif status == "Mismatch":
            badge = _pill("Determinism Mismatch", "aphde-pill-warn")
        else:
            badge = _pill("Determinism Unknown", "aphde-pill-info")

        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Version Information")
            st.markdown(f"Engine Version: `{latest.get('engine_version', 'unknown')}`")
            st.markdown(f"Confidence Version: `{confidence_version}`")
            st.markdown(f"Context Version: `{context_version}`")
            st.markdown(f"Domain Version: `{governance.get('domain_version', 'unknown')}`")
        with g2:
            st.markdown("#### Output Verification")
            st.markdown("**Output Hash (SHA-256)**")
            st.markdown(f'<div class="aphde-hash">{governance.get("output_hash","")}</div>', unsafe_allow_html=True)
            with st.expander("Governance Details"):
                st.markdown("<div style='margin-top:0.35rem;'>" + badge + "</div>", unsafe_allow_html=True)
                st.caption(
                    f"reason={governance.get('determinism_reason', 'n/a')} | baseline={governance.get('baseline_decision_id', 'n/a')}"
                )
                st.markdown("**Input Signature Hash**")
                st.markdown(
                    f'<div class="aphde-hash">{governance.get("input_signature_hash","")}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("#### Version Diff")
        if diff_payload is None:
            st.info("Select two different runs to view diff.")
        else:
            score_delta = diff_payload.get("score_delta", {})
            d1, d2, d3 = st.columns(3)
            d1.metric("Alignment Delta", f"{float(score_delta.get('alignment_score_delta', 0.0)):+.2f}")
            d2.metric("Risk Delta", f"{float(score_delta.get('risk_score_delta', 0.0)):+.2f}")
            d3.metric("Confidence Delta", f"{float(score_delta.get('alignment_confidence_delta', 0.0)):+.2f}")

            rec_changes = diff_payload.get("recommendation_changes", {})
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Added Recommendations**")
                added = rec_changes.get("added", [])
                st.write(added if added else "None")
                st.markdown("**Removed Recommendations**")
                removed = rec_changes.get("removed", [])
                st.write(removed if removed else "None")
            with c2:
                st.markdown("**Rank Shifts**")
                shifts = rec_changes.get("rank_shifts", [])
                if shifts:
                    st.dataframe(pd.DataFrame(shifts), use_container_width=True, hide_index=True)
                else:
                    st.write("None")

            context_changes = diff_payload.get("context_changes", {})
            context_applied_to = bool(context_changes.get("context_applied_to", False))
            context_applied_from = bool(context_changes.get("context_applied_from", False))
            compared = "Yes" if context_applied_from != context_applied_to else "No"
            st.markdown("**Context Summary**")
            st.markdown(f"- Context Applied: {'Yes' if context_applied_to else 'No'}")
            st.markdown(f"- Context Version: {context_changes.get('context_version_to', 'n/a')}")
            st.markdown(f"- Compared To Baseline: {compared}")
            with st.expander("Technical Trace"):
                st.json(diff_payload)

        st.markdown("#### History Analytics")
        h1, h2, h3 = st.columns(3)
        h1.metric("Run Count", int(history_payload.get("count", 0)))
        h2.metric("Context Frequency", f"{float(history_payload.get('context_application_frequency', 0.0)):.2f}")
        h3.metric("Determinism Pass Rate", f"{float(history_payload.get('determinism_pass_rate', 0.0)):.2f}")

        trend_col1, trend_col2 = st.columns(2)
        with trend_col1:
            alignment_trend = history_payload.get("alignment_trend", [])
            st.markdown("**Alignment Trend**")
            if alignment_trend:
                st.line_chart(pd.DataFrame({"alignment_score": alignment_trend}))
            else:
                st.info("No alignment trend data.")
        with trend_col2:
            confidence_trend = history_payload.get("confidence_trend", [])
            st.markdown("**Confidence Trend**")
            if confidence_trend:
                st.line_chart(pd.DataFrame({"alignment_confidence": confidence_trend}))
            else:
                st.info("No confidence trend data.")

        st.markdown("**Rule Trigger Distribution**")
        rule_dist = history_payload.get("rule_trigger_distribution", {})
        if rule_dist:
            rule_df = pd.DataFrame(
                [{"rule": rule, "count": count} for rule, count in rule_dist.items()]
            ).sort_values(by="count", ascending=False)
            st.dataframe(rule_df, use_container_width=True, hide_index=True)
        else:
            st.info("No triggered rules in selected history window.")
