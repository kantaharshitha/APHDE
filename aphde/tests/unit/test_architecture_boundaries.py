from pathlib import Path

from scripts.check_architecture_boundaries import collect_issues


def test_architecture_boundaries_hold() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    issues = collect_issues(repo_root)
    assert issues == []
