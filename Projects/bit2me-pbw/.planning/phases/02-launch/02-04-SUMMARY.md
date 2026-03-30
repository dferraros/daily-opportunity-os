---
phase: 02-launch
plan: "04"
subsystem: email-campaigns
tags: [email, clevertap, katy, b2c, b2b, pbw2026, campaign-brief]
completed: "2026-03-30"
duration: "~5 minutes"

dependency_graph:
  requires:
    - 01-diego-review-package.md (Section 4 subject lines, Section 8 legal footer)
    - 01-b2b-icp-list.md (B2B outreach templates referenced in Section 9)
    - 02-RESEARCH.md (Section 5: CleverTap Email #1 Setup)
  provides:
    - 02-email-brief-katy.md (complete CleverTap build brief for Katy, ready to execute)
  affects:
    - Phase 3: Email #2 urgency campaign (same segment, send Day 14-15)
    - Phase 5: Post-event B2C and B2B follow-up sequences

tech_stack:
  added: []
  patterns:
    - CleverTap campaign brief with segment definition (INCLUDE 4 + EXCLUDE 3)
    - UTM taxonomy: utm_source=email / utm_medium=clevertap / utm_campaign=pbw2026_warmup
    - Safety control pattern: "don't send if segment exceeds N" threshold
    - A/B send protocol: 45/45/10 split, winner metric = open rate, auto-send at 24h

key_files:
  created:
    - .planning/phases/02-launch/02-email-brief-katy.md
  modified: []

decisions:
  - "B2C email type is awareness (not conversion push) — prime existing users, do not hard-sell"
  - "Send gate: Diego approval + live landing page URL are both required before Katy hits send"
  - "Safety threshold set at 200,000 — prevents accidental full-base send if segment filter misconfigures"
  - "10:00 AM Madrid time (fixed timezone, not user local) — optimizes open rate for Spain/EU B2B-adjacent audience"
  - "B2B email may bypass CleverTap if list < 30 contacts — confirmed as design choice, not oversight"
  - "A/B split only if segment > 10,000 per variant — otherwise send Diego-approved variant to 100%"

metrics:
  duration: "~5 minutes"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
  completed_date: "2026-03-30"
---

# Phase 02 Plan 04: Email Campaign Brief for Katy — Summary

**One-liner:** Full CleverTap execution brief for Email #1 (B2C awareness + B2B invite) with segment definition, Diego-approved copy variants, UTM taxonomy, and a 12-item pre-send checklist gating send on Diego approval + live landing page.

---

## What Was Built

Created `02-email-brief-katy.md` — a complete handoff document enabling Katy to build both PBW email campaigns in CleverTap during March 29-31 and execute within 2 hours of Diego's April 1 approval.

### Part A: B2C Awareness Email (`pbw_warmup_email_v1_apr01`)
- **Segment `pbw_warmup_v1`:** 4 inclusion criteria (EU country, kyc_status=complete, 1+ deposit, email_opt_in=true) + 3 exclusion criteria (churned_zero tag, excluded tag, unsubscribed status). BigQuery validation query included.
- **Safety control:** "Don't send if segment exceeds 200,000" — prevents accidental full-base send.
- **Subject lines:** 3 Diego-approved options (A/B/C from diego-review-package.md Section 4). Katy awaits Daniel's confirmation of which Diego approved.
- **A/B test protocol:** 45/45/10 split if segment > 10,000, winner metric = open rate, auto-send winner at 24h.
- **Email body:** 5-element structure (opening line + offer block + CTA button + 3 trust signals + legal footer), word count target under 150 words.
- **CTA UTM:** `?utm_source=email&utm_medium=clevertap&utm_campaign=pbw2026_warmup`
- **Legal footer:** Verbatim from Diego review package Section 8 (MiCA CASP disclosure + CNMV + risk statement).
- **Send time:** 10:00 AM Madrid time, April 1 (Tuesday) or April 2 fallback. Fixed Europe/Madrid timezone.
- **Performance targets:** 25-35% open rate / 8-12% CTOR / 15-30% conversion from email traffic.

### Part B: B2B Invite Email (`pbw_b2b_invite_v1_apr01`)
- **Recipients:** LinkedIn-connected contacts from Google Sheet who have not booked a meeting.
- **3 Diego-approved B2B subject line options** (A/B/C from diego-review-package.md Section 4).
- **Body:** Persona-appropriate template (A/B/C from 01-b2b-icp-list.md) + Calendly link + same legal footer.
- **Send method:** Manual if < 30 contacts, CleverTap if Katy manages the list. Decision needed by March 31.

### Part C: Pre-Send Checklist
12-item B2C checklist + 6-item B2B checklist. Two hard gates enforced:
1. DO NOT send before Diego-approved subject line confirmed by Daniel in writing.
2. DO NOT send while bit2me.com/pbw returns a 404 — test URL manually before scheduling.

Post-send monitoring table: 4h / 24h / 48h checks with alert thresholds (open rate < 10% = deliverability issue, unsubscribe > 0.5% = alert Daniel).

---

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Create email #1 brief for Katy (B2C awareness + B2B invite) | b0e78fa | `.planning/phases/02-launch/02-email-brief-katy.md` (296 lines) |

---

## Deviations from Plan

None — plan executed exactly as written.

The brief includes all 13 acceptance criteria items:
- `pbw_warmup_v1` appears 4 times (>= 3 required)
- `utm_source=email` appears 4 times (>= 2 required)
- `Diego-approved` appears 12 times (>= 3 required)
- `200,000` safety threshold present
- All 3 B2C subject line options (A, B, C) present
- All 3 B2B subject line options present
- Full legal disclaimer from Diego review package Section 8 present verbatim
- `10:00 AM Madrid time` appears 5 times
- 4 inclusion criteria (country, kyc_status, deposit behavior, email_opt_in)
- 3 exclusion criteria (churned_zero, excluded, unsubscribed)
- Pre-send checklist has 18 checkbox items across B2C (12) and B2B (6) sections
- "under 150 words" body length target present

---

## Self-Check: PASSED

- [x] `02-email-brief-katy.md` exists at `.planning/phases/02-launch/02-email-brief-katy.md`
- [x] Commit b0e78fa exists in git log
- [x] All acceptance criteria satisfied (verified via grep)
