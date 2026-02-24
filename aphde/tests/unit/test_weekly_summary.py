from __future__ import annotations

from core.insights.weekly_summary import build_weekly_insight


def _run(*, compliance: float, recovery: float, volatility: float, overload: float) -> dict:
    return {
        "trace": {
            "computed_signals": {
                "compliance_ratio": compliance,
                "recovery_index": recovery,
                "volatility_index": volatility,
                "progressive_overload_score": overload,
            }
        }
    }


def test_weekly_summary_contains_expected_fields() -> None:
    runs = [
        _run(compliance=0.72, recovery=0.60, volatility=0.10, overload=0.52),
        _run(compliance=0.74, recovery=0.61, volatility=0.09, overload=0.55),
        _run(compliance=0.76, recovery=0.63, volatility=0.08, overload=0.58),
        _run(compliance=0.78, recovery=0.64, volatility=0.08, overload=0.60),
    ]
    summary = build_weekly_insight(recent_runs=runs)
    assert "week_start" in summary
    assert "week_end" in summary
    assert "planned_sessions" in summary
    assert "completed_sessions" in summary
    assert "compliance_pct" in summary
    assert "compliance_avg_pct" in summary
    assert "recovery_shift" in summary
    assert "volatility_direction" in summary
    assert "overload_progress" in summary
    assert summary["data_sufficient"] is True


def test_weekly_summary_marks_insufficient_data_when_window_small() -> None:
    runs = [
        _run(compliance=0.70, recovery=0.60, volatility=0.10, overload=0.52),
        _run(compliance=0.71, recovery=0.61, volatility=0.09, overload=0.53),
    ]
    summary = build_weekly_insight(recent_runs=runs)
    assert summary["data_sufficient"] is False
