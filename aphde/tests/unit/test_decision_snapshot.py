from __future__ import annotations

import json
from pathlib import Path

from core.decision.engine import run_decision_engine
from core.models.enums import GoalType
from core.signals.aggregator import SignalBundle
from core.strategies.factory import StrategyFactory


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "decision_weight_loss_snapshot.json"


def test_weight_loss_decision_snapshot() -> None:
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

    actual = {
        "alignment_score": result.alignment_score,
        "risk_score": result.risk_score,
        "recommendations": result.recommendations,
        "trace": result.trace,
    }
    expected = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))
    assert actual == expected
