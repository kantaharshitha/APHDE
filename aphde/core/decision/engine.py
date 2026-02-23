from dataclasses import dataclass
from typing import Any

from core.context.registry import apply_context
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
    context_applied: bool = False
    context_notes: list[str] | None = None
    context_version: str = "ctx_v1"
    context_json: dict[str, Any] | None = None
    engine_version: str = "v1"


def run_decision_engine(
    *,
    strategy: GoalStrategy,
    signals: SignalBundle,
    target: dict[str, Any],
    input_summary: dict[str, Any],
    context_input: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
    previous_alignment_confidence: float | None = None,
    engine_version: str = "v1",
) -> DecisionResult:
    evaluation = strategy.evaluate(signals, target)

    base_thresholds = {
        "max_volatility": float(target.get("max_volatility", 0.08)),
        "min_recovery": float(target.get("min_recovery", 0.55)),
    }
    context_result = apply_context(
        goal_type=strategy.goal_name,
        base_thresholds=base_thresholds,
        score_inputs={"priority_score": float(evaluation.get("priority_score", 0.5))},
        context_input=context_input,
    )

    deviations = dict(evaluation.get("deviations", {}))
    if "volatility_miss" in deviations and signals.volatility_index is not None:
        v_cap = context_result.modulated_thresholds.get("max_volatility", base_thresholds["max_volatility"])
        deviations["volatility_miss"] = float(signals.volatility_index) > float(v_cap)
    if "recovery_miss" in deviations and signals.recovery_index is not None:
        r_floor = context_result.modulated_thresholds.get("min_recovery", base_thresholds["min_recovery"])
        deviations["recovery_miss"] = float(signals.recovery_index) < float(r_floor)
    evaluation["deviations"] = deviations

    additional_risks = detect_additional_risks(signals)
    triggered_rules = sorted(set(evaluation.get("risks", []) + additional_risks))

    urgency = float(evaluation.get("priority_score", 0.5))
    urgency *= float(context_result.penalty_scalars.get("priority_score_scale", 1.0))
    urgency = max(0.0, min(1.0, urgency))
    evaluation["priority_score"] = urgency

    base_recommendations = strategy.recommend(evaluation)
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

    context_json = {
        "modulated_thresholds": context_result.modulated_thresholds,
        "penalty_scalars": context_result.penalty_scalars,
        "tolerance_adjustments": context_result.tolerance_adjustments,
        "metadata": context_result.context_metadata,
    }

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
        context_applied=context_result.context_applied,
        context_notes=context_result.context_notes,
        context_version=context_result.context_version,
        context_json=context_json,
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
        context_applied=context_result.context_applied,
        context_notes=context_result.context_notes,
        context_version=context_result.context_version,
        context_json=context_json,
        engine_version=engine_version,
    )
