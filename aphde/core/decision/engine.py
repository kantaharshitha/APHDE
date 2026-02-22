from dataclasses import dataclass


@dataclass(slots=True)
class DecisionResult:
    alignment_score: float
    risk_score: float
    recommendations: list[dict]
    trace: dict
    engine_version: str = "v1"
