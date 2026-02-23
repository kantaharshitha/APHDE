from __future__ import annotations

from core.models.enums import GoalType
from core.strategies.base import GoalStrategy
from core.strategies.factory import StrategyFactory


def get_health_strategy(goal_type: str) -> GoalStrategy:
    normalized = goal_type.strip().lower()
    return StrategyFactory.create(GoalType(normalized))
