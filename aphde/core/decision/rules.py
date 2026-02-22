from __future__ import annotations

from core.models.enums import RiskCode
from core.signals.aggregator import SignalBundle


def detect_additional_risks(signals: SignalBundle) -> list[str]:
    risks: list[str] = []
    if signals.recovery_index is not None and signals.recovery_index < 0.45:
        risks.append(RiskCode.RECOVERY_DROP.value)
    if signals.compliance_ratio is not None and signals.compliance_ratio < 0.65:
        risks.append(RiskCode.COMPLIANCE_DROP.value)
    if signals.volatility_index is not None and signals.volatility_index > 0.10:
        risks.append(RiskCode.VOLATILITY_SPIKE.value)
    if signals.progressive_overload_score is not None and signals.progressive_overload_score < 0.5:
        risks.append(RiskCode.STALL_RISK.value)
    return sorted(set(risks))
