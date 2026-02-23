from __future__ import annotations

from pathlib import Path

import pytest

from core.engine.contracts import (
    DomainDefinition,
    DomainLogs,
    SignalBundleLike,
    StrategyLike,
    validate_domain_definition,
)


class _FakeSignals:
    def __init__(self) -> None:
        self.sufficiency = {"signal_a": True}


class _FakeStrategy:
    goal_name = "generic_goal"

    def evaluate(self, signals: SignalBundleLike, target: dict) -> dict:
        return {"deviations": {}, "priority_score": 0.5}

    def recommend(self, evaluation: dict) -> list[dict]:
        return []


class _FakeDomain:
    def compute_signals(self, logs: DomainLogs, config: dict) -> SignalBundleLike:
        return _FakeSignals()

    def get_strategy(self, goal_type: str) -> StrategyLike:
        return _FakeStrategy()

    def get_domain_config(self) -> dict:
        return {"window_days": 7}

    def normalize_goal_type(self, raw_goal_type: str) -> str:
        return raw_goal_type.strip().lower()

    def domain_name(self) -> str:
        return "health"

    def domain_version(self) -> str:
        return "health_v1"


class _InvalidDomainMissingMethods:
    def domain_name(self) -> str:
        return "invalid"


def test_validate_domain_definition_accepts_conforming_candidate() -> None:
    candidate = _FakeDomain()
    validated = validate_domain_definition(candidate)
    assert isinstance(validated, DomainDefinition)
    assert validated.domain_name() == "health"


def test_validate_domain_definition_rejects_non_conforming_candidate() -> None:
    with pytest.raises(TypeError):
        validate_domain_definition(_InvalidDomainMissingMethods())


def test_core_engine_package_has_no_health_terms() -> None:
    forbidden_terms = {"weight", "calorie", "workout", "recovery", "cycle"}
    engine_dir = Path(__file__).resolve().parents[2] / "core" / "engine"

    for path in engine_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            assert term not in text, f"found forbidden term '{term}' in {path.name}"
