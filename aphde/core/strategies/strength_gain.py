from __future__ import annotations

from typing import Any

from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory, RiskCode
from core.strategies.base import GoalStrategy


class StrengthGainStrategy(GoalStrategy):
    goal_name = "strength_gain"

    def evaluate(self, signals, target: dict[str, Any]) -> dict[str, Any]:
        overload = self._safe(signals.progressive_overload_score, 0.5)
        recovery = self._safe(signals.recovery_index, 0.5)
        compliance = self._safe(signals.compliance_ratio, 0.5)
        trend = self._safe(signals.trend_slope, 0.0)

        min_overload = float(target.get("min_overload", 0.72))
        min_recovery = float(target.get("min_recovery", 0.6))
        min_compliance = float(target.get("min_compliance", 0.8))
        min_trend = float(target.get("min_strength_trend", 0.0))

        deviations = {
            "overload_miss": overload < min_overload,
            "recovery_miss": recovery < min_recovery,
            "compliance_miss": compliance < min_compliance,
            "progress_miss": trend < min_trend,
        }
        risks: list[str] = []
        if deviations["overload_miss"] or deviations["progress_miss"]:
            risks.append(RiskCode.STALL_RISK.value)
        if deviations["recovery_miss"]:
            risks.append(RiskCode.RECOVERY_DROP.value)
        if deviations["compliance_miss"]:
            risks.append(RiskCode.COMPLIANCE_DROP.value)

        priority_score = (
            0.4 * (1.0 - self._clamp01(overload))
            + 0.25 * (1.0 - self._clamp01(recovery))
            + 0.2 * (1.0 - self._clamp01(compliance))
            + 0.15 * self._clamp01(max(0.0, min_trend - trend))
        )
        return {
            "goal": self.goal_name,
            "deviations": deviations,
            "risks": risks,
            "signals": {"overload_score": overload, "recovery_index": recovery, "trend_slope": trend},
            "priority_score": self._clamp01(priority_score),
        }

    def recommend(self, evaluation: dict[str, Any]) -> list[Recommendation]:
        deviations = evaluation["deviations"]
        risks = evaluation["risks"]
        recs: list[Recommendation] = []
        if deviations["overload_miss"]:
            recs.append(
                Recommendation(
                    rec_id="sg_training_01",
                    priority=1,
                    category=RecommendationCategory.TRAINING,
                    action="Increase top-set load by 2.5% and keep accessory volume stable.",
                    expected_effect="Restores progressive overload signal.",
                    reason_codes=risks,
                    confidence=0.85,
                )
            )
        if deviations["recovery_miss"]:
            recs.append(
                Recommendation(
                    rec_id="sg_recovery_01",
                    priority=2,
                    category=RecommendationCategory.RECOVERY,
                    action="Insert one low-intensity day after each heavy session.",
                    expected_effect="Improves readiness for high-intensity lifts.",
                    reason_codes=risks,
                    confidence=0.8,
                )
            )
        if deviations["compliance_miss"]:
            recs.append(
                Recommendation(
                    rec_id="sg_habit_01",
                    priority=3,
                    category=RecommendationCategory.HABIT,
                    action="Lock a fixed weekly lifting schedule with 3 non-negotiable sessions.",
                    expected_effect="Improves consistency and training frequency.",
                    reason_codes=risks,
                    confidence=0.79,
                )
            )
        return recs
