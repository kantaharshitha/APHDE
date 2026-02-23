from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_history(runs: list[dict[str, Any]]) -> dict[str, Any]:
    alignment_trend = [float(item.get("alignment_score", 0.0)) for item in runs]
    confidence_trend = [float(item.get("alignment_confidence", 0.0)) for item in runs]
    context_applied_count = sum(1 for item in runs if bool(item.get("context_applied", False)))
    determinism_verified_count = sum(1 for item in runs if item.get("determinism_verified") is True)
    determinism_checked_count = sum(1 for item in runs if item.get("determinism_verified") is not None)

    rule_counter: Counter[str] = Counter()
    for item in runs:
        for rule in item.get("triggered_rules", []):
            rule_counter[str(rule)] += 1

    total_runs = len(runs)
    context_frequency = (context_applied_count / total_runs) if total_runs else 0.0
    determinism_pass_rate = (
        determinism_verified_count / determinism_checked_count if determinism_checked_count else 0.0
    )

    return {
        "count": total_runs,
        "alignment_trend": alignment_trend,
        "confidence_trend": confidence_trend,
        "context_application_frequency": round(context_frequency, 4),
        "rule_trigger_distribution": dict(sorted(rule_counter.items())),
        "determinism_pass_rate": round(determinism_pass_rate, 4),
    }
