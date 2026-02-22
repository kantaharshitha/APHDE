from abc import ABC, abstractmethod

from core.models.entities import Recommendation
from core.signals.aggregator import SignalBundle


class GoalStrategy(ABC):
    @abstractmethod
    def evaluate(self, signals: SignalBundle, target: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def recommend(self, evaluation: dict) -> list[Recommendation]:
        raise NotImplementedError
