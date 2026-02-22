def build_trace(
    *,
    input_summary: dict,
    computed_signals: dict,
    strategy_name: str,
    triggered_rules: list[str],
    score_breakdown: dict,
    recommendation_ranking_trace: list[dict],
    confidence_notes: list[str],
    engine_version: str,
) -> dict:
    return {
        "input_summary": input_summary,
        "computed_signals": computed_signals,
        "goal_strategy_applied": strategy_name,
        "triggered_rules": triggered_rules,
        "score_breakdown": score_breakdown,
        "recommendation_ranking_trace": recommendation_ranking_trace,
        "confidence_notes": confidence_notes,
        "engine_version": engine_version,
    }
