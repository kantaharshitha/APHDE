from abc import ABC, abstractmethod
from typing import Any

from core.models.entities import Recommendation
from core.signals.aggregator import SignalBundle


class GoalStrategy(ABC):
    goal_name: str

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _safe(signal: float | None, default: float = 0.5) -> float:
        if signal is None:
            return default
        return float(signal)

    @abstractmethod
    def evaluate(self, signals: SignalBundle, target: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def recommend(self, evaluation: dict[str, Any]) -> list[Recommendation]:
        raise NotImplementedError
