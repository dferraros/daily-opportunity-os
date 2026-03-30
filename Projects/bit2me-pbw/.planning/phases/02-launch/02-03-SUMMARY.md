---
phase: 02-launch
plan: 03
subsystem: b2b-outreach
tags: [linkedin, calendly, b2b, outreach, pbw, playbook]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: B2B ICP seed list (19 entries), 3 message templates (A/B/C), 192-char connection note, Google Sheet schema
  - phase: 02-launch
    provides: 02-RESEARCH.md Section 6 LinkedIn workflow, Calendly spec, day-by-day sequence, benchmarks
provides:
  - Day-by-day LinkedIn outreach playbook March 29 - April 4 (7 days)
  - Calendly page setup spec with exact dates, time slots, buffer, and event type
  - Persona-to-template routing map (BANK/FINTECH/ASSET_MANAGER/FUND/CUSTODY/INFRASTRUCTURE)
  - Second outreach owner split protocol
  - Google Sheet daily tracking protocol
affects:
  - phase: 02-launch (02-04, 02-05, 02-06) — meeting bookings drive Phase 3 follow-up wave volume
  - phase: 03-amplify — Phase 3 B2B follow-up plan depends on connections sent in Phase 2

# Tech tracking
tech-stack:
  added: [Calendly (Essentials plan — meeting booking), Google Sheets (PBW_B2B_Targets tracker)]
  patterns: [connection-first outreach (no pitch until accepted), one-full-calendar-day wait rule before messaging, 15-20 daily request limit for LinkedIn account safety]

key-files:
  created:
    - .planning/phases/02-launch/02-linkedin-outreach-playbook.md
  modified: []

key-decisions:
  - "Calendly set up FIRST before any connection request — booking window is 24-72h after acceptance, no link = lost opportunity"
  - "15-20 connection requests per day maximum — LinkedIn soft restriction, do not exceed 25"
  - "One full calendar day wait between connection acceptance and pitch message — prevents transactional feel"
  - "No follow-up within 5-7 days of message — Phase 3 handles follow-up, Phase 2 plants seeds only"
  - "Split outreach by persona if second owner available: BANK+AM to Owner A, FINTECH+INFRA+CUSTODY to Owner B"

patterns-established:
  - "Pre-work-first pattern: Calendly live before first outreach; Google Sheet populated before first connection"
  - "Persona-routing pattern: BANK → Template A, FINTECH/INFRA → Template B, ASSET_MANAGER/FUND → Template C"
  - "Daily sheet update rule: update at end of every outreach session, not weekly"

requirements-completed: [REQ-15]

# Metrics
duration: 5min
completed: 2026-03-30
---

# Phase 2 Plan 03: LinkedIn Outreach Playbook Summary

**Day-by-day LinkedIn outreach playbook for March 29 - April 4 with Calendly spec (20-min slots Apr 15-16), persona-to-template routing, and second-owner split protocol — zero Diego dependency, B2B track can start immediately**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-30T12:09:49Z
- **Completed:** 2026-03-30T12:14:16Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Complete 7-day LinkedIn outreach playbook (March 29 - April 4) with specific daily actions, limits, and timing rules
- Calendly page setup spec with exact event type name, April 15-16 slots, 10 time slots per day (9:00-11:30 + 14:00-15:30), 10-minute buffer, and location field
- All 3 message templates from Phase 1 reproduced verbatim with Calendly link appendix and persona routing table mapping company names to templates
- Second outreach owner split protocol addressing the STATE.md blocker (Daniel cannot own outreach + booth + campaigns alone)
- Google Sheet daily tracking protocol with column-by-column update schedule

## Task Commits

Each task was committed atomically:

1. **Task 1: Create LinkedIn outreach playbook with Calendly setup** - `98e0d2e` (feat)

**Plan metadata:** (see final commit below)

## Files Created/Modified

- `.planning/phases/02-launch/02-linkedin-outreach-playbook.md` — Complete LinkedIn outreach playbook: pre-work checklist, Calendly setup guide, day-by-day execution March 29-April 4, benchmarks, all 3 message templates with persona routing, Google Sheet protocol, second owner split protocol, risk watch list

## Decisions Made

- Calendly setup is mandated as the first action on March 29 — before any connection request is sent. Rationale: the booking window is 24-72 hours after connection acceptance; if Calendly is not live when a connection accepts, the opportunity closes.
- 15-20 daily request hard limit enforced throughout the playbook to prevent LinkedIn account restrictions.
- One full calendar day wait between connection acceptance and pitch message — prevents transactional feel that lowers reply rates.
- Phase 2 target set at 5+ meetings (not 8-12) — remaining meetings close in Phase 3 follow-up wave where 5-7 day wait has elapsed.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria met:
- File exists at `.planning/phases/02-launch/02-linkedin-outreach-playbook.md`
- "Calendly" appears 19 times (requirement: at least 8)
- "Template A" appears 2 times (requirement: at least 2)
- All 7 days spelled out March 29 through April 4
- 192-character connection note verbatim from 01-b2b-icp-list.md
- "15-20" daily LinkedIn limit present
- "one full calendar day" wait rule before messaging present
- Calendly time slots 9:00, 9:30, 10:00 etc. (Paris time) present
- "5+ meetings booked" Phase 2 target present
- Pre-Work Checklist with 7 checkbox items
- Second outreach owner section (Section 7)

## Issues Encountered

None.

## User Setup Required

Daniel must complete the following manual steps before March 29 outreach starts:

1. **Set up Calendly page** — Event type: "20-min Coffee at PBW — Bit2Me B2B". Dates: April 15-16 only. Time slots: 9:00, 9:30, 10:00, 10:30, 11:00, 11:30, 14:00, 14:30, 15:00, 15:30 (Paris/CET). Buffer: 10 min. Paste final URL in playbook Section 2.
2. **Test Calendly booking** — Book a dummy meeting yourself. Confirm confirmation email arrives. Verify timezone shows Paris/CET.
3. **Populate Google Sheet** — Create "PBW_B2B_Targets" tab with the schema from 01-b2b-icp-list.md. Add all 19 seed entries. Aim for 50+ rows by end of Day 5.
4. **Identify second outreach owner** — STATE.md blocker. Decide by Day 5 (March 30) or adjust daily volume expectations.
5. **Personalize first 15-20 connection notes** — Replace [Name] and [Company] placeholders for the H-priority seed list entries before sending.

## Next Phase Readiness

- Phase 2 B2B track is fully specified and executable starting March 29 with no external dependencies
- Phase 3 follow-up wave (Days 11-14, April 5-9) will pick up connections sent in Phase 2 after the 5-7 day wait window
- Meeting count from this playbook feeds the Phase 3 plan target (8-12 confirmed meetings by April 10)
- Calendly slots (20 available across April 15-16) are sufficient to absorb the full 8-12 meeting target

---
*Phase: 02-launch*
*Completed: 2026-03-30*
