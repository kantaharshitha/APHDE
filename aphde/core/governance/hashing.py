from __future__ import annotations

import hashlib
import json
from typing import Any


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, float):
        # Keep stable persisted precision across runs.
        return round(value, 8)
    return value


def canonical_json(value: Any) -> str:
    normalized = _normalize(value)
    return json.dumps(normalized, separators=(",", ":"), sort_keys=True)


def canonical_sha256(value: Any) -> str:
    payload = canonical_json(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
