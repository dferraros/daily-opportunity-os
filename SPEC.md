# Opportunity OS — Project Spec

> Source of truth for Claude. Update this file when scope or constraints change.

## Objective

Build and maintain a production-grade daily business intelligence system that scouts, scores, and ranks business opportunities — with mandatory LATAM and Venezuela focus.

**Success metrics:**
- Daily pipeline runs without errors (zero crashes in Step 12)
- AI scorer uses claude-haiku-4-5 and produces differentiated 1-10 scores (not clustered at 7-9)
- 105+ tests passing on every commit
- Dashboard loads in < 3s with 79+ opportunities
- "now" lane populates with fast_cash opps that have speed_to_mvp >= 7

## Commands

```bash
uv run pytest                          # test suite (105 tests)
uv run opp-os daily --dry-run          # daily pipeline dry run
uv run opp-os rescore-all --dry-run    # preview scoring changes
uv run streamlit run src/opportunity_os/dashboard.py  # dashboard
git push origin master                 # deploy (no CI, direct push)
```

## Project Structure

```
src/opportunity_os/          # all Python source
  engines/                   # scoring, kill gate, TAM, benchmark
  pipelines/                 # daily_run, enrichment, deep_dive, validation, weekly
  dashboard_tabs/            # 6 Streamlit tabs
  *.py                       # models, storage, clients, normalization, filters
config/                      # scoring_weights.yaml, weekly_quotas.yaml
data/opportunities/          # JSONL store (gitignored)
data/backups/                # snapshots (gitignored)
tasks/                       # plan.md and todo.md (agent-skills workflow)
docs/plans/                  # implementation plans (archived)
```

## Code Style

```python
# Immutability — always spread, never mutate
result = {**opp, "final_score": 7.5}   # correct
opp["final_score"] = 7.5               # NEVER

# Max 400 lines per file, 40 lines per function
# snake_case functions, PascalCase classes, UPPER_SNAKE constants
# Boolean prefixes: is_, has_, should_, can_
# No bare except, no print(), no hardcoded credentials
```

## Testing Strategy

- Framework: pytest + uv run pytest
- Location: alongside modules (test_*.py next to *.py)
- Coverage: unit tests for all engines, integration for pipeline steps
- TDD: write failing test first, then implementation
- Run after every task: `uv run pytest -q`

## Boundaries

**Always do:**
- `{**opp, ...}` spread — never mutate dicts in place
- `git commit -m "type(scope): description"` — conventional commits
- `uv run pytest -q` before every commit
- `uv run opp-os rescore-all --dry-run` after any scoring formula change
- `git push origin master` after each task to keep GitHub current

**Ask first:**
- Changing scoring weights (affects all 79+ stored opportunities)
- Adding new API integrations (cost implications)
- Deleting or restructuring JSONL data files

**Never do:**
- Commit to `data/opportunities/` (gitignored — runtime data)
- Use worktrees for this project (too much confusion — one branch, master)
- Use `hash()` for IDs (not deterministic — use hashlib.md5)
- Skip tests before committing
- Use `opp.pop()` or direct dict assignment to mutate storage-returned dicts
