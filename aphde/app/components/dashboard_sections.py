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
            padding: 1rem 1rem 0.9rem 1rem;
            background: #ffffff;
            margin-bottom: 1rem;
        }
        .aphde-title {
            font-size: 0.85rem;
            color: #64748b;
            letter-spacing: 0.02em;
            margin-bottom: 0.3rem;
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


def render_metric_row(*, latest: dict[str, Any], governance: dict[str, Any], confidence_version: str, context_version: str) -> None:
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


def render_recommendations_section(rows: list[dict[str, Any]]) -> None:
    st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
    st.markdown("### Recommendations")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No recommendations for the current run.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_diagnostics_tabs(*, confidence_breakdown: dict[str, Any], context_json: dict[str, Any], context_notes: list[str], trace: dict[str, Any]) -> None:
    tab1, tab2, tab3 = st.tabs(["Confidence", "Context", "Trace"])
    with tab1:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("#### Confidence Breakdown")
        st.json(confidence_breakdown or {})
        notes = trace.get("confidence_notes", []) if isinstance(trace, dict) else []
        if notes:
            st.markdown("#### Confidence Notes")
            for note in notes:
                st.write(f"- {note}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
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

    with tab3:
        st.markdown('<div class="aphde-section">', unsafe_allow_html=True)
        st.markdown("#### Explanation Trace")
        st.json(trace or {})
        st.markdown("</div>", unsafe_allow_html=True)


def render_governance_panel(
    *,
    governance: dict[str, Any],
    diff_payload: dict[str, Any] | None,
    history_payload: dict[str, Any],
) -> None:
    st.markdown('<div class="aphde-governance">', unsafe_allow_html=True)
    st.markdown("### Governance & Observability")
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

    st.markdown("#### Version Diff")
    if diff_payload is None:
        st.info("Select two different runs to view diff.")
    else:
        st.json(diff_payload)

    st.markdown("#### History Analytics")
    st.json(history_payload)
    st.markdown("</div>", unsafe_allow_html=True)
