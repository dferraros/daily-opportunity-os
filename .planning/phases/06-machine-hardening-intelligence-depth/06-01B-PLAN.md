---
id: 06-01B
wave: 1
depends_on: []
files_modified:
  - src/opportunity_os/pipelines/daily_run.py
  - scripts/run_research_backfill.py
autonomous: true
---

# Plan 06-01B: Research Scope Expansion -- top-5 to top-20

## Goal

Expand research executor coverage from top 5 to top 20 opportunities per daily run, and benchmark mapping from top 10 to top 30, so that 59/64 opportunities no longer have null research fields.

## must_haves

- [ ] Research executor runs on top 20 opps (not top 5)
- [ ] Benchmark mapping runs on top 30 opps (not top 10)
- [ ] Pain intelligence and distribution intelligence run on top 20 opps (not top 5)
- [ ] Progress output shows "Researching opp {n}/{total}: {name}"
- [ ] Backfill script default batch size updated from 5 to 20

## Tasks

<task id="1">
<title>Expand research, pain, distribution, and benchmark scope in daily_run.py</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find exact lines: `top_5 = all_opps_sorted[:5]`, `top_10 = all_opps_sorted[:10]`, and all `for opp in top_5:` loops)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`, make these exact changes:

1. **Step 9.7 (Benchmark Mapping)** -- around line 167-168:
   - Change: `print("Step 9.7: Running Benchmark Mapper on top 10 opportunities...")`
   - To: `print("Step 9.7: Running Benchmark Mapper on top 30 opportunities...")`
   - Change: `top_10 = all_opps_sorted[:10]`
   - To: `top_30 = all_opps_sorted[:30]`
   - Change: `for opp in top_10:` to `for opp in top_30:`
   - Change: `bench_populated = sum(1 for o in top_10 if o.get("benchmark_archetype"))`
   - To: `bench_populated = sum(1 for o in top_30 if o.get("benchmark_archetype"))`
   - Change: `print(f"  Benchmark archetypes populated for {bench_populated}/10 opportunities")`
   - To: `print(f"  Benchmark archetypes populated for {bench_populated}/{len(top_30)} opportunities")`

2. **Step 10 (Customer Pain OS)** -- around line 183:
   - Change: `print("Step 10: Running Customer Pain OS on top 5 opportunities...")`
   - To: `print("Step 10: Running Customer Pain OS on top 20 opportunities...")`
   - Change: `top_5 = all_opps_sorted[:5]`
   - To: `top_20 = all_opps_sorted[:20]`
   - Change ALL subsequent `top_5` references in Steps 10, 11, 11.5, 11.8, and Step 12 (save enriched records) to `top_20`

3. **Step 11 (Distribution OS)** -- around line 197:
   - Change: `print("Step 11: Running Distribution OS on top 5 opportunities...")`
   - To: `print("Step 11: Running Distribution OS on top 20 opportunities...")`
   - All `for opp in top_5:` become `for opp in top_20:`

4. **Step 11.5 (Research Executor)** -- around line 211:
   - Change: `print("Step 11.5: Running Research Executor on top 5 opportunities...")`
   - To: `print(f"Step 11.5: Running Research Executor on top {len(top_20)} opportunities...")`
   - Change `for opp in top_5:` to:
     ```python
     for i, opp in enumerate(top_20, 1):
         if not opp.get("research_executed_at"):
             print(f"  Researching opp {i}/{len(top_20)}: {opp.get('name', 'unknown')[:50]}")
             run_research_executor(opp)
             print(f"  Research complete: {opp.get('name', 'unknown')[:50]}")
         else:
             print(f"  Already researched ({i}/{len(top_20)}): {opp.get('name', 'unknown')[:50]}")
     ```

5. **Step 11.8 (Pain Library)** -- around line 227:
   - Change: `for opp in top_5:` to `for opp in top_20:`

6. **Step 12 (Save enriched records)** -- around line 244-245:
   - Change: `enriched_ids = {o["id"]: o for o in top_5 if o.get("id")}`
   - To: `enriched_ids = {o["id"]: o for o in top_20 if o.get("id")}`
   - Change: `print(f"  Saved {len(top_5)} enriched records")`
   - To: `print(f"  Saved {len(top_20)} enriched records")`
</action>
<acceptance_criteria>
- grep "top_5" src/opportunity_os/pipelines/daily_run.py returns NO matches (all converted to top_20 or top_30)
- grep "top_20" src/opportunity_os/pipelines/daily_run.py returns at least 8 matches
- grep "top_30" src/opportunity_os/pipelines/daily_run.py returns at least 2 matches
- grep "Researching opp" src/opportunity_os/pipelines/daily_run.py returns a match
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Update backfill script default batch size</title>
<read_first>
- scripts/run_research_backfill.py (find the default batch size value)
</read_first>
<action>
In `scripts/run_research_backfill.py`:
1. Find the default batch size (currently 5) and change it to 20
2. If there is a variable like `BATCH_SIZE = 5` or a CLI arg default of 5, change to 20
3. If the script uses `[:5]` slicing, change to `[:20]`
4. Add a progress print: after each opp is processed, print `f"Backfill {i}/{total}: {opp_name}"`
</action>
<acceptance_criteria>
- grep "20" scripts/run_research_backfill.py returns at least one match for the batch size
- grep -c "[:5]" scripts/run_research_backfill.py returns 0
- python -c "import ast; ast.parse(open('scripts/run_research_backfill.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
grep -c "top_5" src/opportunity_os/pipelines/daily_run.py  # should be 0
grep -c "top_20" src/opportunity_os/pipelines/daily_run.py  # should be >= 8
grep "Researching opp" src/opportunity_os/pipelines/daily_run.py  # should match
```
