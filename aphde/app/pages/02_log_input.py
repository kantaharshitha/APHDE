from __future__ import annotations

from datetime import date
import json

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.context_repo import ContextInputRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository

st.title("Log Input")
user_id = bootstrap_db_and_user()

st.caption("Capture daily weight, nutrition, workouts, and optional cycle context.")
log_date = st.date_input("Log date", value=date.today())
st.markdown(
    """
    <style>
    .aphde-card {
        border: 1px solid #d9e3f0;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.4rem;
        background: #f8fbff;
        min-height: 96px;
    }
    .aphde-card-selected {
        border: 2px solid #0f6cbd;
        background: #eef6ff;
    }
    .aphde-card-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }
    .aphde-card-body {
        color: #36506b;
        font-size: 0.83rem;
        line-height: 1.35;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Weight")
    with st.form("weight_form"):
        weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=75.0, step=0.1)
        weight_submit = st.form_submit_button("Save Weight")
        if weight_submit:
            with get_connection(DB_PATH) as conn:
                repo = WeightLogRepository(conn)
                repo.add(user_id=user_id, log_date=log_date, weight_kg=float(weight_kg))
            st.success("Weight log saved")

    st.subheader("Calories")
    with st.form("calorie_form"):
        calories_kcal = st.number_input("Calories (kcal)", min_value=500, max_value=6000, value=2200, step=50)
        protein_g = st.number_input("Protein (g)", min_value=0, max_value=400, value=130, step=5)
        calorie_submit = st.form_submit_button("Save Calories")
        if calorie_submit:
            with get_connection(DB_PATH) as conn:
                repo = CalorieLogRepository(conn)
                repo.add(
                    user_id=user_id,
                    log_date=log_date,
                    calories_kcal=int(calories_kcal),
                    protein_g=int(protein_g),
                )
            st.success("Calorie log saved")

with col2:
    st.subheader("Workout")
    st.caption("Choose a workout type tile before saving the session.")

    workout_tiles = [
        ("Upper", "upper", "Upper-body strength or hypertrophy."),
        ("Lower", "lower", "Lower-body strength or hypertrophy."),
        ("Push", "push", "Chest, shoulders, triceps focus."),
        ("Pull", "pull", "Back, rear delts, biceps focus."),
        ("Core", "core", "Core and trunk-focused training."),
        ("Full Body", "full_body", "Whole-body session."),
        ("Recovery", "recovery", "Light activity or mobility day."),
    ]
    if "selected_session_type" not in st.session_state:
        st.session_state["selected_session_type"] = "upper"

    grid = st.columns(3)
    for index, (label, value, help_text) in enumerate(workout_tiles):
        is_selected = st.session_state["selected_session_type"] == value
        with grid[index % 3]:
            class_name = "aphde-card aphde-card-selected" if is_selected else "aphde-card"
            st.markdown(
                f"""
                <div class="{class_name}">
                    <div class="aphde-card-title">{label}</div>
                    <div class="aphde-card-body">{help_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Use {label}",
                key=f"tile_{value}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
                help=help_text,
            ):
                st.session_state["selected_session_type"] = value

    selected_session_type = st.session_state["selected_session_type"]
    st.caption(f"Selected session: `{selected_session_type}`")

    with st.form("workout_form"):
        duration_min = st.number_input("Duration (min)", min_value=10, max_value=240, value=60, step=5)
        volume_load = st.number_input("Volume load", min_value=0.0, max_value=100000.0, value=5000.0, step=100.0)
        avg_rpe = st.number_input("Avg RPE", min_value=1.0, max_value=10.0, value=7.5, step=0.1)
        planned_flag = st.checkbox("Planned session", value=True)
        completed_flag = st.checkbox("Completed", value=True)

        workout_submit = st.form_submit_button("Save Workout")
        if workout_submit:
            with get_connection(DB_PATH) as conn:
                repo = WorkoutLogRepository(conn)
                repo.add(
                    user_id=user_id,
                    log_date=log_date,
                    session_type=selected_session_type,
                    duration_min=int(duration_min),
                    volume_load=float(volume_load),
                    avg_rpe=float(avg_rpe),
                    planned_flag=planned_flag,
                    completed_flag=completed_flag,
                )
            st.success("Workout log saved")

st.divider()
st.subheader("Cycle Context (Optional)")
with st.form("cycle_context_form"):
    cc1, cc2 = st.columns(2)
    with cc1:
        cycle_phase = st.selectbox(
            "Cycle phase",
            ["menstrual", "follicular", "ovulatory", "luteal"],
            index=0,
        )
    with cc2:
        cycle_day = st.number_input("Cycle day (optional)", min_value=1, max_value=35, value=1, step=1)
    symptom_load = st.slider("Perceived symptom load (0-10)", min_value=0, max_value=10, value=3, step=1)
    add_cycle_context = st.form_submit_button("Save Cycle Context")
    if add_cycle_context:
        payload = {
            "phase": cycle_phase,
            "cycle_day": int(cycle_day),
            "symptom_load": int(symptom_load),
            "source": "streamlit_v3",
        }
        with get_connection(DB_PATH) as conn:
            ContextInputRepository(conn).add(
                user_id=user_id,
                log_date=log_date,
                context_type="cycle",
                payload=payload,
            )
        st.success(f"Cycle context saved for {log_date.isoformat()}: {cycle_phase}")

with get_connection(DB_PATH) as conn:
    weight_count = len(WeightLogRepository(conn).list_recent(user_id, days=28))
    calorie_count = len(CalorieLogRepository(conn).list_recent(user_id, days=28))
    workout_count = len(WorkoutLogRepository(conn).list_recent(user_id, days=28))
    latest_cycle = ContextInputRepository(conn).latest_for_user(user_id=user_id, context_type="cycle")

st.write(f"Last 28 days: weights={weight_count}, calories={calorie_count}, workouts={workout_count}")
if latest_cycle is not None:
    payload_obj = {}
    try:
        payload_obj = json.loads(latest_cycle["context_payload_json"])
    except (TypeError, json.JSONDecodeError):
        payload_obj = {"raw": latest_cycle["context_payload_json"]}
    st.caption(
        f"Latest cycle context date: {latest_cycle['log_date']}"
    )
    st.json(payload_obj)
