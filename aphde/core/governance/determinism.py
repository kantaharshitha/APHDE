from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.governance.hashing import canonical_sha256


@dataclass(slots=True)
class DeterminismResult:
    input_signature_hash: str
    output_hash: str
    determinism_verified: bool | None
    determinism_reason: str


def verify_determinism(
    *,
    input_signature_payload: dict[str, Any],
    output_payload: dict[str, Any],
    baseline_output_payload: dict[str, Any] | None = None,
) -> DeterminismResult:
    input_signature_hash = canonical_sha256(input_signature_payload)
    output_hash = canonical_sha256(output_payload)

    if baseline_output_payload is None:
        return DeterminismResult(
            input_signature_hash=input_signature_hash,
            output_hash=output_hash,
            determinism_verified=None,
            determinism_reason="NO_BASELINE",
        )

    baseline_hash = canonical_sha256(baseline_output_payload)
    matches = baseline_hash == output_hash
    return DeterminismResult(
        input_signature_hash=input_signature_hash,
        output_hash=output_hash,
        determinism_verified=matches,
        determinism_reason="MATCH" if matches else "MISMATCH",
    )
