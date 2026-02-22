from core.models.enums import GoalType
from core.strategies.base import GoalStrategy


class StrategyFactory:
    @staticmethod
    def create(goal_type: GoalType) -> GoalStrategy:
        raise NotImplementedError(f"Strategy implementation pending for: {goal_type}")
