---
phase: 03-scoring-system-master-trigger-table
plan: 03
subsystem: strategy
tags: [mvp-selection, channel-policy, deep-links, quiet-hours, conflict-resolution, trigger-prioritization]

# Dependency graph
requires:
  - phase: 03-scoring-system-master-trigger-table (plans 01, 02)
    provides: 8 scoring formulas, 33-trigger master table with top 10 MVP
  - phase: 02-taxonomy-competitive-benchmark
    provides: 6 trigger families, compliance classification, competitive gaps
  - phase: 01-foundation-safety-architecture
    provides: frequency caps, DND hours, suppression system, priority tiers
provides:
  - Top 10 triggers NOT to launch with reasoning, timeline, and prerequisites
  - 30-day MVP launch plan in 4 waves with owner assignments
  - V2/V3 roadmap preview for deferred triggers
  - 4-step channel selection algorithm with pseudocode
  - Deep link architecture for all 11 Bit2Me products with testing protocol
  - Quiet hours policy (22:00-08:00) for 4 regions
  - Journey vs alert conflict resolution matrix (J1-J6)
affects: [phase-04-measurement, playbook-final-assembly]

# Tech tracking
tech-stack:
  added: []
  patterns: [channel-decision-tree, deep-link-fallback, journey-conflict-sql-filter]

key-files:
  created:
    - .planning/phases/03-scoring-system-master-trigger-table/playbook-section-mvp-selection.md
    - .planning/phases/03-scoring-system-master-trigger-table/playbook-section-channel-policy.md
  modified: []

key-decisions:
  - "Editorial commentary in Family B market triggers is a PERMANENT prohibition, not timeline-dependent"
  - "Family B simultaneous send (MiCA Art. 89) overrides all conflict logic but NOT quiet hours (P3, not P0)"
  - "Deep link web fallback URLs mapped for all 11 products for email/no-app scenarios"
  - "Journey exit resets active_journey to NULL on next Hightouch sync (30-min), no additional cooldown"
  - "Queue overflow at 08:00 mitigated by existing global daily caps from Section 2.2"

patterns-established:
  - "active_journey IS NULL SQL filter: applied to Family C, D, E campaigns; bypassed by A, B, F"
  - "Deep link testing protocol: 4-step validation (iOS, Android, no-app fallback, web email)"
  - "NOT-to-launch documentation: trigger_id, WHY NOT, WHEN, PREREQUISITE, consequence analysis"

requirements-completed: [TRIG-04, CHAN-01, CHAN-02, CHAN-03, CHAN-04]

# Metrics
duration: 18min
completed: 2026-03-22
---

# Phase 3 Plan 03: MVP Selection + Channel Policy Summary

**Top 10 NOT-to-launch triggers with compliance/data reasoning, 4-step channel decision tree, deep links for 11 products, quiet hours for 4 regions, and J1-J6 conflict resolution matrix**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-22T19:36:10Z
- **Completed:** 2026-03-22T19:54:32Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- Documented 10 triggers NOT to launch with concrete reasoning (compliance risk, data unavailability, engineering dependency), V2/V3 timelines, prerequisites, and consequence analysis per trigger
- Built 4-step channel selection algorithm with Python pseudocode and per-family channel assignment matrix covering all 6 families
- Mapped deep links for all 11 Bit2Me products with web fallback URLs and 4-step testing protocol
- Specified quiet hours (22:00-08:00) for 4 regions with DELAY action and P0 exemption
- Defined journey conflict resolution for all 6 families against J1-J6, with SQL implementation (`active_journey IS NULL`)
- All 16 Phase 3 requirement checks pass validation (16/16 PASS)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write MVP Selection playbook section** - `f44b664` (feat)
2. **Task 2: Write Channel Policy playbook section** - `42000a1` (feat)

## Files Created/Modified
- `.planning/phases/03-scoring-system-master-trigger-table/playbook-section-mvp-selection.md` - Top 10 NOT-to-launch triggers, 30-day launch plan, V2/V3 roadmap preview
- `.planning/phases/03-scoring-system-master-trigger-table/playbook-section-channel-policy.md` - Channel decision tree, deep link architecture, quiet hours, conflict resolution

## Decisions Made
- Editorial commentary in Family B market triggers is permanently prohibited (not deferred to a future version) due to MiCA Art. 87-92 market abuse risk
- Family B simultaneous send requirement overrides conflict resolution but NOT quiet hours (Family B is P3, so DND applies; notifications queue for 08:00)
- Deep link web fallback URLs documented for all products to handle email clicks and no-app-installed scenarios
- Journey exit does not trigger an additional cooldown; standard family-level cooldowns apply
- Queue overflow at 08:00 morning delivery is mitigated by existing global daily caps (Section 2.2)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 is now COMPLETE (all 3 plans: scoring formulas, master trigger table, MVP selection + channel policy)
- All 16 Phase 3 requirements pass validation (SCORE-01 through SCORE-08, TRIG-01 through TRIG-04, CHAN-01 through CHAN-04)
- Ready for Phase 4: Measurement + Final Recommendations
- Phase 4 depends on: KPI framework, incremental lift design, Net Notification Value formula, executive summary, MVP/V2/V3 implementation roadmap

---
*Phase: 03-scoring-system-master-trigger-table*
*Completed: 2026-03-22*
