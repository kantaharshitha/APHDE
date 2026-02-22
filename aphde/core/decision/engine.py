from dataclasses import dataclass
from typing import Any

from core.decision.ranker import rank_recommendations
from core.decision.rules import detect_additional_risks
from core.explain.serializers import recommendations_to_dicts
from core.explain.trace_builder import build_trace
from core.scoring.alignment import compute_alignment_score
from core.scoring.breakdown import build_score_breakdown, penalties_from_breakdown
from core.signals.aggregator import SignalBundle
from core.strategies.base import GoalStrategy


@dataclass(slots=True)
class DecisionResult:
    alignment_score: float
    risk_score: float
    recommendations: list[dict[str, Any]]
    trace: dict[str, Any]
    engine_version: str = "v1"


def run_decision_engine(
    *,
    strategy: GoalStrategy,
    signals: SignalBundle,
    target: dict[str, Any],
    input_summary: dict[str, Any],
    engine_version: str = "v1",
) -> DecisionResult:
    evaluation = strategy.evaluate(signals, target)
    base_recommendations = strategy.recommend(evaluation)

    additional_risks = detect_additional_risks(signals)
    triggered_rules = sorted(set(evaluation.get("risks", []) + additional_risks))

    urgency = float(evaluation.get("priority_score", 0.5))
    ranked = rank_recommendations(base_recommendations, urgency=urgency)

    sufficiency = signals.sufficiency or {}
    missing_signal_count = sum(1 for is_ok in sufficiency.values() if not is_ok)
    score_breakdown = build_score_breakdown(
        priority_score=urgency,
        risk_count=len(triggered_rules),
        missing_signal_count=missing_signal_count,
    )
    alignment = compute_alignment_score(penalties_from_breakdown(score_breakdown))
    risk_score = max(0.0, min(100.0, 100.0 - alignment))

    recommendation_dicts = recommendations_to_dicts(ranked)
    ranking_trace = [
        {
            "id": rec["id"],
            "priority": rec["priority"],
            "confidence": rec["confidence"],
            "reason_codes": rec["reason_codes"],
        }
        for rec in recommendation_dicts
    ]

    confidence_notes = []
    if missing_signal_count > 0:
        confidence_notes.append(f"{missing_signal_count} signal(s) missing; uncertainty penalty applied.")
    if len(triggered_rules) == 0:
        confidence_notes.append("No critical risk rules triggered in this run.")

    trace = build_trace(
        input_summary=input_summary,
        computed_signals={
            "trend_slope": signals.trend_slope,
            "volatility_index": signals.volatility_index,
            "compliance_ratio": signals.compliance_ratio,
            "muscle_balance_index": signals.muscle_balance_index,
            "recovery_index": signals.recovery_index,
            "progressive_overload_score": signals.progressive_overload_score,
            "sufficiency": sufficiency,
        },
        strategy_name=strategy.goal_name,
        triggered_rules=triggered_rules,
        score_breakdown=score_breakdown,
        recommendation_ranking_trace=ranking_trace,
        confidence_notes=confidence_notes,
        engine_version=engine_version,
    )

    return DecisionResult(
        alignment_score=round(alignment, 2),
        risk_score=round(risk_score, 2),
        recommendations=recommendation_dicts,
        trace=trace,
        engine_version=engine_version,
    )
