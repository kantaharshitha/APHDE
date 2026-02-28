from __future__ import annotations

from typing import Any

import streamlit as st

from .auth_ui import require_authenticated_user
from .ui.layout import render_page_header, render_sidebar_navigation
from .utils import DB_PATH
from core.data.db import get_connection
from core.data.repositories.goal_repo import GoalRepository

st.set_page_config(page_title="Stratify", layout="wide")


GOAL_DESCRIPTIONS: dict[str, str] = {
    "weight_loss": "Optimize adherence and trend stability for sustained reduction.",
    "recomposition": "Balance fat reduction and strength-supporting recovery.",
    "strength_gain": "Prioritize overload progression with controlled recovery risk.",
    "general_health": "Maintain broad consistency and recovery under moderate thresholds.",
    "not_set": "No active goal configured yet.",
}


def inject_home_css() -> None:
    st.markdown(
        """
        <style>
        .home-card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .home-label {
            color: #6B7280;
            font-size: 0.82rem;
            margin-bottom: 0.3rem;
        }
        .home-value {
            color: #1F2937;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .home-sub {
            color: #6B7280;
            font-size: 0.9rem;
        }
        .home-action {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 1rem;
            min-height: 148px;
            transition: border-color 0.18s ease;
        }
        .home-action:hover {
            border-color: #3B82F6;
        }
        .home-action-title {
            color: #1F2937;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .home-action-desc {
            color: #6B7280;
            font-size: 0.88rem;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_state(*, user_id: int) -> dict[str, Any]:
    with get_connection(DB_PATH) as conn:
        goal_row = GoalRepository(conn).get_active_goal(user_id)
    goal_name = str(goal_row["goal_type"]) if goal_row else "not_set"
    return {
        "active_goal": goal_name,
        "db_path": str(DB_PATH),
        "user_id": user_id,
    }


def render_active_goal_card(state: dict[str, Any]) -> None:
    goal_name = state["active_goal"]
    description = GOAL_DESCRIPTIONS.get(goal_name, GOAL_DESCRIPTIONS["not_set"])
    st.markdown(
        f"""
        <div class="home-card">
            <div class="home-label">Active Goal</div>
            <div class="home-value">{goal_name}</div>
            <div class="home-sub">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _navigate(page_path: str) -> None:
    try:
        st.switch_page(page_path)
    except Exception:  # noqa: BLE001
        st.caption(f"Open sidebar and navigate to: {page_path}")


def render_quick_actions() -> None:
    st.markdown("### Quick Actions")
    cols = st.columns(5)
    items = [
        ("Configure Goal", "Set optimization strategy and thresholds.", "pages/01_goal_setup.py"),
        ("Log Input", "Capture structured daily logs for evaluation.", "pages/02_log_input.py"),
        ("Action Center", "See the single prioritized tomorrow action.", "pages/04_action_center.py"),
        ("Decision Dashboard", "Review alignment, recommendations, and governance.", "pages/03_decision_dashboard.py"),
        ("Insights & Trends", "Analyze weekly patterns, drift, and stagnation alerts.", "pages/05_insights_trends.py"),
    ]
    for col, (title, desc, page) in zip(cols, items, strict=True):
        with col:
            st.markdown(
                f"""
                <div class="home-action">
                    <div class="home-action-title">{title}</div>
                    <div class="home-action-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {title}", key=f"action_{title}", use_container_width=True):
                _navigate(page)


def render_technical_trace(state: dict[str, Any]) -> None:
    with st.expander("Technical Trace (Advanced)"):
        st.write(f"Database path: {state['db_path']}")
        st.write(f"Local user id: {state['user_id']}")


def main() -> None:
    user_id = require_authenticated_user()
    render_sidebar_navigation(current_page="main", db_path=str(DB_PATH), user_id=user_id)
    inject_home_css()
    state = load_state(user_id=user_id)

    render_page_header(
        title="Stratify",
        subtitle="Deterministic, explainable optimization framework.",
    )
    render_active_goal_card(state)
    render_quick_actions()
    render_technical_trace(state)


main()


