from __future__ import annotations

from collections.abc import Sequence
from statistics import pstdev


def coefficient_of_variation(values: Sequence[float]) -> float | None:
    """
    Return stddev/mean for a numeric series.
    Returns None when data is insufficient or mean is near zero.
    """
    n = len(values)
    if n < 2:
        return None

    mean = sum(values) / n
    if abs(mean) < 1e-9:
        return None

    return pstdev(values) / abs(mean)
