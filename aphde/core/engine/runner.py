from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from core.engine.contracts import SignalBundleLike, StrategyLike
from core.engine.pipeline import ContextComputation, EngineRunOutput
from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _maintenance_fallback_candidates(*, urgency: float) -> list[Recommendation]:
    base_conf = _clamp01(0.58 + (0.22 * (1.0 - urgency)))
    return [
        Recommendation(
            rec_id="maintain_progression",
            priority=99,
            category=RecommendationCategory.HABIT,
            action="Maintain current progression with consistent session execution.",
            expected_effect="Stabilizes short-window variance and improves next-run reliability.",
            reason_codes=["MAINTENANCE_FALLBACK"],
            confidence=round(base_conf, 4),
        ),
        Recommendation(
            rec_id="incremental_overload",
            priority=99,
            category=RecommendationCategory.TRAINING,
            action="Apply a small incremental overload only if recovery remains stable.",
            expected_effect="Supports controlled progression without abrupt fatigue spikes.",
            reason_codes=["MAINTENANCE_FALLBACK"],
            confidence=round(_clamp01(base_conf - 0.03), 4),
        ),
        Recommendation(
            rec_id="calorie_target_band",
            priority=99,
            category=RecommendationCategory.NUTRITION,
            action="Keep calorie intake within the configured target band.",
            expected_effect="Reduces behavioral drift and maintains signal consistency.",
            reason_codes=["MAINTENANCE_FALLBACK"],
            confidence=round(_clamp01(base_conf - 0.05), 4),
        ),
        Recommendation(
            rec_id="recovery_consistency",
            priority=99,
            category=RecommendationCategory.RECOVERY,
            action="Preserve recovery consistency across sleep and low-intensity sessions.",
            expected_effect="Supports resilience and lowers volatility in recovery signals.",
            reason_codes=["MAINTENANCE_FALLBACK"],
            confidence=round(_clamp01(base_conf - 0.02), 4),
        ),
    ]


def _ensure_minimum_recommendations(
    *,
    ranked_recommendations: list[Recommendation],
    urgency: float,
    recommendation_ranker: Callable[[list[Recommendation], float], list[Recommendation]],
) -> list[Recommendation]:
    if len(ranked_recommendations) >= 2:
        return ranked_recommendations

    fallback_candidates = _maintenance_fallback_candidates(urgency=urgency)

    if len(ranked_recommendations) == 1:
        existing_ids = {item.rec_id for item in ranked_recommendations}
        fallback = next((item for item in fallback_candidates if item.rec_id not in existing_ids), None)
        if fallback is None:
            return ranked_recommendations
        return ranked_recommendations + [replace(fallback, priority=2)]

    fallback_ranked = recommendation_ranker(fallback_candidates[:2], urgency=urgency)
    return fallback_ranked


def run_engine_pipeline(
    *,
    strategy: StrategyLike,
    signals: SignalBundleLike,
    target: dict[str, Any],
    input_summary: dict[str, Any],
    context_input: dict[str, Any] | None,
    history: list[dict[str, Any]] | None,
    previous_alignment_confidence: float | None,
    engine_version: str,
    available_observation_count: int,
    required_observation_count: int,
    context_adapter: Callable[[StrategyLike, SignalBundleLike, dict[str, Any], dict[str, Any], dict[str, Any] | None], ContextComputation],
    additional_risk_detector: Callable[[SignalBundleLike], list[str]],
    recommendation_ranker: Callable[[list[Recommendation], float], list[Recommendation]],
    recommendation_serializer: Callable[[list[Any]], list[dict[str, Any]]],
    score_breakdown_builder: Callable[[float, int, int], dict[str, float]],
    penalty_extractor: Callable[[dict[str, float]], dict[str, float]],
    alignment_scorer: Callable[[dict[str, float]], float],
    confidence_calculator: Callable[..., dict[str, Any]],
    computed_signal_builder: Callable[[SignalBundleLike, dict[str, Any]], dict[str, Any]],
    trace_builder: Callable[..., dict[str, Any]],
) -> EngineRunOutput:
    evaluation = strategy.evaluate(signals, target)
    context_state = context_adapter(strategy, signals, target, evaluation, context_input)

    additional_risks = additional_risk_detector(signals)
    triggered_rules = sorted(set(context_state.evaluation.get("risks", []) + additional_risks))

    base_recommendations = strategy.recommend(context_state.evaluation)
    ranked = recommendation_ranker(base_recommendations, context_state.urgency)
    ranked = _ensure_minimum_recommendations(
        ranked_recommendations=ranked,
        urgency=context_state.urgency,
        recommendation_ranker=recommendation_ranker,
    )
    recommendation_dicts = recommendation_serializer(ranked)

    sufficiency = signals.sufficiency or {}
    missing_signal_count = sum(1 for is_ok in sufficiency.values() if not is_ok)
    score_breakdown = score_breakdown_builder(
        priority_score=context_state.urgency,
        risk_count=len(triggered_rules),
        missing_signal_count=missing_signal_count,
    )

    alignment = alignment_scorer(penalty_extractor(score_breakdown))
    risk_score = max(0.0, min(100.0, 100.0 - alignment))

    confidence = confidence_calculator(
        signals=signals,
        deviations=context_state.evaluation.get("deviations", {}),
        recommendations=recommendation_dicts,
        history=history,
        threshold_distances=context_state.evaluation.get("threshold_distances"),
        available_days=available_observation_count if available_observation_count > 0 else required_observation_count,
        required_days=required_observation_count,
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

    confidence_notes: list[str] = []
    if missing_signal_count > 0:
        confidence_notes.append(f"{missing_signal_count} signal(s) missing; uncertainty penalty applied.")
    if len(triggered_rules) == 0:
        confidence_notes.append("No critical risk rules triggered in this run.")
    confidence_notes.extend(confidence["confidence_notes"])

    trace = trace_builder(
        input_summary=input_summary,
        computed_signals=computed_signal_builder(signals, context_state.evaluation),
        strategy_name=strategy.goal_name,
        triggered_rules=triggered_rules,
        score_breakdown=score_breakdown,
        recommendation_ranking_trace=ranking_trace,
        confidence_notes=confidence_notes,
        alignment_confidence=confidence["alignment_confidence"],
        recommendation_confidence=confidence["recommendation_confidence"],
        confidence_breakdown=confidence["confidence_breakdown"],
        confidence_version=confidence["confidence_version"],
        context_applied=context_state.context_applied,
        context_notes=context_state.context_notes,
        context_version=context_state.context_version,
        context_json=context_state.context_payload,
        engine_version=engine_version,
    )

    return EngineRunOutput(
        alignment_score=round(alignment, 2),
        risk_score=round(risk_score, 2),
        recommendations=recommendation_dicts,
        trace=trace,
        alignment_confidence=confidence["alignment_confidence"],
        recommendation_confidence=confidence["recommendation_confidence"],
        confidence_breakdown=confidence["confidence_breakdown"],
        confidence_version=confidence["confidence_version"],
        context_applied=context_state.context_applied,
        context_notes=context_state.context_notes,
        context_version=context_state.context_version,
        context_json=context_state.context_payload,
    )
