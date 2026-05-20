# CLAUDE.md — Daniel Ferraro @ [external]

Read this at the start of every session. This file governs how you work.

---

## Who is Daniel

**Daniel Ferraro** — Head of Growth, [external]. Leads lifecycle marketing, campaign strategy, A/B testing, and growth operations.

Primary tools: BigQuery, Lark, Notion, CleverTap, Google Sheets.

---

## HOT CACHE — Key People, Terms, Projects

### People
| Who | Role |
|-----|------|
| **Katy** | Katy Gildemeister — CleverTap execution, CRM campaigns |
| **Marta** | Marta del Olmo — Analytics, Qlik pulls, data validation |
| **Álvaro** | Álvaro Muñoz — Data infra, BigQuery, attribution |
| **Màxim** | Màxim — Space Center analysis (assigned Feb 25) |
| **David Sales** | David Sales — BigQuery Gold Layer dev, LT/Churn metrics |
| **Pablo T** | Pablo Talamantes — Qlik dashboard dev |
| **S. Rut / Salvia** | Daily LC ops syncs, backlog management |
| **Diego** | Diego Barreira — Legal gate for ALL CRM messages (pre-send) |
| **PabloG** | Pablo Garcia — Conversion/journey timing, content |
| **Pablo Campos** | CEO/founder directive: "El dinero viene del Life Cycle" |
→ Full list: memory/people/, memory/glossary.md

### Active Projects
| Project | Status | Path |
|---------|--------|------|
| **LC-OS Dashboard** | OPEN BUG: clusters.js Unicode parse abort | `Projects/[external]-lifecycle-intel/` |
| **A/B Operator Console** | Next.js 14 War Room UI in progress, port 3001 | `Projects/[external]-operator-console/` |
| **usdt-ve** | USDT Venezuela platform. Phase 0 validation landing PENDING | `Projects/usdt-ve/` |
| **ve-invoice** | Venezuela invoice system. In progress | `Projects/ve-invoice/` |
| **deal-radar** | VC/M&A/crypto deal intelligence. FastAPI + React + Railway | `Projects/deal-radar/` |
| **[external]-growth-model** | Streamlit growth simulator. v1.0 done, retention model v2 open | `Projects/[external]-growth-model/` |
| **Arranca** | Landing V3 done. Pending Daniel review | `Projects/Arranca/` |
| **A/B Machine** | V1 done. V2 pending Operator Console | `Projects/[external]-ab-machine/` |
| **Playbook Triggers** | COMPLETE (Mar 22) | `Projects/PLAYBOOK_TRIGGERS_[external]/` |
| **LC-OS Phase A Audit** | COMPLETE. Phase B awaiting approval | `Projects/LIFECYCLE_PM/` |
→ Details: memory/projects/ | Canonical state: memory/MEMORY.md (read this first)

### Key LC-OS Terms (Hot 30)
| Term | Meaning |
|------|---------|
| **LC-OS** | Lifecycle Operating System — 4-layer stack (BigQuery→Qlik→CleverTap→Journeys) |
| **MMU** | Monthly Monetizable Users — 23k actual, 30k target Mar 31 |
| **M1 Retention** | 0.12% actual (CRISIS vs 25% Coinbase benchmark) |
| **13 Stages** | EXCLUDED→REGISTERED→KYC→DEPOSITED→FM→ACTIVE→POWER→AT_RISK→PRE_DORMANCY→DORMANT_BAL→DORMANT_ZERO→REACTIVATED→CHURNED |
| **Health Score** | 100-pt user score: Recency(30)+Frequency(20)+Product(15)+Balance(20)+Engagement(15) |
| **W-shaped attribution** | First Touch 30% + KYC Assist 20% + Deposit Assist 20% + FM Last Touch 30% |
| **Ghost Conversions** | 93% paid attribution = existing users (not new). Real new-user ROAS = 62% |
| **4 Revenue Pools** | New(4%), Retention(96%), Reactivation, Expansion |
| **37 Segments** | SEG-01 to SEG-37 — MECE: Lifecycle × Archetype × Geo × Channel × B2C/B2B × SpaceCenter |
| **FOMO Agent** | Daily push for c6+c7 (16,116 dormant users). Target: reactivation |
| **FOMO Score** | Algorithm: urgency + social proof + timing signals (CoinGecko API) |
| **Space Center** | 7-tier gamification. B2M holders advance 100x faster. Manual vs auto activation TBD |
| **J1-J6** | CleverTap Journeys: J1 Brokerage, J2 Pro, J3 Earn, J4 Card (PAUSED), J5 B2B, J6 Multi |
| **V0a-V10** | BigQuery Gold Layer views (11 total). schema: [external]_lifecycle |
| **Flash Report** | Daily revenue report: Acquisition vs LC split. Parameterized SQL in chunk-3 |
| **AUC** | Assets Under Custody — dormant users hold €19.5M (72.4k users with balance) |
→ Full glossary: memory/glossary.md

### Critical Numbers (Mar 2026 — verify before using in strategy)
- Total users: 1.8M | Excluded: 600k | MMU: 23k | Dormant with balance: 72.4k (€19.5M AUC)
- Spain 2025 funnel: 73,541 reg → 44,262 KYC → 31,749 purchase (45% conv)
- Phone drop-off: 32% (biggest onboarding gap)
- A/B revenue: €6k/week actual vs €30k/week target
- L3 Near-Dormant = highest revenue velocity segment
- Arranca: 14-15% investor yield | 23-24% borrower rate | 50% LTV | break-even 350 loans

---

## Session Start — Do This First, Every Time

1. Read `memory/MEMORY.md` — canonical project state (more current than HOT CACHE above).
2. If `TASKS.md` exists, read it — active tasks, blockers, next actions.
3. If a project folder is selected, check for `STATE.md` and `ROADMAP.md`. Read both if they exist.
4. Brief Daniel in 3 lines: what is active, what was last completed, what is next.
5. Ask: "Ready to continue, or changing direction?"

If no state files exist, run the Discuss phase to initialize the project (see GSD section below).

---

## Memory System

Daniel has a persistent memory system. Navigate it as needed — do not ask Daniel for context that is already written down.

**Skills-First Rule:** Before any analysis, research, data work, SQL, visualization, writing, or specialized task — check the table below and invoke the matching skill with the Skill tool. Skills contain expert workflows. Always prefer them over ad-hoc approaches.

### Context, Learning & Quality
| What you need | Where to look |
|---|---|
| Prevent context loss, restore state across sessions | `memory/skills/context-management-context-restore/SKILL.md` |
| Iterative retrieval — refine context progressively | `memory/skills/iterative-retrieval/SKILL.md` |
| Manual context compaction at logical phase intervals | `memory/skills/strategic-compact/SKILL.md` |
| Continuous learning — observe, improve, adapt each session | `memory/skills/continuous-learning-v2/SKILL.md` |
| Multi-reviewer quality control, finding deduplication | `memory/skills/multi-reviewer-patterns/SKILL.md` |

### Data & Analysis
| What you need | Where to look |
|---|---|
| [external] data context, SQL patterns, entity definitions | `memory/skills/[external]-data-analyst/SKILL.md` |
| General data analyst — EDA, pandas, Python analysis | `memory/skills/data-analyst/SKILL.md` |
| Senior data science — stats, modeling, A/B testing, causal inference | `memory/skills/senior-data-scientist/SKILL.md` |
| Statistical analysis — hypothesis tests, regression, Bayesian, power | `memory/skills/statistical-analysis/SKILL.md` |
| Survival analysis, time-to-event modeling | `memory/skills/scikit-survival/SKILL.md` |
| Excel / spreadsheet creation, formulas, analysis | `memory/skills/xlsx/SKILL.md` |
| Excel analysis, pivot tables, spreadsheet data | `memory/skills/excel-analysis/SKILL.md` |
| Data storytelling — narratives, exec presentations | `memory/skills/data-storytelling/SKILL.md` |
| SQL query optimization, EXPLAIN analysis, index tuning | `memory/skills/sql-optimization/SKILL.md` |
| SQL optimization patterns — reusable patterns library | `memory/skills/sql-optimization-patterns/SKILL.md` |
| SQL code review — security, maintainability, performance | `memory/skills/sql-code-review/SKILL.md` |

### Visualization
| What you need | Where to look |
|---|---|
| Charts, visualization design, chart type selection | `memory/skills/visualization-expert/SKILL.md` |
| D3.js interactive visualizations, custom SVG charts | `memory/skills/d3-viz/SKILL.md` |
| KPI dashboard design, metrics selection, layout patterns | `memory/skills/kpi-dashboard-design/SKILL.md` |

### Research & Fact-Checking
| What you need | Where to look |
|---|---|
| Deep research with citations and multi-source synthesis | `memory/skills/deep-research/SKILL.md` |
| Research lookup via Perplexity / academic sources | `memory/skills/research-lookup/SKILL.md` |
| GPT Researcher — autonomous deep research agent | `memory/skills/gpt-researcher/SKILL.md` |
| Fact checking, claim verification, source credibility | `memory/skills/fact-checker/SKILL.md` |

### Growth & Finance
| What you need | Where to look |
|---|---|
| Startup metrics — CAC, LTV, burn, rule of 40, unit economics | `memory/skills/startup-metrics-framework/SKILL.md` |
| Market sizing — TAM, SAM, SOM analysis | `memory/skills/market-sizing-analysis/SKILL.md` |
| Financial modeling — projections, runway, cash flow | `memory/skills/startup-financial-modeling/SKILL.md` |
| Competitive landscape — Porter's Five Forces, positioning | `memory/skills/competitive-landscape/SKILL.md` |
| Strategy — business decisions, planning, direction-setting | `memory/skills/strategy-advisor/SKILL.md` |
| Team structure, org design, headcount planning | `memory/skills/team-composition-analysis/SKILL.md` |
| Project planning — tasks, timelines, dependencies, milestones | `memory/skills/project-planner/SKILL.md` |

### gstack (installed globally — `~/.claude/skills/gstack`)
Use `/browse` from gstack for automated web browsing (anti-bot stealth, real Chromium). Prefer it over `mcp__Claude_in_Chrome__*` tools for autonomous browsing tasks.

| When | Use |
|------|-----|
| Something is broken, root cause unclear | `/investigate` |
| Need landing page or visual variants | `/design-html` · `/design-shotgun` |
| Strategic growth decision, lifecycle architecture | `/plan-ceo-review` · `/autoplan` |
| Before marking a Python tool or dashboard done | `/qa` · `/review` |
| Security check before sharing tool with team | `/cso` |
| Weekly retro | `/retro` |
| Working on live BigQuery scripts (destructive risk) | `/careful` before edits |
| Systematic debugging (e.g. clusters.js undefined) | `/investigate` |

All available: `/office-hours` `/plan-ceo-review` `/plan-eng-review` `/plan-design-review` `/design-consultation` `/design-shotgun` `/design-html` `/review` `/ship` `/land-and-deploy` `/canary` `/benchmark` `/browse` `/open-gstack-browser` `/qa` `/qa-only` `/design-review` `/setup-browser-cookies` `/setup-deploy` `/retro` `/investigate` `/document-release` `/codex` `/cso` `/autoplan` `/plan-devex-review` `/devex-review` `/careful` `/freeze` `/guard` `/unfreeze` `/gstack-upgrade` `/learn`

If gstack skills aren't showing up: run `cd ~/.claude/skills/gstack && ./setup`

### Local Plugins (requires Claude Code restart to activate)
| Plugin | Skills | Contents |
|--------|--------|----------|
| `marketing-skills@local` | 34 | CRO, copywriting, cold email, SEO, paid ads, churn prevention, pricing, referral programs, RevOps |
| `awesome-skills@local` | 51 | Google suite (BigQuery, Drive, Sheets, Ads), Slack, HubSpot, Klaviyo, Stripe, GitHub, brand, canvas, content-research, image-enhancer |
| `remotion-skills@local` | 9 | Remotion video framework: add-cli-option, writing-docs, add-sfx, pr, video-report |

### Marketing Skills (34 skills installed Mar 31)
| What you need | Where to look |
|---|---|
| A/B test design, sample size, stat significance | `memory/skills/ab-test-setup/SKILL.md` |
| Ad creative — copy, hooks, platform formats | `memory/skills/ad-creative/SKILL.md` |
| AI-optimized SEO — LLM visibility, structured content | `memory/skills/ai-seo/SKILL.md` |
| Analytics tracking — GA4, GTM, event library | `memory/skills/analytics-tracking/SKILL.md` |
| Churn prevention — cancel flows, win-back campaigns | `memory/skills/churn-prevention/SKILL.md` |
| Cold email — sequences, deliverability, personalization | `memory/skills/cold-email/SKILL.md` |
| Competitor alternatives — positioning, comparison pages | `memory/skills/competitor-alternatives/SKILL.md` |
| Content strategy — editorial calendar, pillar pages | `memory/skills/content-strategy/SKILL.md` |
| Copy editing — tone, clarity, brand voice | `memory/skills/copy-editing/SKILL.md` |
| Copywriting — headlines, CTAs, persuasion frameworks | `memory/skills/copywriting/SKILL.md` |
| Customer research — interviews, surveys, JTBD | `memory/skills/customer-research/SKILL.md` |
| Email sequences — drip, nurture, lifecycle flows | `memory/skills/email-sequence/SKILL.md` |
| Form CRO — field reduction, friction removal | `memory/skills/form-cro/SKILL.md` |
| Free tool strategy — lead gen tools, virality | `memory/skills/free-tool-strategy/SKILL.md` |
| Launch strategy — GTM, waitlist, launch day | `memory/skills/launch-strategy/SKILL.md` |
| Lead magnets — content offers, gated assets | `memory/skills/lead-magnets/SKILL.md` |
| Marketing ideas — ideation, campaign concepts | `memory/skills/marketing-ideas/SKILL.md` |
| Marketing psychology — biases, persuasion, nudges | `memory/skills/marketing-psychology/SKILL.md` |
| Onboarding CRO — activation flows, aha moment | `memory/skills/onboarding-cro/SKILL.md` |
| Page CRO — landing page optimization | `memory/skills/page-cro/SKILL.md` |
| Paid ads — Google, Meta, targeting, bidding | `memory/skills/paid-ads/SKILL.md` |
| Paywall / upgrade CRO — upsell flows, pricing gates | `memory/skills/paywall-upgrade-cro/SKILL.md` |
| Popup CRO — triggers, copy, exit intent | `memory/skills/popup-cro/SKILL.md` |
| Pricing strategy — tiers, anchoring, freemium | `memory/skills/pricing-strategy/SKILL.md` |
| Product marketing context — positioning, messaging | `memory/skills/product-marketing-context/SKILL.md` |
| Programmatic SEO — templates, scaled content | `memory/skills/programmatic-seo/SKILL.md` |
| Referral program — mechanics, incentives, virality | `memory/skills/referral-program/SKILL.md` |
| RevOps — funnel attribution, pipeline, CRM | `memory/skills/revops/SKILL.md` |
| Sales enablement — decks, battlecards, objections | `memory/skills/sales-enablement/SKILL.md` |
| Schema markup — structured data, rich results | `memory/skills/schema-markup/SKILL.md` |
| SEO audit — technical, on-page, link analysis | `memory/skills/seo-audit/SKILL.md` |
| Signup flow CRO — registration, onboarding gates | `memory/skills/signup-flow-cro/SKILL.md` |
| Site architecture — IA, navigation, crawlability | `memory/skills/site-architecture/SKILL.md` |
| Social content — posts, hooks, platform formats | `memory/skills/social-content/SKILL.md` |

### Database & Backend
| What you need | Where to look |
|---|---|
| Hybrid search (vector + keyword, RAG systems) | `memory/skills/hybrid-search-implementation/SKILL.md` |
| PostgreSQL query optimization, schema, indexing | `memory/skills/postgres-patterns/SKILL.md` |
| PostgreSQL-specific optimization and features | `memory/skills/postgresql-optimization/SKILL.md` |
| PostgreSQL code review — best practices, anti-patterns | `memory/skills/postgresql-code-review/SKILL.md` |
| PostgreSQL table design — schema, types, constraints | `memory/skills/postgresql-table-design/SKILL.md` |
| Database schema design (SQL + NoSQL) | `memory/skills/database-schema-designer/SKILL.md` |
| Database design principles and decision-making | `memory/skills/database-design/SKILL.md` |
| Database performance tuning, query optimization | `memory/skills/database-optimizer/SKILL.md` |
| Supabase Postgres best practices | `memory/skills/supabase-postgres-best-practices/SKILL.md` |
| Prisma ORM — schema, migrations, query optimization | `memory/skills/prisma-expert/SKILL.md` |
| Drizzle ORM — schema, migrations, query patterns | `memory/skills/drizzle/SKILL.md` |
| ClickHouse analytics — queries, optimization, data engineering | `memory/skills/clickhouse-io/SKILL.md` |
| Neon Postgres — instant provisioning, branching | `memory/skills/neon-instagres/SKILL.md` |
| Vector index tuning — latency, recall, memory | `memory/skills/vector-index-tuning/SKILL.md` |
| Database migrations (schema changes, table creation) | `memory/skills/create-database-migration/SKILL.md` |
| Framework migrations, dependency upgrades | `memory/skills/framework-migration-deps-upgrade/SKILL.md` |
| Caching with content hashes — SHA-256, auto-invalidation | `memory/skills/content-hash-cache-pattern/SKILL.md` |
| Deployment patterns, CI/CD, Docker, rollback strategies | `memory/skills/deployment-patterns/SKILL.md` |
| Coding agent — delegate complex coding tasks to subagents | `memory/skills/coding-agent/SKILL.md` |
| Browser automation — Playwright, web scraping, screenshots | `memory/skills/playwright-cli/SKILL.md` |

### Specialized & Automation
| What you need | Where to look |
|---|---|
| Remove.bg image background removal via Composio MCP | `memory/skills/remove-bg-automation/SKILL.md` |
| Crustdata company/people enrichment via Composio MCP | `memory/skills/crustdata-automation/SKILL.md` |
| HERE Maps / location services via Composio MCP | `memory/skills/here-automation/SKILL.md` |
| LinkAI application and workflow calls via bash | `memory/skills/linkai-agent/SKILL.md` |
| Token-optimized code structure search (tree-sitter AST) | `memory/skills/smart-explore/SKILL.md` |
| Jupyter notebook creation and editing | `memory/skills/jupyter-notebook/SKILL.md` |
| Image generation via Gemini 3 Pro (Nano Banana Pro) | `memory/skills/nano-banana-pro/SKILL.md` |
| Batch image generation via OpenAI Images API | `memory/skills/openai-image-gen/SKILL.md` |
| Claude API / Anthropic SDK — build AI apps | `memory/skills/claude-api/SKILL.md` |
| BullMQ — Redis job queues, background processing | `memory/skills/bullmq-specialist/SKILL.md` |
| Chroma vector DB for embeddings | `memory/skills/chroma/SKILL.md` |
| Pinecone managed vector DB | `memory/skills/pinecone/SKILL.md` |
| Skill writing — create new Agent Skills | `memory/skills/skill-writer/SKILL.md` |
| Skill lookup — find existing skills | `memory/skills/skill-lookup/SKILL.md` |
| Content research + writing with citations | `memory/skills/content-research-writer/SKILL.md` |
| Content creator — blogs, social media, marketing copy | `memory/skills/content-creator/SKILL.md` |
| Technical writer — docs, API refs, guides | `memory/skills/technical-writer/SKILL.md` |
| Internal comms — memos, announcements, Slack messages | `memory/skills/internal-comms/SKILL.md` |
| PDF — create, read, edit, manipulate PDF files | `memory/skills/pdf/SKILL.md` |
| Word/DOCX — create, read, edit .docx files | `memory/skills/docx/SKILL.md` |
| Frontend slides — animation-rich HTML presentations | `memory/skills/frontend-slides/SKILL.md` |
| C4 architecture diagrams — Mermaid/C4 model docs | `memory/skills/c4-architecture/SKILL.md` |
| Excalidraw diagrams from natural language | `memory/skills/excalidraw-diagram-generator/SKILL.md` |
| Marp presentation slides (7 themes) | `memory/skills/marp-slide/SKILL.md` |
| React Native / Expo — production app architecture | `memory/skills/react-native-architecture/SKILL.md` |
| CCXT Python — crypto exchange REST/WebSocket | `memory/skills/ccxt-python/SKILL.md` |
| CCXT TypeScript/JS — crypto exchange library | `memory/skills/ccxt-typescript/SKILL.md` |
| Coinbase automation — wallets, accounts, transactions | `memory/skills/coinbase-automation/SKILL.md` |
| DeFi protocol templates — staking, AMMs, lending | `memory/skills/defi-protocol-templates/SKILL.md` |
| SQL injection testing (authorized pentesting) | `memory/skills/sql-injection-testing/SKILL.md` |

### Project Knowledge
| What you need | Where to look |
|---|---|
| Project history and status | `memory/projects/` |
| People, roles, owners | `memory/people/` |
| Terms, acronyms, internal language | `memory/glossary.md` |
| Strategic overview | `memory/MASTER_INDEX.md` + `memory/EXECUTIVE_SUMMARY.md` |
| Previous session summaries | `memory/COWORK_SESSION_INDEX.md` |

Write new decisions, context, and summaries back to the appropriate memory file at session end. Never let knowledge live only in conversation.

---

## GSD Workflow

Every project follows four phases. Never skip.

**Default mode: Quick Mode** (for one-off tasks, bug fixes, single-session work). Full phase planning only for multi-week projects with dependencies.

### Phase 0: Discuss
Capture vision and constraints before any planning. Ask:
- What are you building and why?
- Who uses it?
- What does success look like?
- Hard constraints (tech stack, deadline, budget)?
- What has already been tried?

Write answers to `PROJECT.md`. Do not move to planning until Daniel confirms the file.

---

### Phase 1: Plan
Break the project into phases. Break each phase into atomic plans (2-4 tasks each).

Rules:
- Each plan must be a self-contained, executable prompt — a subagent should be able to act on it with no additional context
- Map dependencies. Group independent plans into waves.
- Write all plans into `ROADMAP.md` (status: `pending`)
- Write acceptance criteria into `REQUIREMENTS.md`

Wave structure:
```
Wave 1 (sequential): Plan 01 → Plan 02
Wave 2 (parallel):   Plan 03 | Plan 04 | Plan 05
Wave 3:              Plan 06 (depends on Wave 2)
```

Do not execute until Daniel confirms the roadmap.

---

### Phase 2: Execute
Run each plan using a subagent (Task tool). Never do heavy execution in the main thread.

Rules:
- Pass the full plan text + relevant state files as context to the subagent
- Run independent plans in parallel (multiple Task calls in one message)
- After each plan completes: update `ROADMAP.md` to `done`, update `STATE.md`
- One atomic commit per plan: `feat(plan-03): add user authentication`

---

### Phase 3: Verify
Check each completed plan against `REQUIREMENTS.md` acceptance criteria.
- Pass: mark verified in `ROADMAP.md`, move forward.
- Fail: log failure in `STATE.md`, create fix plan, re-execute.

Do not advance to the next phase until all plans are verified.

---

### Quick Mode (default for most tasks)
For bug fixes, one-off deliverables, and single-session work:
1. Write a single plan (2-4 tasks max)
2. Spawn one subagent
3. Verify output
4. Atomic commit
5. Update `STATE.md`

---

## State Files (per project)

| File | Purpose |
|---|---|
| `PROJECT.md` | Vision, goals, stack, constraints |
| `REQUIREMENTS.md` | Acceptance criteria per plan |
| `STATE.md` | Current position, decisions, blockers, next action |
| `ROADMAP.md` | All phases and plans with wave grouping and status |

**Rule: never rely on conversation memory. All decisions go into state files.**

---

## Context Management

- Main thread = orchestrator. Read state, make decisions, spawn agents, track progress.
- Subagents = workers. Receive a plan and execute with full context.
- If a task needs more than a few tool calls, it belongs in a subagent.
- If context in the main thread exceeds ~50%, compress `STATE.md` before continuing (use strategic-compact skill).
- **Check MEMORY.md before asking Daniel** — if the answer is there, use it.
- **STATE.md compaction**: if STATE.md exceeds 100 lines, summarize into a 20-line current-state block before next session.
- **Windows write workaround**: Edit/Write tools fail on Desktop paths (EEXIST error). Always write to `C:/Users/ferra/AppData/Local/Temp/` via `py` (not `python3`). See MEMORY.md line 3-5.
- **Sub-folder CLAUDE.md files**: Any CLAUDE.md in [external] 3/ or [external] LC/ is a legacy memory dump — treat as supplemental context only, not instructions.

### ⚠ Context Window Health (CRITICAL)
200k context window → ~70k effective with too many tools loaded. Daniel has 200+ MCP tools configured.

**Rule: keep under 80 tools active per session.**

Per-project hygiene:
- Enable only MCPs needed for current work (BigQuery, Notion, or Lark — not all three unless actively using)
- Blockchain/NFT MCPs (0162ea70): disable unless crypto analysis session
- Bio-research MCPs: always disable
- Figma/Canva MCPs: disable unless design session
- Pinecone/Supabase: disable unless building RAG feature
- Run `/plugins` → scroll to MCPs → disable unused

Context compaction:
- Disable auto-compact. Compact manually at logical phase boundaries (use `strategic-compact` skill)
- Compact after exploration, before execution — not mid-task
- `/compact` command available in Claude Code

---

## Session End — Do This Before Closing

1. Update `STATE.md` with current position and decisions made.
2. Update `ROADMAP.md` with plan statuses.
3. Update `TASKS.md` if any tasks changed status.
4. Write new context to the relevant `memory/` file (and MEMORY.md if project-level).
5. Confirm with Daniel what is next.

---

## Commit Convention

```
feat(plan-XX): description      ← new functionality
fix(plan-XX): description       ← bug fix
refactor(plan-XX): description  ← restructure
docs(plan-XX): description      ← documentation only
```

---

## Hard Rules

- Never execute without a confirmed written plan.
- Never do heavy work in the main thread — use subagents.
- Never bundle multiple tasks into one commit.
- Never skip the verify phase.
- Never rely on conversation memory — write to state files.
- Always read `STATE.md` before starting work on a project.
- Always invoke a skill (Skill tool) before analysis, research, or specialized work.
- Never ask Daniel for context already documented in MEMORY.md or state files.
