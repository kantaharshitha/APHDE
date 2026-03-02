from __future__ import annotations

from core.decision.ranker import rank_recommendations
from core.engine.runner import _ensure_minimum_recommendations
from core.models.entities import Recommendation
from core.models.enums import RecommendationCategory


def _rec(rec_id: str, category: RecommendationCategory, confidence: float, priority: int = 1) -> Recommendation:
    return Recommendation(
        rec_id=rec_id,
        priority=priority,
        category=category,
        action=f"action-{rec_id}",
        expected_effect=f"effect-{rec_id}",
        reason_codes=["RULE_X"],
        confidence=confidence,
    )


def test_minimum_recommendations_keeps_ranked_when_already_two() -> None:
    ranked = rank_recommendations(
        [
            _rec("r1", RecommendationCategory.TRAINING, 0.9),
            _rec("r2", RecommendationCategory.NUTRITION, 0.8),
        ],
        urgency=0.7,
    )

    ensured = _ensure_minimum_recommendations(
        ranked_recommendations=ranked,
        urgency=0.7,
        recommendation_ranker=rank_recommendations,
    )

    assert len(ensured) == 2
    assert ensured[0].rec_id == ranked[0].rec_id
    assert ensured[1].rec_id == ranked[1].rec_id


def test_minimum_recommendations_adds_deterministic_fallback_when_one() -> None:
    ranked = rank_recommendations([_rec("r1", RecommendationCategory.RECOVERY, 0.82)], urgency=0.6)

    ensured = _ensure_minimum_recommendations(
        ranked_recommendations=ranked,
        urgency=0.6,
        recommendation_ranker=rank_recommendations,
    )

    assert len(ensured) == 2
    assert ensured[0].rec_id == "r1"
    assert ensured[1].rec_id == "maintain_progression"
    assert ensured[1].priority == 2
    assert ensured[1].confidence > 0.0


def test_minimum_recommendations_returns_two_fallbacks_when_zero() -> None:
    ensured = _ensure_minimum_recommendations(
        ranked_recommendations=[],
        urgency=0.5,
        recommendation_ranker=rank_recommendations,
    )

    assert len(ensured) == 2
    assert all(rec.rec_id for rec in ensured)
    assert all(rec.confidence > 0.0 for rec in ensured)
    assert [rec.priority for rec in ensured] == [1, 2]
