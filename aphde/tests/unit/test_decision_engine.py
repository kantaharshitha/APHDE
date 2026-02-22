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
    assert "score_breakdown" in result.trace
    assert "triggered_rules" in result.trace
    assert isinstance(result.recommendations, list)
