---
phase: 01-j02-journey-system
plan: 07
subsystem: documentation
tags: [mermaid, jira, journey-os, j02, crm, clevertap, bigquery]

# Dependency graph
requires:
  - phase: 01-j02-journey-system/01-02
    provides: Hub J02-CORE touchpoints S0-S4 specification
  - phase: 01-j02-journey-system/01-03
    provides: Spokes SP-01 to SP-05 specification
  - phase: 01-j02-journey-system/01-04
    provides: LatAm variant specification (WhatsApp, USD framing)
  - phase: 01-j02-journey-system/01-05
    provides: Recovery A/B/C and J02.5 Loyalty specification
  - phase: 01-j02-journey-system/01-06
    provides: J05 B2B architecture specification
provides:
  - Mermaid flowchart diagram of complete J02 system (Hub+Spokes+Recovery+LatAm+B2B+Loyalty)
  - 25 Jira-ready tickets with owner, sprint, priority, acceptance criteria
  - Critical path analysis (5 business days to Hub in production)
  - A/B test spec for SP-01 loss vs gain framing (600 users/variant, Welch t-test)
affects: [01-08, execution-by-katy, diego-approval-batches, alvaro-bigquery-work]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Mermaid flowchart TD with classDef color coding by subsystem
    - Jira ticket format with Titulo/Epic/Sprint/Prioridad/Owner/Estimacion/Descripcion/Criterios de aceptacion/Bloqueado por

key-files:
  created:
    - docs/plans/2026-03-23-j02-diagram.mmd
    - docs/plans/2026-03-23-j02-jira-tickets.md
  modified: []

key-decisions:
  - "Ticket J02-12 Recovery B1 is P0 Sprint 1 — executable this week without journey automation via manual CSV export + CleverTap one-off"
  - "A/B test SP-01: 600 users per variant, loss framing vs gain framing, 14-day window, Welch t-test, Marta owns analysis"
  - "Diego approval batched by layer: Hub batch (Sprint 1) + Spokes batch (Sprint 2) = 2 cycles instead of 25"
  - "Critical path: J02-01 (Alvaro BigQuery) blocks all Hub tickets — must be Day 1 priority"
  - "Diagram uses subgraphs: HUB, SPOKES, RECOVERY, LATAM, B2B, LOYALTY with distinct classDef colors"

patterns-established:
  - "Jira tickets include Bloqueado por field to make dependency chain explicit for sprint planning"
  - "A/B test tickets specify: hypothesis, sample size formula, minimum detectable effect, analysis method"

requirements-completed: [R07, R08]

# Metrics
duration: 5min
completed: 2026-03-23
---

# Phase 01 Plan 07: J02 Architecture Diagram and Jira Backlog Summary

**Mermaid flowchart TD covering full J02 system (Hub+8 Spokes+Recovery A/B/C+LatAm+B2B+J02.5) plus 25 Jira tickets with sprint assignments, owners, and checkboxable acceptance criteria**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-23T14:53:34Z
- **Completed:** 2026-03-23T14:58:59Z
- **Tasks:** 2 (Task 1: Mermaid diagram, Task 2: Jira tickets)
- **Files modified:** 2

## Accomplishments

- Mermaid diagram with 6 subgraphs (HUB, SPOKES, RECOVERY, LATAM, B2B, LOYALTY), 8 classDef color codes, all decision nodes, exit paths, and fallback logic documented
- 25 Jira tickets covering every touchpoint, spoke, recovery track, and cross-cutting concern (holdout, A/B test, Diego approval batches)
- Recovery B1 ticket (J02-12) marked P0 Sprint 1 with complete step-by-step manual execution instructions (Marta SQL export + Katy CleverTap one-off) — executable this week
- A/B test ticket (J02-25) fully specified: hypothesis, 600 users/variant sample size, 14-day minimum duration, Welch t-test at alpha=0.05, Marta as analysis owner
- Critical path analysis embedded in appendix: Hub live in 5 business days minimum if Alvaro delivers J02-01 on day 1

## Task Commits

1. **Tasks 1+2: Mermaid diagram + Jira tickets** - `8ee3cbc` (docs)

## Files Created/Modified

- `docs/plans/2026-03-23-j02-diagram.mmd` - Complete Mermaid flowchart TD of J02 system, 6 subgraphs, 8 classDef color themes, all decision nodes
- `docs/plans/2026-03-23-j02-jira-tickets.md` - 25 Jira tickets J02-01 to J02-25, 3 sprints, summary table, critical path section

## Decisions Made

- Tickets J02-08 and J02-20 are the same concern (Diego Hub batch approval) — kept both as they appear in the plan spec but J02-20 is the primary ticket and J02-08 describes the email prep work; this gives Daniel an actionable item separate from the approval gate
- Diego approval batching documented as 2 cycles (Hub + Spokes) to minimize SLA overhead
- Recovery B1 manual launch explicitly flagged as not requiring journey automation — simplifies the week-1 execution path for Katy and Marta
- Diagram keeps node IDs strictly alphanumeric (no spaces/special chars) per Mermaid syntax requirements; all labels with spaces wrapped in double quotes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - document generation only, no external service configuration required.

## Next Phase Readiness

- 01-07 complete. 01-08 (Master Word .docx) is the final remaining plan in phase 01.
- Outputs ready for Confluence: diagram.mmd renders natively, tickets.md can be pasted directly into Jira
- Immediate actions for team: Daniel can start Diego batch prep today (J02-08/J02-20), Katy should initiate Meta WhatsApp template approval process (J02-18) in parallel

---
*Phase: 01-j02-journey-system*
*Completed: 2026-03-23*
