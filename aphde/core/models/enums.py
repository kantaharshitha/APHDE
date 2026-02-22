from enum import StrEnum


class GoalType(StrEnum):
    WEIGHT_LOSS = "weight_loss"
    RECOMPOSITION = "recomposition"
    STRENGTH_GAIN = "strength_gain"
    GENERAL_HEALTH = "general_health"


class RiskCode(StrEnum):
    RECOVERY_DROP = "RECOVERY_DROP"
    STALL_RISK = "STALL_RISK"
    COMPLIANCE_DROP = "COMPLIANCE_DROP"
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE"


class RecommendationCategory(StrEnum):
    TRAINING = "training"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    HABIT = "habit"
