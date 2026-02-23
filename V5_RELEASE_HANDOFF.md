# APHDE V5 Release Handoff

## Release
- Tag: `v5.0.0`
- Release theme: Governance, Reproducibility, Observability

## Included Capabilities
- Governance layer (`core/governance/*`)
- Deterministic hashing and verification metadata:
  - `input_signature_hash`
  - `output_hash`
  - `determinism_verified`
  - `governance_json`
- Version diff utilities for run-to-run comparison
- History analyzer for alignment/confidence/context/rule analytics
- Governance panel in dashboard (hash, determinism status, diff view, history summary)

## Validation Evidence
Run these from `aphde/`:

```bash
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\check_architecture_boundaries.py
.venv\Scripts\python.exe -m scripts.run_demo_scenarios
```

Expected:
- test suite passes
- architecture boundaries pass
- scenario outputs print successfully including context/no-context comparison

## Demo Checklist
1. Start Streamlit:
```bash
.venv\Scripts\python.exe -m streamlit run app/main.py
```
2. Open `Decision Dashboard`.
3. Run evaluation.
4. Verify governance block:
- determinism status
- output hash
- input signature hash
- domain/version metadata
5. Compare two runs in Version Diff Viewer.
6. Review History Analytics summary.

## Notes
- V5 does not change scoring, confidence, or context formulas.
- V5 is a maturity layer; core decision behavior remains deterministic and parity-tested.
