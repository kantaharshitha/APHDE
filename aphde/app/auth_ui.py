from __future__ import annotations

import streamlit as st

from aphde.app.ui.layout import render_page_header
from aphde.app.utils import DB_PATH, bootstrap_db
from core.auth.service import AuthError, AuthService
from core.auth.session import (
    clear_auth_session,
    get_authenticated_user_id,
    is_authenticated,
    set_authenticated_session,
)
from core.data.db import get_connection
from core.data.repositories.user_repo import UserRepository


def _render_login_form() -> None:
    st.markdown("#### Log In")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

    if not submitted:
        return

    try:
        with get_connection(DB_PATH) as conn:
            service = AuthService(UserRepository(conn))
            identity = service.login(email=email, password=password)
    except AuthError as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"Login failed: {exc}")
        return

    set_authenticated_session(
        user_id=identity.id,
        email=identity.email,
        display_name=identity.display_name,
    )
    st.rerun()


def _render_signup_form() -> None:
    st.markdown("#### Sign Up")
    with st.form("signup_form", clear_on_submit=False):
        display_name = st.text_input("Display name (optional)", key="signup_display_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

    if not submitted:
        return

    try:
        with get_connection(DB_PATH) as conn:
            service = AuthService(UserRepository(conn))
            identity = service.signup(email=email, password=password, display_name=display_name or None)
    except AuthError as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"Signup failed: {exc}")
        return

    set_authenticated_session(
        user_id=identity.id,
        email=identity.email,
        display_name=identity.display_name,
    )
    st.success("Account created.")
    st.rerun()


def render_auth_gate() -> None:
    render_page_header(
        title="Stratify",
        subtitle="Sign in to continue to your deterministic decision workspace.",
    )
    col_left, col_right = st.columns([1, 1])
    with col_left:
        with st.container(border=True):
            _render_login_form()
    with col_right:
        with st.container(border=True):
            _render_signup_form()

    with st.expander("Technical Trace (Advanced)"):
        st.caption("Authentication is session-based and scoped by user_id.")


def require_authenticated_user() -> int:
    bootstrap_db()
    if is_authenticated():
        user_id = get_authenticated_user_id()
        if user_id is not None:
            with get_connection(DB_PATH) as conn:
                row = UserRepository(conn).get_by_id(user_id)
            if row is not None and int(row["is_active"]) == 1:
                return user_id
        clear_auth_session()

    render_auth_gate()
    st.stop()

