from __future__ import annotations

from core.context.cycle_context import CycleContext
from core.context.registry import apply_context


def test_cycle_context_luteal_modulates_thresholds_and_scalars() -> None:
    base_thresholds = {"max_volatility": 0.08, "min_recovery": 0.55}
    result = CycleContext().apply(
        goal_type="weight_loss",
        base_thresholds=base_thresholds,
        score_inputs={"priority_score": 0.45},
        context_input={"phase": "luteal"},
    )

    assert result.context_applied is True
    assert result.context_version == "ctx_v1"
    assert result.modulated_thresholds["max_volatility"] == 0.092
    assert result.modulated_thresholds["min_recovery"] == 0.52
    assert result.penalty_scalars["priority_score_scale"] == 0.95
    assert len(result.context_notes) >= 1
    assert base_thresholds == {"max_volatility": 0.08, "min_recovery": 0.55}


def test_cycle_context_menstrual_softens_recovery_only() -> None:
    result = CycleContext().apply(
        goal_type="weight_loss",
        base_thresholds={"max_volatility": 0.08, "min_recovery": 0.55},
        score_inputs={"priority_score": 0.45},
        context_input={"phase": "menstrual"},
    )

    assert result.context_applied is True
    assert result.modulated_thresholds["max_volatility"] == 0.08
    assert result.modulated_thresholds["min_recovery"] == 0.5
    assert result.penalty_scalars["priority_score_scale"] == 0.95


def test_cycle_context_invalid_phase_is_not_applied() -> None:
    result = CycleContext().apply(
        goal_type="weight_loss",
        base_thresholds={"max_volatility": 0.08, "min_recovery": 0.55},
        score_inputs={"priority_score": 0.45},
        context_input={"phase": "invalid-phase"},
    )

    assert result.context_applied is False
    assert result.modulated_thresholds["max_volatility"] == 0.08
    assert result.modulated_thresholds["min_recovery"] == 0.55
    assert result.context_metadata["phase"] is None


def test_context_registry_passthrough_when_context_absent() -> None:
    base_thresholds = {"max_volatility": 0.08, "min_recovery": 0.55}
    result = apply_context(
        goal_type="weight_loss",
        base_thresholds=base_thresholds,
        score_inputs={"priority_score": 0.45},
        context_input=None,
    )

    assert result.context_applied is False
    assert result.modulated_thresholds == base_thresholds
    assert base_thresholds == {"max_volatility": 0.08, "min_recovery": 0.55}


def test_context_registry_unsupported_type_is_ignored() -> None:
    result = apply_context(
        goal_type="weight_loss",
        base_thresholds={"max_volatility": 0.08, "min_recovery": 0.55},
        score_inputs={"priority_score": 0.45},
        context_input={"context_type": "travel", "state": "jetlag"},
    )

    assert result.context_applied is False
    assert result.context_metadata["context_type"] == "travel"
    assert any("Unsupported context_type" in note for note in result.context_notes)
