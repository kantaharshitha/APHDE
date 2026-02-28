from __future__ import annotations

import json
from typing import Any

import streamlit as st

from aphde.app.auth_ui import require_authenticated_user
from aphde.app.ui.layout import render_page_header, render_sidebar_navigation
from aphde.app.utils import DB_PATH
from core.data.db import get_connection
from core.data.repositories.goal_repo import GoalRepository
from core.models.enums import GoalType
from core.scoring.confidence import CONFIDENCE_VERSION
from domains.health.domain_definition import HealthDomainDefinition

st.set_page_config(layout="wide")

ENGINE_VERSION = "v1"
CONTEXT_VERSION = "ctx_v1"


STRATEGY_CONFIG: dict[GoalType, dict[str, Any]] = {
    GoalType.WEIGHT_LOSS: {
        "title": "Weight Loss",
        "description": "Reduce body mass with consistency-first thresholding.",
        "focus": "Focus: adherence and stable downward trend.",
        "philosophy": "Prioritizes compliance and trend consistency while limiting volatility spikes.",
        "signal_priority": "Compliance ratio + trend slope",
        "recovery_tolerance": "Moderate recovery tolerance",
        "volatility_profile": "Low volatility tolerance",
        "defaults": {
            "min_compliance": 0.80,
            "min_recovery": 0.55,
            "max_volatility": 0.08,
            "min_overload": 0.50,
        },
    },
    GoalType.RECOMPOSITION: {
        "title": "Recomposition",
        "description": "Balance fat reduction and muscle support under stable load.",
        "focus": "Focus: overload quality and recovery balance.",
        "philosophy": "Balances threshold strictness across recovery, overload, and compliance.",
        "signal_priority": "Overload score + recovery index",
        "recovery_tolerance": "Lower tolerance for recovery drops",
        "volatility_profile": "Moderate volatility tolerance",
        "defaults": {
            "min_compliance": 0.78,
            "min_recovery": 0.58,
            "max_volatility": 0.09,
            "min_overload": 0.60,
        },
    },
    GoalType.STRENGTH_GAIN: {
        "title": "Strength Gain",
        "description": "Drive progressive overload without destabilizing recovery.",
        "focus": "Focus: overload progression with recovery floor.",
        "philosophy": "Sets stricter overload thresholds while monitoring fatigue and variability.",
        "signal_priority": "Progressive overload + recovery index",
        "recovery_tolerance": "Lower tolerance for under-recovery",
        "volatility_profile": "Moderate volatility tolerance",
        "defaults": {
            "min_compliance": 0.71,
            "min_recovery": 0.55,
            "max_volatility": 0.08,
            "min_overload": 0.65,
        },
    },
    GoalType.GENERAL_HEALTH: {
        "title": "General Health",
        "description": "Maintain stable behavioral quality with broad tolerance.",
        "focus": "Focus: broad consistency and sustainable recovery.",
        "philosophy": "Uses balanced thresholds to support long-term adherence over aggressive tuning.",
        "signal_priority": "Compliance ratio + recovery index",
        "recovery_tolerance": "Higher recovery tolerance",
        "volatility_profile": "Higher volatility tolerance",
        "defaults": {
            "min_compliance": 0.72,
            "min_recovery": 0.50,
            "max_volatility": 0.11,
            "min_overload": 0.45,
        },
    },
}

THRESHOLD_META: dict[str, dict[str, Any]] = {
    "min_compliance": {
        "label": "Minimum compliance",
        "min": 0.50,
        "max": 1.00,
        "step": 0.01,
        "range_text": "Recommended: 0.70-0.85",
        "impact": "Higher values enforce stricter adherence before alignment is considered stable.",
    },
    "min_recovery": {
        "label": "Minimum recovery index",
        "min": 0.30,
        "max": 0.90,
        "step": 0.01,
        "range_text": "Recommended: 0.48-0.62",
        "impact": "Higher values reduce tolerance for accumulated fatigue and incomplete recovery.",
    },
    "max_volatility": {
        "label": "Maximum volatility",
        "min": 0.02,
        "max": 0.20,
        "step": 0.01,
        "range_text": "Recommended: 0.06-0.12",
        "impact": "Lower values tighten acceptance of short-term instability in behavioral signals.",
    },
    "min_overload": {
        "label": "Minimum overload",
        "min": 0.30,
        "max": 0.90,
        "step": 0.01,
        "range_text": "Recommended: 0.45-0.70",
        "impact": "Higher values require stronger progressive signal quality for positive evaluation.",
    },
}


def inject_goal_page_css() -> None:
    st.markdown(
        """
        <style>
        .cfg-card-title { color: #0f172a; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.25rem; }
        .cfg-card-body { color: #475569; font-size: 0.88rem; margin-bottom: 0.3rem; }
        .cfg-focus { color: #475569; font-size: 0.84rem; font-weight: 600; }
        .cfg-badge { display: inline-block; padding: 0.15rem 0.62rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
        .cfg-badge-active { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
        .cfg-badge-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .cfg-badge-warning { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
        .cfg-meta { color: #475569; font-size: 0.86rem; line-height: 1.5; }
        .cfg-meta strong { color: #0f172a; font-weight: 600; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
        div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background: #0f172a; border: 1px solid #1e293b; }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child { background: #cbd5e1; }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:nth-child(2) { background: #475569; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _apply_defaults(goal_type: GoalType) -> None:
    defaults = STRATEGY_CONFIG[goal_type]["defaults"]
    st.session_state["thr_min_compliance"] = float(defaults["min_compliance"])
    st.session_state["thr_min_recovery"] = float(defaults["min_recovery"])
    st.session_state["thr_max_volatility"] = float(defaults["max_volatility"])
    st.session_state["thr_min_overload"] = float(defaults["min_overload"])


def _normalize_goal(raw_goal: str | None) -> GoalType:
    if not raw_goal:
        return GoalType.STRENGTH_GAIN
    for goal in GoalType:
        if goal.value == raw_goal:
            return goal
    return GoalType.STRENGTH_GAIN


def initialize_state(*, active_row: Any) -> None:
    if "active_goal" not in st.session_state:
        initial_goal = _normalize_goal(active_row["goal_type"] if active_row else GoalType.STRENGTH_GAIN.value)
        st.session_state["active_goal"] = initial_goal.value
        _apply_defaults(initial_goal)
        if active_row and active_row["target_json"]:
            saved = json.loads(active_row["target_json"])
            st.session_state["thr_min_compliance"] = float(saved.get("min_compliance", st.session_state["thr_min_compliance"]))
            st.session_state["thr_min_recovery"] = float(saved.get("min_recovery", st.session_state["thr_min_recovery"]))
            st.session_state["thr_max_volatility"] = float(saved.get("max_volatility", st.session_state["thr_max_volatility"]))
            st.session_state["thr_min_overload"] = float(saved.get("min_overload", st.session_state["thr_min_overload"]))


def render_strategy_cards() -> GoalType:
    st.markdown("### Strategy Selection")
    cols = st.columns(4)
    selected = _normalize_goal(st.session_state.get("active_goal"))

    for col, goal_type in zip(cols, list(GoalType), strict=True):
        cfg = STRATEGY_CONFIG[goal_type]
        is_active = selected == goal_type
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="cfg-card-title">{cfg["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cfg-card-body">{cfg["description"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cfg-focus">{cfg["focus"]}</div>', unsafe_allow_html=True)
                if is_active:
                    st.markdown('<span class="cfg-badge cfg-badge-active">Active</span>', unsafe_allow_html=True)
                clicked = st.button(
                    "Select",
                    key=f"select_strategy_{goal_type.value}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                )
                if clicked:
                    st.session_state["active_goal"] = goal_type.value
                    _apply_defaults(goal_type)
                    st.rerun()

    return _normalize_goal(st.session_state["active_goal"])


def render_strategy_summary(goal_type: GoalType) -> None:
    cfg = STRATEGY_CONFIG[goal_type]
    with st.container(border=True):
        st.markdown("### Strategy Summary")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.write(cfg["philosophy"])
        with c2:
            st.markdown(f"**Primary signal priority:** {cfg['signal_priority']}")
            st.markdown(f"**Recovery tolerance:** {cfg['recovery_tolerance']}")
            st.markdown(f"**Volatility profile:** {cfg['volatility_profile']}")


def render_threshold_config(goal_type: GoalType) -> dict[str, float]:
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown("### Threshold Configuration")
        with c2:
            if st.button("Reset to Defaults", use_container_width=True, key="reset_thresholds"):
                _apply_defaults(goal_type)
                st.rerun()

        for key in ["min_compliance", "min_recovery", "max_volatility", "min_overload"]:
            meta = THRESHOLD_META[key]
            slider_key = f"thr_{key}"
            value = st.slider(
                label=meta["label"],
                min_value=float(meta["min"]),
                max_value=float(meta["max"]),
                step=float(meta["step"]),
                key=slider_key,
            )
            st.caption(f"Current: {value:.2f} | {meta['range_text']}")
            st.caption(meta["impact"])

    return {
        "min_compliance": float(st.session_state["thr_min_compliance"]),
        "min_recovery": float(st.session_state["thr_min_recovery"]),
        "max_volatility": float(st.session_state["thr_max_volatility"]),
        "min_overload": float(st.session_state["thr_min_overload"]),
    }


def compute_strictness_score(*, goal_type: GoalType, thresholds: dict[str, float]) -> tuple[str, float]:
    defaults = STRATEGY_CONFIG[goal_type]["defaults"]
    compliance_dev = (thresholds["min_compliance"] - defaults["min_compliance"]) / max(0.01, 1.0 - defaults["min_compliance"])
    recovery_dev = (thresholds["min_recovery"] - defaults["min_recovery"]) / max(0.01, 0.90 - defaults["min_recovery"])
    overload_dev = (thresholds["min_overload"] - defaults["min_overload"]) / max(0.01, 0.90 - defaults["min_overload"])
    volatility_dev = (defaults["max_volatility"] - thresholds["max_volatility"]) / max(0.01, defaults["max_volatility"] - 0.02)

    avg_dev = (compliance_dev + recovery_dev + overload_dev + volatility_dev) / 4.0
    score = max(0.0, min(100.0, 50.0 + (avg_dev * 40.0)))

    if avg_dev <= -0.08:
        return "Conservative", score
    if avg_dev >= 0.08:
        return "Aggressive", score
    return "Moderate", score


def render_strictness_indicator(goal_type: GoalType, thresholds: dict[str, float]) -> None:
    level, score = compute_strictness_score(goal_type=goal_type, thresholds=thresholds)
    badge_map = {
        "Conservative": "cfg-badge cfg-badge-success",
        "Moderate": "cfg-badge cfg-badge-active",
        "Aggressive": "cfg-badge cfg-badge-warning",
    }
    with st.container(border=True):
        st.markdown("### Strategy Strictness")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.progress(int(round(score)))
            st.caption(f"Strictness score: {score:.1f}/100 (relative to {goal_type.value} defaults)")
        with c2:
            st.markdown(
                f'<span class="{badge_map[level]}">{level}</span>',
                unsafe_allow_html=True,
            )


def render_version_metadata() -> None:
    domain_version = HealthDomainDefinition().domain_version()
    with st.container(border=True):
        st.markdown("### Version Metadata")
        st.markdown(
            f"""
            <div class="cfg-meta">
                Evaluated under:<br/>
                <strong>engine_version</strong>: {ENGINE_VERSION}<br/>
                <strong>confidence_version</strong>: {CONFIDENCE_VERSION}<br/>
                <strong>context_version</strong>: {CONTEXT_VERSION}<br/>
                <strong>domain_version</strong>: {domain_version}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_activate_button(*, user_id: int, goal_type: GoalType, thresholds: dict[str, float]) -> None:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Activate Goal", type="primary", use_container_width=True, key="activate_goal_btn"):
        with get_connection(DB_PATH) as conn:
            goal_repo = GoalRepository(conn)
            goal_id = goal_repo.set_active_goal(user_id=user_id, goal_type=goal_type, target=thresholds)
        st.success(f"Active goal saved (goal_id={goal_id}, type={goal_type.value})")


def render_current_goal(user_id: int) -> None:
    with get_connection(DB_PATH) as conn:
        row = GoalRepository(conn).get_active_goal(user_id)

    if row is None:
        st.info("No active goal found yet.")
        return

    target_json = json.loads(row["target_json"]) if row["target_json"] else {}
    with st.container(border=True):
        st.markdown("### Current Active Goal")
        st.write(f"{row['goal_type']} (id={row['id']})")
        st.caption(
            "min_compliance={:.2f} | min_recovery={:.2f} | max_volatility={:.2f} | min_overload={:.2f}".format(
                float(target_json.get("min_compliance", 0.0)),
                float(target_json.get("min_recovery", 0.0)),
                float(target_json.get("max_volatility", 0.0)),
                float(target_json.get("min_overload", 0.0)),
            )
        )


def main() -> None:
    user_id = require_authenticated_user()
    render_sidebar_navigation(current_page="goal_setup", db_path=str(DB_PATH), user_id=user_id)
    inject_goal_page_css()

    with get_connection(DB_PATH) as conn:
        active_row = GoalRepository(conn).get_active_goal(user_id)

    initialize_state(active_row=active_row)

    render_page_header(
        title="Goal Configuration",
        subtitle="Configure deterministic optimization strategy and threshold behavior.",
    )

    selected_goal = render_strategy_cards()
    render_strategy_summary(selected_goal)
    thresholds = render_threshold_config(selected_goal)
    render_strictness_indicator(selected_goal, thresholds)
    render_version_metadata()
    render_activate_button(user_id=user_id, goal_type=selected_goal, thresholds=thresholds)
    st.divider()
    render_current_goal(user_id)


main()

