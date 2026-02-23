from __future__ import annotations

from core.engine.pipeline import ContextComputation
from core.engine.runner import run_engine_pipeline


class _FakeSignals:
    def __init__(self) -> None:
        self.sufficiency = {"signal_a": True, "signal_b": False}


class _FakeStrategy:
    goal_name = "generic_goal"

    def evaluate(self, signals, target):
        return {"deviations": {"rule_a": True}, "priority_score": 0.5, "risks": ["RISK_A"]}

    def recommend(self, evaluation):
        return [{"id": "rec_1", "priority": 1, "confidence": 0.7, "reason_codes": ["RISK_A"]}]


def test_run_engine_pipeline_orchestrates_generic_components() -> None:
    output = run_engine_pipeline(
        strategy=_FakeStrategy(),
        signals=_FakeSignals(),
        target={},
        input_summary={"goal_type": "generic_goal"},
        context_input=None,
        history=[],
        previous_alignment_confidence=None,
        engine_version="v4_test",
        available_observation_count=7,
        required_observation_count=7,
        context_adapter=lambda strategy, signals, target, evaluation, context_input: ContextComputation(
            evaluation=evaluation,
            urgency=0.5,
            context_applied=False,
            context_notes=[],
            context_version="ctx_v1",
            context_payload={"metadata": {"context_type": None}},
        ),
        additional_risk_detector=lambda signals: [],
        recommendation_ranker=lambda recommendations, urgency: recommendations,
        recommendation_serializer=lambda ranked: ranked,
        score_breakdown_builder=lambda **kwargs: {
            "goal_adherence_penalty": 10.0,
            "risk_penalty": 5.0,
            "uncertainty_penalty": 2.0,
            "recovery_risk_penalty": 4.0,
            "stability_penalty": 2.0,
        },
        penalty_extractor=lambda breakdown: breakdown,
        alignment_scorer=lambda penalties: 77.0,
        confidence_calculator=lambda **kwargs: {
            "alignment_confidence": 0.82,
            "recommendation_confidence": [{"id": "rec_1", "confidence": 0.88}],
            "confidence_breakdown": {"components": {"data_completeness": 1.0}},
            "confidence_notes": [],
            "confidence_version": "conf_v1",
        },
        computed_signal_builder=lambda signals, evaluation: {"sufficiency": signals.sufficiency},
        trace_builder=lambda **kwargs: kwargs,
    )

    assert output.alignment_score == 77.0
    assert output.risk_score == 23.0
    assert output.alignment_confidence == 0.82
    assert output.confidence_version == "conf_v1"
    assert output.context_applied is False
    assert output.trace["engine_version"] == "v4_test"
    assert output.trace["strategy_name"] == "generic_goal"
    assert isinstance(output.recommendations, list)
