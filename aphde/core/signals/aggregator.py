from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SignalBundle:
    trend_slope: float | None = None
    volatility_index: float | None = None
    compliance_ratio: float | None = None
    muscle_balance_index: float | None = None
    recovery_index: float | None = None
    progressive_overload_score: float | None = None
