from dataclasses import dataclass
from typing import Any

from core.decision.ranker import rank_recommendations
from core.decision.rules import detect_additional_risks
from core.explain.serializers import recommendations_to_dicts
from core.explain.trace_builder import build_trace
from core.scoring.alignment import compute_alignment_score
from core.scoring.breakdown import build_score_breakdown, penalties_from_breakdown
from core.scoring.confidence import compute_confidence
from core.signals.aggregator import SignalBundle
from core.strategies.base import GoalStrategy


@dataclass(slots=True)
class DecisionResult:
    alignment_score: float
    risk_score: float
    recommendations: list[dict[str, Any]]
    trace: dict[str, Any]
    alignment_confidence: float = 0.0
    recommendation_confidence: list[dict[str, Any]] | None = None
    confidence_breakdown: dict[str, Any] | None = None
    confidence_version: str = "conf_v1"
    engine_version: str = "v1"


def run_decision_engine(
    *,
    strategy: GoalStrategy,
    signals: SignalBundle,
    target: dict[str, Any],
    input_summary: dict[str, Any],
    history: list[dict[str, Any]] | None = None,
    previous_alignment_confidence: float | None = None,
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
    available_days = max(
        int(input_summary.get("weight_log_count", 0)),
        int(input_summary.get("workout_log_count", 0)),
        int(input_summary.get("calorie_log_count", 0)),
        0,
    )
    confidence = compute_confidence(
        signals=signals,
        deviations=evaluation.get("deviations", {}),
        recommendations=recommendation_dicts,
        history=history,
        threshold_distances=evaluation.get("threshold_distances"),
        available_days=available_days if available_days > 0 else 7,
        required_days=7,
        previous_alignment_confidence=previous_alignment_confidence,
    )
    rec_conf_by_id = {item["id"]: item["confidence"] for item in confidence["recommendation_confidence"]}
    ranking_trace = [
        {
            "id": rec["id"],
            "priority": rec["priority"],
            "confidence": rec["confidence"],
            "computed_confidence": rec_conf_by_id.get(rec["id"]),
            "reason_codes": rec["reason_codes"],
        }
        for rec in recommendation_dicts
    ]

    confidence_notes = []
    if missing_signal_count > 0:
        confidence_notes.append(f"{missing_signal_count} signal(s) missing; uncertainty penalty applied.")
    if len(triggered_rules) == 0:
        confidence_notes.append("No critical risk rules triggered in this run.")
    confidence_notes.extend(confidence["confidence_notes"])

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
            "deviations": evaluation.get("deviations", {}),
        },
        strategy_name=strategy.goal_name,
        triggered_rules=triggered_rules,
        score_breakdown=score_breakdown,
        recommendation_ranking_trace=ranking_trace,
        confidence_notes=confidence_notes,
        alignment_confidence=confidence["alignment_confidence"],
        recommendation_confidence=confidence["recommendation_confidence"],
        confidence_breakdown=confidence["confidence_breakdown"],
        confidence_version=confidence["confidence_version"],
        engine_version=engine_version,
    )

    return DecisionResult(
        alignment_score=round(alignment, 2),
        risk_score=round(risk_score, 2),
        recommendations=recommendation_dicts,
        trace=trace,
        alignment_confidence=confidence["alignment_confidence"],
        recommendation_confidence=confidence["recommendation_confidence"],
        confidence_breakdown=confidence["confidence_breakdown"],
        confidence_version=confidence["confidence_version"],
        engine_version=engine_version,
    )
