# PREVIOUS SESSION SUMMARY & STRATEGIC INSIGHTS
**Date**: 2026-02-24  
**Session ID**: aa354d00-f848-4558-a240-3a726a9507b0  
**Agent Topic**: Bit2Me Lifecycle A/B Testing Dashboard / Agent Design

---

## KEY STRATEGIC DISCUSSION

### User Request
Daniel (Head of Growth at Bit2Me) requested help designing a **specialized AI agent** for analyzing and managing A/B tests in the lifecycle segment. He showed a reference dashboard called "Poly" (built by a colleague for brokerage analytics) and wanted to understand:

1. How to build something similar for **lifecycle/activation/retention analytics**
2. What **Anthropic tools** are best suited (Agent SDK, MCP, Claude Code, etc.)
3. How to **connect multiple data sources**: Qlik, CleverTap, BigQuery
4. Architecture for **A/B test design** and **statistical analysis**

---

## RECOMMENDED ARCHITECTURE (from research)

### 1. **Three-Tier Architecture**

```
[User Input] 
    ↓
[Claude Agent (Cowork Plugin)]
    ↓
[MCP Servers] (data bridges)
    ├─ CleverTap (lifecycle events, segments, journeys)
    ├─ Qlik (BI layer, pre-calculated metrics)
    ├─ BigQuery (if direct DB connection available)
    └─ Bitquery (on-chain crypto data for validation)
    ↓
[Specialized Skills]
    ├─ Data exploration
    ├─ A/B test design (sample size, power analysis, MDE)
    ├─ Lifecycle analysis (retention curves, cohorts, churn)
    └─ Statistical significance testing
```

### 2. **Core Components**

| Component | Purpose | Status |
|-----------|---------|--------|
| **MCP Servers** | Bridge to data sources (Qlik, CleverTap, BigQuery) | Need custom build (no existing) |
| **Agent SDK** | Autonomous decision-making, tool orchestration | Available (Python/TypeScript) |
| **Claude Code** | Code execution, analysis, visualization | Recommended use |
| **Cowork Plugin** | Package the agent as shareable interface | Recommended container |
| **Skills** | Specialized instruction sets (A/B test design, retention analysis) | Need custom definition |

### 3. **Key Differentiator from Poly**

The Brokerage "Poly" agent works on **single data source (BigQuery)** with natural language queries. 

For Bit2Me Lifecycle, the challenge is **multi-source orchestration**:
- CleverTap has the user journey/event data
- Qlik has pre-built retention/activation metrics
- BigQuery/internal DB has user attributes & clustering
- Bitquery has on-chain behavior validation

The agent must **intelligently route queries** to the right source and **synthesize insights** across all three.

---

## AGENT USE CASES (Proposed)

Once built, users would ask:

**Example 1 - Exploratory**
> "Analyze retention for Spanish users who completed KYC in Feb 2026 and had their first transaction in the Earn product. Break down by age, device, acquisition channel."

**Example 2 - Test Design**
> "I want to run an A/B test on a push notification variant for churned users with dormant balances. Design the test: control, variant A, hypothesis, sample size, minimum runtime, success metrics."

**Example 3 - Diagnostic**
> "Why are Loan product conversions 3.5% churn while Earn is 1%? What lifecycle events differ?"

**Example 4 - Activation Strategy**
> "Show me the onboarding funnel for new users in Portugal. Where do we drop most? What's the correlation with their first purchase timing?"

---

## DATA INFRASTRUCTURE REQUIRED

### Questions Daniel Should Answer:

1. **Database Layer**: Where lives the source of truth?
   - Is it BigQuery, Postgres, Snowflake, or other?
   - Who owns schema documentation?

2. **CleverTap**: What events/attributes are available?
   - Can we query raw events via API, or only pre-built segments?
   - Do you have a CRM engineer available to help build MCP server?

3. **Qlik**: What's available via Engine API?
   - Which apps/sheets are most critical?
   - Can Qlik be bypassed in favor of underlying DB?

4. **Bitquery**: How much on-chain validation is critical?
   - Is it nice-to-have or core to A/B test analysis?

### Work Required:

- **80% is data plumbing** (MCP servers, schema documentation, API integration)
- **20% is the agent itself** (Anthropic handles the intelligence)

---

## IMMEDIATE NEXT STEPS

1. **Daniel to gather specs**:
   - Database architecture diagram
   - CleverTap API documentation
   - Qlik schema/available fields
   - Bitquery integration preferences

2. **Agent design phase**:
   - Define top 10 most-used queries
   - Write skill definitions (A/B test design, retention analysis)
   - Design error handling & guardrails

3. **MCP server builds**:
   - CleverTap → MCP server (highest priority)
   - BigQuery → MCP server (if not using Qlik bypass)
   - Bitquery → optional (nice-to-have for validation)

4. **Prototype in Cowork**:
   - Build Cowork plugin container
   - Test with sample data
   - Iterate with user feedback

---

## KEY DECISION: Qlik vs. Direct DB

**Current assumption**: Qlik sits on top of underlying DB (BigQuery/Postgres).

**Recommendation**: 
- Use Qlik as reference for "which tables matter"
- Build MCP servers to **underlying DB** directly
- Qlik only for pre-calculated metrics that are expensive to recompute

**Reason**: 
- Faster queries
- More flexible joins
- Avoids Qlik licensing bottlenecks
- Claude can understand raw schema better

---

## TECHNICAL RESOURCES PROVIDED

From research phase:

### Core Anthropic Docs:
- [Claude Agent SDK Quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart.md)
- [Tool Use Overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md)
- [Claude Code Plugin Documentation](https://code.claude.com/docs/en/plugins.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)

### Data Integration (MCP):
- [BigQuery MCP Server Documentation](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)
- [Snowflake via CData Connect AI](https://www.cdata.com/kb/tech/snowflake-cloud-claude-agent-sdk.rst)
- [Fully Managed BigQuery MCP Server](https://cloud.google.com/blog/products/data-analytics/using-the-fully-managed-remote-bigquery-mcp-server-to-build-data-ai-agents)
- [Google Official MCP Support](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)

---

## ESTIMATED EFFORT

| Phase | Effort | Timeline |
|-------|--------|----------|
| Requirements gathering + schema docs | 2-3 days | Week 1 |
| MCP server build (CleverTap priority) | 3-5 days | Week 2-3 |
| MCP servers 2-3 (BigQuery + optional Bitquery) | 2-3 days | Week 3 |
| Agent + skills design + testing | 2-3 days | Week 3-4 |
| Integration testing + iteration | 2-3 days | Week 4-5 |
| **Total** | **~12-17 days** | **~5 weeks** |

---

## CRITICAL SUCCESS FACTORS

1. **Data quality**: Schema documentation must be clear & accurate
2. **API stability**: CleverTap/Qlik APIs must be reliable for production use
3. **User feedback loop**: Iterate on skills based on actual team usage
4. **Governance**: Define what the agent CAN'T do (compliance, financial decisions)
5. **Guardrails**: Statistical significance thresholds, minimum sample sizes, etc.

---

## FOLLOW-UP QUESTION

> "If you can connect me to the data (share schemas, API docs, or sample exports), I can start designing the agent architecture in detail, write the skill definitions, and help spec out the MCP servers. What does your current data setup look like?"

**This is the blocker question for Phase 2 of design.**

---

## SESSION ARTIFACTS

- **Full Conversation**: See `PREV_SESSION_EXTRACTED.md` (978 lines)
- **Research Summary**: Comprehensive breakdown of Claude Agent SDK, MCP, Claude Code, and architecture patterns
- **Tool Recommendations**: Specific tech stack decision matrix

---

## RELATED TO CLAUDE.MD CONTEXT

This session directly supports **Daniel's A/B Testing Framework** priorities:
- **T1, T2, T3 tests** need statistical design + analysis tools
- **LC Daily syncs** could be automated/augmented with agent insights
- **Loan Journey** (launching Feb 26) needs segment analysis + hypothesis testing
- **Flash Diario Growth** dashboard could be fed by agent outputs

The agent would reduce manual analysis work, enabling Daniel to focus on **strategy** (his assigned role per Pablo Campos directive) rather than **operational data work**.

---

**Status**: Research complete. Awaiting data infrastructure details from Daniel to proceed to architecture design phase.
