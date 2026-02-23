from __future__ import annotations

from core.engine.contracts import DomainLogs, validate_domain_definition
from domains.health.domain_definition import HealthDomainDefinition


def test_health_domain_definition_conforms_to_contract() -> None:
    domain = HealthDomainDefinition()
    validated = validate_domain_definition(domain)

    assert validated.domain_name() == "health"
    assert validated.domain_version() == "health_v1"


def test_health_domain_strategy_resolution_and_goal_normalization() -> None:
    domain = HealthDomainDefinition()

    strategy = domain.get_strategy(domain.normalize_goal_type("  WEIGHT_LOSS "))
    assert strategy.goal_name == "weight_loss"


def test_health_domain_compute_signals_matches_expected_shape() -> None:
    domain = HealthDomainDefinition()
    logs = DomainLogs(
        items={
            "weight_logs": [
                {"weight_kg": 78.0},
                {"weight_kg": 78.2},
                {"weight_kg": 78.1},
            ],
            "workout_logs": [
                {"session_type": "upper", "planned_flag": True, "completed_flag": True, "avg_rpe": 8.0, "volume_load": 5000.0},
                {"session_type": "lower", "planned_flag": True, "completed_flag": True, "avg_rpe": 8.2, "volume_load": 5200.0},
            ],
        }
    )
    signals = domain.compute_signals(logs, config=domain.get_domain_config())

    assert hasattr(signals, "trend_slope")
    assert hasattr(signals, "volatility_index")
    assert hasattr(signals, "recovery_index")
    assert isinstance(signals.sufficiency, dict)
    assert "trend_slope" in signals.sufficiency
