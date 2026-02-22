# Decision Rules

## Pipeline

1. Build `SignalBundle` from recent logs.
2. Execute active goal strategy (`evaluate` + `recommend`).
3. Apply cross-cutting risk rules.
4. Rank recommendations by deterministic weighted score.
5. Build score breakdown penalties and compute alignment/risk scores.
6. Build structured trace and persist decision run.

## Cross-Cutting Risk Rules

Implemented in `core/decision/rules.py`:
- `RECOVERY_DROP` when `recovery_index < 0.45`
- `COMPLIANCE_DROP` when `compliance_ratio < 0.65`
- `VOLATILITY_SPIKE` when `volatility_index > 0.10`
- `STALL_RISK` when `progressive_overload_score < 0.50`

## Recommendation Ranking

Implemented in `core/decision/ranker.py`:

`priority_score = impact_weight * impact + urgency_weight * urgency + confidence_weight * confidence - effort_weight * effort`

Current defaults:
- `impact_weight = 0.40`
- `urgency_weight = 0.20`
- `confidence_weight = 0.35`
- `effort_weight = 0.15`

Category priors:
- Impact: training `0.90`, nutrition `0.85`, recovery `0.75`, habit `0.70`
- Effort: training `0.60`, nutrition `0.50`, recovery `0.35`, habit `0.40`

## Composite Alignment Score

Implemented in `core/scoring/breakdown.py` + `core/scoring/alignment.py`.

Penalty components:
- `goal_adherence_penalty = 35 * priority_score`
- `risk_penalty = min(25, 6 * risk_count)`
- `uncertainty_penalty = min(10, 2 * missing_signal_count)`
- `recovery_risk_penalty = 20 * priority_score`
- `stability_penalty = 10 * priority_score`

Final score:
- `alignment_score = clamp(100 - sum(penalties), 0, 100)`
- `risk_score = 100 - alignment_score`

## Explainability Contract

Each decision run stores:
- input summary (counts + active goal)
- computed signal values + sufficiency map
- applied strategy name
- triggered rules
- score breakdown
- recommendation ranking trace
- confidence notes
- engine version

This supports deterministic replay and interview-grade reasoning audit.
