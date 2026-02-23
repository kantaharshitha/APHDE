from core.scoring.confidence import compute_confidence
from core.signals.aggregator import SignalBundle


def _signals(
    *,
    volatility_index: float | None = 0.05,
    sufficiency: dict[str, bool] | None = None,
) -> SignalBundle:
    return SignalBundle(
        trend_slope=0.01,
        volatility_index=volatility_index,
        compliance_ratio=0.8,
        muscle_balance_index=0.7,
        recovery_index=0.7,
        progressive_overload_score=0.7,
        sufficiency=sufficiency
        or {
            "trend_slope": True,
            "volatility_index": True,
            "compliance_ratio": True,
            "muscle_balance_index": True,
            "recovery_index": True,
            "progressive_overload_score": True,
        },
    )


def test_compute_confidence_bounds_alignment_and_recommendation_values() -> None:
    result = compute_confidence(
        signals=_signals(),
        deviations={"trend_miss": False, "compliance_miss": False},
        recommendations=[{"id": "r1", "confidence": 0.8, "reason_codes": ["A", "B"]}],
    )

    assert 0.0 <= result["alignment_confidence"] <= 1.0
    assert 0.0 <= result["recommendation_confidence"][0]["confidence"] <= 1.0


def test_compute_confidence_penalizes_sparse_data() -> None:
    sparse = _signals(
        sufficiency={
            "trend_slope": False,
            "volatility_index": False,
            "compliance_ratio": True,
            "muscle_balance_index": False,
            "recovery_index": False,
            "progressive_overload_score": True,
        }
    )
    dense = _signals()

    sparse_res = compute_confidence(
        signals=sparse,
        deviations={"trend_miss": True, "compliance_miss": True},
        recommendations=[],
    )
    dense_res = compute_confidence(
        signals=dense,
        deviations={"trend_miss": True, "compliance_miss": True},
        recommendations=[],
    )

    assert sparse_res["alignment_confidence"] < dense_res["alignment_confidence"]


def test_compute_confidence_penalizes_high_volatility() -> None:
    stable = compute_confidence(
        signals=_signals(volatility_index=0.03),
        deviations={"trend_miss": False},
        recommendations=[],
    )
    unstable = compute_confidence(
        signals=_signals(volatility_index=0.15),
        deviations={"trend_miss": False},
        recommendations=[],
    )

    assert unstable["alignment_confidence"] < stable["alignment_confidence"]


def test_compute_confidence_with_smoothing_uses_previous_value() -> None:
    result = compute_confidence(
        signals=_signals(),
        deviations={"trend_miss": True, "compliance_miss": True},
        recommendations=[],
        previous_alignment_confidence=1.0,
        alpha=0.5,
    )

    assert result["confidence_breakdown"]["smoothing"]["previous_used"] is True
    assert 0.0 <= result["alignment_confidence"] <= 1.0


def test_compute_confidence_is_deterministic_for_same_inputs() -> None:
    kwargs = {
        "signals": _signals(),
        "deviations": {"trend_miss": True, "compliance_miss": False},
        "recommendations": [{"id": "r1", "confidence": 0.75, "reason_codes": ["COMPLIANCE_DROP"]}],
        "history": [{"deviations": {"trend_miss": True, "compliance_miss": False}}],
        "available_days": 5,
        "required_days": 7,
    }
    a = compute_confidence(**kwargs)
    b = compute_confidence(**kwargs)
    assert a == b
