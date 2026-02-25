# Context Engine (V3)

## Purpose

The Context Engine modulates interpretation parameters based on contextual state while keeping Stratify deterministic and explainable.

It does not:
- change raw signals
- disable scoring
- override core strategy/rule outputs

## Module Layout

- `core/context/base.py`
- `core/context/registry.py`
- `core/context/cycle_context.py`

## Interface

`BaseContext.apply(...) -> ContextResult`

`ContextResult` includes:
- `modulated_thresholds`
- `penalty_scalars`
- `tolerance_adjustments`
- `context_applied`
- `context_notes`
- `context_version`
- `context_metadata`

## Cycle Context (First Plugin)

Supported phases:
- menstrual
- follicular
- ovulatory
- luteal

Current rules:
- luteal:
- widen volatility tolerance (`max_volatility * 1.15`, bounded)
- soften recovery threshold (`min_recovery - 0.03`, bounded)
- reduce urgency scale (`priority_score_scale = 0.95`)
- menstrual:
- soften recovery threshold (`min_recovery - 0.05`, bounded)
- reduce urgency scale (`priority_score_scale = 0.95`)
- follicular/ovulatory:
- no threshold changes in current version

Version marker:
- `context_version = ctx_v1`

## Persistence Contract

Inputs:
- `context_inputs` table stores context entries (date, type, payload).

Outputs:
- `decision_runs.context_applied`
- `decision_runs.context_version`
- `decision_runs.context_json`
- trace JSON fields:
- `context_applied`
- `context_notes`
- `context_version`
- `context_json`

## UI Touchpoints

- `Goal Setup` remains goal-only.
- `Log Input` captures cycle context (phase/day/symptom load).
- `Decision Dashboard` shows context summary, notes, and modulation details.

## Extensibility

Future plugins can use same interface:
- sleep disruption
- illness
- injury
- travel stress

New plugins must preserve deterministic and bounded behavior.
