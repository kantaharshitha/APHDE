from __future__ import annotations

from typing import Any

import streamlit as st


AUTH_USER_ID_KEY = "auth_user_id"
AUTH_EMAIL_KEY = "auth_email"
AUTH_DISPLAY_NAME_KEY = "auth_display_name"
AUTH_IS_AUTHENTICATED_KEY = "is_authenticated"


def set_authenticated_session(*, user_id: int, email: str, display_name: str | None) -> None:
    st.session_state[AUTH_USER_ID_KEY] = int(user_id)
    st.session_state[AUTH_EMAIL_KEY] = email
    st.session_state[AUTH_DISPLAY_NAME_KEY] = display_name
    st.session_state[AUTH_IS_AUTHENTICATED_KEY] = True


def clear_auth_session() -> None:
    for key in (
        AUTH_USER_ID_KEY,
        AUTH_EMAIL_KEY,
        AUTH_DISPLAY_NAME_KEY,
        AUTH_IS_AUTHENTICATED_KEY,
    ):
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated() -> bool:
    return bool(st.session_state.get(AUTH_IS_AUTHENTICATED_KEY, False))


def get_authenticated_user_id() -> int | None:
    value: Any = st.session_state.get(AUTH_USER_ID_KEY)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_authenticated_email() -> str | None:
    value: Any = st.session_state.get(AUTH_EMAIL_KEY)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def get_authenticated_display_name() -> str | None:
    value: Any = st.session_state.get(AUTH_DISPLAY_NAME_KEY)
    if value is None:
        return None
    text = str(value).strip()
    return text or None
