from __future__ import annotations

from typing import Any

from core.context.base import BaseContext, ContextResult


class CycleContext(BaseContext):
    context_name = "cycle"
    context_version = "ctx_v1"
    supported_phases = {"menstrual", "follicular", "ovulatory", "luteal"}

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def apply(
        self,
        *,
        goal_type: str,
        base_thresholds: dict[str, float],
        score_inputs: dict[str, float],
        context_input: dict[str, Any],
    ) -> ContextResult:
        phase = str(context_input.get("phase", "")).strip().lower()
        if phase not in self.supported_phases:
            return ContextResult(
                modulated_thresholds=dict(base_thresholds),
                context_applied=False,
                context_version=self.context_version,
                context_metadata={"context_type": self.context_name, "phase": None},
            )

        modulated = dict(base_thresholds)
        penalty_scalars = {"priority_score_scale": 1.0}
        adjustments: dict[str, float] = {}
        notes: list[str] = []

        if phase == "luteal":
            if "max_volatility" in modulated:
                prev = modulated["max_volatility"]
                modulated["max_volatility"] = self._clamp(prev * 1.15, 0.02, 0.5)
                adjustments["max_volatility_delta"] = round(modulated["max_volatility"] - prev, 4)
                notes.append("Luteal phase: widened volatility tolerance.")
            if "min_recovery" in modulated:
                prev = modulated["min_recovery"]
                modulated["min_recovery"] = self._clamp(prev - 0.03, 0.35, 0.95)
                adjustments["min_recovery_delta"] = round(modulated["min_recovery"] - prev, 4)
                notes.append("Luteal phase: slightly softened recovery expectation.")
            penalty_scalars["priority_score_scale"] = 0.95

        if phase == "menstrual":
            if "min_recovery" in modulated:
                prev = modulated["min_recovery"]
                modulated["min_recovery"] = self._clamp(prev - 0.05, 0.35, 0.95)
                adjustments["min_recovery_delta"] = round(modulated["min_recovery"] - prev, 4)
                notes.append("Menstrual phase: softened recovery expectation.")
            penalty_scalars["priority_score_scale"] = 0.95

        return ContextResult(
            modulated_thresholds=modulated,
            penalty_scalars=penalty_scalars,
            tolerance_adjustments=adjustments,
            context_applied=True,
            context_notes=notes or [f"Cycle context applied for phase: {phase}."],
            context_version=self.context_version,
            context_metadata={
                "context_type": self.context_name,
                "phase": phase,
                "goal_type": goal_type,
                "score_inputs": score_inputs,
            },
        )
