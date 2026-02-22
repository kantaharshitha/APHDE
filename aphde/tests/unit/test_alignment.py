from core.scoring.alignment import compute_alignment_score


def test_compute_alignment_score_clamps_range() -> None:
    assert compute_alignment_score([200]) == 0.0
    assert compute_alignment_score([-20]) == 100.0
    assert compute_alignment_score([10, 15]) == 75.0
