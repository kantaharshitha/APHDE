from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextComputation:
    evaluation: dict[str, Any]
    urgency: float
    context_applied: bool = False
    context_notes: list[str] = field(default_factory=list)
    context_version: str = "ctx_v1"
    context_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EngineRunOutput:
    alignment_score: float
    risk_score: float
    recommendations: list[dict[str, Any]]
    trace: dict[str, Any]
    alignment_confidence: float
    recommendation_confidence: list[dict[str, Any]]
    confidence_breakdown: dict[str, Any]
    confidence_version: str
    context_applied: bool
    context_notes: list[str]
    context_version: str
    context_json: dict[str, Any]
