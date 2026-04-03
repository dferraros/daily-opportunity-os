---
id: 06-01C
wave: 1
depends_on: []
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
  - src/opportunity_os/pipelines/weekly_run.py
autonomous: true
---

# Plan 06-01C: Deep Dive Auto-Trigger

## Goal

Auto-trigger deep dives on top opportunities: top 1 with score >= 8.0 in daily runs, top 3 with score >= 7.0 in weekly runs. Skip if deep dive already exists for that opp this week.

## must_haves

- [ ] Daily pipeline auto-triggers deep dive on top 1 opp with final_score >= 8.0
- [ ] Weekly pipeline auto-triggers deep dives on top 3 opps with final_score >= 7.0
- [ ] Deep dive outputs go to `reports/deep-dives/YYYY-MM-DD-{opp_id}.md`
- [ ] Existing deep dives for same opp this week are skipped (no duplicates)

## Tasks

<task id="1">
<title>Add Step 14.5: auto deep-dive in daily_run.py</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find the end of Step 14 -- auto-validation section, around line 338. The new step goes AFTER Step 14 and BEFORE the report rendering section)
- src/opportunity_os/pipelines/deep_dive.py (confirm `run_deep_dive(opp_id, dry_run)` signature)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`, add a new step AFTER Step 14 (auto-validation, around line 338) and BEFORE the "Render reports" section (around line 341):

```python
# --- Step 14.5: Auto deep-dive on top scorer >= 8.0 ---
print("Step 14.5: Checking for auto deep-dive candidates...")
try:
    from opportunity_os.pipelines.deep_dive import run_deep_dive
    deep_dive_candidates = [
        o for o in all_opps_sorted
        if float(o.get("final_score", 0)) >= 8.0
        and not o.get("kill_decision")
    ][:1]  # top 1 only
    for opp in deep_dive_candidates:
        opp_id = opp.get("id", "unknown")
        # Skip if deep dive already exists this week
        dd_path = os.path.join(
            root, "reports", "deep-dives", f"{date}-{opp_id[:40]}.md"
        )
        if os.path.exists(dd_path):
            print(f"  Deep dive already exists for {opp_id}, skipping")
            continue
        if not dry_run:
            result = run_deep_dive(opp_id=opp_id, dry_run=dry_run)
            if "error" not in result:
                print(f"  Auto deep-dive triggered: {opp.get('name', 'unknown')[:50]} (score {opp.get('final_score', 0):.1f})")
            else:
                print(f"  Deep dive failed for {opp_id}: {result['error']}")
        else:
            print(f"  [dry-run] Would deep-dive: {opp.get('name', 'unknown')[:50]}")
    if not deep_dive_candidates:
        print("  No opportunities scored >= 8.0 -- no auto deep-dive")
except Exception as e:
    print(f"WARNING  Step 14.5 auto deep-dive error (non-blocking): {e}")
```

NOTE: `root` variable is already defined earlier in `run_daily()` (line ~60: `root = _get_project_root()`). Use that variable.
</action>
<acceptance_criteria>
- grep "Step 14.5" src/opportunity_os/pipelines/daily_run.py returns a match
- grep "auto deep-dive" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- grep "run_deep_dive" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- grep ">= 8.0" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Add auto deep-dive to weekly_run.py for top 3 opps >= 7.0</title>
<read_first>
- src/opportunity_os/pipelines/weekly_run.py (full file -- find where `promote` is computed, around line 37-39)
- src/opportunity_os/pipelines/deep_dive.py (confirm interface)
</read_first>
<action>
In `src/opportunity_os/pipelines/weekly_run.py`, add a new section AFTER the `promote` and `to_kill` computation (around line 44) and BEFORE `quota_status` (around line 46):

```python
# Auto deep-dive on top 3 with score >= 7.0
print("Running auto deep-dive on top 3 weekly candidates (score >= 7.0)...")
try:
    from opportunity_os.pipelines.deep_dive import run_deep_dive
    import os as _os
    from opportunity_os.reports import get_project_root
    _root = get_project_root()
    deep_dive_candidates = [
        o for o in scored
        if float(o.get("final_score", 0)) >= 7.0
    ][:3]
    for opp in deep_dive_candidates:
        opp_id = opp.get("id", "unknown")
        # Check if deep dive exists this week (any file matching opp_id in reports/deep-dives/ with date >= week_start)
        dd_dir = _os.path.join(_root, "reports", "deep-dives")
        already_exists = False
        if _os.path.exists(dd_dir):
            for fname in _os.listdir(dd_dir):
                if opp_id[:40] in fname and fname[:10] >= str(week_start):
                    already_exists = True
                    break
        if already_exists:
            print(f"  Deep dive already exists this week for {opp_id}, skipping")
            continue
        if not dry_run:
            result = run_deep_dive(opp_id=opp_id, dry_run=dry_run)
            if "error" not in result:
                print(f"  Auto deep-dive: {opp.get('name', 'unknown')[:50]} (score {opp.get('final_score', 0):.1f})")
            else:
                print(f"  Deep dive failed: {result.get('error')}")
        else:
            print(f"  [dry-run] Would deep-dive: {opp.get('name', 'unknown')[:50]}")
    if not deep_dive_candidates:
        print("  No weekly candidates scored >= 7.0")
except Exception as e:
    print(f"WARNING  Weekly auto deep-dive error (non-blocking): {e}")
```
</action>
<acceptance_criteria>
- grep "auto deep-dive" src/opportunity_os/pipelines/weekly_run.py returns at least 1 match
- grep "run_deep_dive" src/opportunity_os/pipelines/weekly_run.py returns at least 1 match
- grep ">= 7.0" src/opportunity_os/pipelines/weekly_run.py returns at least 1 match
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/weekly_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
grep "run_deep_dive" src/opportunity_os/pipelines/daily_run.py src/opportunity_os/pipelines/weekly_run.py
# Both files should have at least 1 match
```
