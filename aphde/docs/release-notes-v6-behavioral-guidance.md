# Release Notes: v6.0.0 Behavioral Guidance Layer

## Summary
V6 introduces a deterministic Behavioral Guidance Layer and separates user experience into operational, guidance, and analytical pages.

## Page Architecture
- **Decision Dashboard** (`app/pages/03_decision_dashboard.py`)
  - operational snapshot only
  - alignment/confidence/risk/context + top recommendation + signals/context summary
- **Action Center** (`app/pages/04_action_center.py`)
  - single deterministic Tomorrow Plan
  - confidence/severity/impact reasoning
  - optional active-risk alert
- **Insights & Trends** (`app/pages/05_insights_trends.py`)
  - weekly insights summary
  - stagnation alerts
  - drift detection
  - trend charts (weight/recovery/compliance/overload)

## New Deterministic Modules
- `core/guidance/tomorrow_plan.py`
- `core/insights/stagnation.py`
- `core/insights/weekly_summary.py`
- `core/insights/trend_views.py`

## New App Service Adapters
- `app/services/action_center_service.py`
- `app/services/insights_service.py`

## Contracts and Documentation
- `docs/v6_behavioral_guidance_contracts.md`
- `IMPLEMENTATION_PLAN_APHDE_V6_BEHAVIORAL_GUIDANCE.md`
- `PRD_APHDE_V6_BEHAVIORAL_GUIDANCE.md`

## Testing Additions
- `tests/integration/test_action_center_service.py`
- `tests/integration/test_insights_service.py`
- `tests/unit/test_stagnation.py`
- `tests/unit/test_weekly_summary.py`

## Validation
- Deterministic architecture preserved.
- Existing evaluation flows remain unchanged.
- New guidance/insight modules are deterministic and test-covered.

## Compatibility
- No database schema changes.
- No scoring formula changes.
- No ML or predictive modeling introduced.
