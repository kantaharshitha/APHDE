def build_trace(input_summary: dict, computed_signals: dict, score_breakdown: dict) -> dict:
    return {
        "input_summary": input_summary,
        "computed_signals": computed_signals,
        "score_breakdown": score_breakdown,
    }
