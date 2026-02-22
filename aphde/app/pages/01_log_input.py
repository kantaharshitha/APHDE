from __future__ import annotations

from datetime import date

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.calorie_repo import CalorieLogRepository
from core.data.repositories.weight_repo import WeightLogRepository
from core.data.repositories.workout_repo import WorkoutLogRepository

st.title("Log Input")
user_id = bootstrap_db_and_user()

st.caption("Capture daily weight, nutrition, and workout logs.")
log_date = st.date_input("Log date", value=date.today())

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
    with st.form("workout_form"):
        session_type = st.selectbox(
            "Session type",
            ["push", "pull", "lower", "core", "upper", "full_body", "recovery"],
            index=0,
        )
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
                    session_type=session_type,
                    duration_min=int(duration_min),
                    volume_load=float(volume_load),
                    avg_rpe=float(avg_rpe),
                    planned_flag=planned_flag,
                    completed_flag=completed_flag,
                )
            st.success("Workout log saved")

with get_connection(DB_PATH) as conn:
    weight_count = len(WeightLogRepository(conn).list_recent(user_id, days=28))
    calorie_count = len(CalorieLogRepository(conn).list_recent(user_id, days=28))
    workout_count = len(WorkoutLogRepository(conn).list_recent(user_id, days=28))

st.divider()
st.write(f"Last 28 days: weights={weight_count}, calories={calorie_count}, workouts={workout_count}")
