---
id: 06-02G
wave: 2
depends_on: [06-01A, 06-01D]
files_modified:
  - src/opportunity_os/storage.py
  - src/opportunity_os/pipelines/daily_run.py
  - src/opportunity_os/pipelines/weekly_run.py
autonomous: true
---

# Plan 06-02G: Score History + Rising Signals Fix

## Goal

Implement append-only score_history on each opportunity (written during daily scoring), and fix the weekly `rising_signals` computation so it reads real score deltas instead of always returning `[]`.

## must_haves

- [ ] `storage.py` has a new `append_opp_score_history(opp_id, new_score)` function that appends `{date, score, delta}` to the opp's `score_history` list field
- [ ] `daily_run.py` calls `append_opp_score_history` for each scored opp after Step 8 (persist)
- [ ] `weekly_run.py` computes `rising_signals` from `score_history` field (not hardcoded `[]`)
- [ ] Rising = score increased by >= 0.5 in last 7 days, top 3 by delta descending

## Tasks

<task id="1">
<title>Implement append_opp_score_history in storage.py</title>
<read_first>
- src/opportunity_os/storage.py (see existing `append_score_history` at line ~185 -- this writes to opportunity_HISTORY.jsonl which is a separate audit trail. The NEW function writes to the opp's own `score_history` LIST field inside opportunities.jsonl via `update_opportunity`)
- src/opportunity_os/models.py (confirm `score_history: Optional[List[Dict]] = None` field exists after 06-01A)
</read_first>
<action>
In `src/opportunity_os/storage.py`, add a NEW function (do NOT modify the existing `append_score_history` function which writes to opportunity_history.jsonl -- that's the audit trail):

```python
def append_opp_score_history(opp_id: str, new_score: float, path: str = None) -> bool:
    """
    Append a score entry to the opportunity's own score_history list field.

    Format: {"date": "YYYY-MM-DD", "score": float, "delta": float}
    Delta = new_score - previous score. First entry delta = 0.

    Returns True if updated, False if opp not found.
    """
    opp = get_opportunity_by_id(opp_id, path)
    if not opp:
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    history = opp.get("score_history") or []

    # Skip if already recorded today
    if history and history[-1].get("date") == today:
        return True

    prev_score = history[-1]["score"] if history else new_score
    delta = round(new_score - prev_score, 4)

    entry = {"date": today, "score": round(new_score, 4), "delta": delta}
    history.append(entry)

    return update_opportunity(opp_id, {"score_history": history}, path)
```

Place this function AFTER the existing `append_score_history` function (around line ~206) and BEFORE the "Deduplication" section.
</action>
<acceptance_criteria>
- grep "def append_opp_score_history" src/opportunity_os/storage.py returns exactly 1 match
- grep "score_history" src/opportunity_os/storage.py returns at least 3 matches
- python -c "from opportunity_os.storage import append_opp_score_history; print('OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Call append_opp_score_history in daily_run.py after persisting scored opps</title>
<read_first>
- src/opportunity_os/pipelines/daily_run.py (find Step 8: Persist, around line ~143-144: `append_opportunity(opp_dict)`. The score_history append should happen RIGHT AFTER each opp is persisted)
</read_first>
<action>
In `src/opportunity_os/pipelines/daily_run.py`:

1. Add import at the top (near other storage imports, around line ~27-30):
   ```python
   from opportunity_os.storage import append_opp_score_history
   ```
   NOTE: The existing import block uses `from opportunity_os.storage import (read_all_opportunities, append_opportunity, dedupe_check)`. Add `append_opp_score_history` to this import group.

2. AFTER Step 8 (persist) -- after `append_opportunity(opp_dict)` at ~line 144 -- add:
   ```python
            # Step 8.5: Record score history
            try:
                final_score = float(opp_dict.get("final_score", 0))
                if final_score > 0:
                    append_opp_score_history(opp_dict["id"], final_score)
            except Exception as e:
                log_failure("score_history_append", e, opp_id=opp_dict.get("id", "unknown"))
   ```

   This block must be INSIDE the per-opp loop, at the same indentation level as the `append_opportunity(opp_dict)` call above it (inside the `if not dry_run:` block).
</action>
<acceptance_criteria>
- grep "append_opp_score_history" src/opportunity_os/pipelines/daily_run.py returns at least 2 matches (import + usage)
- grep "Step 8.5" src/opportunity_os/pipelines/daily_run.py returns a match
- grep "score_history_append" src/opportunity_os/pipelines/daily_run.py returns a match
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/daily_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

<task id="3">
<title>Fix rising_signals in weekly_run.py to read score_history</title>
<read_first>
- src/opportunity_os/pipelines/weekly_run.py (find where `"rising": []` is hardcoded in the context dict, around line 65. Also find the `# TODO: compute from score history` comment)
</read_first>
<action>
In `src/opportunity_os/pipelines/weekly_run.py`:

1. Add a helper function BEFORE the `run_weekly` function:
   ```python
   def _get_rising_signals(all_opps: list, days: int = 7) -> list:
       """
       Find opportunities whose score increased by >= 0.5 in the last `days` days.
       Returns top 3 sorted by delta descending.
       """
       from datetime import datetime, timedelta
       cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
       risers = []
       for opp in all_opps:
           history = opp.get("score_history") or []
           if len(history) < 2:
               continue
           # Find oldest entry within the window
           recent = [h for h in history if h.get("date", "") >= cutoff]
           if len(recent) < 2:
               continue
           first_in_window = recent[0]["score"]
           latest = recent[-1]["score"]
           delta = latest - first_in_window
           if delta >= 0.5:
               risers.append({
                   "name": opp.get("name", "Unknown"),
                   "id": opp.get("id", ""),
                   "score": latest,
                   "delta": round(delta, 2),
                   "geography": opp.get("geography", ""),
               })
       risers.sort(key=lambda x: x["delta"], reverse=True)
       return risers[:3]
   ```

2. In the `run_weekly` function, REPLACE the hardcoded `"rising": []` (around line 65) with:
   ```python
   "rising": _get_rising_signals(all_opps),
   ```

3. Remove the `# TODO: compute from score history` comment.
</action>
<acceptance_criteria>
- grep "def _get_rising_signals" src/opportunity_os/pipelines/weekly_run.py returns a match
- grep "score_history" src/opportunity_os/pipelines/weekly_run.py returns at least 2 matches
- grep '"rising": \[\]' src/opportunity_os/pipelines/weekly_run.py returns 0 matches (hardcoded empty list removed)
- grep "_get_rising_signals" src/opportunity_os/pipelines/weekly_run.py returns at least 2 matches (definition + usage)
- python -c "import ast; ast.parse(open('src/opportunity_os/pipelines/weekly_run.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
PYTHONPATH=src uv run python -c "
from opportunity_os.storage import append_opp_score_history, read_all_opportunities
from opportunity_os.pipelines.weekly_run import _get_rising_signals
opps = read_all_opportunities()
rising = _get_rising_signals(opps)
print(f'Rising signals: {len(rising)} (expected 0 on first run, will populate after daily runs)')
print('Score history + rising signals wiring OK')
"
```
