from __future__ import annotations

from typing import Any

from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory, RiskCode
from core.strategies.base import GoalStrategy


class WeightLossStrategy(GoalStrategy):
    goal_name = "weight_loss"

    def evaluate(self, signals, target: dict[str, Any]) -> dict[str, Any]:
        trend = self._safe(signals.trend_slope, 0.0)
        compliance = self._safe(signals.compliance_ratio, 0.5)
        recovery = self._safe(signals.recovery_index, 0.5)
        volatility = self._safe(signals.volatility_index, 0.08)

        target_max_slope = float(target.get("max_weight_slope", -0.05))
        max_volatility = float(target.get("max_volatility", 0.06))
        min_compliance = float(target.get("min_compliance", 0.8))
        min_recovery = float(target.get("min_recovery", 0.55))

        deviations = {
            "trend_miss": trend > target_max_slope,
            "compliance_miss": compliance < min_compliance,
            "recovery_miss": recovery < min_recovery,
            "volatility_miss": volatility > max_volatility,
        }
        risks: list[str] = []
        if deviations["trend_miss"]:
            risks.append(RiskCode.STALL_RISK.value)
        if deviations["compliance_miss"]:
            risks.append(RiskCode.COMPLIANCE_DROP.value)
        if deviations["recovery_miss"]:
            risks.append(RiskCode.RECOVERY_DROP.value)
        if deviations["volatility_miss"]:
            risks.append(RiskCode.VOLATILITY_SPIKE.value)

        priority_score = (
            0.35 * (1.0 - self._clamp01(compliance))
            + 0.30 * self._clamp01(max(0.0, trend - target_max_slope))
            + 0.20 * (1.0 - self._clamp01(recovery))
            + 0.15 * self._clamp01(volatility / max(1e-6, max_volatility))
        )
        return {
            "goal": self.goal_name,
            "deviations": deviations,
            "risks": risks,
            "signals": {"trend_slope": trend, "compliance_ratio": compliance, "recovery_index": recovery},
            "priority_score": self._clamp01(priority_score),
        }

    def recommend(self, evaluation: dict[str, Any]) -> list[Recommendation]:
        deviations = evaluation["deviations"]
        risks = evaluation["risks"]
        recs: list[Recommendation] = []
        if deviations["compliance_miss"]:
            recs.append(
                Recommendation(
                    rec_id="wl_compliance_01",
                    priority=1,
                    category=RecommendationCategory.HABIT,
                    action="Pre-log calories for the next 3 days and set a fixed intake range.",
                    expected_effect="Improves adherence and restores deficit consistency.",
                    reason_codes=risks,
                    confidence=0.84,
                )
            )
        if deviations["trend_miss"]:
            recs.append(
                Recommendation(
                    rec_id="wl_nutrition_01",
                    priority=2,
                    category=RecommendationCategory.NUTRITION,
                    action="Reduce daily calories by 150-200 kcal for 7 days.",
                    expected_effect="Increases likelihood of negative weight trend.",
                    reason_codes=risks,
                    confidence=0.78,
                )
            )
        if deviations["recovery_miss"]:
            recs.append(
                Recommendation(
                    rec_id="wl_recovery_01",
                    priority=3,
                    category=RecommendationCategory.RECOVERY,
                    action="Reduce training volume by 10% for one week.",
                    expected_effect="Lowers fatigue and improves training adherence.",
                    reason_codes=risks,
                    confidence=0.73,
                )
            )
        return recs
