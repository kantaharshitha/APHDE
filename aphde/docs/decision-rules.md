# Decision Rules

## Pipeline (V3)

1. Build `SignalBundle` from recent logs.
2. Execute active goal strategy (`evaluate` + `recommend`).
3. Apply context modulation (if context input exists).
4. Apply cross-cutting risk rules.
5. Rank recommendations by deterministic weighted score.
6. Build score breakdown and compute alignment/risk scores.
7. Compute confidence outputs (alignment + recommendation-level).
8. Build trace payload and persist decision run.

## Cross-Cutting Risk Rules

Implemented in `core/decision/rules.py`:
- `RECOVERY_DROP` when `recovery_index < 0.45`
- `COMPLIANCE_DROP` when `compliance_ratio < 0.65`
- `VOLATILITY_SPIKE` when `volatility_index > 0.10`
- `STALL_RISK` when `progressive_overload_score < 0.50`

## Context Modulation Rules (Cycle Plugin)

Implemented in `core/context/cycle_context.py`.

Supported phases:
- `menstrual`
- `follicular`
- `ovulatory`
- `luteal`

Current deterministic modulation:
- `luteal`
- widen `max_volatility` by `+15%` (bounded)
- soften `min_recovery` by `-0.03` (bounded)
- apply `priority_score_scale = 0.95`
- `menstrual`
- soften `min_recovery` by `-0.05` (bounded)
- apply `priority_score_scale = 0.95`
- `follicular` / `ovulatory`
- currently no threshold shifts

Guardrails:
- No raw signal mutation.
- No rule suppression.
- Unsupported context type is ignored with trace note.

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

## Deterministic Confidence Model

Implemented in `core/scoring/confidence.py`.

Outputs:
- `alignment_confidence (0..1)`
- `recommendation_confidence[]`
- `confidence_breakdown`
- `confidence_notes`
- `confidence_version`

Components (weighted, bounded):
- data completeness
- signal stability
- threshold distance strength
- historical persistence
- window sufficiency

Smoothing:
- `C = clamp(alpha * C_prev + (1 - alpha) * C_raw, 0, 1)`

## Explainability Contract

Each decision run stores:
- input summary
- computed signals + sufficiency + deviations
- strategy name
- triggered rules
- score breakdown
- recommendation ranking trace
- confidence outputs
- context outputs (`context_applied`, `context_notes`, `context_version`, `context_json`)
- version triad (`engine_version`, `confidence_version`, `context_version`)

This supports deterministic replay and interview-grade reasoning audits.
