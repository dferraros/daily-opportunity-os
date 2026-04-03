---
id: 06-02H
wave: 2
depends_on: [06-01D]
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
  - src/opportunity_os/main.py
autonomous: true
---

# Plan 06-02H: Quota Tracking from Config File

## Goal

Read weekly quotas from `config/weekly_quotas.yaml` instead of hardcoded values. Track actual counts per daily run and append progress to `data/machine_metrics.jsonl`. Show weekly quota progress in `opp-os stats`.

## must_haves

- [ ] daily_run.py reads `config/weekly_quotas.yaml` at end of run
- [ ] Daily run appends quota progress to `data/machine_metrics.jsonl`
- [ ] `opp-os stats` shows weekly quota progress line: "This week: X/40 signals, Y/10 opps, Z/3 deep dives"
- [ ] Quota targets come from config file, not hardcoded values
- [ ] weekly_run.py quota_status reads from config file too

## Tasks

<task id="1">
<title>Add quota progress tracking to end of daily_run.py</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find the end of the run_daily function -- around line 430-435 where summary is returned)
- config/weekly_quotas.yaml (exact structure: weekly_quotas.signals_ingested.target=40, structured_opportunities.target=10, deep_dives_produced.target=3, validations_run.target=2)
- src/opportunity_os/storage.py (see append_machine_metrics function at line ~253)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`, BEFORE the `return summary` statement at the end of `run_daily()`:

1. Add a quota tracking block:
   ```python
   # Step 15: Track quota progress from config
   try:
       import yaml
       config_path = os.path.join(root, "config", "weekly_quotas.yaml")
       with open(config_path, "r", encoding="utf-8") as f:
           quotas_config = yaml.safe_load(f)
       quotas = quotas_config.get("weekly_quotas", {})

       from opportunity_os.storage import append_machine_metrics
       metrics = {
           "date": date,
           "run_type": "daily",
           "signals_ingested": len(raw_signals),
           "opportunities_scored": summary["scored"],
           "opportunities_killed": summary["killed"],
           "deep_dives_produced": 0,  # counted separately
           "validations_run": len(validation_packages_for_sync) if validation_packages_for_sync else 0,
           "quota_targets": {
               "signals": quotas.get("signals_ingested", {}).get("target", 40),
               "opps": quotas.get("structured_opportunities", {}).get("target", 10),
               "deep_dives": quotas.get("deep_dives_produced", {}).get("target", 3),
               "validations": quotas.get("validations_run", {}).get("target", 2),
           },
       }
       append_machine_metrics(metrics)
       print(f"Step 15: Quota progress tracked (signals: {metrics['signals_ingested']}, opps: {metrics['opportunities_scored']})")
   except Exception as e:
       log_failure("quota_tracking", e)
   ```

2. Also update the weekly_run.py `quota_status` section (around line 46-55) to read from config:
   This is actually in 06-02H Task 2 scope -- see below.
</action>
<acceptance_criteria>
- grep "Step 15" src/opportunity_os/pipelines/daily_run.py returns a match
- grep "weekly_quotas.yaml" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- grep "append_machine_metrics" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- grep "quota_targets" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Add weekly quota progress to opp-os stats command</title>
<read_first>
- src/opportunity_os/main.py (see `stats` command at line ~119-173)
- config/weekly_quotas.yaml (exact target values)
- src/opportunity_os/storage.py (see append_machine_metrics and _default_metrics_path for reading metrics)
</read_first>
<action>
In `src/opportunity_os/main.py`, update the `stats` command to show weekly quota progress:

1. After the existing stats output (around line 169, before the final `if not all_opps:` block), add:

   ```python
   # Weekly quota progress
   try:
       import yaml
       from pathlib import Path
       project_root = Path(__file__).resolve().parent.parent.parent
       config_path = project_root / "config" / "weekly_quotas.yaml"
       metrics_path = project_root / "data" / "machine_metrics.jsonl"

       if config_path.exists():
           with open(config_path, "r") as f:
               quotas = yaml.safe_load(f).get("weekly_quotas", {})

           # Count this week's metrics from machine_metrics.jsonl
           from datetime import timedelta
           week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
           week_signals = 0
           week_opps = 0
           week_deep_dives = 0
           week_validations = 0

           if metrics_path.exists():
               import json
               with open(metrics_path, "r") as f:
                   for line in f:
                       line = line.strip()
                       if not line:
                           continue
                       try:
                           m = json.loads(line)
                           if m.get("date", "") >= week_start:
                               week_signals += m.get("signals_ingested", 0)
                               week_opps += m.get("opportunities_scored", 0)
                               week_deep_dives += m.get("deep_dives_produced", 0)
                               week_validations += m.get("validations_run", 0)
                       except json.JSONDecodeError:
                           continue

           sig_target = quotas.get("signals_ingested", {}).get("target", 40)
           opp_target = quotas.get("structured_opportunities", {}).get("target", 10)
           dd_target = quotas.get("deep_dives_produced", {}).get("target", 3)
           val_target = quotas.get("validations_run", {}).get("target", 2)

           click.echo(f"\n Weekly quotas (since {week_start}):")
           click.echo(f"   Signals:     {week_signals}/{sig_target}")
           click.echo(f"   Opps scored: {week_opps}/{opp_target}")
           click.echo(f"   Deep dives:  {week_deep_dives}/{dd_target}")
           click.echo(f"   Validations: {week_validations}/{val_target}")
   except Exception:
       pass  # quota display is non-critical
   ```
</action>
<acceptance_criteria>
- grep "Weekly quotas" src/opportunity_os/main.py returns a match
- grep "weekly_quotas.yaml" src/opportunity_os/main.py returns at least 1 match
- grep "sig_target" src/opportunity_os/main.py returns a match
- grep "week_signals" src/opportunity_os/main.py returns at least 2 matches
- PYTHONPATH=src uv run python -m opportunity_os.main stats succeeds (shows quota section even if all zeros)
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
PYTHONPATH=src uv run python -m opportunity_os.main stats
# Should show "Weekly quotas" section with X/40 signals, Y/10 opps, etc.
```
