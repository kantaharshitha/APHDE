from __future__ import annotations

from typing import Any

from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory, RiskCode
from core.strategies.base import GoalStrategy


class RecompositionStrategy(GoalStrategy):
    goal_name = "recomposition"

    def evaluate(self, signals, target: dict[str, Any]) -> dict[str, Any]:
        trend = self._safe(signals.trend_slope, 0.0)
        overload = self._safe(signals.progressive_overload_score, 0.5)
        balance = self._safe(signals.muscle_balance_index, 0.5)
        compliance = self._safe(signals.compliance_ratio, 0.5)

        max_abs_trend = float(target.get("max_abs_weight_slope", 0.06))
        min_overload = float(target.get("min_overload", 0.65))
        min_balance = float(target.get("min_balance", 0.65))
        min_compliance = float(target.get("min_compliance", 0.8))

        deviations = {
            "weight_drift": abs(trend) > max_abs_trend,
            "overload_miss": overload < min_overload,
            "balance_miss": balance < min_balance,
            "compliance_miss": compliance < min_compliance,
        }
        risks: list[str] = []
        if deviations["overload_miss"] or deviations["weight_drift"]:
            risks.append(RiskCode.STALL_RISK.value)
        if deviations["compliance_miss"]:
            risks.append(RiskCode.COMPLIANCE_DROP.value)

        priority_score = (
            0.35 * (1.0 - self._clamp01(overload))
            + 0.25 * (1.0 - self._clamp01(balance))
            + 0.25 * (1.0 - self._clamp01(compliance))
            + 0.15 * self._clamp01(abs(trend) / max(1e-6, max_abs_trend))
        )
        return {
            "goal": self.goal_name,
            "deviations": deviations,
            "risks": risks,
            "signals": {"trend_slope": trend, "overload_score": overload, "balance_score": balance},
            "priority_score": self._clamp01(priority_score),
        }

    def recommend(self, evaluation: dict[str, Any]) -> list[Recommendation]:
        deviations = evaluation["deviations"]
        risks = evaluation["risks"]
        recs: list[Recommendation] = []
        if deviations["overload_miss"]:
            recs.append(
                Recommendation(
                    rec_id="rc_training_01",
                    priority=1,
                    category=RecommendationCategory.TRAINING,
                    action="Add one progressive overload anchor lift and track weekly top set.",
                    expected_effect="Improves strength stimulus while preserving recomposition.",
                    reason_codes=risks,
                    confidence=0.82,
                )
            )
        if deviations["weight_drift"]:
            recs.append(
                Recommendation(
                    rec_id="rc_nutrition_01",
                    priority=2,
                    category=RecommendationCategory.NUTRITION,
                    action="Adjust calories by +/-100 based on trend direction for 7 days.",
                    expected_effect="Keeps bodyweight inside recomposition band.",
                    reason_codes=risks,
                    confidence=0.77,
                )
            )
        if deviations["balance_miss"]:
            recs.append(
                Recommendation(
                    rec_id="rc_training_02",
                    priority=3,
                    category=RecommendationCategory.TRAINING,
                    action="Rebalance weekly split to even push/pull/lower volume.",
                    expected_effect="Improves muscular symmetry and training quality.",
                    reason_codes=risks,
                    confidence=0.72,
                )
            )
        return recs
