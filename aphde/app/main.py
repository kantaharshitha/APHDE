import streamlit as st

st.set_page_config(page_title="APHDE", layout="wide")
st.title("Adaptive Personal Health Decision Engine")
st.caption("Architecture-first MVP scaffold")

st.markdown(
    """
    Use the sidebar/pages to:
    1. Log weight, calorie, and workout entries.
    2. Configure optimization goals.
    3. Run deterministic evaluation and inspect explainable decisions.
    """
)
