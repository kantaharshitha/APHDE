from __future__ import annotations

from pathlib import Path
import re


FORBIDDEN_ENGINE_TERMS = ("weight", "calorie", "workout", "recovery", "cycle")
FORBIDDEN_ENGINE_IMPORTS = ("domains.", "core.signals", "core.strategies")
FORBIDDEN_SERVICE_IMPORTS = ("domains.health", "HealthDomainDefinition")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def collect_issues(repo_root: Path) -> list[str]:
    issues: list[str] = []
    core_dir = repo_root / "core"
    engine_dir = core_dir / "engine"
    service_file = core_dir / "services" / "run_evaluation.py"

    for path in sorted(engine_dir.glob("*.py")):
        text = _read_text(path)
        for term in FORBIDDEN_ENGINE_TERMS:
            if term in text:
                issues.append(f"{path}: forbidden core/engine term '{term}'")
        for imp in FORBIDDEN_ENGINE_IMPORTS:
            if imp in text:
                issues.append(f"{path}: forbidden core/engine import fragment '{imp}'")

    if service_file.exists():
        service_text = _read_text(service_file)
        for imp in FORBIDDEN_SERVICE_IMPORTS:
            if re.search(re.escape(imp.lower()), service_text):
                issues.append(f"{service_file}: forbidden core/service dependency '{imp}'")

    return issues


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    issues = collect_issues(repo_root)
    if issues:
        print("Architecture boundary violations found:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Architecture boundary checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
