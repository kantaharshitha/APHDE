# V5 Release Notes

## Release

Stratify V5 introduces governance, reproducibility, and observability capabilities while preserving deterministic decision behavior.

## What Changed

1. Governance core module added:
- `core/governance/hashing.py`
- `core/governance/determinism.py`
- `core/governance/version_diff.py`
- `core/governance/history_analyzer.py`

2. Persistence and migration updates:
- `decision_runs` now stores:
  - `input_signature_hash`
  - `output_hash`
  - `determinism_verified`
  - `governance_json`
- migration added:
  - `core/data/migrations/migrate_v5_governance.py`

3. Evaluation lifecycle integration:
- `run_evaluation` now computes and persists governance metadata.
- trace now includes a `governance` block.

4. Dashboard observability panel:
- determinism status
- output hash and input signature hash
- run diff viewer
- history analytics summary

5. Test hardening:
- governance unit tests
- migration tests
- integration tests for governance persistence/diff/history

## Behavior Guarantees

- No ML introduced.
- No predictive analytics introduced.
- No scoring/confidence/context formula changes.
- V4 behavior parity preserved for core decision outputs.

## Validation

- Test suite passing.
- Architecture boundary checks passing.
- Demo scenarios still reproducible.
