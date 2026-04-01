# COWORK SESSION INDEX

---

## SESSION: 2026-03-10 — Phase A Desktop Audit (11 PM Documents)

**Date**: 2026-03-10
**Topic**: Full Phase A audit of Desktop filesystem for LC-OS project. Produced 11 PM documents as canonical project management layer.
**Files produced**:
- `LIFECYCLE_PM_00_MASTER_INVENTORY.md` (7,351 bytes) — full file catalog
- `LIFECYCLE_PM_01_SOURCE_OF_TRUTH.md` (6,185 bytes) — canonical SOT per workstream
- `LIFECYCLE_PM_02_CURRENT_STATE.md` (6,974 bytes) — honest current state all layers
- `LIFECYCLE_PM_03_BLOCKERS_RACI.md` (7,081 bytes) — 9 blockers, full RACI 15 people
- `LIFECYCLE_PM_04_MASTER_BACKLOG.md` (7,505 bytes) — 55 work items P0-P3
- `LIFECYCLE_PM_05_ROADMAP_30_60_90.md` (5,814 bytes) — 30/60/90 day roadmap
- `LIFECYCLE_PM_06_FILE_MAP.md` (7,757 bytes) — bidirectional task-to-file lookup
- `LIFECYCLE_PM_07_DECISION_LOG.md` (3,443 bytes) — 23 decisions logged
- `LIFECYCLE_PM_08_RISKS_AND_GAPS.md` (4,362 bytes) — 15 risks, coverage gaps
- `LIFECYCLE_PM_09_EXEC_SUMMARY.md` (2,973 bytes) — one-pager for Pablo Campos
- `LIFECYCLE_PM_10_RECOMMENDED_RESTRUCTURE.md` (4,097 bytes) — Phase B plan

### What happened
- Write tool fails on Windows OneDrive Desktop (EEXIST mkdir error) — permanent issue
- Workaround established: python3 -c with triple-quoted strings (no double quotes in content)
- For content with double quotes: write .py script to AppData/Local/Temp, execute via Bash
- All 11 files confirmed written (ls -la verification)
- Executive readout delivered in chat: 10 findings, 10 conflicts, canonical SOTs, Phase B prompt
- LC_PROJECT_STATE.md and COWORK_SESSION_INDEX.md updated per GSD/memory protocol

### Key findings from audit
- J-Post-FM 48h = #1 critical gap (60% D+7 drop, ZERO coverage, no owner)
- 6 duplicate file groups causing confusion across Bit2me LC / Lifecycle 2 / Bit2me 3 folders
- InApp UTM gap = invisible revenue (13.93% CTR -> EUR 0 Qlik attribution)
- C8 Suppression CSV not uploaded to CleverTap (risk: whale exposure)
- Diego bottleneck: 7/9 journeys blocked behind single legal gate
- Álvaro SPOF: V0a, token-holder filter, attribution — 3 P0 items on 1 person

### Phase B status
NOT started. Awaiting explicit approval from Daniel.

---


## SESSION: 2026-03-09 — W10 Lifecycle Team Plan + Pablo Deliverables

**Date**: 2026-03-09
**Topic**: Full W10 plan for LC team — Pablo CEO evaluation context, Maxim ownership assignment, A/B replication launch, communications to all stakeholders
**Files produced**:
- `W10_MASTER_PLAN_260309.md` — 11-section W10 plan with day-by-day tasks
- `W10_Pablo_Deliverables.xlsx` — Excel workbook (3 sheets: AB Calendar, LC Metrics, Instrucciones)
- `create_pablo_deliverables.py` — Python/openpyxl script generating the Excel
- `W10_Comms_260309.md` — 5 internal comms (3P update, Maxim script, Katy msg, Álvaro msg, Pablo Friday msg)
- Scheduled task: `maxim-weekly-reporting-check` (every Monday 16:00 local)

### What happened
- Pablo Campos furious at Maxim's weak plan — evaluation in 2 weeks
- Pablo demands: (1) weekly A/B Calendar and (2) weekly LC Metrics from Maxim
- Confirmed: Maxim HAS Qlik access ("si tiene")
- Synthesized ALL lifecycle research: health score, W08-W09 A/B results, 13-stage model, 37 segments, LC-OS V0a status
- Created Excel workbook with formula-driven WoW% and vs Target% calculations (not hardcoded values)
- Fixed Python TypeError: `Font()` not `ifont()` with bold param
- Created conversation script for Daniel→Maxim in Castellón today

### Key decisions locked in
- **Maxim ownership**: weekly A/B Calendar + LC Metrics, first delivery today 17:00
- **REP-2**: `W10_SEN_BTC_HV_260303` activated (pending Diego OK → Katy config → Tue Mar 10 send). Decision: Mar 17
- **REP-1**: BLOCKED on Álvaro token-holder filter (ETA Thu Mar 12). Decision: Mar 17
- **REP-3**: BLOCKED on UTM staging confirmation (ETA Mar 10). Decision: Mar 10
- **C6+C7 diagnosis**: Do NOT run more copy tests until post-click UX drop-off resolved
- **Space Center**: Maxim delivers by Thu Mar 12 for W11 brief

### Skills used
- `superpowers:writing-plans` — plan structure
- `anthropic-skills:xlsx` — Excel workbook with formula-based calculations
- `anthropic-skills:internal-comms` — 5 communication pieces (3P + scripts + direct messages)
- `anthropic-skills:ab-test-setup` — A/B test card formalization
- `anthropic-skills:schedule` — Monday weekly reporting reminder (scheduled task)
- `memory/skills/data-storytelling/SKILL.md` — Pablo narrative framework

### Memory updated
- `memory/projects/ab-testing.md` — W10 campaign status (REP-2 ACTIVE, REP-1 BLOCKED, REP-3 PENDING)
- `TASKS.md` — W10 assignments with owners + blockers + ETAs
- `COWORK_SESSION_INDEX.md` — this entry

---

## SESSION: 2026-03-05 — Dashboard v2 Smoke Test + Verify

**Date**: 2026-03-05
**Topic**: Complete smoke test of all 16 dashboard tabs + verify v2, fix dormant-matrix bug
**Files produced**: STATE.md (smoke test results added), app/routers/reactivation.py (dormant-matrix endpoint), memory/projects/lifecycle-intel-dashboard.md (NEW)

### What happened
- Completed visual smoke test of all 16 dashboard tabs at localhost:8000 via JS click navigation
- Ran API smoke test via curl: 20/20 endpoints confirmed 200 (used /openapi.json to discover correct route names — many non-obvious e.g. `/abtesting/dashboard` not `/experimentation/overview`)
- Found and fixed bug: `reactivation-enhance.js` called `/api/v1/reactivation/dormant-matrix` but router only had `/overview`. Added full dormant-matrix endpoint (6×6 balance-tier × login-recency heatmap)
- Found stale uvicorn process (PID 13328) running pre-P1 code — killed + restarted
- Console check: 0 app errors (2 extension-level errors from accessibility tree tool, not app code)
- Tagged v2 as VERIFIED in STATE.md
- Committed: `36e1eb2`

### Key technical patterns locked in
- **JS tab navigation**: `document.querySelector('[data-tab="X"]').click()` — reliable, survives page state changes
- **Route discovery**: Always use `/openapi.json` — NEVER guess API paths (many are non-obvious)
- **Git on Windows**: `git.exe -C 'C:/Users/ferra/...'` with forward slashes, calling Windows git.exe binary (wslpath not available)
- **Uvicorn gotcha**: Stale processes from prior sessions run old code — kill + restart before testing

### V2 smoke test results
- API: 20/20 PASS
- Visual: 16/16 PASS (2 tabs disabled intentionally: activation, spacecenter)
- Console: 0 app errors
- Market Context: LIVE data from CoinGecko (BTC $71,570, F&G 22, 30d chart)

### Memory updated
- memory/projects/lifecycle-intel-dashboard.md — CREATED (full dashboard project knowledge)
- bit2me-lifecycle-intel/STATE.md — updated with smoke test evidence + next steps

---

## SESSION: 2026-03-04 — W10 A/B Analysis + Replication Logic

**Date**: 2026-03-04
**Topic**: W08-W09 A/B test analysis, E1-Riesgo critique, W10 replication campaign design
**Files produced**: W10_Launches_Today_260303.md, W10_Replication_Logic_260303.md, W10_AB_Test_Briefs_Formal_260303.md, W10_Clear_Logic_260303.md

### What happened
- Ran full analysis of AB_Testing_Tracker_Bit2Me_v7.xlsx (Pruebas, Qlik, CleverTap, Significancia sheets)
- Applied Bonferroni correction to 8 simultaneous tests → only 2 survive: DOT-HV (p_adj=0.029) and V3-BTC-HV (p_adj<0.001)
- Diagnosed W08-W09 main flaw: 86/14 split imbalance → MDE=193%, impossible to detect real effects
- Confirmed Endowment Effect frame wins consistently: "Revisa tu portfolio / Movimiento en [token]" beats price-data copy
- Diagnosed E1-Riesgo (Mar 2): 8.77% CTR but 2 transactions. Root cause = C6+C7 UX friction, not copy problem
- Diagnosed InApp attribution gap: missing UTM → €0 Qlik revenue despite 13.93% CTR
- Designed 3 W10 replications with full Clear Logic (Evidence → Gap → Hypothesis → Design → What we'll learn)

### Key numbers locked in
- DOT-HV Var A: 201 trans, €538.52 revenue, 54 TAUs, p_bonf=0.029
- V3-BTC-HV Var A: 303 trans, €597.75 revenue, 80 TAUs, p_bonf<0.001
- E1-Riesgo: 3,935 sent, 36.87% open, 8.77% CTR, 2 transactions, €5.89
- InApp T2 Activos: 13.93% CTR, €0 Qlik (UTM missing)
- CAMBIO24H_V2 Var B: €91.24/TAU (anomalous, minority arm — investigate W11)

### Decision rule locked in
Replication qualifies only if: p_bonf < 0.05 AND pattern confirmed in ≥2 distinct waves.

### Pending (execution, not Claude tasks)
- Diego approves copy for REP-1, REP-2, REP-3
- Juan Fornell confirms C9 universe size
- Álvaro builds token-holder filter for REP-1
- Katy sets up 3 campaigns in CleverTap
- UTM staging test for REP-3 before activation

### Memory updated
- memory/projects/ab-testing.md — full W08-W10 results + rules
- TASKS.md — W10 launches + C6C7 diagnosis added as In Progress

---

# COWORK SESSION EXTRACTION - INDEX (2026-02-24)
**Extraction Date**: 2026-02-24  
**Session ID**: aa354d00-f848-4558-a240-3a726a9507b0  
**Agent ID**: a0bb373 (subagent for research)

---

## QUICK REFERENCE

### Session Topic
**Building a Specialized AI Agent for Bit2Me Lifecycle A/B Testing Dashboard**

### Key Stakeholder
**Daniel Ferraro**, Head of Growth / LC Lead at Bit2Me

### Duration & Effort
- Research phase: ~107 seconds of active agent work
- Total tokens: 58,342
- Tool uses: 9 (web search, task delegation, todo management)

---

## EXTRACTED FILES

### 1. **SESSION_SUMMARY.md** (221 lines)
**Quick overview of strategic decisions and recommendations**

Contents:
- Key strategic discussion summary
- Recommended 3-tier architecture (Agent → MCP Servers → Data Sources)
- Core components breakdown
- Proposed agent use cases (4 examples)
- Data infrastructure requirements
- Immediate next steps
- Key decision: Qlik vs. Direct DB access
- Estimated effort: 12-17 days across 5 phases
- Follow-up question blocking Phase 2

**Read this first** for quick context on decisions made.

---

### 2. **PREV_SESSION_EXTRACTED.md** (978 lines)
**Full conversation transcript with all tool results and research output**

Contents:
- Complete user-agent exchange (13 messages)
- Detailed research on Claude Agent SDK
- MCP (Model Context Protocol) deep dive
- Claude Code plugin architecture
- Cowork plugin structure
- BigQuery, Snowflake, and Bitquery integration approaches
- Sample code examples
- Comprehensive resource links

**Read this for** detailed technical information and research findings.

---

## STRATEGIC CONTENT EXTRACTED

### Bit2Me-Specific Insights

**Problem Statement**
- Daniel needs an analytics dashboard for A/B testing lifecycle interventions
- Reference exists: "Poly" (colleague's brokerage analytics agent)
- Multiple data sources (Qlik, CleverTap, BigQuery) need orchestration
- Manual analysis work blocks Daniel from strategic role

**Proposed Solution Architecture**
```
User Query → Claude Agent (in Cowork) → MCP Servers → Data Sources
                        ↓
            [Skills: A/B Design, Retention Analysis, Stat Testing]
```

**Three Key Data Sources**
1. **CleverTap** - User journeys, events, segments (lifecycle-critical)
2. **Qlik** - Pre-built BI metrics, dashboards
3. **BigQuery/Internal DB** - User attributes, clustering, transaction data
4. **Bitquery** (optional) - On-chain crypto validation

**Most Important Finding**
> "80% of effort is data plumbing (MCP servers, schema docs, API integration). 20% is the agent itself."

### Critical Success Factors
1. Clean schema documentation (must be accurate for Claude to navigate)
2. Reliable API connectivity (CleverTap, Qlik, BigQuery)
3. User feedback loop (iterate skills based on actual LC team usage)
4. Statistical guardrails (minimum sample sizes, significance thresholds, MDE)
5. Governance (define what agent cannot do: compliance, financial decisions)

---

## ANTHROPIC TOOLS RESEARCH RESULTS

### Recommended Stack

| Layer | Tool | Purpose | Status |
|-------|------|---------|--------|
| **Intelligence** | Claude Agent SDK (Python/TypeScript) | Autonomous decision-making, tool orchestration | Available, stable |
| **Data Bridge** | MCP Servers (custom) | CleverTap, Qlik, BigQuery connectors | Need custom build |
| **Code Execution** | Claude Code | Analysis, visualization, data processing | Available |
| **Packaging** | Cowork Plugin | Shareable interface, skill definitions | Recommended |

### Key Technical Decisions

1. **MCP Over Direct API Calls**
   - MCP = standard protocol for Claude ↔ External System
   - Each data source gets an MCP server
   - Agent queries via unified interface

2. **Qlik vs. Direct Database**
   - Recommendation: Bypass Qlik, connect to underlying DB
   - Faster queries, more flexible joins
   - Use Qlik as reference for "which tables matter"

3. **Skills-Based Agent Design**
   - Not a single "do everything" agent
   - Multiple specialized skills: data exploration, A/B design, retention analysis, stat testing
   - Skills = instruction sets that enforce best practices

---

## NEXT PHASE BLOCKERS

**Question from Agent (awaiting Daniel response)**:
> "If you can connect me to the data (share schemas, API docs, or sample exports), I can start designing the agent architecture in detail, write the skill definitions, and help spec out the MCP servers. **What does your current data setup look like?**"

**Daniel Must Provide**:
1. Database architecture diagram (BigQuery? Postgres? Snowflake?)
2. CleverTap API documentation + available events/attributes
3. Qlik schema/available fields
4. Bitquery integration preferences (critical vs. nice-to-have?)
5. Top 10 most-asked queries from LC team

---

## ALIGNMENT WITH CLAUDE.MD PRIORITIES

**Related to Daniel's Active Projects**:
- **Lifecycle Definition** (HIGHEST PRIORITY) - Agent would accelerate this
- **LC Daily Syncs** - Could be automated with agent insights
- **CleverTap A/B Tests** (T1, T2, T3) - Agent provides statistical rigor
- **Loan Journey** (launching Feb 26) - Segment analysis automation
- **Flash Diario Growth** - Agent outputs could feed dashboard

**Aligns with Pablo Campos Directives**:
- **Daniel's role**: STRATEGIST (not operational data work)
- **This agent reduces** manual analysis, freeing Daniel for strategy
- **"Cuando domines los datos es cuando empezará lo bueno"** - Agent enables data mastery

---

## RESEARCH RESOURCES PROVIDED

### Anthropic Official Documentation
- Claude Agent SDK Quickstart
- Tool Use Overview
- Claude Code Plugin Documentation
- Model Context Protocol Specification (v2025-11-25)

### Data Integration (MCP)
- BigQuery MCP Server Documentation
- Fully Managed Remote BigQuery MCP Server
- Google Official MCP Support Announcement
- Snowflake + CData Connect AI approach

### Related Frameworks
- Claude Skills Best Practices
- Anthropic Engineering: Demystifying Evals for AI Agents

---

## SESSION TIMELINE

| Phase | What Happened | Duration |
|-------|---------------|----------|
| **Initial Request** | Daniel explains need for lifecycle A/B dashboard agent | User message |
| **Research Delegation** | Agent researches Anthropic tools, MCP, Agent SDK | Task + WebSearch tools |
| **Planning** | Agent synthesizes research findings | Internal thinking |
| **Architecture Design** | Agent proposes 3-tier architecture with MCP servers | Text output |
| **Blocking Issue** | Agent requests data specs from Daniel | Follow-up question |

---

## USAGE NOTES

**To understand this session:**
1. Start with `SESSION_SUMMARY.md` (strategic overview)
2. Then read `PREV_SESSION_EXTRACTED.md` for details
3. Use this index to navigate between sections

**To move forward:**
1. Daniel gathers data specs (schemas, API docs)
2. Next phase: detailed architecture design document
3. Phase after: MCP server specifications for engineering team

---

## ARCHIVE METADATA

- **Files created**: 2
- **Total lines extracted**: 1,199
- **Full conversation preserved**: Yes
- **Tool results included**: Yes (research, schemas, code examples)
- **Strategic insights captured**: Yes
- **Next phase blocking question**: Yes

---

Generated by Claude Research Agent  
Part of Bit2Me Growth Team Documentation  
For: Daniel Ferraro (Head of Growth)
