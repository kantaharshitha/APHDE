from __future__ import annotations

import streamlit as st


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
