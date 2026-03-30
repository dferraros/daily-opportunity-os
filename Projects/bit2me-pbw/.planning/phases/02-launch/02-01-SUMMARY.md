---
phase: 02-launch
plan: "01"
subsystem: launch-briefs
tags: [landing-page, health-score, clevertap, utm, dev-handoff, engineering-handoff]
dependency_graph:
  requires: [01-offer-brief, 01-diego-review-package]
  provides: [02-landing-page-brief, 02-health-score-brief]
  affects: [dev-team, design-team, engineering, katy-clevertap, alvaro-utm]
tech_stack:
  added: []
  patterns: [utm-taxonomy, clevertap-event-spec, configurable-copy-pattern]
key_files:
  created:
    - .planning/phases/02-launch/02-landing-page-brief.md
    - .planning/phases/02-launch/02-health-score-brief.md
  modified: []
decisions:
  - "Landing page form fires pbw_lead CleverTap event with 5 properties (source, campaign, name, email, gdpr_consent)"
  - "Health Score output text stored as configurable JSON/CMS — never hardcoded — to enable Diego copy changes without code deploy"
  - "All Diego-approved copy in landing page brief marked as placeholders for April 1 drop-in; page structure builds without it"
  - "Health Score build can start April 1 with zero Diego dependency; regulated copy risk isolated to gap text configuration"
metrics:
  duration_minutes: 7
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  completed_date: "2026-03-30"
---

# Phase 2 Plan 01: Landing Page Brief + Health Score MVP Brief

**One-liner:** Dev/design handoff brief for bit2me.com/pbw with full CleverTap pbw_lead spec, and engineering brief for a 10-day Crypto Health Score MVP with configurable output text, 5-question scoring logic, and health_score_completed analytics event.

---

## What Was Built

### 02-landing-page-brief.md (290 lines)

A complete handoff document for the dev/design team to build `bit2me.com/pbw` starting March 29 without waiting for Diego approval. The brief covers:

- **URL and hosting spec**: `/pbw` primary, `/paris` fallback, mobile-first at 375px, no login wall, hard deadline April 1
- **5-section page architecture**: Hero (with countdown + CTA), Offer block, 3 differentiators (MiCA + banks + Europol), Social proof (press logos), CTA repeat + legal footer — all Diego-required copy marked as `[APPROVED COPY DROPS IN APR 1: "..."]` placeholders
- **Form specification**: 2 fields (Name + Email), GDPR checkbox pre-unchecked, inline validation, no page reload, duplicate-email handling, loading state
- **UTM table**: 6 sources fully specced (X/Twitter paid, Google paid, QR booth, Email #1, LinkedIn organic, QR lanyards) — Alvaro validates
- **CleverTap spec**: `pbw_lead` event with 5 properties, `pbw_2026_lead` profile tag, PBW B2C Journey enrollment trigger — for Katy
- **QR code spec**: Bitly/UTM.io, SVG preferred, 2000×2000px PNG minimum, error correction Level H, booth + lanyard variants
- **13-item handoff checklist** with owners and dates through April 1
- **8 open questions** for dev (URL availability, deployment pipeline, CleverTap endpoint, dev hours estimate)
- **Appendix**: Full copy status table showing what is confirmed vs. placeholder, with Diego Section 8 legal footer text pasted verbatim

### 02-health-score-brief.md (329 lines)

A complete engineering handoff document for a 10-day Crypto Health Score build. The brief covers:

- **Tool definition**: Mobile web (not native app), anonymous (no login, no email), hosted at bit2me.com/pbw/health, NOT a financial product
- **5 questions with all options**: Experience, Portfolio split, Rebalancing cadence, Custody, MiCA awareness
- **Scoring table**: 15 answer options with exact point values, max 120 raw points
- **Normalization formula**: `round((raw / 120) * 100)`, with min/max examples
- **Output screen spec**: Score gauge (0-100), color coding (0-40 red / 41-70 yellow / 71-100 green), configurable Strength + Gap text by bracket, CTA to bit2me.com/pbw
- **Configurable text pattern**: All 3 score brackets with default Strength + Gap text — stored in JSON config, not hardcoded
- **Share mechanic**: Web Share API primary, Twitter intent fallback, score-only (no PII)
- **Analytics**: `health_score_completed` CleverTap event with 6 properties (score + 5 answers), plus 5 supplemental metrics
- **Technical requirements**: 500KB page weight limit, client-side scoring (no server round-trip), existing Bit2Me stack
- **Diego Review Note**: Critical section explaining that configurable copy is a compliance requirement, not a nice-to-have
- **14-item handoff checklist** with dates through April 10
- **Appendix**: Full 6-screen flow diagram + 4 example scoring scenarios (expert, beginner, mid-tier, experienced-unregulated)

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Landing page brief separates layout (build now) from copy (drop in April 1) | Enables dev/design to start March 29 without Diego bottleneck; copy swaps in April 1 in minutes |
| pbw_lead event fires 5 properties including gdpr_consent | Katy needs source + campaign for attribution; gdpr_consent required for GDPR-compliant CleverTap segmentation |
| Health Score output text in configurable JSON — no hardcoded strings | Diego may require gap text changes before April 15; a config file update avoids a booth-day code deploy |
| Health Score: zero Diego dependency for build start | Tool contains no offer copy; MiCA risk is isolated to gap recommendations which are in the config |
| 2 form fields maximum (Name + Email) on landing page | Each additional field reduces conversion rate; phone number adds friction with zero benefit at this stage |

---

## Deviations from Plan

None — plan executed exactly as written. Both briefs were expanded beyond the plan skeleton with complete tables, examples, verification checklists, and appendices to ensure true self-sufficiency for each recipient.

---

## Self-Check

Verifying key claims before state update.

| Check | Result |
|-------|--------|
| `.planning/phases/02-launch/02-landing-page-brief.md` exists | FOUND |
| `.planning/phases/02-launch/02-health-score-brief.md` exists | FOUND |
| `.planning/phases/02-launch/02-01-SUMMARY.md` exists | FOUND |
| Commit b0e78fa (Task 1) exists | FOUND |
| Commit e9d9421 (Task 2) exists | FOUND |

## Self-Check: PASSED
