---
phase: 02-launch
plan: "05"
subsystem: marketing
tags: [social-media, buffer, luma, pbw2026, content-calendar, side-events]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: offer framing (PBW-60-ZERO), Diego review package, MiCA compliance notes
  - phase: 02-launch
    provides: 02-RESEARCH.md sections 8-9 (social calendar spec, Luma event data)
provides:
  - 18-post social content calendar ready for Buffer scheduling (March 29 – April 24)
  - Luma side event shortlist with 4 confirmed events, evaluation criteria, RSVP protocol
  - Visual asset requirements list for design team
  - Iberoamerican Crypto Happy Hour opportunity flagged for Phase 3 decision
affects:
  - Phase 3 (Amplify): side event attendance confirmation, Buffer offer posts activation after Diego approval
  - Phase 4 (Execute): event-week post templates and on-site social workflow
  - Phase 5 (Convert): post-event recap posts pre-drafted

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Offer posts drafted as Buffer drafts with [PENDING DIEGO] placeholder — swapped for approved copy on April 1"
    - "Side event evaluation via 4-factor 1-5 scoring with explicit priority thresholds"

key-files:
  created:
    - .planning/phases/02-launch/02-social-calendar.md
    - .planning/phases/02-launch/02-luma-side-events.md
  modified: []

key-decisions:
  - "Offer posts saved as Buffer DRAFTS (not scheduled) until Diego approval on April 1 — avoids rebuilding structural post work"
  - "Instagram deprioritized: do not start without a designated visual content creator owner"
  - "Iberoamerican Crypto Happy Hour flagged as Phase 3 decision — no other exchange can replicate this positioning"
  - "RSVP protocol requires adding contacts to B2B Google Sheet within 24h with source tag LUMA_[event_name]"

patterns-established:
  - "PENDING DIEGO pattern: any offer copy in social posts or materials blocked with literal [PENDING DIEGO] tag until April 1 approval"
  - "5-8 target events on Luma with evaluation before committing RSVPs (not first-come-first-serve)"

requirements-completed: [REQ-07, REQ-14]

# Metrics
duration: 4min
completed: 2026-03-30
---

# Phase 2 Plan 05: Social Calendar + Luma Side Events Summary

**18-post social content calendar for Buffer (March 29–April 24) with offer posts gated on Diego approval, plus Luma side event shortlist covering 4 confirmed events with RSVP protocol and contact-to-CRM workflow.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-30T12:10:39Z
- **Completed:** 2026-03-30T12:14:47Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Complete Buffer-ready social calendar with 18 numbered posts across 3 periods (pre-event, event week, post-event) — 9 READY posts, 3 BLOCKED on Diego, 4 on-site templates, 2 post-event drafts
- Visual asset requirements defined for design team: 4 assets needed (bank logo strip, offer card, two stat cards) with specific post assignments and priority levels
- Luma side event shortlist with 4 confirmed events (3 HIGH priority), 7 discovery search queries, evaluation criteria, and RSVP protocol that routes every new contact into the B2B Google Sheet
- Iberoamerican Crypto Happy Hour opportunity documented as Phase 3 decision item — no competitor can replicate Spanish-language ownership at PBW

## Task Commits

Each task was committed atomically:

1. **Task 1: Social content calendar with 18 posts** — `878fc3e` (feat)
2. **Task 2: Luma side event shortlist with RSVP guide** — `9651599` (feat)

## Files Created/Modified

- `.planning/phases/02-launch/02-social-calendar.md` — 18-post Buffer calendar, 5 content pillars, visual asset requests, 7-step scheduling workflow
- `.planning/phases/02-launch/02-luma-side-events.md` — 4 confirmed events, 7 discovery queries, 4-factor evaluation rubric, 5-step RSVP protocol, tracking table, hosting opportunity flag

## Decisions Made

- Offer posts saved as Buffer DRAFTS with literal `[PENDING DIEGO]` tag — structural post work is done, copy placeholder swaps in on April 1 without rebuilding
- Instagram deprioritized: plan specifies do not start without a designated visual content creator; X + LinkedIn are sufficient for PBW audience
- Iberoamerican Crypto Happy Hour: no confirmed Spanish-language side event exists at PBW 2025 or 2026 — flagged as Phase 3 decision (not executed here) because it requires budget approval and venue booking

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. Buffer account setup is a Daniel action item on March 29 per the scheduling workflow documented in 02-social-calendar.md Section 7.

## Next Phase Readiness

**Ready for Phase 3 (Amplify):**
- Daniel can draft all 18 posts in Buffer on March 29–30 using 02-social-calendar.md as the source of truth
- Offer posts will activate on April 1 when Diego approval arrives (swap [PENDING DIEGO] for approved copy, move from Draft to Scheduled)
- Luma RSVP actions can start immediately: 3 HIGH priority RSVPs to submit by April 1
- Visual asset request can go to design team today (March 30)

**Open items for Phase 3:**
- Confirm Iberoamerican Crypto Happy Hour decision (yes/no) by April 4
- Track RSVP confirmation status in the Side Event Tracking Table (Section 6 of 02-luma-side-events.md)
- Update tracking table as additional events are discovered from the 7 search queries

---
*Phase: 02-launch*
*Completed: 2026-03-30*
