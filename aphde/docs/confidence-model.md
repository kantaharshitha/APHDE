# Confidence Model

## Purpose

V2 introduces deterministic reliability modeling for decision outputs without ML.

It quantifies:
- alignment confidence (0..1)
- recommendation confidence (per recommendation)

## Inputs

From decision runtime:
- computed `SignalBundle`
- current strategy deviations
- recommendation list
- optional threshold-distance values
- optional historical decision context
- available vs required window coverage
- optional previous alignment confidence

## Components

1. Data completeness: ratio of available signal sufficiency flags.
2. Signal stability: inverse of normalized volatility.
3. Threshold distance strength: stronger threshold separation yields higher confidence.
4. Historical persistence: deviation pattern consistency across recent runs.
5. Window sufficiency: available lookback / required lookback.

All components are clamped to `[0,1]`.

## Weighted Aggregation

Default weights (`conf_v1`):
- data completeness: 0.30
- signal stability: 0.20
- threshold distance: 0.20
- historical persistence: 0.20
- window sufficiency: 0.10

`C_raw = sum(weight_i * component_i)`

## Smoothing

When previous confidence is available:

`C = clamp(alpha * C_prev + (1 - alpha) * C_raw, 0, 1)`

Current default: `alpha = 0.2`.

## Recommendation Confidence

For each recommendation:
- uses alignment confidence
- reason-code evidence strength
- specificity and conflict penalty
- base recommendation confidence field

Output is deterministic and clamped to `[0,1]`.

## Persistence and Trace

Persisted in `decision_runs`:
- `alignment_confidence`
- `recommendation_confidence_json`
- `confidence_breakdown_json`
- `confidence_version`

Trace includes:
- alignment confidence
- recommendation confidence
- component breakdown
- confidence notes
- confidence version

## Versioning

Confidence model version is independent of decision engine version.

- Decision logic: `engine_version`
- Confidence logic: `confidence_version`

Any coefficient/formula change requires `confidence_version` increment.
