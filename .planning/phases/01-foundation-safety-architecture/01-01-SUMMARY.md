---
phase: 01-foundation-safety-architecture
plan: 01
subsystem: crm-safety
tags: [clevertap, gdpr, eprivacy, mica, frequency-caps, consent, preference-center, bigquery, hightouch]

# Dependency graph
requires:
  - phase: none
    provides: first phase, no dependencies
provides:
  - Preference Center architecture with 6 consent categories, per-channel consent model, 11-field data model, 5 CleverTap Subscription Groups
  - Frequency Cap Policy with exact daily/weekly/monthly caps, P0-P5 priority tiers, cooldown escalation, fatigue risk formula
affects: [01-02-PLAN, phase-02-taxonomy, phase-03-scoring, phase-04-measurement]

# Tech tracking
tech-stack:
  added: [CleverTap Subscription Groups, Hightouch Reverse ETL (design)]
  patterns: [per-channel GDPR consent, P0-P5 priority tiers with cap exemption, fatigue risk scoring]

key-files:
  created:
    - .planning/phases/01-foundation-safety-architecture/playbook-section-preference-center.md
    - .planning/phases/01-foundation-safety-architecture/playbook-section-frequency-caps.md
  modified: []

key-decisions:
  - "6 notification categories (CAT-SEC through CAT-PRO) with GDPR lawful basis per category -- CAT-SEC/TXN use Art. 6(1)(b), CAT-MKT/PRD/PRO use Art. 6(1)(a)"
  - "OS push permission is NOT marketing consent (ePrivacy Art. 13) -- requires separate in-app consent screen"
  - "P0-P1 campaigns marked Exclude from Global campaign limits in CleverTap; P2-P5 subject to global caps"
  - "Fatigue risk formula uses 3 components: send volume (0.4), dismissal rate (0.3), engagement recency (0.3)"
  - "Push daily cap set at 2/day, 8/week, 20/month for marketing notifications"

patterns-established:
  - "Consent hierarchy: MSG-push + consent_marketing_push + Subscription Group + frequency/suppression checks"
  - "Priority tier override: when cap hit, suppress P5 first, then P4, P3, P2; P0-P1 always deliver"
  - "Cooldown escalation: 3 dismissals = 7-day family cooldown; 5 dismissals = 14-day P0-P1 only"
  - "8-step campaign creation checklist for every new CleverTap campaign"

requirements-completed: [FOUND-01, FOUND-02]

# Metrics
duration: 6min
completed: 2026-03-22
---

# Phase 1 Plan 01: Preference Center Architecture + Frequency Cap Policy Summary

**Preference Center with 6 GDPR-mapped consent categories, per-channel consent model, and Frequency Cap Policy with P0-P5 priority tiers, fatigue risk scoring formula, and 8-step campaign creation checklist**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-22T16:11:12Z
- **Completed:** 2026-03-22T16:17:32Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- Preference Center architecture with 6 notification categories (CAT-SEC through CAT-PRO), each mapped to its GDPR lawful basis, with per-channel consent model covering Push, Email, In-App, and future SMS
- Complete data model with 11 fields (3 consent booleans, 3 consent timestamps, 1 GDPR basis string, 4 CleverTap MSG-* system properties) stored in BigQuery and synced via Hightouch
- Frequency Cap Policy with exact daily/weekly/monthly caps per channel, P0-P5 priority tier system with cap exemptions for transactional/user-configured notifications
- Fatigue Risk Score formula with 4 threshold levels (GREEN/AMBER/RED/CRITICAL) and corresponding tier suppression rules
- 5 cooldown rules with escalation logic (individual dismissals through global notification lockdown)
- 8-step campaign creation checklist ensuring every new campaign has correct priority, DND, suppression, fatigue filter, and Diego approval

## Task Commits

Each task was committed atomically:

1. **Task 1: Write Preference Center Architecture Section (FOUND-01)** - `51a4b90` (feat)
2. **Task 2: Write Frequency Cap Policy Section (FOUND-02)** - `bda9984` (feat)

## Files Created/Modified
- `.planning/phases/01-foundation-safety-architecture/playbook-section-preference-center.md` - Preference Center architecture: 7 subsections (1.1-1.7), consent categories, data model, CleverTap Subscription Groups, consent collection flow, compliance checklist, UI wireframe description
- `.planning/phases/01-foundation-safety-architecture/playbook-section-frequency-caps.md` - Frequency Cap Policy: 7 subsections (2.1-2.7), global caps, P0-P5 tiers, cooldown rules, fatigue formula, campaign checklist, monitoring KPIs

## Decisions Made
- 6 notification categories with strict GDPR lawful basis mapping: security/transactional use contractual necessity (Art. 6(1)(b)), marketing categories require explicit consent (Art. 6(1)(a))
- OS push permission treated as technical gate only; separate in-app marketing consent screen required (ePrivacy Art. 13)
- BigQuery as consent source of truth, synced to CleverTap via Hightouch every 30 minutes
- Push cap set conservatively at 2/day, 8/week, 20/month based on 46% opt-out rate at 2-5/week benchmark
- Fatigue risk formula weights: send volume (0.4) + dismissal rate (0.3) + engagement recency (0.3), with 4 threshold levels
- Diego approval mandatory for ALL campaign copy (MiCA Art. 66 compliance gate)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. These are design documents, not software.

## Next Phase Readiness
- Both playbook sections are complete and internally consistent
- Cross-references between Section 1 (Preference Center) and Section 2 (Frequency Cap) are documented
- Consent categories (CAT-SEC through CAT-PRO) from FOUND-01 align with priority tiers (P0-P5) from FOUND-02
- Ready for Plan 01-02 (Suppression System + Event Schema + Hightouch Reverse ETL) to reference these sections
- Ready for Phase 2 to reference consent categories and frequency caps when defining trigger eligibility

## Self-Check: PASSED

- FOUND: playbook-section-preference-center.md
- FOUND: playbook-section-frequency-caps.md
- FOUND: 01-01-SUMMARY.md
- FOUND: Task 1 commit (51a4b90)
- FOUND: Task 2 commit (bda9984)

---
*Phase: 01-foundation-safety-architecture*
*Plan: 01*
*Completed: 2026-03-22*
