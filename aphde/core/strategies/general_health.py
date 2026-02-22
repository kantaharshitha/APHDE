from __future__ import annotations

from typing import Any

from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory, RiskCode
from core.strategies.base import GoalStrategy


class GeneralHealthStrategy(GoalStrategy):
    goal_name = "general_health"

    def evaluate(self, signals, target: dict[str, Any]) -> dict[str, Any]:
        compliance = self._safe(signals.compliance_ratio, 0.5)
        recovery = self._safe(signals.recovery_index, 0.5)
        volatility = self._safe(signals.volatility_index, 0.08)
        balance = self._safe(signals.muscle_balance_index, 0.5)

        min_compliance = float(target.get("min_compliance", 0.7))
        min_recovery = float(target.get("min_recovery", 0.55))
        max_volatility = float(target.get("max_volatility", 0.08))
        min_balance = float(target.get("min_balance", 0.6))

        deviations = {
            "compliance_miss": compliance < min_compliance,
            "recovery_miss": recovery < min_recovery,
            "volatility_miss": volatility > max_volatility,
            "balance_miss": balance < min_balance,
        }
        risks: list[str] = []
        if deviations["compliance_miss"]:
            risks.append(RiskCode.COMPLIANCE_DROP.value)
        if deviations["recovery_miss"]:
            risks.append(RiskCode.RECOVERY_DROP.value)
        if deviations["volatility_miss"]:
            risks.append(RiskCode.VOLATILITY_SPIKE.value)

        priority_score = (
            0.35 * (1.0 - self._clamp01(compliance))
            + 0.25 * (1.0 - self._clamp01(recovery))
            + 0.2 * self._clamp01(volatility / max(1e-6, max_volatility))
            + 0.2 * (1.0 - self._clamp01(balance))
        )
        return {
            "goal": self.goal_name,
            "deviations": deviations,
            "risks": risks,
            "signals": {"compliance_ratio": compliance, "recovery_index": recovery, "volatility_index": volatility},
            "priority_score": self._clamp01(priority_score),
        }

    def recommend(self, evaluation: dict[str, Any]) -> list[Recommendation]:
        deviations = evaluation["deviations"]
        risks = evaluation["risks"]
        recs: list[Recommendation] = []
        if deviations["compliance_miss"]:
            recs.append(
                Recommendation(
                    rec_id="gh_habit_01",
                    priority=1,
                    category=RecommendationCategory.HABIT,
                    action="Set a weekly minimum activity target with calendar reminders.",
                    expected_effect="Improves consistency and baseline health behaviors.",
                    reason_codes=risks,
                    confidence=0.81,
                )
            )
        if deviations["recovery_miss"]:
            recs.append(
                Recommendation(
                    rec_id="gh_recovery_01",
                    priority=2,
                    category=RecommendationCategory.RECOVERY,
                    action="Add one extra rest day and cap high-RPE sessions this week.",
                    expected_effect="Reduces fatigue accumulation and supports sustainability.",
                    reason_codes=risks,
                    confidence=0.76,
                )
            )
        if deviations["volatility_miss"]:
            recs.append(
                Recommendation(
                    rec_id="gh_nutrition_01",
                    priority=3,
                    category=RecommendationCategory.NUTRITION,
                    action="Standardize meal timing and calorie range on weekdays.",
                    expected_effect="Lowers behavioral volatility and improves routine.",
                    reason_codes=risks,
                    confidence=0.7,
                )
            )
        return recs
