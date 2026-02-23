from __future__ import annotations

from typing import Any

from core.signals.aggregator import SignalBundle


CONFIDENCE_VERSION = "conf_v1"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _data_completeness(signals: SignalBundle) -> float:
    sufficiency = signals.sufficiency or {}
    if not sufficiency:
        return 0.0
    return _clamp01(sum(1 for ok in sufficiency.values() if ok) / len(sufficiency))


def _signal_stability(signals: SignalBundle, volatility_cap: float = 0.12) -> float:
    volatility = signals.volatility_index
    if volatility is None:
        return 0.5
    normalized = _clamp01(_safe_float(volatility) / max(1e-6, volatility_cap))
    return _clamp01(1.0 - normalized)


def _threshold_distance_strength(
    *,
    deviations: dict[str, bool],
    threshold_distances: dict[str, float] | None = None,
) -> float:
    if threshold_distances:
        vals = [_clamp01(_safe_float(v)) for v in threshold_distances.values()]
        if vals:
            return sum(vals) / len(vals)

    if not deviations:
        return 0.5
    miss_count = sum(1 for is_miss in deviations.values() if is_miss)
    total = len(deviations)
    return _clamp01(1.0 - (miss_count / total))


def _historical_persistence(
    *,
    current_deviations: dict[str, bool],
    history: list[dict[str, Any]] | None,
) -> float:
    if not history:
        return 0.5

    current_active = {k for k, v in current_deviations.items() if v}
    if not current_active:
        return 0.7

    matches = 0
    for item in history:
        prev = item.get("deviations", {})
        prev_active = {k for k, v in prev.items() if bool(v)}
        if prev_active == current_active:
            matches += 1
    return _clamp01(matches / len(history))


def _window_sufficiency(*, available_days: int, required_days: int) -> float:
    if required_days <= 0:
        return 1.0
    return _clamp01(available_days / required_days)


def compute_confidence(
    *,
    signals: SignalBundle,
    deviations: dict[str, bool],
    recommendations: list[dict[str, Any]],
    history: list[dict[str, Any]] | None = None,
    threshold_distances: dict[str, float] | None = None,
    available_days: int = 7,
    required_days: int = 7,
    previous_alignment_confidence: float | None = None,
    alpha: float = 0.2,
    model_version: str = CONFIDENCE_VERSION,
) -> dict[str, Any]:
    c_data = _data_completeness(signals)
    c_stability = _signal_stability(signals)
    c_distance = _threshold_distance_strength(
        deviations=deviations,
        threshold_distances=threshold_distances,
    )
    c_persistence = _historical_persistence(
        current_deviations=deviations,
        history=history,
    )
    c_window = _window_sufficiency(available_days=available_days, required_days=required_days)

    weights = {
        "data_completeness": 0.30,
        "signal_stability": 0.20,
        "threshold_distance": 0.20,
        "historical_persistence": 0.20,
        "window_sufficiency": 0.10,
    }
    raw_alignment_confidence = (
        weights["data_completeness"] * c_data
        + weights["signal_stability"] * c_stability
        + weights["threshold_distance"] * c_distance
        + weights["historical_persistence"] * c_persistence
        + weights["window_sufficiency"] * c_window
    )
    raw_alignment_confidence = _clamp01(raw_alignment_confidence)

    alpha = _clamp01(alpha)
    if previous_alignment_confidence is None:
        alignment_confidence = raw_alignment_confidence
        previous_used = False
    else:
        prev = _clamp01(previous_alignment_confidence)
        alignment_confidence = _clamp01(alpha * prev + (1.0 - alpha) * raw_alignment_confidence)
        previous_used = True

    recommendation_confidence: list[dict[str, Any]] = []
    for rec in recommendations:
        rec_id = str(rec.get("id", "unknown"))
        reason_codes = rec.get("reason_codes", [])
        confidence_base = _safe_float(rec.get("confidence"), 0.5)
        evidence_strength = _clamp01(min(len(reason_codes), 4) / 4)
        rule_specificity = 0.8 if reason_codes else 0.4
        conflict_penalty = 0.0 if reason_codes else 0.1

        rec_conf = _clamp01(
            0.20
            + 0.35 * alignment_confidence
            + 0.20 * evidence_strength
            + 0.15 * rule_specificity
            + 0.20 * confidence_base
            - conflict_penalty
        )
        recommendation_confidence.append(
            {
                "id": rec_id,
                "confidence": round(rec_conf, 4),
            }
        )

    notes: list[str] = []
    if c_data < 0.7:
        notes.append("Lower confidence due to incomplete signal coverage.")
    if c_stability < 0.5:
        notes.append("Lower confidence due to high volatility.")
    if c_window < 1.0:
        notes.append("Lower confidence due to insufficient lookback window.")
    if not notes:
        notes.append("Confidence supported by sufficient and stable inputs.")

    return {
        "alignment_confidence": round(alignment_confidence, 4),
        "recommendation_confidence": recommendation_confidence,
        "confidence_breakdown": {
            "components": {
                "data_completeness": round(c_data, 4),
                "signal_stability": round(c_stability, 4),
                "threshold_distance": round(c_distance, 4),
                "historical_persistence": round(c_persistence, 4),
                "window_sufficiency": round(c_window, 4),
            },
            "weights": weights,
            "smoothing": {
                "alpha": alpha,
                "previous_used": previous_used,
            },
            "confidence_version": model_version,
        },
        "confidence_notes": notes,
        "confidence_version": model_version,
    }
