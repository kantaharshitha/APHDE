from __future__ import annotations

from typing import Any

from core.engine.contracts import DomainDefinition, DomainLogs, SignalBundleLike, StrategyLike
from domains.health.signals import compute_health_signals
from domains.health.strategy import get_health_strategy
from domains.health.thresholds import DEFAULT_SIGNAL_WINDOW_DAYS, DEFAULT_TARGETS


class HealthDomainDefinition(DomainDefinition):
    def compute_signals(self, logs: DomainLogs, config: dict[str, Any]) -> SignalBundleLike:
        return compute_health_signals(logs.items, config)

    def get_strategy(self, goal_type: str) -> StrategyLike:
        return get_health_strategy(goal_type)

    def get_domain_config(self) -> dict[str, Any]:
        return {"window_days": DEFAULT_SIGNAL_WINDOW_DAYS, "default_targets": dict(DEFAULT_TARGETS)}

    def normalize_goal_type(self, raw_goal_type: str) -> str:
        return raw_goal_type.strip().lower()

    def domain_name(self) -> str:
        return "health"

    def domain_version(self) -> str:
        return "health_v1"
