from __future__ import annotations

from collections.abc import Sequence


def linear_regression_slope(values: Sequence[float]) -> float | None:
    """Return slope for equally spaced points x=[0..n-1], or None if insufficient data."""
    n = len(values)
    if n < 2:
        return None

    x_sum = n * (n - 1) / 2
    xx_sum = (n - 1) * n * (2 * n - 1) / 6
    y_sum = sum(values)
    xy_sum = sum(i * y for i, y in enumerate(values))

    denominator = n * xx_sum - x_sum * x_sum
    if denominator == 0:
        return None
    return (n * xy_sum - x_sum * y_sum) / denominator
