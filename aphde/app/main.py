import streamlit as st

from app.utils import DB_PATH, bootstrap_db_and_user

st.set_page_config(page_title="APHDE", layout="wide")
user_id = bootstrap_db_and_user()

st.title("Adaptive Personal Health Decision Engine")
st.caption("Deterministic, explainable health decision system")

st.info(f"Using database: {DB_PATH}")
st.success(f"Active local user id: {user_id}")

st.markdown(
    """
    Use the sidebar pages to:
    1. Configure optimization goal.
    2. Input daily behavioral logs.
    3. Run evaluation and inspect scored recommendations.
    """
)
