from core.governance.determinism import verify_determinism
from core.governance.hashing import canonical_json, canonical_sha256
from core.governance.history_analyzer import summarize_history
from core.governance.version_diff import diff_runs


def test_canonical_hash_is_stable_for_reordered_dicts() -> None:
    payload_a = {"b": 2, "a": {"y": 2, "x": 1}}
    payload_b = {"a": {"x": 1, "y": 2}, "b": 2}
    assert canonical_json(payload_a) == canonical_json(payload_b)
    assert canonical_sha256(payload_a) == canonical_sha256(payload_b)


def test_verify_determinism_without_baseline_marks_no_baseline() -> None:
    result = verify_determinism(
        input_signature_payload={"goal_type": "weight_loss"},
        output_payload={"alignment_score": 70.0},
        baseline_output_payload=None,
    )
    assert result.determinism_verified is None
    assert result.determinism_reason == "NO_BASELINE"


def test_verify_determinism_detects_match_and_mismatch() -> None:
    match = verify_determinism(
        input_signature_payload={"goal_type": "weight_loss"},
        output_payload={"alignment_score": 70.0},
        baseline_output_payload={"alignment_score": 70.0},
    )
    mismatch = verify_determinism(
        input_signature_payload={"goal_type": "weight_loss"},
        output_payload={"alignment_score": 70.0},
        baseline_output_payload={"alignment_score": 69.9},
    )
    assert match.determinism_verified is True
    assert match.determinism_reason == "MATCH"
    assert mismatch.determinism_verified is False
    assert mismatch.determinism_reason == "MISMATCH"


def test_version_diff_returns_expected_delta_structure() -> None:
    run_a = {
        "alignment_score": 70.0,
        "risk_score": 30.0,
        "alignment_confidence": 0.72,
        "recommendations": [{"id": "rec_a", "priority": 1}],
        "context_applied": False,
        "context_version": "ctx_v1",
    }
    run_b = {
        "alignment_score": 72.0,
        "risk_score": 28.0,
        "alignment_confidence": 0.75,
        "recommendations": [{"id": "rec_b", "priority": 1}],
        "context_applied": True,
        "context_version": "ctx_v1",
    }
    diff = diff_runs(run_a, run_b)
    assert diff["score_delta"]["alignment_score_delta"] == 2.0
    assert diff["recommendation_changes"]["added"] == ["rec_b"]
    assert diff["recommendation_changes"]["removed"] == ["rec_a"]
    assert diff["context_changes"]["context_applied_from"] is False
    assert diff["context_changes"]["context_applied_to"] is True


def test_history_analyzer_builds_trends_and_frequencies() -> None:
    runs = [
        {
            "alignment_score": 70.0,
            "alignment_confidence": 0.72,
            "context_applied": False,
            "triggered_rules": ["RECOVERY_DROP"],
            "determinism_verified": None,
        },
        {
            "alignment_score": 71.0,
            "alignment_confidence": 0.74,
            "context_applied": True,
            "triggered_rules": ["RECOVERY_DROP", "STALL_RISK"],
            "determinism_verified": True,
        },
    ]
    summary = summarize_history(runs)
    assert summary["count"] == 2
    assert summary["alignment_trend"] == [70.0, 71.0]
    assert summary["confidence_trend"] == [0.72, 0.74]
    assert summary["context_application_frequency"] == 0.5
    assert summary["rule_trigger_distribution"]["RECOVERY_DROP"] == 2
    assert summary["determinism_pass_rate"] == 1.0
