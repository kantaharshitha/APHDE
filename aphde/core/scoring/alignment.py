def compute_alignment_score(penalties: list[float], base_score: float = 100.0) -> float:
    score = base_score - sum(penalties)
    return max(0.0, min(100.0, score))
