# Phase 4: Measurement + Final Recommendations - Research

**Researched:** 2026-03-22
**Domain:** Notification measurement frameworks, incremental lift testing, executive reporting for crypto/fintech CRM
**Confidence:** HIGH

## Summary

Phase 4 closes the Playbook Maestro with three deliverables: (1) a measurement framework that quantifies per-trigger and per-family ROI using a Net Notification Value (NNV) formula, (2) a phased implementation roadmap (MVP/V2/V3) with exact team dependencies, and (3) an executive summary pitched at CEO Pablo Campos. This is a synthesis phase -- all inputs exist from Phases 1-3. No new trigger design, no new scoring formulas.

The measurement framework must balance two competing needs: proving that triggers generate incremental revenue (not just attributed revenue) while monitoring deliverability health to prevent the irreversible damage of push opt-outs. The holdout test design is critical because [external]'s small active user base (23k MMU) constrains statistical power -- per-trigger holdouts will be underpowered for low-frequency triggers, so family-level holdouts are the practical unit.

**Primary recommendation:** Design NNV as a per-trigger weekly metric computed in BigQuery. Use a 10% global holdout for aggregate lift measurement, with per-family holdouts only for the MVP top 3 families (A, F, D). Frame the executive summary around the gap between current state (M1 retention 0.12%) and achievable state with triggers (industry benchmark 8-12% for fintech).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MEAS-01 | KPIs por trigger y por familia -- CTR, session rate, trade rate, deposit rate | Industry benchmarks section provides fintech CTR ranges (2-9% push, 24% in-app). Phase 3 master trigger table provides the 33 triggers to map KPIs against. |
| MEAS-02 | Metricas de presion y fatiga -- notification pressure score, push disable lift, negative action rate | Phase 1 fatigue risk formula (Section 2.5) already defines the score. Research adds opt-out benchmarks (46% opt-out at 2-5/week) and negative action tracking patterns. |
| MEAS-03 | Metricas de deliverability -- push token health, email reputation, opt-in rate trend | Research provides opt-in benchmarks (72.3% finance, 43.9% iOS, 91.1% Android), delivery rate targets (>95%), and alert thresholds. |
| MEAS-04 | Incremental lift framework -- holdout design (10% control), A/B test design por trigger | Research covers holdout sizing (10% for >10k users, family-level aggregation for small triggers), CleverTap A/B test setup, and Welch's t-test for significance. |
| MEAS-05 | Net Notification Value formula -- incremental revenue minus opt-out cost minus complaint cost | NNV formula designed from industry components: incremental revenue per send - opt-out cost (LTV-weighted) - complaint cost. |
| REC-01 | Executive summary con impacto de negocio estimado (reactivacion, retencion, revenue) | Framing uses gap analysis: current M1 retention 0.12% vs 25% Coinbase benchmark; dormant AUC EUR 19.5M reactivation opportunity; EUR 30k/week A/B revenue target. |
| REC-02 | MVP 30 dias -- triggers, canales, recursos necesarios, dependencias | Phase 3 Section 12.3 already defines 4-wave 30-day plan. Phase 4 adds measurement overlay and resource quantification per team. |
| REC-03 | V2 90 dias -- triggers, nuevas capacidades, dependencias tecnicas | Phase 3 Section 12.4 defines V2 triggers (A-05, E-03, Earn APY). Phase 4 adds capability milestones and team sprint allocation. |
| REC-04 | V3 180 dias -- sistema completo, ML scoring, portfolio alerts | Phase 3 Section 12.4 defines V3 blockers (ESMA, ML, WhatsApp). Phase 4 adds strategic sequencing and budget implications. |
| REC-05 | Dependencias exactas por equipo (Katy CRM, Alvaro data, Diego legal, Engineering) | Research identifies existing blockers (Alvaro SPOF, Diego single gate, C8 CSV unresolved). Phase 4 maps each requirement to specific person-weeks. |
</phase_requirements>

## Standard Stack

This phase produces playbook content (markdown documents), not software. No libraries or packages are needed. The "stack" is the measurement infrastructure already in place from Phases 1-3.

### Core Infrastructure (Already Built)
| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| Fatigue Risk Score | Phase 1, Section 2.5 | Per-user fatigue quantification | Defined, needs BigQuery implementation |
| Send Score Final | Phase 3, Section 10 | Composite send eligibility score | Defined, needs BigQuery implementation |
| Master Trigger Table | Phase 3, Section 11 | 33 triggers x 14 columns | Complete |
| MVP Selection | Phase 3, Section 12 | Top 10 MVP + Top 10 NOT + 4-wave plan | Complete |
| Frequency Cap KPIs | Phase 1, Section 2.7 | 6 monitoring KPIs with AMBER/RED thresholds | Complete |

### New Components Phase 4 Must Define
| Component | Purpose | Dependency |
|-----------|---------|------------|
| NNV Formula | Per-trigger ROI quantification | Needs incremental revenue attribution + opt-out cost model |
| Holdout Architecture | Causal lift measurement | CleverTap A/B test + BigQuery analysis |
| Deliverability Dashboard | Token health + reputation monitoring | CleverTap Push Reachability + Google Postmaster |
| Executive Summary | CEO-facing business case | All prior phases |

## Architecture Patterns

### Pattern 1: Net Notification Value (NNV) Formula

**What:** A per-trigger, per-week metric that quantifies the net business impact of sending a notification, accounting for both revenue generated and channel damage caused.

**Formula:**
```
NNV_per_trigger = (incremental_revenue_per_send * sends_per_week)
                 - (opt_out_rate * sends_per_week * avg_LTV_per_opted_out_user)
                 - (complaint_rate * sends_per_week * complaint_handling_cost)

Where:
  incremental_revenue_per_send = (treatment_revenue - holdout_revenue) / treatment_sends
  opt_out_rate = push_disables_after_send / total_sends  (attributed within 24h window)
  complaint_rate = spam_reports / total_email_sends  (email channel only)
  avg_LTV_per_opted_out_user = projected_12mo_revenue_per_user * push_channel_contribution
```

**Simplified V1 (no LTV model yet):**
```
NNV_simple = incremental_sessions_per_send * avg_revenue_per_session
            - opt_out_rate * estimated_annual_push_revenue_per_user

Where:
  avg_revenue_per_session = total_weekly_revenue / total_weekly_sessions  (from BigQuery)
  estimated_annual_push_revenue_per_user = EUR 2.50  (industry benchmark for fintech, calibrate after 30 days)
```

**Confidence:** MEDIUM -- the formula structure is standard (industry sources MoEngage, Pushwoosh, VWO all converge on revenue-minus-cost framing). The EUR 2.50 annual push revenue estimate needs calibration with [external] data after MVP launch.

### Pattern 2: Holdout Test Architecture

**What:** A 10% global holdout + per-family holdouts for high-volume families.

**Design:**
```
Total addressable users (MMU): ~23,000

Global holdout (10%): 2,300 users
  - Receives NO trigger-based notifications (P2-P5)
  - Still receives P0 transactional and P1 user-configured
  - Purpose: measure aggregate trigger system lift

Per-family holdout (within treatment group):
  Family A (user-configured): NO holdout -- user explicitly requested these
  Family B (market): 10% holdout within eligible users
  Family D (lifecycle): 10% holdout within eligible users
  Family F (protective): NO holdout -- safety/compliance, cannot withhold
  Family C (behavioral): 10% holdout within eligible users
  Family E (cross-sell): 10% holdout within eligible users
```

**Statistical power note:** With 23k MMU and 10% holdout (2,300 control):
- For triggers targeting >5,000 users (e.g., D-02 Dormant with Balance = 72.4k eligible): detectable effect size ~2 percentage points at 80% power, alpha 0.05. Sufficient.
- For triggers targeting <2,000 users: aggregate over 4+ weeks before testing significance. Use family-level aggregation.

**CleverTap implementation:** Use CleverTap's built-in A/B test with control group (1:9 split). Statistical significance via Welch's t-test (built into CleverTap). For global holdout, create a persistent segment `holdout_global_10pct` in BigQuery, synced to CleverTap via Hightouch, excluded from all P2-P5 campaigns.

**Confidence:** HIGH -- holdout methodology is well-established. CleverTap supports the required A/B test infrastructure natively.

### Pattern 3: KPI Tree (Per-Trigger and Per-Family)

**What:** Hierarchical KPI structure from send-level metrics up to business impact.

```
Level 1: Send Metrics (per trigger, daily)
  - sends, deliveries, delivery_rate
  - opens, open_rate, CTR
  - dismissals, dismissal_rate

Level 2: Engagement Metrics (per trigger, weekly)
  - session_rate (sessions within 1h of open / opens)
  - action_rate (target action within 24h of open / opens)
  - trade_rate, deposit_rate, staking_rate (action-specific)

Level 3: Health Metrics (per family, weekly)
  - opt_out_rate (push disables within 24h of send / sends)
  - fatigue_score_avg (average fatigue_risk for recipients)
  - complaint_rate (email spam reports / email sends)

Level 4: Business Impact (aggregate, weekly)
  - incremental_revenue (treatment vs holdout)
  - incremental_sessions
  - NNV (net notification value)
  - push_permission_rate_trend (iOS opt-in % week-over-week)
```

**Confidence:** HIGH -- these are standard notification measurement layers used across MoEngage, CleverTap, and Airship documentation.

### Pattern 4: Executive Summary Framing

**What:** CEO-facing narrative structure for Pablo Campos.

**Frame around three gaps:**
1. **Retention gap:** M1 retention 0.12% vs Coinbase 25% (208x gap). Trigger system addresses the post-first-trade silence. Estimated lift: 3-5x current M1 retention in 90 days (conservative, based on fintech push engagement benchmarks showing 4x higher retention for push-engaged users).

2. **Dormant revenue gap:** 72.4k users with EUR 19.5M AUC sitting idle. Family D triggers (D-01 At-Risk, D-02 Dormant with Balance) directly target reactivation. Even 1% reactivation = 724 users returning to active trading. At avg EUR 12/user/month revenue: EUR 8,688/month incremental.

3. **A/B revenue gap:** EUR 6k/week actual vs EUR 30k/week target. Triggers create the testing surface -- 10 MVP triggers x 4 waves = 40+ testable variants in 30 days.

**Confidence:** MEDIUM -- the gap numbers are from [external] actuals (CLAUDE.md). The lift estimates are directional, based on industry benchmarks, not [external] historical data.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Statistical significance testing | Custom p-value calculator | CleverTap built-in Welch's t-test | CleverTap already computes significance for A/B tests natively |
| Push token health monitoring | Custom token audit pipeline | CleverTap Push Reachability dashboard | Real-time token status is already tracked by CleverTap |
| Email reputation monitoring | Custom bounce/complaint tracker | Google Postmaster Tools | Domain reputation, spam rate, delivery errors already surfaced |
| Holdout randomization | Manual user list management | BigQuery FARM_FINGERPRINT hash mod 10 | Deterministic, reproducible, no drift over time |
| Revenue attribution | Custom event joining | CleverTap Goals + BigQuery join on user_id + timestamp window | Multi-touch attribution is complex; use 24h post-click window as V1 |

## Common Pitfalls

### Pitfall 1: Survivorship Bias in Opt-Out Measurement
**What goes wrong:** Only measuring CTR/conversion for users who remain opted in. This overstates trigger value because the users most harmed by notifications have already left.
**Why it happens:** Standard campaign reports exclude opted-out users from denominator.
**How to avoid:** Track cumulative opt-out rate per trigger family over time. Include opt-out users in the NNV denominator.
**Warning signs:** CTR increasing while total reachable audience shrinking.

### Pitfall 2: Holdout Contamination
**What goes wrong:** Holdout users receive triggers through other channels (email when excluded from push, or lifecycle journey notifications that overlap with trigger-based notifications).
**Why it happens:** Holdout is applied per-channel, not per-user across all channels.
**How to avoid:** Global holdout must suppress ALL P2-P5 trigger-based notifications across ALL channels for the holdout segment. P0/P1 still deliver.
**Warning signs:** Holdout group showing suspiciously high engagement (because they received notifications through a side channel).

### Pitfall 3: Underpowered Per-Trigger Tests
**What goes wrong:** Declaring a trigger "doesn't work" based on 2 weeks of data with 500 recipients and a 2% conversion rate.
**Why it happens:** Small segment sizes + low base rates = need weeks/months of data.
**How to avoid:** Pre-calculate minimum detectable effect (MDE) for each trigger based on segment size. For triggers with <2,000 eligible users, commit to 4-week minimum observation window. Aggregate at family level for faster reads.
**Warning signs:** "No significant difference" after 1 week with <1,000 users per group.

### Pitfall 4: Attributing Organic Conversions to Triggers
**What goes wrong:** A user who would have traded anyway receives a price alert 10 minutes before trading. The trade is attributed to the notification.
**Why it happens:** Post-notification attribution windows capture organic behavior.
**How to avoid:** The holdout group is the solution. Compare treatment vs holdout conversion rates. The DIFFERENCE is the incremental lift. Absolute numbers are meaningless without the holdout baseline.

### Pitfall 5: Ignoring Notification Pressure Compound Effects
**What goes wrong:** Each trigger family passes its own fatigue check, but the combined load across families pushes users past the opt-out cliff (46% opt out at 2-5/week).
**Why it happens:** Family-level fatigue checks don't account for cross-family cumulative sends.
**How to avoid:** The fatigue_risk score (Phase 1, Section 2.5) already handles this -- it counts ALL sends across families. Ensure NNV reporting includes the cross-family fatigue_risk trend, not just per-family metrics.

## Industry Benchmarks (Crypto/Fintech Push Notifications)

### CTR Benchmarks
| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|
| Fintech push CTR (Android) | 2.84% (Pushwoosh) / ~9% (CleverTap) | Pushwoosh 2025, CleverTap 2025 | MEDIUM -- range reflects methodology differences |
| Fintech push CTR (iOS) | 2.09% (Pushwoosh) / ~6% (CleverTap) | Pushwoosh 2025, CleverTap 2025 | MEDIUM |
| Segmented/personalized push CTR | Up to 9.35% | Pushwoosh 2025 | HIGH |
| In-app notification CTR | ~24% | Promodo 2026 | MEDIUM |
| All-industry push CTR (Android) | 4.6% | Pushwoosh 2025 | HIGH |
| All-industry push CTR (iOS) | 3.4% | Pushwoosh 2025 | HIGH |

### Opt-In / Opt-Out Benchmarks
| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|
| Finance app push opt-in rate | 72.3% | Pushwoosh 2025 | HIGH |
| iOS push opt-in rate (all industries) | 43.9% | Pushwoosh 2025 | HIGH |
| Android push opt-in rate (all industries) | 91.1% | Pushwoosh 2025 | HIGH |
| Opt-out cliff: 2-5 messages/week | 46% of users opt out | Pushwoosh 2025 | HIGH |
| Opt-out cliff: 6-10 messages/week | 32% additional opt out | Pushwoosh 2025 | HIGH |
| 1 push/week opt-out rate | 10% disable notifications | Mobiloud 2025 | MEDIUM |

### Retention Impact
| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|
| Push-engaged users retention lift | 4x more engaged, 2x more retained | Airship 2025 | HIGH |
| Weekly notification retention lift | 440% higher retention | Mobiloud 2025 | MEDIUM |
| Zero notifications in 90 days churn rate | 95% churn | Airship 2025 | HIGH |

### Deliverability Health Thresholds (Recommended for [external])
| Metric | GREEN | AMBER | RED | Source |
|--------|-------|-------|-----|--------|
| Push delivery rate | >95% | 85-95% | <85% = token hygiene needed | Phase 1 Section 2.7 + industry |
| Push opt-out rate (weekly) | <0.5% | 0.5-0.8% | >1% = STOP P3+ | Phase 1 Section 2.7 |
| Email spam complaint rate | <0.1% | 0.08-0.1% | >0.1% = pause email | Google Postmaster standards |
| iOS push permission rate | >60% | 50-60% | <50% = consent UX issue | Phase 1 Section 2.7 |
| Notification dismissal rate | <40% | 40-50% | >50% = relevance issue | Phase 1 Section 2.7 |
| Avg fatigue_risk score (active users) | <0.4 | 0.4-0.6 | >0.6 = reduce P3-P5 frequency | Phase 1 Section 2.5 |

## Code Examples

### BigQuery: Global Holdout Assignment (Deterministic)
```sql
-- Deterministic holdout: same user always in same group
-- Uses FARM_FINGERPRINT for reproducible hashing
SELECT
  user_id,
  CASE
    WHEN MOD(ABS(FARM_FINGERPRINT(CAST(user_id AS STRING))), 10) = 0
    THEN 'holdout'
    ELSE 'treatment'
  END AS holdout_group
FROM `[external]_lifecycle.user_profiles`
WHERE lifecycle_stage NOT IN ('EXCLUDED', 'CHURNED')
```

### BigQuery: NNV Calculation (Weekly, Per Trigger)
```sql
-- Net Notification Value per trigger per week
WITH trigger_sends AS (
  SELECT
    trigger_id,
    COUNT(*) AS total_sends,
    COUNTIF(user_opened = TRUE) AS opens,
    COUNTIF(user_converted = TRUE) AS conversions,
    COUNTIF(user_opted_out_24h = TRUE) AS opt_outs,
    SUM(CASE WHEN user_converted THEN attributed_revenue ELSE 0 END) AS gross_revenue
  FROM `[external]_lifecycle.notification_events`
  WHERE send_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
    AND holdout_group = 'treatment'
  GROUP BY trigger_id
),
holdout_baseline AS (
  SELECT
    trigger_id,
    COUNT(*) AS holdout_users,
    COUNTIF(user_converted = TRUE) AS holdout_conversions,
    SUM(CASE WHEN user_converted THEN attributed_revenue ELSE 0 END) AS holdout_revenue
  FROM `[external]_lifecycle.notification_events`
  WHERE send_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
    AND holdout_group = 'holdout'
  GROUP BY trigger_id
)
SELECT
  t.trigger_id,
  t.total_sends,
  t.gross_revenue,
  -- Incremental revenue (treatment rate - holdout rate) * treatment sends
  (t.gross_revenue / NULLIF(t.total_sends, 0)
   - h.holdout_revenue / NULLIF(h.holdout_users, 0)
  ) * t.total_sends AS incremental_revenue,
  -- Opt-out cost (opt_outs * estimated annual push value per user)
  t.opt_outs * 2.50 AS opt_out_cost,  -- EUR 2.50 calibrate after 30 days
  -- NNV
  (t.gross_revenue / NULLIF(t.total_sends, 0)
   - h.holdout_revenue / NULLIF(h.holdout_users, 0)
  ) * t.total_sends - (t.opt_outs * 2.50) AS nnv_weekly
FROM trigger_sends t
LEFT JOIN holdout_baseline h USING (trigger_id)
ORDER BY nnv_weekly DESC
```

### CleverTap: Holdout Segment Exclusion (Campaign Targeting)
```
Segment: holdout_global_10pct = false
AND consent_marketing_push = true
AND notification_fatigue_score < [threshold_per_tier]
AND C8_Whale_Suppression = false
AND Excluded_Users = false
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Last-touch attribution for notifications | Holdout-based incremental lift | 2023-2024 (industry shift) | 23% more accurate ROI per AppsFlyer |
| Global frequency caps only | Per-user adaptive fatigue scoring | 2024-2025 | Reduces opt-outs without reducing reach for engaged users |
| Manual A/B test significance | Platform-native Welch's t-test | CleverTap built-in | No custom stats needed |
| Channel-specific opt-out tracking | Cross-channel notification pressure | 2024 (Chrome Safety Check, iOS 18) | Must track cumulative cross-channel pressure |

## Open Questions

1. **[external]-specific push opt-in rate unknown**
   - What we know: Industry benchmark for finance apps is 72.3%. [external]'s actual rate is not documented.
   - What's unclear: Whether [external]'s rate is above or below benchmark. iOS vs Android split for [external] users.
   - Recommendation: Katy pulls current push reachability from CleverTap before MVP launch. This number becomes the baseline for MEAS-03.

2. **Revenue per session for NNV calibration**
   - What we know: Total weekly revenue and session counts exist in BigQuery.
   - What's unclear: What is the actual avg_revenue_per_session for [external] users?
   - Recommendation: Alvaro runs a one-time query to calculate this. Used as the NNV calibration constant.

3. **CleverTap External Trigger API stability**
   - What we know: API is Public Beta (flagged in STATE.md).
   - What's unclear: Whether holdout group management can be done via API or must be segment-based.
   - Recommendation: Use segment-based holdout (BigQuery -> Hightouch -> CleverTap segment). Do not depend on API for holdout logic.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual review (playbook document, not code) |
| Config file | N/A |
| Quick run command | `grep -c "MEAS-\|REC-" playbook-section-*.md` (verify requirement coverage) |
| Full suite command | Manual cross-reference of each MEAS/REC requirement against playbook sections |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MEAS-01 | KPIs per trigger and family documented | manual-review | Verify KPI tree exists with CTR, session, trade, deposit per trigger | Wave 0 |
| MEAS-02 | Pressure/fatigue metrics documented | manual-review | Verify fatigue score thresholds + opt-out tracking defined | Wave 0 |
| MEAS-03 | Deliverability metrics documented | manual-review | Verify token health, email reputation, opt-in trend thresholds | Wave 0 |
| MEAS-04 | Holdout design documented | manual-review | Verify 10% holdout + per-family holdout + statistical power notes | Wave 0 |
| MEAS-05 | NNV formula documented | manual-review | Verify formula includes incremental revenue, opt-out cost, complaint cost | Wave 0 |
| REC-01 | Executive summary with business impact | manual-review | Verify reactivation, retention, revenue estimates with sources | Wave 0 |
| REC-02 | MVP 30 days with resources/dependencies | manual-review | Verify cross-references Phase 3 Section 12.3 + adds resource quantification | Wave 0 |
| REC-03 | V2 90 days documented | manual-review | Verify triggers, capabilities, dependencies per team | Wave 0 |
| REC-04 | V3 180 days documented | manual-review | Verify ML, portfolio, WhatsApp roadmap items | Wave 0 |
| REC-05 | Team dependencies exact | manual-review | Verify Katy, Alvaro, Diego, Engineering person-week estimates | Wave 0 |

### Sampling Rate
- **Per task commit:** Manual review of playbook section completeness
- **Per wave merge:** Full requirement cross-reference
- **Phase gate:** All 10 requirements (MEAS-01 to MEAS-05, REC-01 to REC-05) verified present in playbook sections

### Wave 0 Gaps
None -- this is a document-only phase. No test infrastructure needed. Validation is requirement coverage verification.

## Sources

### Primary (HIGH confidence)
- Phase 1 Section 2.5-2.7: Fatigue risk formula, monitoring KPIs, campaign checklist (internal playbook)
- Phase 3 Section 11-12: Master trigger table, MVP selection, 30-day launch plan (internal playbook)
- CleverTap A/B Testing docs: https://docs.clevertap.com/docs/create-ab-tests
- CleverTap Product A/B Tests docs: https://docs.clevertap.com/docs/product-ab-tests

### Secondary (MEDIUM confidence)
- Pushwoosh 2025 Push Notification Benchmarks: https://www.pushwoosh.com/blog/push-notification-benchmarks/
- Pushwoosh Fintech Push Notifications 2025: https://www.pushwoosh.com/blog/push-notifications-fintech/
- CleverTap Push Notification Metrics: https://clevertap.com/blog/push-notification-metrics-ctr-open-rate/
- MoEngage Push Notification ROI: https://www.moengage.com/blog/push-notification-metrics/
- Promodo Fintech Marketing Benchmarks 2026: https://www.promodo.com/blog/fintech-marketing-benchmarks
- Airship 2025 Mobile Push Benchmarks: https://www.airship.com/resources/benchmark-report/mobile-app-push-notification-benchmarks-for-2025/
- Mobiloud Push Notification Statistics 2025: https://www.mobiloud.com/blog/push-notification-statistics

### Tertiary (LOW confidence)
- Holdout group sizing guidance: https://zyabkina.com/control-holdout-group-sample-size-calculation/
- CXL holdout group analysis: https://cxl.com/blog/hold-out-groups/
- Incremental lift test methodology: https://towardsdatascience.com/marketing-incremental-lift-test-101-f2983af1da8e/

## Metadata

**Confidence breakdown:**
- Industry benchmarks: HIGH - multiple independent sources (Pushwoosh, CleverTap, Airship) converge on ranges
- NNV formula: MEDIUM - formula structure is standard, but EUR constants need [external] calibration
- Holdout design: HIGH - well-established methodology, CleverTap supports natively
- Executive framing: MEDIUM - gap numbers are from [external] actuals, but lift estimates are industry-based projections
- Deliverability thresholds: HIGH - Phase 1 already defined these; research validates alignment with industry

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days -- stable domain, benchmarks update annually)
