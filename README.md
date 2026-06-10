# Daily Opportunity OS

Production-grade daily business intelligence system — scouts, scores, and ranks business opportunities with LATAM and Venezuela focus.

Built for Claude Code. Runs daily. Produces Notion-ready outputs.

**Version:** v2.0 | **Tests:** 105 passing

---

## Quick start

```bash
uv sync
cp .env.example .env          # add ANTHROPIC_API_KEY at minimum
uv run opp-os stats           # verify installation
uv run opp-os daily --dry-run # preview (no files written)
uv run opp-os daily           # full run
```

**Dashboard:**

```bash
uv run streamlit run src/opportunity_os/dashboard.py
# -> http://localhost:8501
```

---

## CLI reference

| Command | Description |
|---------|-------------|
| `opp-os daily` | Full pipeline: harvest → score → enrich → reports |
| `opp-os daily --dry-run` | Preview — no files written |
| `opp-os harvest` | Harvest signals only → `data/raw/` |
| `opp-os weekly` | Weekly review — 4 mandatory outputs |
| `opp-os deep-dive <id>` | Deep dive report for one opportunity |
| `opp-os validate <id>` | 8-section validation package |
| `opp-os research <id>` | Pain + distribution research (paid) |
| `opp-os free-research` | Tavily + free-source enrichment, top-20 |
| `opp-os rescore-all` | Rescore all opps with current formula |
| `opp-os rescore-all --dry-run` | Preview score deltas |
| `opp-os like <id>` | Mark as liked (conviction flag, sets recommendation=build) |
| `opp-os liked` | List liked opportunities |
| `opp-os export <id>` | Self-contained report bundle → `exports/<id>/report.md` |
| `opp-os kickoff <id>` | Claude Code starter pack (PROJECT.md + kickoff prompt) |
| `opp-os search <query>` | Keyword search |
| `opp-os stats` | Portfolio summary + weekly quota |
| `opp-os backup` | Snapshot opportunities.jsonl |
| `opp-os backups` | List snapshots |
| `opp-os restore <file>` | Restore from snapshot |
| `opp-os audit` | Pipeline failure audit by step |

---

## API keys (.env)

| Key | Required | Purpose |
|-----|----------|---------|
| `ANTHROPIC_API_KEY` | Yes | AI scoring (claude-haiku-4-5), research, validation |
| `TAVILY_API_KEY` | Recommended | News signal count, content extraction |
| `APIFY_API_TOKEN` | Optional | LinkedIn job count, G2 reviews |
| `SERPER_API_KEY` | Optional | Google SERP (2,500 free/month) |
| `EXA_API_KEY` | Optional | Semantic search (1,000 free/month) |
| `FIRECRAWL_API_KEY` | Optional | Competitor pricing page extraction |

All integrations fail gracefully — missing keys produce neutral scores, not penalties.

---

## Scoring model

Three-layer weighted composite (0–10):

| Layer | Weight | Key fields |
|-------|--------|-----------|
| Attractiveness | 50% | market_size, pain_severity, timing_tailwind, willingness_to_pay, monetization_clarity, pain_validation_score |
| Executability | 30% | speed_to_mvp, capital_efficiency, distribution_accessibility, distribution_quality |
| Strategic Value | 20% | competition_intensity, defensibility, regional_fit, founder_fit, ai_leverage, operational_simplicity, regulatory_simplicity, revenue_speed_score, gross_margin_potential, network_effect_strength, switching_cost_score, **market_momentum_score**, **competitor_weakness_score** |

**Data-backed sub-scores (no AI guessing):**
- `market_momentum_score` — LinkedIn job postings via Apify: 0 jobs → 0, 50+ → 10
- `competitor_weakness_score` — G2 negative review rate: 0% → 5 (neutral), 80%+ → 10

**Modifiers:** Venezuela wedge +1.5 to regional_fit | Daniel's wedge low (<2) → −1.0

**Hard caps:** kill_decision → 0.0 | 2+ filter failures → cap 5.0

**Portfolio normalisation:** per-cohort spread to 2.0–9.5, max inflation +1.5 (prevents mediocre batches from looking excellent).

---

## Portfolio lanes

| Lane | Criteria |
|------|----------|
| `now` | fast_cash + revenue path + (time_to_mvp set OR speed_to_mvp ≥ 7) |
| `strategic` | venture_scale + TAM ≥ $100M |
| `soon` | All surviving opps not matched above |
| `no` | kill_decision = True |

---

## Geography lens

| Geo | WTP | Rail | Notes |
|-----|-----|------|-------|
| `venezuela` | 0.25× | Zelle, USDT | WhatsApp-first, 55% informal, 10 wedge categories |
| `latam` | 0.40× | Varies | WhatsApp 90%, informal 45% |
| `spain` | 1.0× | Card | EU regulatory context |
| `global` | 1.0× | Card | Default |

Venezuela wedge categories: payments, remittances, SMB software, retail/inventory, logistics, commerce trust, creator monetization, cross-border services, diaspora finance, AI labor replacement.

---

## Architecture

```
Harvest (HN / Reddit / Serper / Exa / Jina)
    ↓
Normalization (Pydantic schema, geo lens, bucket inference, noise filter)
    ↓
Kill Gate (7 criteria, 2+ fail = killed, no API tokens wasted on dead opps)
    ↓
AI Scoring (Claude Haiku batch, 16 dimensions, 1 API call per ≤10 opps)
    ↓
Scoring Engine (3-layer composite, Venezuela wedge bonus, portfolio normalisation)
    ↓
Enrichment Steps
  ├── 9.5  TAM estimation (4 methods, geo multipliers)
  ├── 9.6  TAM → market_size dimension wiring + rescore
  ├── 9.7  Benchmark mapping (8 archetypes)
  ├── 10   Customer Pain OS (templates + paid research, top 5)
  ├── 11   Distribution OS (channel templates + paid research, top 5)
  ├── 11.5 Research Executor (paid deep research, top 3 unresearched)
  ├── 11.6 Free Research (Tavily/HN/Reddit, top 20, zero cost)
  └── 11.7 Apify enrichment (LinkedIn jobs + G2 reviews, top 10)
    ↓
Step 12: Save ALL enriched opps back to JSONL (not just top 20)
    ↓
Reports (daily / LATAM / Venezuela / deep-dive / validation)
    ↓
Notion sync payload + CSV export + machine metrics
```

---

## Source layout

```
src/opportunity_os/
├── main.py                      # CLI (all commands)
├── models.py                    # Pydantic Opportunity schema + new data-backed fields
├── normalization.py             # Signal → Opportunity pipeline
├── storage.py                   # JSONL persistence, dedup, score history
├── ai_scorer.py                 # Claude Haiku batch scoring (claude-haiku-4-5)
├── geo_lens.py                  # Venezuela / LATAM adjustments
├── filters.py                   # Portfolio lane assignment
├── free_research.py             # Zero-cost enrichment
├── tavily_client.py             # search + search_news + search_with_content
├── firecrawl_client.py          # scrape_structured (competitor pages)
├── apify_client.py              # fetch_linkedin_jobs + fetch_g2_reviews
├── engines/
│   ├── scoring_engine.py        # 3-layer scoring + normalisation + data-backed sub-scores
│   ├── kill_gate.py             # 7-criteria gate
│   ├── tam_engine.py            # TAM estimation (4 methods)
│   └── benchmark_engine.py      # Archetype mapping (8 archetypes)
├── pipelines/
│   ├── daily_run.py             # Full 18-step daily pipeline
│   ├── enrichment.py            # Steps 9.7–11.7 (extracted for file-size compliance)
│   ├── signal_harvester.py      # Free signal sources
│   ├── deep_dive.py             # Deep dive report
│   ├── validation_run.py        # 8-section validation package
│   └── weekly_run.py            # Weekly review
└── dashboard_tabs/              # Streamlit 6-tab dashboard
    ├── components.py            # Design system (hero_card, subsection, radar_chart)
    ├── tab_command_center.py
    ├── tab_all_opportunities.py
    ├── tab_deep_dive.py
    ├── tab_pipeline_health.py
    ├── tab_venezuela_focus.py
    └── tab_weekly_ritual.py
```

---

## Data files

| Path | Description | git |
|------|-------------|-----|
| `data/opportunities/opportunities.jsonl` | Master store | ignored — back up manually |
| `data/backups/` | Pre-run snapshots | ignored |
| `data/machine_metrics.jsonl` | Run metrics | ignored |
| `data/raw/YYYY-MM-DD-signals.jsonl` | Harvested signals | ignored |
| `reports/` | Generated markdown reports | ignored |
| `exports/notion/` | CSV exports | ignored |

---

## Development

```bash
uv run pytest                           # 105 tests
uv run pytest -v -k "test_kill_gate"    # specific suite
uv run opp-os rescore-all --dry-run     # preview score changes
uv run opp-os free-research --top-n 20 # free enrichment pass
```

---

*Built with Claude Code — opportunity-os v2.0*
