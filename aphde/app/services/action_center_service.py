from __future__ import annotations

from typing import Any

from app.services.dashboard_service import load_dashboard_data
from core.guidance.tomorrow_plan import build_tomorrow_plan


def load_action_center_view(*, user_id: int, db_path: str, recent_limit: int = 28) -> dict[str, Any]:
    data = load_dashboard_data(user_id=user_id, db_path=db_path, recent_limit=recent_limit)
    latest = data.get("latest")
    recent_runs = data.get("recent_runs", [])

    if latest is None:
        return {
            "latest": None,
            "tomorrow_plan": None,
            "risk_alert": None,
            "recent_runs": recent_runs,
        }

    plan = build_tomorrow_plan(latest_run=latest, recent_runs=recent_runs)
    trace = latest.get("trace", {}) if isinstance(latest.get("trace"), dict) else {}
    rules = trace.get("triggered_rules", [])
    risk_alert = None
    if rules:
        risk_alert = {
            "severity": "high" if len(rules) >= 4 else "medium",
            "message": f"{len(rules)} risk rule(s) active in the latest run.",
            "rules": rules,
        }

    return {
        "latest": latest,
        "tomorrow_plan": plan,
        "risk_alert": risk_alert,
        "recent_runs": recent_runs,
    }
