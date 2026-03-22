---
phase: 01-foundation-safety-architecture
plan: 02
subsystem: crm-safety
tags: [clevertap, bigquery, hightouch, suppression, event-schema, reverse-etl, gdpr]

requires:
  - phase: 01-foundation-safety-architecture (plan 01)
    provides: Preference Center architecture and Frequency Cap Policy (Sections 1-2)
provides:
  - Suppression system design with C8 whale list, quiet hours, opt-out handling, escalating cooldowns
  - Event schema for CleverTap SDK (7 events), Backend Upload (6 events), Cloud Function (2 events)
  - Hightouch Reverse ETL integration design with BigQuery source view, 17-field mapping, sync config
affects: [02-trigger-taxonomy, 03-trigger-table, 04-measurement]

tech-stack:
  added: [hightouch-business-tier]
  patterns: [custom-list-api-suppression, upload-events-api-batching, reverse-etl-upsert-sync]

key-files:
  created:
    - .planning/phases/01-foundation-safety-architecture/playbook-section-suppression.md
    - .planning/phases/01-foundation-safety-architecture/playbook-section-event-schema.md
    - .planning/phases/01-foundation-safety-architecture/playbook-section-hightouch.md

key-decisions:
  - "Suppression is additive (4 layers in sequence) -- notification must pass ALL layers"
  - "Charged event mandatory for all purchases (CleverTap built-in revenue/LTV tracking)"
  - "Hightouch sync every 30 minutes with upsert mode; EXCLUDED users filtered from view"
  - "Escalating cooldowns use 5 levels (L0-L4) computed daily in BigQuery"

patterns-established:
  - "Custom List API workflow for suppression segments (pre-signed URL upload)"
  - "Title_Case with underscores for all event names"
  - "17-field profile sync from BigQuery to CleverTap via Hightouch"

requirements-completed: [FOUND-03, FOUND-04, FOUND-05]

duration: 6min
completed: 2026-03-22
---

# Phase 1 Plan 02: Suppression, Event Schema, and Hightouch Reverse ETL Summary

**Suppression system with C8 whale protection and 5-level cooldown escalation, 15-event CleverTap schema (SDK + Backend + Cloud Function), and Hightouch Reverse ETL design with 17-field BigQuery-to-CleverTap sync**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-22T16:11:11Z
- **Completed:** 2026-03-22T16:17:14Z
- **Tasks:** 3
- **Files created:** 3

## Accomplishments

- Suppression system covering C8 whale list (Custom List API workflow), quiet hours (22:00-08:00 DND), opt-out handling per channel, and 5-level escalating cooldowns with an 8-item campaign launch checklist
- Event schema defining all 15 CleverTap events across 3 ingestion paths (SDK, Backend Upload API, Cloud Function), plus API constraints, reserved names, and event-to-trigger mapping with priority tiers
- Hightouch Reverse ETL integration design with full BigQuery SQL view, 17-field mapping table, sync configuration (upsert, 30-min, incremental), monitoring KPIs, and 13-step implementation checklist for Alvaro

## Task Commits

Each task was committed atomically:

1. **Task 1: Write Suppression System Section** - `cbbd74b` (feat)
2. **Task 2: Write Event Schema Section** - `a8deae7` (feat)
3. **Task 3: Write Hightouch Reverse ETL Integration Design Section** - `64d6ac7` (feat)

## Files Created

- `.planning/phases/01-foundation-safety-architecture/playbook-section-suppression.md` - Suppression system (C8, DND, opt-out, cooldowns, checklist)
- `.planning/phases/01-foundation-safety-architecture/playbook-section-event-schema.md` - Event schema (SDK, Backend, Cloud Function events + API constraints)
- `.planning/phases/01-foundation-safety-architecture/playbook-section-hightouch.md` - Hightouch Reverse ETL (BigQuery view, field mapping, sync config, monitoring)

## Decisions Made

- Suppression is additive (4 layers in sequence) -- a notification must pass ALL layers to send
- Charged event is mandatory for all purchase/trade events (CleverTap built-in revenue/LTV tracking)
- Hightouch sync set to every 30 minutes with upsert mode; EXCLUDED users (~600K) filtered from BigQuery view
- Escalating cooldowns use 5 levels (L0-L4) computed daily in BigQuery
- DND action is DELAY (queue until 08:00), not DISCARD

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. These are design documents (playbook sections), not code deployments.

## Next Phase Readiness

- All five FOUND requirements (FOUND-01 through FOUND-05) are now documented across Plans 01 and 02
- Phase 1 playbook sections are ready for cross-document consistency review
- C8 whale suppression CSV upload remains an open P0 action item (blocker documented in Section 3.2)
- Alvaro SPOF risk noted: Hightouch setup + BigQuery view creation add to his workload

## Self-Check: PASSED

All 3 playbook files exist. All 3 task commits verified.

---
*Phase: 01-foundation-safety-architecture*
*Completed: 2026-03-22*
