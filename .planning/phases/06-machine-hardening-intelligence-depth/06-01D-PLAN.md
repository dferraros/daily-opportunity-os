---
id: 06-01D
wave: 1
depends_on: []
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
  - src/opportunity_os/pipeline_monitor.py
  - src/opportunity_os/main.py
autonomous: true
---

# Plan 06-01D: Pipeline Health Monitor -- Zero Silent Failures

## Goal

Replace all 12 silent `try/except: pass/continue` blocks in daily_run.py with failure logging to `data/pipeline_failures.jsonl`. Add `opp-os audit` CLI command to surface failure patterns.

## must_haves

- [ ] New `pipeline_monitor.py` module with `_log_failure(step, error, opp_id)` function
- [ ] All silent except blocks in daily_run.py call `_log_failure` instead of `pass`/`continue`
- [ ] Failures append to `data/pipeline_failures.jsonl` with `{date, step, error_type, error_msg, opp_id, recovered}`
- [ ] `opp-os audit` CLI command reads pipeline_failures.jsonl and shows failure rate by step
- [ ] Zero silent failures remain in daily_run.py

## Tasks

<task id="1">
<title>Create pipeline_monitor.py with failure logging</title>
<read_first>
- src/opportunity_os/storage.py (see get_project_root() and _ensure_dir() patterns for file path handling)
</read_first>
<action>
Create `src/opportunity_os/pipeline_monitor.py` with:

```python
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


def read_failures() -> list[dict]:
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
```
</action>
<acceptance_criteria>
- File src/opportunity_os/pipeline_monitor.py exists
- grep "def log_failure" src/opportunity_os/pipeline_monitor.py returns a match
- grep "def audit_report" src/opportunity_os/pipeline_monitor.py returns a match
- grep "pipeline_failures.jsonl" src/opportunity_os/pipeline_monitor.py returns at least 2 matches
- python -c "from opportunity_os.pipeline_monitor import log_failure, audit_report; print('OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Replace all silent except blocks in daily_run.py with log_failure calls</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find EVERY `except Exception as e:` or `except Exception as exc:` or `except ImportError as e:` block that ends with pass, continue, or just a print statement without logging)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`:

1. Add import at the top (after other imports, around line 5):
   ```python
   from opportunity_os.pipeline_monitor import log_failure
   ```

2. Find and replace EVERY except block that silently swallows errors. Current pattern:
   ```python
   except Exception as e:
       print(f"WARNING  ... error (non-blocking): {e}")
   ```
   Replace with:
   ```python
   except Exception as e:
       log_failure("step_name", e, opp_id="unknown")
   ```

   Specific replacements (match the step names to the actual step):
   - Step 2.5 (AI scoring, ~line 96): `log_failure("ai_scoring", exc)`
   - Step 9.5 (TAM estimation, ~line 163-164): `log_failure("tam_estimation", e)`
   - Step 9.7 (Benchmark mapping, ~line 179-180): `log_failure("benchmark_mapping", e)`
   - Step 10 (Pain OS, ~line 193-194): `log_failure("pain_os", e)`
   - Step 11 (Distribution OS, ~line 207-208): `log_failure("distribution_os", e)`
   - Step 11.5 (Research executor, ~line 222-223): `log_failure("research_executor", e)`
   - Step 11.8 (Pain library, ~line 237-238): `log_failure("pain_library", e)`
   - Step 12 (Save enriched, ~line 252-253): `log_failure("save_enriched", e)`
   - Step 13 (Notion sync, ~line 316): `log_failure("notion_sync", e)`
   - Step 14 pre-collect (~line 282): `log_failure("validation_pre_collect", e)`
   - Step 14 write (~line 338): `log_failure("validation_write", e)`
   - JSON parse error in Step 1 (~line 71): `log_failure("signal_parse", exc)`

   For `except ImportError as e:` blocks, keep those as-is (they indicate missing optional modules, not runtime failures).

3. For per-opportunity errors inside loops, pass the opp_id:
   ```python
   log_failure("step_name", e, opp_id=opp.get("id", "unknown"))
   ```
</action>
<acceptance_criteria>
- grep "from opportunity_os.pipeline_monitor import log_failure" src/opportunity_os/pipelines/daily_run.py returns a match
- grep -c "log_failure" src/opportunity_os/pipelines/daily_run.py returns at least 8
- grep "pass  #" src/opportunity_os/pipelines/daily_run.py returns 0 matches (no silent pass blocks left)
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

<task id="3">
<title>Add opp-os audit CLI command</title>
<read_first>
- src/opportunity_os/main.py (see existing CLI commands pattern -- click.group + @cli.command)
</read_first>
<action>
In `src/opportunity_os/main.py`, add a new CLI command after the `stats` command (before `if __name__ == "__main__":`):

```python
@cli.command()
def audit():
    """Show pipeline failure audit -- failure rates by step and error type."""
    from opportunity_os.pipeline_monitor import audit_report
    click.echo(audit_report())
```
</action>
<acceptance_criteria>
- grep "def audit" src/opportunity_os/main.py returns a match
- grep "audit_report" src/opportunity_os/main.py returns a match
- PYTHONPATH=src uv run python -m opportunity_os.main audit succeeds (may show "No pipeline failures recorded")
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
PYTHONPATH=src uv run python -m opportunity_os.main audit
# Should print either "No pipeline failures recorded" or a failure report
```
