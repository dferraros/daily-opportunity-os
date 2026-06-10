# Research / Scoring / Validation Upgrade + Conviction-to-Action Bridge

> Approved 2026-06-10. Wave 1 first. Status tracked in tasks/todo.md.

## Diagnosis

- **Deep research confirms, never kills.** All sources hunt demand evidence; deep_dive.py is template-fill, not synthesis. Confirmation bias is structural.
- **Scoring lacks provenance and stability.** AI-guessed 8 == data-backed 8. Normalization is not idempotent (~75/80 phantom drift per rescore). outcome_tracking.py exists with zero data — weights tuned by intuition.
- **Validation cannot fail.** 8 sections re-state stored fields; auto-validation gates on the inflated normalized score; output is write-only markdown.
- **No path from conviction to action.** At the moment the machine convinces Daniel, it offers nothing: no bundle, no bridge to building.

## Model policy

- Runtime: Haiku everywhere; ONE Sonnet call for deep-dive synthesis on the #1 opp only (Wave 2.2).
- Implementation: Waves 1, 2.3, 3.2, 4.2 = any model (mechanical). Waves 2.1, 3.1, 3.3, 4.1 = strong model or careful review (rank-order semantics).

## Budget (Daniel, 2026-06-10): hard ceiling $20/mo total

- Anthropic: $10 cap (console limit) -- expected $4-8
- Apify: $5 cap beyond free credit (console usage limit) -- expected $0-3.
  DECISION: Apify stays (curious_coder actor is pay-per-result $0.40/1k, NOT rental;
  earlier $30/mo figure was a different rental actor). Serper site: proxy demoted to
  fallback-only -- LinkedIn blocks Google indexing, proxy counts would be noise
  laundered as "data-backed". Watch first-run cost in Apify console; if the G2 actor
  is rental-priced, swap to a pay-per-result alternative.
- Tavily/Serper/Firecrawl/Exa/Reddit/Jina: free tiers ($0; Serper one-time top-up when
  signup credits exhaust, ~$1-2/mo amortized)
- Headroom funds: Wave 2.2 Sonnet synthesis (~$3/mo) first, then widen paid research
  top-5 -> top-8 (~$2-3/mo) after deep-dive quality is proven.

## Wave 1 — Conviction-to-action bridge (key-independent, zero API cost)

- **1.1 `opp-os like <opp_id>`** (S): stamps `liked_at` + `recommendation="build"`; `opp-os liked` lists; dashboard surfaces liked opps. `--undo` clears.
- **1.2 `opp-os export <opp_id>`** (M): one self-contained markdown in `exports/<opp_id>/report.md` — scoring breakdown w/ per-dimension reasons, evidence + sources, TAM, kill gate, risks, revenue paths, competitor pricing, attached validation/deep-dive md if present. Dashboard `st.download_button` on deep-dive tab.
- **1.3 `opp-os kickoff <opp_id>`** (M): writes `exports/<opp_id>/PROJECT.md` (seed brief: problem, customer, geography, WTP anchor, pricing benchmark, first-revenue path, distribution + trust, competitors, top kill risks) + `kickoff-prompt.md` (paste into a fresh Claude Code session: read PROJECT.md → /spec → /plan, constraints inline). `--to <dir>` overrides output dir.

## Wave 2 — Research that can say no (needs .env keys)

- **2.1 Kill-thesis pass** (M): inverted queries for top-5 → `kill_thesis` + `kill_thesis_strength` (1-10); >= 7 caps score like decision filters.
- **2.2 Real deep-dive synthesis** (M): #1 opp only — one Sonnet call over ALL evidence → verdict-first analysis (build/test/pass, because...).
- **2.3 Evidence provenance tags** (S): stamp research fields with source + date. Prereq for 3.1.

## Wave 3 — Scoring you can trust

- **3.1 Confidence-weighted scoring** (M): provenance multiplier — validated x1.0, data-backed x0.9, AI-inferred x0.7.
- **3.2 Idempotent normalization** (S): always normalize from raw_final_score; kills phantom drift.
- **3.3 Calibration loop** (M): 4 outcomes (interviewed / first contact / first revenue / killed-in-validation) recorded by like/kickoff/validate; `opp-os calibration` prints score-vs-outcome correlation per dimension.

## Wave 4 — Validation that can fail

- **4.1 Evidence-gated sections** (M): pass/unverified/fail per section with explicit criteria; header "N/8 verified"; auto-validation gates on raw score.
- **4.2 Experiment kit** (M): WhatsApp outreach scripts (reuse interview_tracker generator), landing copy draft, 7-day checklist; results feed 3.3.

## Explicitly NOT building

PDF rendering (md/HTML enough), multi-agent research orchestration (gated single-call is the right cost shape), scoring ML (80 opps is too few — the calibration loop is the honest version).

## Done signals

- Wave 1: `like` -> `export` -> `kickoff` produces a folder Daniel can act on in < 1 min, with tests.
- Wave 2: at least one live opp carries a kill_thesis with strength >= 7 and a capped score.
- Wave 3: `rescore-all --dry-run` on unchanged data reports 0 score changes.
- Wave 4: a validation package shows at least one FAILED section on a weak opp.
