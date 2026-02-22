from __future__ import annotations

from core.models.entities import Recommendation


def recommendation_to_dict(rec: Recommendation) -> dict:
    return {
        "id": rec.rec_id,
        "priority": rec.priority,
        "category": rec.category.value,
        "action": rec.action,
        "expected_effect": rec.expected_effect,
        "reason_codes": rec.reason_codes,
        "confidence": rec.confidence,
    }


def recommendations_to_dicts(recommendations: list[Recommendation]) -> list[dict]:
    return [recommendation_to_dict(rec) for rec in recommendations]
