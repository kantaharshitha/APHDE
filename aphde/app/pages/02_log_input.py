from __future__ import annotations

from datetime import date
import json
from typing import Any

import streamlit as st

from app.ui.layout import render_page_header, render_sidebar_navigation
from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.context_repo import ContextInputRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository

st.set_page_config(layout="wide")


WORKOUT_TILES: list[tuple[str, str, str]] = [
    ("Upper", "upper", "Upper-body strength/hypertrophy."),
    ("Lower", "lower", "Lower-body strength/hypertrophy."),
    ("Push", "push", "Chest, shoulders, triceps focus."),
    ("Pull", "pull", "Back and biceps focus."),
    ("Core", "core", "Core and trunk-focused session."),
    ("Full Body", "full_body", "Whole-body training day."),
    ("Recovery", "recovery", "Mobility/light recovery session."),
]


def inject_log_page_css() -> None:
    st.markdown(
        """
        <style>
        .log-meta { color: #6B7280; font-size: 0.88rem; }
        .tile-caption { color: #6B7280; font-size: 0.82rem; line-height: 1.25; }
        .tile-focus { color: #1F2937; font-weight: 600; font-size: 0.92rem; margin-bottom: 0.22rem; }
        div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
            background: #4B5563;
            border: 1px solid #374151;
        }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child { background: #D1D5DB; }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:nth-child(2) { background: #6B7280; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "log_date": date.today(),
        "weight_kg": 75.0,
        "calories_kcal": 2200,
        "protein_g": 130,
        "selected_session_type": "upper",
        "duration_min": 60,
        "volume_load": 5000.0,
        "avg_rpe": 7.5,
        "planned_flag": True,
        "completed_flag": True,
        "cycle_phase": "",
        "cycle_day": None,
        "symptom_load": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_biometrics() -> None:
    with st.container(border=True):
        st.markdown("### Daily Biometrics")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input(
                "Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                step=0.1,
                key="weight_kg",
            )
        with c2:
            st.number_input(
                "Calories (kcal)",
                min_value=500,
                max_value=6000,
                step=50,
                key="calories_kcal",
            )
        with c3:
            st.number_input(
                "Protein (g)",
                min_value=0,
                max_value=400,
                step=5,
                key="protein_g",
            )
        st.caption("Values are staged locally and persisted only when you commit the log entry.")


def render_workout_section() -> None:
    with st.container(border=True):
        st.markdown("### Training Session")
        st.caption("Select one session type tile.")

        cols = st.columns(4)
        selected = st.session_state["selected_session_type"]
        for index, (label, value, helper) in enumerate(WORKOUT_TILES):
            with cols[index % 4]:
                is_selected = selected == value
                with st.container(border=True):
                    st.markdown(f'<div class="tile-focus">{label}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="tile-caption">{helper}</div>', unsafe_allow_html=True)
                    if is_selected:
                        st.caption("Selected")
                    # Streamlit does not support clickable container events, so this button acts as tile click target.
                    if st.button(
                        f"Select {label}",
                        key=f"select_tile_{value}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                    ):
                        st.session_state["selected_session_type"] = value
                        st.rerun()

        st.caption(f"Current session type: {st.session_state['selected_session_type']}")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.number_input("Duration (min)", min_value=10, max_value=240, step=5, key="duration_min")
        with d2:
            st.number_input("Volume load", min_value=0.0, max_value=100000.0, step=100.0, key="volume_load")
        with d3:
            st.number_input("Avg RPE", min_value=1.0, max_value=10.0, step=0.1, key="avg_rpe")

        f1, f2 = st.columns(2)
        with f1:
            st.checkbox("Planned session", key="planned_flag")
        with f2:
            st.checkbox("Completed", key="completed_flag")


def render_context_section(*, latest_context_date: str | None, latest_context_payload: dict[str, Any] | None) -> None:
    with st.expander("Physiological Context (Optional)", expanded=False):
        st.markdown(
            '<div style="font-size:0.84rem; color:#6B7280; margin-bottom:0.55rem;">'
            "This information helps modulate recovery and risk scoring. Leave blank if not applicable."
            "</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.get("cycle_phase", "") == "":
            st.selectbox(
                "Cycle phase",
                ["", "menstrual", "follicular", "ovulatory", "luteal"],
                key="cycle_phase",
            )
            selected_phase = st.session_state.get("cycle_phase", "")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.selectbox(
                    "Cycle phase",
                    ["", "menstrual", "follicular", "ovulatory", "luteal"],
                    key="cycle_phase",
                )
            selected_phase = st.session_state.get("cycle_phase", "")
            with c2:
                st.number_input(
                    "Cycle day",
                    min_value=1,
                    max_value=35,
                    value=None,
                    placeholder="Optional",
                    key="cycle_day",
                )
            with c3:
                st.slider(
                    "Symptom load",
                    min_value=0,
                    max_value=10,
                    value=st.session_state.get("symptom_load", 0),
                    key="symptom_load",
                )
                st.caption("0 = no symptoms, 10 = severe symptoms")

            st.markdown(
                '<div style="font-size:0.82rem; color:#065F46; margin-top:0.25rem;">'
                "Context will be applied during next evaluation."
                "</div>",
                unsafe_allow_html=True,
            )

        if latest_context_date:
            st.caption(f"Latest context recorded: {latest_context_date}")
        else:
            st.caption("Latest context recorded: none")

        with st.expander("Technical Trace (Advanced)"):
            st.write("Latest context payload")
            st.json(latest_context_payload or {})


def render_system_snapshot(*, weight_count: int, calorie_count: int, workout_count: int) -> None:
    st.markdown(
        f"""
        <div class="log-meta">
            Last 28 days: weights={weight_count} | calories={calorie_count} | workouts={workout_count}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_commit_button(*, user_id: int) -> None:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Commit Log Entry", type="primary", use_container_width=True, key="commit_log_entry"):
        log_date = st.session_state["log_date"]
        phase = st.session_state.get("cycle_phase", "")

        with get_connection(DB_PATH) as conn:
            WeightLogRepository(conn).add(
                user_id=user_id,
                log_date=log_date,
                weight_kg=float(st.session_state["weight_kg"]),
            )
            CalorieLogRepository(conn).add(
                user_id=user_id,
                log_date=log_date,
                calories_kcal=int(st.session_state["calories_kcal"]),
                protein_g=int(st.session_state["protein_g"]),
            )
            WorkoutLogRepository(conn).add(
                user_id=user_id,
                log_date=log_date,
                session_type=str(st.session_state["selected_session_type"]),
                duration_min=int(st.session_state["duration_min"]),
                volume_load=float(st.session_state["volume_load"]),
                avg_rpe=float(st.session_state["avg_rpe"]),
                planned_flag=bool(st.session_state["planned_flag"]),
                completed_flag=bool(st.session_state["completed_flag"]),
            )
            if phase:
                payload: dict[str, Any] = {
                    "phase": phase,
                    "symptom_load": int(st.session_state.get("symptom_load", 0)),
                    "source": "streamlit_refactor_v5",
                }
                cycle_day = st.session_state.get("cycle_day")
                if cycle_day is not None:
                    payload["cycle_day"] = int(cycle_day)
                ContextInputRepository(conn).add(
                    user_id=user_id,
                    log_date=log_date,
                    context_type="cycle",
                    payload=payload,
                )

        st.success("Log entry recorded successfully.")


def load_snapshot_data(*, user_id: int) -> dict[str, Any]:
    with get_connection(DB_PATH) as conn:
        weight_count = len(WeightLogRepository(conn).list_recent(user_id, days=28))
        calorie_count = len(CalorieLogRepository(conn).list_recent(user_id, days=28))
        workout_count = len(WorkoutLogRepository(conn).list_recent(user_id, days=28))
        latest_cycle = ContextInputRepository(conn).latest_for_user(user_id=user_id, context_type="cycle")

    payload_obj: dict[str, Any] | None = None
    latest_date: str | None = None
    if latest_cycle is not None:
        latest_date = str(latest_cycle["log_date"])
        try:
            payload_obj = json.loads(latest_cycle["context_payload_json"])
        except (TypeError, json.JSONDecodeError):
            payload_obj = {"raw_payload": str(latest_cycle["context_payload_json"])}

    return {
        "weight_count": weight_count,
        "calorie_count": calorie_count,
        "workout_count": workout_count,
        "latest_context_date": latest_date,
        "latest_context_payload": payload_obj,
    }


def main() -> None:
    user_id = bootstrap_db_and_user()
    render_sidebar_navigation(current_page="log_input", db_path=str(DB_PATH), user_id=user_id)
    inject_log_page_css()
    init_state()

    render_page_header(
        title="Log Input",
        subtitle="Capture structured daily signals for deterministic evaluation.",
    )

    st.date_input("Log date", key="log_date")
    render_biometrics()
    render_workout_section()

    snapshot = load_snapshot_data(user_id=user_id)
    render_context_section(
        latest_context_date=snapshot["latest_context_date"],
        latest_context_payload=snapshot["latest_context_payload"],
    )
    render_system_snapshot(
        weight_count=int(snapshot["weight_count"]),
        calorie_count=int(snapshot["calorie_count"]),
        workout_count=int(snapshot["workout_count"]),
    )
    render_commit_button(user_id=user_id)


main()
