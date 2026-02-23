from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class DomainLogs:
    """
    Domain-neutral log container passed into domain signal computation.

    Domains can use either specific named buckets in `items` or keep a
    single `raw` payload shape. The core remains agnostic either way.
    """

    items: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class SignalBundleLike(Protocol):
    """
    Minimal signal contract consumed by the deterministic decision pipeline.
    """

    sufficiency: dict[str, bool] | None


@runtime_checkable
class StrategyLike(Protocol):
    """
    Domain strategy contract. Implementations must be deterministic.
    """

    goal_name: str

    def evaluate(self, signals: SignalBundleLike, target: dict[str, Any]) -> dict[str, Any]:
        ...

    def recommend(self, evaluation: dict[str, Any]) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class DomainDefinition(Protocol):
    """
    Domain adapter contract used by core engine/service orchestration.
    """

    def compute_signals(self, logs: DomainLogs, config: dict[str, Any]) -> SignalBundleLike:
        ...

    def get_strategy(self, goal_type: str) -> StrategyLike:
        ...

    def get_domain_config(self) -> dict[str, Any]:
        ...

    def normalize_goal_type(self, raw_goal_type: str) -> str:
        ...

    def domain_name(self) -> str:
        ...

    def domain_version(self) -> str:
        ...


def validate_domain_definition(candidate: object) -> DomainDefinition:
    """
    Runtime guard used at composition boundaries before the domain
    implementation is injected into the core pipeline.
    """

    if not isinstance(candidate, DomainDefinition):
        raise TypeError("candidate does not satisfy DomainDefinition contract")
    return candidate
