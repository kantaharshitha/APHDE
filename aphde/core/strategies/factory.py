from core.models.enums import GoalType
from core.strategies.base import GoalStrategy
from core.strategies.general_health import GeneralHealthStrategy
from core.strategies.recomposition import RecompositionStrategy
from core.strategies.strength_gain import StrengthGainStrategy
from core.strategies.weight_loss import WeightLossStrategy


class StrategyFactory:
    @staticmethod
    def create(goal_type: GoalType) -> GoalStrategy:
        if goal_type == GoalType.WEIGHT_LOSS:
            return WeightLossStrategy()
        if goal_type == GoalType.RECOMPOSITION:
            return RecompositionStrategy()
        if goal_type == GoalType.STRENGTH_GAIN:
            return StrengthGainStrategy()
        if goal_type == GoalType.GENERAL_HEALTH:
            return GeneralHealthStrategy()
        raise ValueError(f"Unsupported goal type: {goal_type}")
