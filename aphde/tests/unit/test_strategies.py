from core.models.enums import GoalType
from core.signals.aggregator import SignalBundle
from core.strategies.factory import StrategyFactory


def _sample_signals() -> SignalBundle:
    return SignalBundle(
        trend_slope=0.03,
        volatility_index=0.09,
        compliance_ratio=0.62,
        muscle_balance_index=0.5,
        recovery_index=0.46,
        progressive_overload_score=0.58,
        sufficiency={},
    )


def test_strategy_factory_returns_expected_types() -> None:
    wl = StrategyFactory.create(GoalType.WEIGHT_LOSS)
    rc = StrategyFactory.create(GoalType.RECOMPOSITION)
    sg = StrategyFactory.create(GoalType.STRENGTH_GAIN)
    gh = StrategyFactory.create(GoalType.GENERAL_HEALTH)

    assert wl.goal_name == "weight_loss"
    assert rc.goal_name == "recomposition"
    assert sg.goal_name == "strength_gain"
    assert gh.goal_name == "general_health"


def test_weight_loss_strategy_flags_trend_and_compliance_risks() -> None:
    strategy = StrategyFactory.create(GoalType.WEIGHT_LOSS)
    evaluation = strategy.evaluate(_sample_signals(), {})
    recs = strategy.recommend(evaluation)

    assert evaluation["deviations"]["trend_miss"] is True
    assert evaluation["deviations"]["compliance_miss"] is True
    assert any(rec.rec_id.startswith("wl_") for rec in recs)


def test_recomposition_prioritizes_overload_and_balance() -> None:
    strategy = StrategyFactory.create(GoalType.RECOMPOSITION)
    evaluation = strategy.evaluate(_sample_signals(), {})
    recs = strategy.recommend(evaluation)

    assert evaluation["deviations"]["overload_miss"] is True
    assert evaluation["deviations"]["balance_miss"] is True
    assert any(rec.rec_id.startswith("rc_") for rec in recs)


def test_strength_gain_and_general_health_generate_different_top_recommendations() -> None:
    signals = _sample_signals()
    sg = StrategyFactory.create(GoalType.STRENGTH_GAIN)
    gh = StrategyFactory.create(GoalType.GENERAL_HEALTH)

    sg_recs = sg.recommend(sg.evaluate(signals, {}))
    gh_recs = gh.recommend(gh.evaluate(signals, {}))

    assert len(sg_recs) > 0
    assert len(gh_recs) > 0
    assert sg_recs[0].rec_id != gh_recs[0].rec_id
