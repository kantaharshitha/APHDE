from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        .aphde-section {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem;
            background: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .aphde-header {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        }
        .aphde-kpi-strip {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.8rem;
            margin-bottom: 1rem;
            background: #ffffff;
        }
        .aphde-governance {
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 1rem;
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        }
        .aphde-hash {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            font-size: 0.75rem;
            padding: 0.45rem 0.55rem;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #f8fafc;
            word-break: break-all;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header() -> None:
    st.markdown(
        """
        <div class="aphde-header">
            <div style="font-size:1.1rem; font-weight:600; color:#0f172a;">Decision Dashboard</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:0.2rem;">
                Deterministic decision outputs with diagnostic and governance observability.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(*, latest: dict[str, Any], governance: dict[str, Any], confidence_version: str, context_version: str) -> None:
    st.markdown('<div class="aphde-kpi-strip">', unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Alignment Score", f"{latest['alignment_score']:.2f}")
    m2.metric("Alignment Confidence", f"{latest['alignment_confidence']:.2f}")
    m3.metric("Risk Score", f"{latest['risk_score']:.2f}")
    m4.metric("Determinism", governance["determinism_status"])
    m5.metric("Context Applied", "Yes" if latest.get("context_applied") else "No")
    st.caption(
        f"Engine: {latest.get('engine_version','v1')} | "
        f"Confidence: {confidence_version} | Context: {context_version} | "
        f"Domain: {governance['domain_name']} ({governance['domain_version']})"
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_recommendations_section(rows: list[dict[str, Any]]) -> None:
    st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
    st.markdown("### Recommendations")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No recommendations for the current run.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_operational_view(
    *,
    latest: dict[str, Any],
    governance: dict[str, Any],
    recommendation_rows: list[dict[str, Any]],
) -> None:
    left, right = st.columns([2, 1])

    with left:
        render_recommendations_section(recommendation_rows)

    with right:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("### Run Snapshot")
        st.write(f"Decision ID: `{latest.get('id', 'n/a')}`")
        st.write(f"Engine Version: `{latest.get('engine_version', 'unknown')}`")
        st.write(f"Determinism: `{governance.get('determinism_status', 'Unknown')}`")
        st.write(f"Context Applied: `{'Yes' if latest.get('context_applied') else 'No'}`")
        top_rec = recommendation_rows[0] if recommendation_rows else None
        if top_rec:
            st.markdown("#### Top Recommendation")
            st.write(f"Priority: `{top_rec.get('Priority')}`")
            st.write(top_rec.get("Action", "No action text available."))
            st.caption(f"Category: {top_rec.get('Category', 'n/a')}")
        else:
            st.info("No recommendation generated for this run.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
    st.markdown("### Operational Signals")
    c1, c2, c3 = st.columns(3)
    c1.metric("Alignment Score", f"{latest.get('alignment_score', 0.0):.2f}")
    c2.metric("Alignment Confidence", f"{latest.get('alignment_confidence', 0.0):.2f}")
    c3.metric("Risk Score", f"{latest.get('risk_score', 0.0):.2f}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_diagnostics_tabs(*, confidence_breakdown: dict[str, Any], context_json: dict[str, Any], context_notes: list[str], trace: dict[str, Any]) -> None:
    tab1, tab2, tab3, tab4 = st.tabs(["Signals", "Confidence Breakdown", "Context Details", "Score Breakdown"])

    with tab1:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("#### Computed Signals")
        computed_signals = trace.get("computed_signals", {}) if isinstance(trace, dict) else {}
        if computed_signals:
            signal_rows: list[dict[str, Any]] = []
            for key, value in computed_signals.items():
                if isinstance(value, dict):
                    for nested_key, nested_value in value.items():
                        signal_rows.append(
                            {
                                "Signal": f"{key}.{nested_key}",
                                "Value": nested_value,
                            }
                        )
                else:
                    signal_rows.append({"Signal": key, "Value": value})
            st.dataframe(pd.DataFrame(signal_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No computed signals available in this trace.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("#### Confidence Breakdown")
        st.json(confidence_breakdown or {})
        notes = trace.get("confidence_notes", []) if isinstance(trace, dict) else []
        if notes:
            st.markdown("#### Confidence Notes")
            for note in notes:
                st.write(f"- {note}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("#### Score Breakdown")
        score_breakdown = trace.get("score_breakdown", {}) if isinstance(trace, dict) else {}
        if score_breakdown:
            st.dataframe(
                pd.DataFrame(
                    [{"Component": key, "Value": value} for key, value in score_breakdown.items()]
                ),
                use_container_width=True,
                hide_index=True,
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

        with st.expander("Raw Trace"):
            st.json(trace or {})
        st.markdown("</div>", unsafe_allow_html=True)


def render_governance_panel(
    *,
    governance: dict[str, Any],
    latest: dict[str, Any],
    confidence_version: str,
    context_version: str,
    diff_payload: dict[str, Any] | None,
    history_payload: dict[str, Any],
) -> None:
    st.markdown('<div class="aphde-governance">', unsafe_allow_html=True)
    st.markdown("### Governance & Observability")
    status = governance.get("determinism_status", "Unknown")
    if status == "Verified":
        badge = "VERIFIED"
    elif status == "Mismatch":
        badge = "MISMATCH"
    else:
        badge = "UNKNOWN"

    st.markdown(f"**Determinism Status Badge:** {badge}")

    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Engine Version", str(latest.get("engine_version", "unknown")))
    v2.metric("Confidence Version", str(confidence_version))
    v3.metric("Context Version", str(context_version))
    v4.metric("Domain Version", str(governance.get("domain_version", "unknown")))

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Output Hash**")
        st.markdown(f'<div class="aphde-hash">{governance.get("output_hash","")}</div>', unsafe_allow_html=True)
        st.markdown("**Input Signature Hash**")
        st.markdown(
            f'<div class="aphde-hash">{governance.get("input_signature_hash","")}</div>',
            unsafe_allow_html=True,
        )
    with g2:
        st.write(f"Determinism Status: `{governance.get('determinism_status')}`")
        st.write(f"Determinism Reason: `{governance.get('determinism_reason')}`")
        st.write(f"Baseline Decision ID: `{governance.get('baseline_decision_id')}`")
        st.write(f"Domain: `{governance.get('domain_name', 'unknown')}`")

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

        st.markdown("**Context Changes**")
        st.json(diff_payload.get("context_changes", {}))

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
    st.markdown("</div>", unsafe_allow_html=True)
