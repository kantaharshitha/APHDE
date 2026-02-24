from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.data.db import get_connection
from core.data.repositories.goal_repo import GoalRepository


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #F7F7F8;
        }
        .block-container {
            padding-top: 1.1rem;
        }
        .aphde-page-header {
            margin-top: 0.05rem;
            margin-bottom: 1.05rem;
            padding-top: 0.15rem;
        }
        .aphde-page-title {
            color: #1F2937;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }
        .aphde-page-subtitle {
            color: #6B7280;
            font-size: 0.97rem;
            line-height: 1.4;
            margin-bottom: 0.75rem;
        }
        .aphde-page-divider {
            border: 0;
            border-top: 1px solid #E5E7EB;
            margin: 0;
        }
        .stButton button[kind="primary"] {
            background: #3B82F6;
            border-color: #3B82F6;
            color: #FFFFFF;
        }
        .stButton button[kind="primary"]:hover {
            background: #2563EB;
            border-color: #2563EB;
            color: #FFFFFF;
        }
        section[data-testid="stSidebar"] {
            background: #F1F3F5;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] {
            display: none;
        }
        .aphde-side-head {
            color: #1F2937;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }
        .aphde-side-sub {
            color: #6B7280;
            font-size: 0.76rem;
            margin-bottom: 0.6rem;
        }
        .aphde-side-divider {
            border: 0;
            border-top: 1px solid #E5E7EB;
            margin: 0.3rem 0 0.55rem 0;
        }
        .aphde-side-group {
            color: #6B7280;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            margin-top: 0.65rem;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
        }
        section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
            border-radius: 8px;
            padding: 0.36rem 0.55rem;
            margin: 0.1rem 0;
            border-left: 4px solid transparent;
            color: #1F2937;
            font-size: 0.92rem;
            text-decoration: none;
        }
        section[data-testid="stSidebar"] div[data-testid="stPageLink"] a[aria-current="page"] {
            background: #E9EEF5;
            border-left-color: #3B82F6;
            font-weight: 600;
        }
        .aphde-side-foot {
            color: #6B7280;
            font-size: 0.72rem;
            opacity: 0.85;
            margin-top: 0.95rem;
            line-height: 1.3;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    inject_global_styles()
    st.markdown(
        f"""
        <div class="aphde-page-header">
            <div class="aphde-page-title">{title}</div>
            <div class="aphde-page-subtitle">{subtitle}</div>
            <hr class="aphde-page-divider" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def _load_active_goal(*, db_path: str, user_id: int) -> str:
    try:
        with get_connection(db_path) as conn:
            row = GoalRepository(conn).get_active_goal(user_id)
            if row is None:
                return "not_set"
            return str(row["goal_type"])
    except Exception:  # noqa: BLE001
        return "unknown"


def _format_goal_name(raw_goal: str) -> str:
    if raw_goal in {"not_set", "unknown"}:
        return "Not Set"
    return raw_goal.replace("_", " ").title()


def render_sidebar_navigation(
    *,
    current_page: str,
    db_path: str | Path,
    user_id: int,
    app_name: str = "Adaptive Health Engine",
    app_version: str = "v1.2",
) -> None:
    inject_global_styles()
    active_goal = _format_goal_name(_load_active_goal(db_path=str(db_path), user_id=user_id))
    with st.sidebar:
        st.markdown(f'<div class="aphde-side-head">{app_name}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="aphde-side-sub">{app_version} · {active_goal}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="aphde-side-divider" />', unsafe_allow_html=True)

        st.markdown('<div class="aphde-side-group">Overview</div>', unsafe_allow_html=True)
        st.page_link("main.py", label="Main")

        st.markdown('<div class="aphde-side-group">Configuration</div>', unsafe_allow_html=True)
        st.page_link("pages/01_goal_setup.py", label="Goal Setup")
        st.page_link("pages/02_log_input.py", label="Log Input")

        st.markdown('<div class="aphde-side-group">Insights</div>', unsafe_allow_html=True)
        st.page_link("pages/03_decision_dashboard.py", label="Decision Dashboard")
        st.page_link("pages/05_insights_trends.py", label="Insights & Trends")
        st.page_link("pages/04_action_center.py", label="Action Center")

        st.markdown(
            '<div class="aphde-side-foot">Engine v1 · conf_v1 · ctx_v1</div>',
            unsafe_allow_html=True,
        )


