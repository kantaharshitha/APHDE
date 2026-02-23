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
- Recommendation focus shifts to training distribution and overload structure.
- Alignment score should be moderate.

## Scenario 3: Strength Gain with Fatigue Accumulation

Expected behavior:
- Trigger recovery-related risks.
- Recommend intensity/volume sequencing changes.
- Risk score rises despite regular training activity.

## Scenario 4: Context Comparison (No Context vs Luteal)

Expected behavior:
- Core signals remain unchanged.
- Context-enabled run shows:
- `context_applied = true`
- `context_version = ctx_v1`
- context notes + modulation JSON
- Alignment score may shift slightly due to context-scaled interpretation.

## Quick Run

```bash
cd aphde
.venv\Scripts\python.exe scripts\run_demo_scenarios.py
```

The script prints scores, triggered rules, confidence, and context metadata.

## UI Demo Walkthrough

```bash
cd aphde
.venv\Scripts\python.exe -m streamlit run app/main.py
```

1. Open `Goal Setup` and set `Weight Loss`.
2. Open `Log Input` and add workout/weight logs.
3. Save cycle phase `luteal` in `Cycle Context`.
4. Open `Decision Dashboard` and run evaluation.
5. Confirm context diagnostics show applied state and modulation details.
