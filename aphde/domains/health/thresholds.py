from __future__ import annotations

DEFAULT_SIGNAL_WINDOW_DAYS = 7

DEFAULT_TARGETS: dict[str, float] = {
    "min_compliance": 0.8,
    "min_recovery": 0.55,
    "max_volatility": 0.08,
    "min_overload": 0.65,
}
