from __future__ import annotations

import json

import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user
from core.data.db import get_connection
from core.data.repositories.goal_repo import GoalRepository
from core.models.enums import GoalType

st.title("Goal Setup")
user_id = bootstrap_db_and_user()

goal_type = st.selectbox(
    "Optimization goal",
    [
        GoalType.WEIGHT_LOSS,
        GoalType.RECOMPOSITION,
        GoalType.STRENGTH_GAIN,
        GoalType.GENERAL_HEALTH,
    ],
    format_func=lambda g: g.value,
)

st.caption("Set strategy thresholds. Defaults are reasonable for MVP.")

with st.form("goal_form"):
    min_compliance = st.slider("Minimum compliance", min_value=0.5, max_value=1.0, value=0.8, step=0.01)
    min_recovery = st.slider("Minimum recovery index", min_value=0.3, max_value=0.9, value=0.55, step=0.01)
    max_volatility = st.slider("Maximum volatility", min_value=0.02, max_value=0.2, value=0.08, step=0.01)
    min_overload = st.slider("Minimum overload", min_value=0.3, max_value=0.9, value=0.65, step=0.01)

    goal_submit = st.form_submit_button("Activate Goal")
    if goal_submit:
        target = {
            "min_compliance": float(min_compliance),
            "min_recovery": float(min_recovery),
            "max_volatility": float(max_volatility),
            "min_overload": float(min_overload),
        }
        with get_connection(DB_PATH) as conn:
            goal_repo = GoalRepository(conn)
            goal_id = goal_repo.set_active_goal(user_id=user_id, goal_type=goal_type, target=target)
        st.success(f"Active goal saved (goal_id={goal_id}, type={goal_type.value})")

with get_connection(DB_PATH) as conn:
    row = GoalRepository(conn).get_active_goal(user_id)

if row is not None:
    st.divider()
    st.write(f"Current active goal: {row['goal_type']} (id={row['id']})")
    target_json = json.loads(row["target_json"]) if row["target_json"] else {}
    st.json(target_json)
else:
    st.warning("No active goal found yet.")
