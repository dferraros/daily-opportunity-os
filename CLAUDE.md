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

## Scoring model (actual — drift fixed 2026-07-22; older docs said 16/18 criteria)
- 23 dimensions in 3 layers: Attractiveness 50% (6 fields) + Executability 30%
  (4 fields) + Strategic Value 20% (13 fields). Source of truth for field lists:
  engines/scoring_engine.py ATTRACTIVENESS/EXECUTABILITY/STRATEGIC_VALUE_FIELDS.
- Every scored dimension carries a source tag in score_sources: data | ai | heuristic
  (stamped by score_opportunity).
- Decision filters (sell-fast / build-lean / compound) are computed fresh on every
  score_opportunity pass; 2+ explicit failures cap final_score at 5.0. Unknown
  (None) answers never count as failures.
- Kill-thesis runs inside the daily pipeline (step 9.25) on the top 3, 30d TTL,
  disabled with OPP_OS_KILL_THESIS=0; strength >= 7 caps final_score at 5.0.

## Conventions
- Never mutate dicts — always `{**opp, ...}`
- `config/scoring_weights.yaml` is the single source of truth for weights; edit manually with an audit comment, never auto-apply
- Tests never write live data files — conftest redirects file paths; extend it for any new file-writing module
- Goal rubric for scoring work: `docs/plans/2026-06-12-scoring-calibration-goal.md`
- Fail fast, log before re-raising, no bare excepts

## Standing Product Requirements (founder-stated)
- 2026-07-22: The OS must support HYPOTHESIS MODE as a first-class pipeline —
  Daniel submits his own idea and the machine validates it: adversarial-first
  (kill-thesis + component feasibility interrogation BEFORE scoring), generate
  3-5 neighboring alternatives the idea must beat, expert-lens panel review,
  then normal evidence -> score x confidence -> deep dive -> MVP build prompt.
  Discovery mode (signal harvesting) is secondary to this.
- Pain statements use the enforced schema: "[customer] loses [money/time/capacity]
  because [specific failing process], currently solved via [workaround]".
- Every score must carry a confidence tag (data-backed / ai / heuristic);
  guessed and evidence-backed scores must be visibly distinguishable.
- Deep dives for infrastructure/fintech plays must include: entry-point ladder
  (aggregator -> orchestration -> ops platform -> regulated infra), hard-to-reverse
  decisions, and the 12-question component feasibility interrogation.
- 2026-07-22 (b): Validation promotion gate = minimum-signal bar, ONE of:
  3 paid pilots | 5 LOIs with agreed price | 10 companies sharing real data |
  1 anchor client funding development. CTA clicks/interview counts are inputs,
  not promotion criteria.
- 2026-07-22 (c): Problem-understanding stack maps evidence type to funnel stage:
  reports->industry structure; workaround archaeology (excel templates, tutorials,
  freelance gigs)->critical processes; reddit/social->demonstrable pain;
  job postings (LinkedIn/Computrabajo via Apify)->buyer with budget + price ceiling;
  interviews only->commercial validation. Closed FB/WhatsApp groups are an
  interview channel, never a scraping target.
- Hypothesis queue #1: VE multi-rail payment reconciliation ops product
  (pago movil + transfers + Zelle + USDT + cash + WhatsApp receipts). Test the
  pricing contradiction: proposed $100-800/mo vs geo lens VE WTP 0.25x.
  Deep dives must answer "what does this become if it wins" (wedge-to-platform path).
- 2026-07-22 (d): Hypothesis mode output = verdict + NEIGHBORHOOD MAP, never
  verdict alone. Generate adjacent options along 5 axes (customer, problem,
  entry rung, geography, business model incl. services track) BEFORE the
  adversarial pass; tag all evidence with which neighbors it touches; mini-score
  neighbors from recycled evidence. Verdicts: build | validate | pivot-to-neighbor
  | drop-but-run-neighbor. Rationale: research spent killing an idea is a map of
  its neighborhood (proof case: API-hub hypothesis -> reconciliation neighbor).
- 2026-07-22 (e): LEGAL is a first-class dimension in hypothesis mode: dedicated
  regulatory lens in the expert panel (VE: SUDEBAN perimeter, sanctions/OFAC,
  crypto/stablecoin treatment, data protection, tax/e-invoicing). Legal viability
  scored PER NEIGHBOR on the neighborhood map (the legal wall's position often
  decides the pivot, e.g. custody vs no-custody rung). Report both directions:
  risk that kills AND regulatory arbitrage as wedge/moat. No legal claim without
  a dated primary source; unverified legal assumptions -> [LEGAL OPINION REQUIRED]
  flag that BLOCKS promotion to build.
- 2026-07-22 (f): From manual VE-reconciliation thesis benchmark: (1) deep dives
  MUST include a unit-economics block (setup+MRR scenarios, break-even at stated
  burn, CAC hypothesis, billed vs collected); (2) new verdict class
  ABSORB-INTO-EXISTING-ASSET — neighborhood map gets a 6th axis checking Daniel's
  existing assets (Konecto, Arranca, bit2me network) for module-vs-company fit,
  with a TWO-SIDED check (ICP match, roadmap conflict, cannibalization);
  (3) when TAM inputs are unverifiable, output a REACHABLE-REVENUE model and say
  so — never a decorated proxy guess; (4) validation engine offers CONCIERGE-TEST
  design (do the job manually on real redacted data, measure match rate/hours)
  whenever the product automates an existing workflow; (5) first-customer strategy
  by CATEGORY with paid-diagnostic entry offer, never invented company lists.
  Hypothesis #1 (VE reconciliation) pending adversarial pass; top kill-questions:
  incumbent inertia (why Galac/eFactory/Alegra have not shipped it) and legality
  of customer bank-data export.
