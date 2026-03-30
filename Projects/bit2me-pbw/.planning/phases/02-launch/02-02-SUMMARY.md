---
phase: 02-launch
plan: 02
subsystem: marketing
tags: [paid-ads, x-twitter, google-ads, campaign-brief, mica, pbw2026]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Diego review package with 4 pre-drafted ad copy variants (Section 3)
  - phase: 02-launch
    provides: 02-RESEARCH.md Section 4 — X/Twitter ad campaign setup spec

provides:
  - Complete paid ads campaign brief for X/Twitter primary + Google Ads secondary
  - 9-section actionable document: cert checks, campaign structure, 2 ad sets, creative specs, launch checklist, performance tracking
  - Go/no-go decision framework for Google Ads certification
  - 15-item launch checklist preventing ads from launching to a non-live landing page

affects:
  - 02-landing-page-brief (destination URL for all ads is /pbw landing page)
  - 01-diego-review-package (ad copy variants reference Diego Section 3)
  - Any phase requiring UTM tracking (utm_source=twitter, utm_source=google specs defined here)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "X Ads Manager certification check before campaign setup — platform gate that cannot be bypassed"
    - "2 separate ad sets (crypto-native B2C vs event-intent B2C+B2B) for independent performance tracking"
    - "Campaign set to Paused status until both certification + Diego approval confirmed"
    - "Belgium geo exclusion mandatory for X crypto ads"

key-files:
  created:
    - .planning/phases/02-launch/02-ad-campaign-brief.md
  modified: []

key-decisions:
  - "X/Twitter is primary channel (60% crypto ad approval rate vs Meta 50%). Google is secondary contingent on existing EU certification."
  - "Campaign starts Paused — flip to Active only when X certification active AND Diego approval confirmed AND landing page is live (prevents wasting budget on 404)"
  - "Google Ads: if not certified, skip entirely for this sprint. X/Twitter can carry the load alone. Certification takes 2-4 weeks — not viable."
  - "EUR 100/day initial budget, scale to EUR 200/day after 48h if CTR > 1% (avoid wasting budget in learning phase)"
  - "Ad Set 1 (crypto-native) gets 60% of budget; Ad Set 2 (event intent) gets 40% — event-intent keywords are smaller audience"

patterns-established:
  - "Certification-first pattern: always verify platform-level ad certification before any campaign setup work"
  - "Paused-until-gates pattern: set campaigns to Paused in advance, have everything ready, flip Active on gate confirmation"
  - "Performance threshold actions: define CTR/CPC thresholds with explicit optimization actions before launch, not after"

requirements-completed: [REQ-03]

# Metrics
duration: 5min
completed: 2026-03-30
---

# Phase 02 Plan 02: Paid Ads Campaign Brief Summary

**9-section X/Twitter + Google Ads brief: cert checks, 2 ad sets, 4 Diego-approved copy variants, 15-item launch checklist, and performance thresholds — everything ready to launch within hours of April 1 approval**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-30T12:09:48Z
- **Completed:** 2026-03-30T12:14:52Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created complete 9-section paid ads campaign brief at `.planning/phases/02-launch/02-ad-campaign-brief.md`
- All 4 Diego-approved ad copy variants included verbatim from 01-diego-review-package.md Section 3
- X/Twitter certification check steps documented for March 29 — 5 steps, covers certified/expired/blocked scenarios
- Google Ads go/no-go decision framework documented: 20-minute time-boxed check, clear skip criteria
- 2 ad sets structured with distinct targeting (crypto-native B2C vs event-intent B2C+B2B) for independent performance tracking
- 15-item launch checklist prevents campaigns from going live before landing page, Diego approval, and X certification are all confirmed

## Task Commits

Each task was committed atomically:

1. **Task 1: Create paid ads campaign brief** - `9651599` (feat)

## Files Created/Modified

- `.planning/phases/02-launch/02-ad-campaign-brief.md` — Complete paid ads brief: X/Twitter certification check, Google cert check, campaign structure, 2 ad set targeting specs, 4 creative variants verbatim, Google track (conditional), prohibited claims, 15-item launch checklist, performance tracking with CTR/CPC thresholds

## Decisions Made

- X/Twitter is primary. Google is conditional — only pursue if EU certification already exists. No pursuing new Google certification during this sprint (2-4 week lead time vs March 29 start).
- Campaign launched in Paused state with all setup done in advance, flipped Active only when the 3 gates clear simultaneously: X certification active + Diego approval confirmed + landing page live at bit2me.com/pbw
- Budget pacing: EUR 100/day to start (algorithm learning phase), scale to EUR 200/day only if CTR > 1% after 48h. Prevents burning budget during underperforming learning phase.
- Belgium explicitly excluded from both ad sets — X platform requirement for crypto ads, cannot be overridden.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria met:
- File exists at correct path
- All 4 ad copy variants included verbatim (11 "Variant" references)
- "utm_source=twitter" appears 4 times
- "Belgium" appears 5 times in exclusion contexts
- "certification" appears 23 times
- 2 ad sets with distinct targeting documented
- Launch Checklist section with 15 checkbox items
- EUR 100-200/day budget specification present
- 1200x1200 creative spec present 3 times
- Performance Tracking section with CTR > 1% and CPC < EUR 2 targets

## Issues Encountered

None. The brief was self-contained from Phase 1 output (Diego package Section 3 ad copy) and Phase 2 research (Section 4 X/Twitter setup spec).

## User Setup Required

None — this is a planning/briefing deliverable, not code. No external service configuration required.

## Next Phase Readiness

- Daniel can execute the X/Twitter certification check on March 29 using Section 1 of the brief
- Google Ads decision can be made in 20 minutes on March 29 using Section 2
- All campaign setup (targeting, copy, images) can be completed before April 1 — campaigns staged in Paused status
- The moment Diego approves copy on April 1: run through the 15-item launch checklist, flip Active

**Upstream blocker:** Ads remain in Paused status until both Diego approval (April 1 deadline) and `bit2me.com/pbw` landing page go live are confirmed. This is expected per plan design.

---
*Phase: 02-launch*
*Completed: 2026-03-30*
