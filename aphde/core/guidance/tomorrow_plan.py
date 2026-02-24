from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _severity_from_context(*, risk_score: float, rule_count: int) -> str:
    if risk_score >= 60.0 or rule_count >= 4:
        return "high"
    if risk_score >= 35.0 or rule_count >= 2:
        return "medium"
    return "low"


def _candidate_confidence(rec: dict[str, Any], conf_map: dict[str, float], fallback: float) -> float:
    rec_id = str(rec.get("id", ""))
    if rec_id in conf_map:
        return _clamp(float(conf_map[rec_id]))
    raw = rec.get("confidence")
    if raw is None:
        return _clamp(fallback)
    return _clamp(float(raw))


def _persistence_score(*, rec_id: str, recent_runs: list[dict[str, Any]]) -> float:
    if not recent_runs:
        return 0.5
    window = recent_runs[: min(5, len(recent_runs))]
    hit_count = 0
    for run in window:
        ids = {str(item.get("id", "")) for item in run.get("recommendations", [])}
        if rec_id in ids:
            hit_count += 1
    return _clamp(hit_count / len(window))


def _strategy_relevance(category: str) -> float:
    category = category.lower().strip()
    mapping = {
        "recovery": 0.90,
        "training": 0.85,
        "habit": 0.80,
        "nutrition": 0.78,
    }
    return mapping.get(category, 0.70)


def build_tomorrow_plan(
    *,
    latest_run: dict[str, Any],
    recent_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    recent_runs = recent_runs or []
    recommendations = latest_run.get("recommendations", [])
    trace = latest_run.get("trace", {}) if isinstance(latest_run.get("trace"), dict) else {}
    triggered_rules = trace.get("triggered_rules", [])
    rule_count = len(triggered_rules)
    risk_score = float(latest_run.get("risk_score", 0.0))
    alignment_confidence = float(latest_run.get("alignment_confidence", 0.0))
    rec_conf_map = {
        str(item.get("id", "")): float(item.get("confidence", 0.0))
        for item in latest_run.get("recommendation_confidence", [])
    }

    if not recommendations:
        return {
            "action_id": "maintain_current_protocol",
            "action": "Maintain current protocol and re-evaluate tomorrow.",
            "reason": "No critical recommendation exceeded deterministic priority threshold.",
            "confidence": round(_clamp(alignment_confidence), 4),
            "severity": _severity_from_context(risk_score=risk_score, rule_count=rule_count),
            "expected_impact": "Preserves stability while monitoring new deviations.",
            "priority_score": 0.0,
        }

    candidates: list[dict[str, Any]] = []
    risk_component = _clamp((risk_score / 100.0) + (0.05 * rule_count))
    for rec in recommendations:
        rec_id = str(rec.get("id", ""))
        confidence_component = _candidate_confidence(rec, rec_conf_map, alignment_confidence)
        persistence_component = _persistence_score(rec_id=rec_id, recent_runs=recent_runs)
        strategy_component = _strategy_relevance(str(rec.get("category", "")))
        score = (
            0.35 * risk_component
            + 0.30 * persistence_component
            + 0.20 * strategy_component
            + 0.15 * confidence_component
        )
        candidates.append(
            {
                "action_id": rec_id or f"action_{len(candidates)+1}",
                "action": str(rec.get("action", "No action text available.")),
                "reason": ", ".join(rec.get("reason_codes", [])) or "Priority recommendation from deterministic ranking.",
                "confidence": round(confidence_component, 4),
                "severity": _severity_from_context(risk_score=risk_score, rule_count=rule_count),
                "expected_impact": str(rec.get("expected_effect", "Supports short-term alignment improvement.")),
                "priority_score": round(score, 4),
                "_priority": int(rec.get("priority") or 999),
            }
        )

    # Deterministic tie-break: score desc, priority asc, action_id asc
    candidates.sort(key=lambda item: (-item["priority_score"], item["_priority"], item["action_id"]))
    winner = candidates[0]
    winner.pop("_priority", None)
    return winner
