from __future__ import annotations

from collections import Counter
from collections.abc import Iterable


DEFAULT_TARGET_DISTRIBUTION = {
    "push": 0.25,
    "pull": 0.25,
    "lower": 0.25,
    "core": 0.25,
}

SESSION_MAP = {
    "upper": "push",
    "chest": "push",
    "shoulders": "push",
    "triceps": "push",
    "push": "push",
    "back": "pull",
    "biceps": "pull",
    "pull": "pull",
    "legs": "lower",
    "lower": "lower",
    "lower_body": "lower",
    "core": "core",
    "abs": "core",
    "full_body": "lower",
}


def _normalize_session(session_type: str) -> str | None:
    key = session_type.strip().lower()
    return SESSION_MAP.get(key)


def muscle_balance_index(
    session_types: Iterable[str],
    target_distribution: dict[str, float] | None = None,
) -> float | None:
    target = target_distribution or DEFAULT_TARGET_DISTRIBUTION
    normalized = [_normalize_session(s) for s in session_types]
    normalized = [s for s in normalized if s in target]
    if not normalized:
        return None

    counts = Counter(normalized)
    total = sum(counts.values())

    deviation = 0.0
    for group, target_share in target.items():
        actual_share = counts[group] / total if total > 0 else 0.0
        deviation += abs(actual_share - target_share)

    # Total variation distance in [0, 2]; convert into quality score [0, 1].
    score = 1.0 - (deviation / 2.0)
    return max(0.0, min(1.0, score))
