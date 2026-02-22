# Demo Scenarios

Use these scenarios to present APHDE end-to-end.

## Scenario 1: Weight Loss Drift + Low Adherence

Expected behavior:
- Trigger `STALL_RISK`, `COMPLIANCE_DROP`, and likely `RECOVERY_DROP`.
- Recommend calorie adherence structure and minor deficit adjustment.
- Alignment score should drop below neutral band.

## Scenario 2: Recomposition with Good Compliance but Poor Balance

Expected behavior:
- Lower risk count than Scenario 1.
- Recommendation focus should shift to training distribution and overload structure.
- Alignment score should be moderate.

## Scenario 3: Strength Gain with Fatigue Accumulation

Expected behavior:
- Trigger recovery-related risks.
- Recommend intensity/volume sequencing changes.
- Risk score increases despite regular training activity.

## Quick Run

```bash
cd aphde
.venv\Scripts\python.exe scripts\run_demo_scenarios.py
```

The script prints scenario-level scores, triggered rules, and top recommendations.
