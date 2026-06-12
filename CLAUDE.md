# CLAUDE.md — Daily Opportunity OS

Daily pipeline that discovers, scores, enriches, and validates startup/business
opportunities. This repo contains ONLY the Daily Opportunity OS — no other
projects, no employer content, ever.

## Commands
- Daily run: `uv run opp-os daily`
- Dashboard: `uv run streamlit run src/opportunity_os/dashboard.py`
- Tests: `uv run pytest -q` (colocated in src/opportunity_os/)
- Rescore: `uv run opp-os rescore-all --dry-run` — idempotency gate: MUST report 0 changed on unchanged data
- Calibration: `uv run opp-os calibrate` — outcome discrimination, Brier skill, weight proposals
- Bridge: `opp-os like <id>` -> `build` -> `outcome <id> <status>`

## Conventions
- Never mutate dicts — always `{**opp, ...}`
- `config/scoring_weights.yaml` is the single source of truth for weights; edit manually with an audit comment, never auto-apply
- Tests never write live data files — conftest redirects file paths; extend it for any new file-writing module
- Goal rubric for scoring work: `docs/plans/2026-06-12-scoring-calibration-goal.md`
- Fail fast, log before re-raising, no bare excepts
