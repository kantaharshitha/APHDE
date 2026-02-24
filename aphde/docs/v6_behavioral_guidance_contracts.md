# V6 Behavioral Guidance Contracts

This document defines the deterministic payload contracts introduced in V6.

## Tomorrow Plan Contract

Produced by: `core/guidance/tomorrow_plan.py`  
Service adapter: `app/services/action_center_service.py`

```json
{
  "action_id": "string",
  "action": "string",
  "reason": "string",
  "confidence": 0.0,
  "severity": "low|medium|high",
  "expected_impact": "string",
  "priority_score": 0.0
}
```

Notes:
- Deterministic tie-break: priority score desc, then recommendation priority asc, then action_id asc.
- No predictive or generative logic.

## Risk Alert Contract (Action Center)

```json
{
  "severity": "medium|high",
  "message": "string",
  "rules": ["RULE_A", "RULE_B"]
}
```

## Stagnation Alert Contract

Produced by: `core/insights/stagnation.py`

```json
{
  "alert_id": "string",
  "type": "string",
  "severity": "low|medium|high",
  "message": "string",
  "recommendation": "string",
  "confidence": 0.0,
  "triggered_at": "YYYY-MM-DD",
  "version": "stg_v1"
}
```

## Weekly Insight Contract

Produced by: `core/insights/weekly_summary.py`

```json
{
  "week_start": "YYYY-MM-DD",
  "week_end": "YYYY-MM-DD",
  "planned_sessions": 7,
  "completed_sessions": 6,
  "compliance_pct": 85.71,
  "compliance_avg_pct": 83.20,
  "recovery_shift": "up|down|flat",
  "volatility_direction": "improving|worsening|flat",
  "overload_progress": "up|down|flat",
  "data_sufficient": true
}
```

## Trend Payload Contract

Produced by: `core/insights/trend_views.py`  
Service adapter: `app/services/insights_service.py`

```json
{
  "values": [1.0, 2.0, 3.0],
  "count": 3,
  "slope": 1.0
}
```

Exposed trend groups:
- `weight`
- `recovery`
- `compliance`
- `overload`

## Service Output Contracts

### `load_action_center_view(...)`

```json
{
  "latest": {},
  "tomorrow_plan": {},
  "risk_alert": {},
  "recent_runs": []
}
```

### `load_insights_view(...)`

```json
{
  "latest": {},
  "weekly_insight": {},
  "stagnation_alerts": [],
  "drift_detection": {},
  "trends": {},
  "recent_runs": []
}
```

## Determinism Requirements

- Identical persisted inputs must produce identical Tomorrow Plan and insight outputs.
- No stochastic operations, no external model calls, and no hidden state.
