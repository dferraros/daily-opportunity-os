---
id: 06-02F
wave: 2
depends_on: [06-01A, 06-01D]
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
autonomous: true
---

# Plan 06-02F: Venezuela Lens Auto-Run

## Goal

Auto-apply Venezuela geo lens to every opportunity where `geography == "venezuela"` immediately after scoring (Step 5.5), so VE opps get regional adjustments before any further processing. Set `venezuela_lens_applied = True` on each adjusted opp.

## must_haves

- [ ] New Step 5.5 in daily_run.py applies `apply_geo_adjustments` to all VE opps right after scoring
- [ ] Each adjusted opp gets `venezuela_lens_applied = True`
- [ ] Log message shows how many VE opps were lens-adjusted
- [ ] Guarded with try/except + log_failure (never breaks pipeline)

## Tasks

<task id="1">
<title>Add Step 5.5: Venezuela lens auto-run in daily_run.py</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find the loop starting at line ~104 `for opp_dict in valid_opps_dicts:`. Inside this loop, Step 5 is the scoring call at line ~130: `opp_dict = score_opportunity(opp_dict)`. Step 6 is `opp_dict = apply_geo_adjustments(opp_dict)` at line ~133. The Venezuela lens needs to go BETWEEN Step 5 and Step 6.)
- src/opportunity_os/geo_lens.py (confirm `apply_geo_adjustments(opp_dict)` signature -- it takes a dict and returns a dict)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`, inside the per-opportunity processing loop, AFTER Step 5 (score_opportunity) at line ~130 and BEFORE Step 6 (apply_geo_adjustments) at line ~133:

Add this block:

```python
        # Step 5.5: Extra Venezuela lens pass for VE opps
        if opp_dict.get("geography") == "venezuela":
            try:
                opp_dict = apply_geo_adjustments(opp_dict)
                opp_dict["venezuela_lens_applied"] = True
            except Exception as e:
                log_failure("venezuela_lens_auto", e, opp_id=opp_dict.get("id", "unknown"))
```

NOTE: This means VE opps go through `apply_geo_adjustments` TWICE: once in Step 5.5 (VE-specific early pass) and once in Step 6 (generic pass for all geos). The Step 6 pass is idempotent (applying LATAM adjustments on top of VE adjustments is the correct behavior -- VE is a subset of LATAM). The `apply_geo_adjustments` function already handles this correctly by checking geography internally.

Also add a counter AFTER the per-opp loop (after line ~144, after `summary["scored"] += 1`) to log the total:

Actually, a cleaner approach: add a counter outside the loop. Before the loop starts (around line ~103), add:
```python
    ve_lens_count = 0
```

Inside the Step 5.5 block, after `opp_dict["venezuela_lens_applied"] = True`, add:
```python
                ve_lens_count += 1
```

After the loop ends (after line ~145, before Step 9), add:
```python
    if ve_lens_count > 0:
        print(f"Step 5.5: Venezuela lens applied to {ve_lens_count} opportunities")
```

IMPORTANT: The `log_failure` import was added in plan 06-01D. If executing this plan before 06-01D is complete, add the import yourself:
```python
from opportunity_os.pipeline_monitor import log_failure
```
</action>
<acceptance_criteria>
- grep "Step 5.5" src/opportunity_os/pipelines/daily_run.py returns a match
- grep "venezuela_lens_applied" src/opportunity_os/pipelines/daily_run.py returns at least 1 match
- grep 'geography.*venezuela' src/opportunity_os/pipelines/daily_run.py returns at least 2 matches (the new check + the existing VE report filter)
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
grep -n "Step 5.5" src/opportunity_os/pipelines/daily_run.py
grep -n "venezuela_lens_applied" src/opportunity_os/pipelines/daily_run.py
```
