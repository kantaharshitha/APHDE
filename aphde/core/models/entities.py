from dataclasses import dataclass, field
from datetime import date
from typing import Any

from core.models.enums import GoalType, RecommendationCategory


@dataclass(slots=True)
class Goal:
    user_id: int
    goal_type: GoalType
    target: dict[str, Any]


@dataclass(slots=True)
class WeightLog:
    user_id: int
    log_date: date
    weight_kg: float


@dataclass(slots=True)
class CalorieLog:
    user_id: int
    log_date: date
    calories_kcal: int
    protein_g: int | None = None


@dataclass(slots=True)
class WorkoutLog:
    user_id: int
    log_date: date
    session_type: str
    duration_min: int
    volume_load: float | None = None
    avg_rpe: float | None = None
    planned_flag: bool = True
    completed_flag: bool = True


@dataclass(slots=True)
class Recommendation:
    rec_id: str
    priority: int
    category: RecommendationCategory
    action: str
    expected_effect: str
    reason_codes: list[str] = field(default_factory=list)
    confidence: float = 0.0
