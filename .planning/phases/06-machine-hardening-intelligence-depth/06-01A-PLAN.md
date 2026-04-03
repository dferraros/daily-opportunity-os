---
id: 06-01A
wave: 1
depends_on: []
files_modified:
  - src/opportunity_os/models.py
  - scripts/migrate_schema_v2.py
autonomous: true
---

# Plan 06-01A: Schema Cleanup -- Remove 15 Dead Fields, Add 4 Missing Fields

## Goal

Remove 15 deprecated fields (0% usage) from the Opportunity model, add 4 missing fields that downstream logic already assumes, and migrate all existing opportunity records.

## must_haves

- [ ] 15 deprecated fields removed from `models.py` Opportunity class
- [ ] 4 new fields added: `score_history`, `tam_formula`, `tam_confidence`, `venezuela_lens_applied`
- [ ] Schema version comment updated to "v2 -- Phase 6 cleanup"
- [ ] Migration script exists and strips deleted fields from opportunities.jsonl
- [ ] `recommendation` field already exists (confirm, do not duplicate)

## Tasks

<task id="1">
<title>Remove 15 deprecated fields and add 4 new fields to Opportunity model</title>
<read_first>
- src/opportunity_os/models.py (full model -- identify exact lines for each deprecated field)
- data/opportunities/opportunities.jsonl (verify 0% usage of deprecated fields before deleting)
</read_first>
<action>
1. First, run a verification check on `data/opportunities/opportunities.jsonl` to confirm all 15 fields have 0 non-null values:
   `pain_cluster_id`, `trust_profile`, `why_now_venezuela`, `first_revenue_path`,
   `daniels_wedge_score`, `non_obviousness_score`, `business_model_type`, `thesis_fit_score`,
   `decision_filter_results`, `distribution_profile`, `benchmark_archetype`, `founder_fit_score`,
   `pain_validation_score`, `pain_evidence_sources`, `workarounds_found`

   IMPORTANT: Some of these fields exist as both sub-model classes and Opportunity fields. The CONTEXT says to delete the "old version" fields but keep the "live" versions that research_executor.py writes to. Check each carefully:
   - `trust_profile` field on Opportunity (line ~269: `trust_profile: Optional[TrustProfile] = None`) -- DELETE the field from Opportunity, but keep the TrustProfile sub-model class definition (it may be imported elsewhere)
   - `why_now_venezuela` field on Opportunity (line ~264) -- DELETE field, keep WhyNowVenezuela class
   - `first_revenue_path` field on Opportunity (line ~252) -- DELETE field, keep FirstRevenuePath class
   - `decision_filter_results` field on Opportunity (line ~249) -- DELETE field, keep DecisionFilterResults class
   - `distribution_profile` field on Opportunity (line ~268) -- DELETE field, keep DistributionProfile class
   - `pain_cluster_id` (line ~149) -- DELETE
   - `daniels_wedge_score` (line ~242) -- DELETE
   - `non_obviousness_score` (line ~155) -- DELETE
   - `business_model_type` (line ~139-143) -- DELETE
   - `benchmark_archetype` (line ~132-137) -- DELETE
   - `founder_fit_score` (line ~241) -- DELETE
   - `thesis_fit_score` (line ~240) -- DELETE
   - `pain_validation_score` -- search for it, DELETE if present
   - `pain_evidence_sources` -- search for it, DELETE if present
   - `workarounds_found` -- search for it, DELETE if present

   NOTE: `pain_validation_score`, `pain_evidence_sources`, and `workarounds_found` may not exist as typed fields in models.py -- they may only exist as runtime dict keys written by research_executor.py. If they are NOT in models.py, skip deleting them from models.py (they will be stripped from JSONL by the migration script).

2. Add these new fields to the Opportunity class (in appropriate sections):
   - In "Action" section: `recommendation` already exists (line ~271) -- confirm it has the correct type: `Optional[Literal["build", "test", "deep_dive", "watch", "ignore"]]`. If it does, do NOT add it again.
   - After the "Scoring" section, add a new "Score History" section:
     ```python
     # -- Score History --------------------------------------------------------
     score_history: Optional[List[Dict]] = None  # append-only: [{date, score, delta}]
     ```
   - In the "TAM" section, after `tam_method`:
     ```python
     tam_formula: Optional[str] = None  # explicit formula string, e.g. "500K users * $5/mo * 12"
     tam_confidence: Optional[Literal["high", "medium", "low"]] = None
     ```
     NOTE: `tam_formula` and `tam_confidence` may already exist (check lines ~224-226). If they do, skip adding them.
   - In the "Venezuela-Specific" section:
     ```python
     venezuela_lens_applied: bool = False
     ```

3. Update the module docstring (line 2) to:
   ```python
   """Opportunity data models -- v2 Phase 6 cleanup.
   Removed 15 deprecated fields, added score_history + tam_formula + tam_confidence + venezuela_lens_applied."""
   ```

4. Update the Opportunity class docstring to reflect the reduced field count (was "56-field schema", count the actual fields after changes).
</action>
<acceptance_criteria>
- grep "pain_cluster_id" src/opportunity_os/models.py returns NO matches
- grep "daniels_wedge_score" src/opportunity_os/models.py returns NO matches
- grep "founder_fit_score" src/opportunity_os/models.py returns NO matches
- grep "thesis_fit_score" src/opportunity_os/models.py returns NO matches (as a field definition)
- grep "score_history" src/opportunity_os/models.py returns a match
- grep "venezuela_lens_applied" src/opportunity_os/models.py returns a match
- grep "v2" src/opportunity_os/models.py returns a match in the docstring
- python -c "from opportunity_os.models import Opportunity; print('OK')" succeeds
</acceptance_criteria>
</task>

<task id="2">
<title>Create and run migration script to strip deleted fields from existing data</title>
<read_first>
- data/opportunities/opportunities.jsonl (current data format)
- src/opportunity_os/models.py (updated model from Task 1)
</read_first>
<action>
Create `scripts/migrate_schema_v2.py` that:

1. Reads `data/opportunities/opportunities.jsonl` line by line
2. For each record, removes these 15 keys if present:
   ```python
   DEPRECATED_FIELDS = [
       "pain_cluster_id", "trust_profile", "why_now_venezuela", "first_revenue_path",
       "daniels_wedge_score", "non_obviousness_score", "business_model_type",
       "thesis_fit_score", "decision_filter_results", "distribution_profile",
       "benchmark_archetype", "founder_fit_score", "pain_validation_score",
       "pain_evidence_sources", "workarounds_found",
   ]
   ```
3. Adds missing fields with defaults:
   - `score_history`: None
   - `venezuela_lens_applied`: False
4. Writes updated records back to `data/opportunities/opportunities.jsonl`
5. Creates a backup first: `data/opportunities/opportunities_pre_v2.jsonl`
6. Prints summary: "Migrated N records. Removed fields: {count per field}. Backup at: {path}"

Run the migration after creating it:
```bash
cd project_root && PYTHONPATH=src uv run python scripts/migrate_schema_v2.py
```
</action>
<acceptance_criteria>
- File `scripts/migrate_schema_v2.py` exists
- File `data/opportunities/opportunities_pre_v2.jsonl` exists (backup)
- grep "pain_cluster_id" data/opportunities/opportunities.jsonl returns NO matches
- grep "daniels_wedge_score" data/opportunities/opportunities.jsonl returns NO matches
- grep "trust_profile" data/opportunities/opportunities.jsonl returns NO matches (as a top-level key)
- PYTHONPATH=src uv run python -c "from opportunity_os.storage import read_all_opportunities; opps = read_all_opportunities(); print(f'{len(opps)} opps loaded OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
PYTHONPATH=src uv run python -c "
from opportunity_os.models import Opportunity
o = Opportunity.empty()
assert hasattr(o, 'score_history'), 'missing score_history'
assert hasattr(o, 'venezuela_lens_applied'), 'missing venezuela_lens_applied'
assert not hasattr(o, 'pain_cluster_id'), 'pain_cluster_id should be removed'
assert not hasattr(o, 'daniels_wedge_score'), 'daniels_wedge_score should be removed'
print('Schema v2 verification PASSED')
"
```
