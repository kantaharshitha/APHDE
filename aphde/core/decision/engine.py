from dataclasses import dataclass
from typing import Any

from core.context.registry import apply_context
from core.decision.ranker import rank_recommendations
from core.decision.rules import detect_additional_risks
from core.engine.pipeline import ContextComputation
from core.engine.runner import run_engine_pipeline
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


def _adapt_context_for_health(
    strategy: GoalStrategy,
    signals: SignalBundle,
    target: dict[str, Any],
    evaluation: dict[str, Any],
    context_input: dict[str, Any] | None,
) -> ContextComputation:
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

    urgency = float(evaluation.get("priority_score", 0.5))
    urgency *= float(context_result.penalty_scalars.get("priority_score_scale", 1.0))
    urgency = max(0.0, min(1.0, urgency))
    evaluation["priority_score"] = urgency

    context_payload = {
        "modulated_thresholds": context_result.modulated_thresholds,
        "penalty_scalars": context_result.penalty_scalars,
        "tolerance_adjustments": context_result.tolerance_adjustments,
        "metadata": context_result.context_metadata,
    }
    return ContextComputation(
        evaluation=evaluation,
        urgency=urgency,
        context_applied=context_result.context_applied,
        context_notes=context_result.context_notes,
        context_version=context_result.context_version,
        context_payload=context_payload,
    )


def _build_health_signal_payload(signals: SignalBundle, evaluation: dict[str, Any]) -> dict[str, Any]:
    sufficiency = signals.sufficiency or {}
    return {
        "trend_slope": signals.trend_slope,
        "volatility_index": signals.volatility_index,
        "compliance_ratio": signals.compliance_ratio,
        "muscle_balance_index": signals.muscle_balance_index,
        "recovery_index": signals.recovery_index,
        "progressive_overload_score": signals.progressive_overload_score,
        "sufficiency": sufficiency,
        "deviations": evaluation.get("deviations", {}),
    }


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
    available_days = max(
        int(input_summary.get("weight_log_count", 0)),
        int(input_summary.get("workout_log_count", 0)),
        int(input_summary.get("calorie_log_count", 0)),
        0,
    )
    output = run_engine_pipeline(
        strategy=strategy,
        signals=signals,
        target=target,
        input_summary=input_summary,
        context_input=context_input,
        history=history,
        previous_alignment_confidence=previous_alignment_confidence,
        engine_version=engine_version,
        available_observation_count=available_days,
        required_observation_count=7,
        context_adapter=_adapt_context_for_health,
        additional_risk_detector=detect_additional_risks,
        recommendation_ranker=lambda recommendations, urgency: rank_recommendations(
            recommendations, urgency=urgency
        ),
        recommendation_serializer=recommendations_to_dicts,
        score_breakdown_builder=build_score_breakdown,
        penalty_extractor=penalties_from_breakdown,
        alignment_scorer=compute_alignment_score,
        confidence_calculator=compute_confidence,
        computed_signal_builder=_build_health_signal_payload,
        trace_builder=build_trace,
    )

    return DecisionResult(
        alignment_score=output.alignment_score,
        risk_score=output.risk_score,
        recommendations=output.recommendations,
        trace=output.trace,
        alignment_confidence=output.alignment_confidence,
        recommendation_confidence=output.recommendation_confidence,
        confidence_breakdown=output.confidence_breakdown,
        confidence_version=output.confidence_version,
        context_applied=output.context_applied,
        context_notes=output.context_notes,
        context_version=output.context_version,
        context_json=output.context_json,
        engine_version=engine_version,
    )
