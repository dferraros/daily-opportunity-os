"""Pipeline health monitor -- logs failures to data/pipeline_failures.jsonl."""

import json
import os
from datetime import datetime


def get_project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(Path(__file__).resolve().parent.parent.parent)


def _failures_path() -> str:
    return os.path.join(get_project_root(), "data", "pipeline_failures.jsonl")


def log_failure(step: str, error: Exception, opp_id: str = "unknown", recovered: bool = True) -> None:
    """Append a failure record to pipeline_failures.jsonl."""
    path = _failures_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = {
        "date": datetime.now().isoformat(),
        "step": step,
        "error_type": type(error).__name__,
        "error_msg": str(error)[:500],
        "opp_id": opp_id,
        "recovered": recovered,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    print(f"WARNING  [{step}] {type(error).__name__}: {str(error)[:200]} (opp: {opp_id})")


def read_failures() -> list:
    """Read all failure records from pipeline_failures.jsonl."""
    path = _failures_path()
    if not os.path.exists(path):
        return []
    failures = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    failures.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return failures


def audit_report() -> str:
    """Generate a human-readable audit report of pipeline failures."""
    failures = read_failures()
    if not failures:
        return "No pipeline failures recorded. Clean run history."

    from collections import Counter
    by_step = Counter(f["step"] for f in failures)
    by_type = Counter(f["error_type"] for f in failures)
    total = len(failures)

    lines = [
        f"Pipeline Failure Audit ({total} total failures)",
        "=" * 50,
        "",
        "Failures by step:",
    ]
    for step, count in by_step.most_common():
        last_error = next(
            (f["error_msg"] for f in reversed(failures) if f["step"] == step), "N/A"
        )
        lines.append(f"  {step:30s} {count:4d} failures | Last: {last_error[:80]}")

    lines.append("")
    lines.append("Failures by error type:")
    for err_type, count in by_type.most_common():
        lines.append(f"  {err_type:30s} {count:4d}")

    recovered = sum(1 for f in failures if f.get("recovered"))
    lines.append(f"\nRecovery rate: {recovered}/{total} ({recovered/total*100:.0f}%)")
    return "\n".join(lines)
