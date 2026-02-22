from __future__ import annotations


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_score_breakdown(*, priority_score: float, risk_count: int, missing_signal_count: int) -> dict[str, float]:
    """
    Build deterministic penalty components in 0-100 scale.
    """
    normalized_priority = _clamp01(priority_score)
    risk_penalty = min(25.0, risk_count * 6.0)
    uncertainty_penalty = min(10.0, missing_signal_count * 2.0)
    adherence_penalty = 35.0 * normalized_priority
    recovery_risk_penalty = 20.0 * normalized_priority
    stability_penalty = 10.0 * normalized_priority

    return {
        "goal_adherence_penalty": round(adherence_penalty, 3),
        "risk_penalty": round(risk_penalty, 3),
        "uncertainty_penalty": round(uncertainty_penalty, 3),
        "recovery_risk_penalty": round(recovery_risk_penalty, 3),
        "stability_penalty": round(stability_penalty, 3),
    }


def penalties_from_breakdown(breakdown: dict[str, float]) -> list[float]:
    return list(breakdown.values())
