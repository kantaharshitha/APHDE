from __future__ import annotations

from typing import Any


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def diff_runs(run_a: dict[str, Any], run_b: dict[str, Any]) -> dict[str, Any]:
    recs_a = run_a.get("recommendations", [])
    recs_b = run_b.get("recommendations", [])
    rec_map_a = {str(item.get("id")): item for item in recs_a}
    rec_map_b = {str(item.get("id")): item for item in recs_b}

    ids_a = set(rec_map_a.keys())
    ids_b = set(rec_map_b.keys())
    shared_ids = sorted(ids_a.intersection(ids_b))

    rank_shifts: list[dict[str, Any]] = []
    for rec_id in shared_ids:
        a_priority = rec_map_a[rec_id].get("priority")
        b_priority = rec_map_b[rec_id].get("priority")
        if a_priority != b_priority:
            rank_shifts.append(
                {"id": rec_id, "from_priority": a_priority, "to_priority": b_priority}
            )

    return {
        "score_delta": {
            "alignment_score_delta": round(_as_float(run_b.get("alignment_score")) - _as_float(run_a.get("alignment_score")), 4),
            "risk_score_delta": round(_as_float(run_b.get("risk_score")) - _as_float(run_a.get("risk_score")), 4),
            "alignment_confidence_delta": round(
                _as_float(run_b.get("alignment_confidence")) - _as_float(run_a.get("alignment_confidence")), 4
            ),
        },
        "recommendation_changes": {
            "added": sorted(ids_b - ids_a),
            "removed": sorted(ids_a - ids_b),
            "rank_shifts": rank_shifts,
        },
        "context_changes": {
            "context_applied_from": bool(run_a.get("context_applied", False)),
            "context_applied_to": bool(run_b.get("context_applied", False)),
            "context_version_from": run_a.get("context_version"),
            "context_version_to": run_b.get("context_version"),
        },
    }
