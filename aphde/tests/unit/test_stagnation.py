from __future__ import annotations

from core.insights.stagnation import detect_stagnation_alerts


def _run(*, trend: float, overload: float, compliance: float, recovery: float) -> dict:
    return {
        "trace": {
            "computed_signals": {
                "trend_slope": trend,
                "progressive_overload_score": overload,
                "compliance_ratio": compliance,
                "recovery_index": recovery,
            }
        }
    }


def test_stagnation_detects_expected_alert_types() -> None:
    # newest -> oldest ordering (matches repository/service contract)
    runs = [
        _run(trend=0.002, overload=0.50, compliance=0.76, recovery=0.41),
        _run(trend=0.003, overload=0.51, compliance=0.79, recovery=0.42),
        _run(trend=0.001, overload=0.50, compliance=0.82, recovery=0.43),
        _run(trend=0.002, overload=0.49, compliance=0.86, recovery=0.45),
        _run(trend=0.001, overload=0.50, compliance=0.90, recovery=0.44),
    ]
    alerts = detect_stagnation_alerts(recent_runs=runs)
    types = {item["type"] for item in alerts}
    assert "weight_trend_stagnation" in types
    assert "overload_flatline" in types
    assert "compliance_drift" in types
    assert "persistent_low_recovery" in types


def test_stagnation_returns_empty_when_no_conditions_met() -> None:
    # newest -> oldest ordering (matches repository/service contract)
    runs = [
        _run(trend=0.07, overload=0.72, compliance=0.83, recovery=0.74),
        _run(trend=0.06, overload=0.68, compliance=0.80, recovery=0.70),
        _run(trend=0.05, overload=0.60, compliance=0.78, recovery=0.66),
        _run(trend=0.04, overload=0.55, compliance=0.75, recovery=0.65),
        _run(trend=0.03, overload=0.45, compliance=0.70, recovery=0.62),
    ]
    alerts = detect_stagnation_alerts(recent_runs=runs)
    assert alerts == []
