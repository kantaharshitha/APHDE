from __future__ import annotations

from collections.abc import Iterable

from core.signals.trend import linear_regression_slope


def build_series_with_slope(values: Iterable[float]) -> dict[str, object]:
    points = [float(v) for v in values]
    slope = linear_regression_slope(points) if len(points) >= 2 else None
    return {
        "values": points,
        "count": len(points),
        "slope": round(float(slope), 6) if slope is not None else None,
    }
