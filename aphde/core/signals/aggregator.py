from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.signals.compliance import compliance_from_workout_logs
from core.signals.muscle_balance import muscle_balance_index
from core.signals.overload import progressive_overload_from_workout_logs
from core.signals.recovery import recovery_from_workout_logs
from core.signals.trend import linear_regression_slope
from core.signals.volatility import coefficient_of_variation


@dataclass(slots=True)
class SignalBundle:
    trend_slope: float | None = None
    volatility_index: float | None = None
    compliance_ratio: float | None = None
    muscle_balance_index: float | None = None
    recovery_index: float | None = None
    progressive_overload_score: float | None = None
    sufficiency: dict[str, bool] | None = None


def build_signal_bundle(
    *,
    weight_values: list[float],
    workout_logs: list[dict[str, Any]],
    window_days: int = 7,
) -> SignalBundle:
    trend = linear_regression_slope(weight_values)
    volatility = coefficient_of_variation(weight_values)
    compliance = compliance_from_workout_logs(workout_logs)
    balance = muscle_balance_index(
        [str(row.get("session_type", "")) for row in workout_logs if row.get("session_type") is not None]
    )
    recovery = recovery_from_workout_logs(workout_logs, window_days=window_days)
    overload = progressive_overload_from_workout_logs(workout_logs)

    return SignalBundle(
        trend_slope=trend,
        volatility_index=volatility,
        compliance_ratio=compliance,
        muscle_balance_index=balance,
        recovery_index=recovery,
        progressive_overload_score=overload,
        sufficiency={
            "trend_slope": trend is not None,
            "volatility_index": volatility is not None,
            "compliance_ratio": compliance is not None,
            "muscle_balance_index": balance is not None,
            "recovery_index": recovery is not None,
            "progressive_overload_score": overload is not None,
        },
    )
