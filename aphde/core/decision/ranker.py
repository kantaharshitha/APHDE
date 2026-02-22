from __future__ import annotations

from dataclasses import replace

from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory


_CATEGORY_IMPACT = {
    RecommendationCategory.TRAINING: 0.9,
    RecommendationCategory.NUTRITION: 0.85,
    RecommendationCategory.RECOVERY: 0.75,
    RecommendationCategory.HABIT: 0.7,
}

_CATEGORY_EFFORT = {
    RecommendationCategory.TRAINING: 0.6,
    RecommendationCategory.NUTRITION: 0.5,
    RecommendationCategory.RECOVERY: 0.35,
    RecommendationCategory.HABIT: 0.4,
}


def rank_recommendations(
    recommendations: list[Recommendation],
    *,
    urgency: float,
    confidence_weight: float = 0.35,
    impact_weight: float = 0.4,
    urgency_weight: float = 0.2,
    effort_weight: float = 0.15,
) -> list[Recommendation]:
    scored: list[tuple[float, Recommendation]] = []
    for rec in recommendations:
        impact = _CATEGORY_IMPACT.get(rec.category, 0.6)
        effort = _CATEGORY_EFFORT.get(rec.category, 0.5)
        score = (
            impact_weight * impact
            + urgency_weight * max(0.0, min(1.0, urgency))
            + confidence_weight * max(0.0, min(1.0, rec.confidence))
            - effort_weight * effort
        )
        scored.append((score, rec))

    scored.sort(key=lambda t: t[0], reverse=True)
    ranked: list[Recommendation] = []
    for idx, (_, rec) in enumerate(scored, start=1):
        ranked.append(replace(rec, priority=idx))
    return ranked
