from __future__ import annotations

from typing import Any

from core.context.base import ContextResult
from core.context.cycle_context import CycleContext


def apply_context(
    *,
    goal_type: str,
    base_thresholds: dict[str, float],
    score_inputs: dict[str, float],
    context_input: dict[str, Any] | None,
) -> ContextResult:
    if not context_input:
        return ContextResult(
            modulated_thresholds=dict(base_thresholds),
            context_applied=False,
            context_version="ctx_v1",
            context_metadata={"context_type": None},
        )

    context_type = str(context_input.get("context_type", "cycle")).lower()
    if context_type == "cycle" or context_input.get("phase"):
        return CycleContext().apply(
            goal_type=goal_type,
            base_thresholds=base_thresholds,
            score_inputs=score_inputs,
            context_input=context_input,
        )

    return ContextResult(
        modulated_thresholds=dict(base_thresholds),
        context_applied=False,
        context_notes=[f"Unsupported context_type '{context_type}' ignored."],
        context_version="ctx_v1",
        context_metadata={"context_type": context_type},
    )
