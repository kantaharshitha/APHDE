from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextResult:
    modulated_thresholds: dict[str, float] = field(default_factory=dict)
    penalty_scalars: dict[str, float] = field(default_factory=dict)
    tolerance_adjustments: dict[str, float] = field(default_factory=dict)
    context_applied: bool = False
    context_notes: list[str] = field(default_factory=list)
    context_version: str = "ctx_v1"
    context_metadata: dict[str, Any] = field(default_factory=dict)


class BaseContext(ABC):
    context_name: str
    context_version: str

    @abstractmethod
    def apply(
        self,
        *,
        goal_type: str,
        base_thresholds: dict[str, float],
        score_inputs: dict[str, float],
        context_input: dict[str, Any],
    ) -> ContextResult:
        raise NotImplementedError
