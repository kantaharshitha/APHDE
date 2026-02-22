# APHDE

Adaptive Personal Health Decision Engine (APHDE) is a modular, deterministic health decision framework.

## Quickstart

```bash
cd aphde
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m streamlit run app/main.py
```

## Test

```bash
cd aphde
pytest
```

## Current Scope

This scaffold includes:
- domain models and enums
- SQLite schema and database helper
- repository and engine module stubs
- Streamlit app entrypoint
