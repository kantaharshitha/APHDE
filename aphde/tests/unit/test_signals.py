from core.signals.aggregator import build_signal_bundle
from core.signals.compliance import compliance_from_workout_logs, compliance_ratio
from core.signals.muscle_balance import muscle_balance_index
from core.signals.overload import progressive_overload_from_volumes
from core.signals.recovery import recovery_index
from core.signals.trend import linear_regression_slope
from core.signals.volatility import coefficient_of_variation


def test_linear_regression_slope_increasing_series() -> None:
    assert linear_regression_slope([1.0, 2.0, 3.0, 4.0]) == 1.0


def test_coefficient_of_variation_returns_none_for_near_zero_mean() -> None:
    assert coefficient_of_variation([1.0, -1.0]) is None


def test_compliance_ratio_bounds() -> None:
    assert compliance_ratio(3, 4) == 0.75
    assert compliance_ratio(5, 4) == 1.0
    assert compliance_ratio(0, 0) is None


def test_compliance_from_workout_logs() -> None:
    logs = [
        {"planned_flag": 1, "completed_flag": 1},
        {"planned_flag": 1, "completed_flag": 0},
        {"planned_flag": 0, "completed_flag": 0},
    ]
    assert compliance_from_workout_logs(logs) == 0.5


def test_muscle_balance_index_balanced_distribution() -> None:
    sessions = ["push", "pull", "lower", "core"]
    assert muscle_balance_index(sessions) == 1.0


def test_recovery_index_weighted_risk() -> None:
    score = recovery_index(1.0, 1.0, 1.0)
    assert score == 0.0


def test_progressive_overload_from_volumes_improves_with_growth() -> None:
    score = progressive_overload_from_volumes([1000.0, 1050.0, 1120.0, 1180.0])
    assert score is not None
    assert score > 0.7


def test_build_signal_bundle_computes_all_primary_signals() -> None:
    weight_values = [80.0, 79.8, 79.6, 79.4, 79.3]
    workouts = [
        {
            "session_type": "push",
            "planned_flag": 1,
            "completed_flag": 1,
            "avg_rpe": 7.5,
            "volume_load": 5200.0,
        },
        {
            "session_type": "pull",
            "planned_flag": 1,
            "completed_flag": 1,
            "avg_rpe": 8.2,
            "volume_load": 5400.0,
        },
        {
            "session_type": "lower",
            "planned_flag": 1,
            "completed_flag": 1,
            "avg_rpe": 8.0,
            "volume_load": 5600.0,
        },
    ]

    bundle = build_signal_bundle(weight_values=weight_values, workout_logs=workouts, window_days=7)

    assert bundle.trend_slope is not None
    assert bundle.volatility_index is not None
    assert bundle.compliance_ratio == 1.0
    assert bundle.muscle_balance_index is not None
    assert bundle.recovery_index is not None
    assert bundle.progressive_overload_score is not None
    assert bundle.sufficiency is not None
    assert all(bundle.sufficiency.values())
