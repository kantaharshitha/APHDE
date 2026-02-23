from core.decision.engine import run_decision_engine
from core.signals.aggregator import SignalBundle
from core.strategies.factory import StrategyFactory
from core.models.enums import GoalType


def test_run_decision_engine_returns_scored_explainable_result() -> None:
    strategy = StrategyFactory.create(GoalType.WEIGHT_LOSS)
    signals = SignalBundle(
        trend_slope=0.02,
        volatility_index=0.11,
        compliance_ratio=0.55,
        muscle_balance_index=0.6,
        recovery_index=0.4,
        progressive_overload_score=0.52,
        sufficiency={
            "trend_slope": True,
            "volatility_index": True,
            "compliance_ratio": True,
            "muscle_balance_index": True,
            "recovery_index": True,
            "progressive_overload_score": True,
        },
    )

    result = run_decision_engine(
        strategy=strategy,
        signals=signals,
        target={},
        input_summary={"user_id": 1, "goal_type": "weight_loss"},
    )

    assert 0.0 <= result.alignment_score <= 100.0
    assert 0.0 <= result.risk_score <= 100.0
    assert 0.0 <= result.alignment_confidence <= 1.0
    assert result.recommendation_confidence is not None
    assert result.confidence_breakdown is not None
    assert result.confidence_version == "conf_v1"
    assert "score_breakdown" in result.trace
    assert "triggered_rules" in result.trace
    assert isinstance(result.recommendations, list)
    rec_ids = {rec["id"] for rec in result.recommendations}
    rec_conf_ids = {item["id"] for item in result.recommendation_confidence}
    assert rec_conf_ids == rec_ids


def test_run_decision_engine_applies_context_without_mutating_signals() -> None:
    strategy = StrategyFactory.create(GoalType.WEIGHT_LOSS)
    signals = SignalBundle(
        trend_slope=0.02,
        volatility_index=0.11,
        compliance_ratio=0.55,
        muscle_balance_index=0.6,
        recovery_index=0.4,
        progressive_overload_score=0.52,
        sufficiency={
            "trend_slope": True,
            "volatility_index": True,
            "compliance_ratio": True,
            "muscle_balance_index": True,
            "recovery_index": True,
            "progressive_overload_score": True,
        },
    )
    original_signals = (
        signals.trend_slope,
        signals.volatility_index,
        signals.compliance_ratio,
        signals.muscle_balance_index,
        signals.recovery_index,
        signals.progressive_overload_score,
        signals.sufficiency.copy() if signals.sufficiency else None,
    )

    result = run_decision_engine(
        strategy=strategy,
        signals=signals,
        target={},
        input_summary={"user_id": 1, "goal_type": "weight_loss"},
        context_input={"phase": "luteal"},
    )

    assert result.context_applied is True
    assert result.context_version == "ctx_v1"
    assert result.context_json is not None
    assert result.context_json["metadata"]["phase"] == "luteal"
    assert (
        signals.trend_slope,
        signals.volatility_index,
        signals.compliance_ratio,
        signals.muscle_balance_index,
        signals.recovery_index,
        signals.progressive_overload_score,
        signals.sufficiency,
    ) == original_signals
