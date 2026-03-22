# Research Summary -- Trigger Based Notifications (Bit2Me)

**Project:** Playbook Maestro de Trigger Based Notifications
**Domain:** Crypto exchange CRM notifications (EU/Spain)
**Researched:** 2026-03-22
**Confidence:** MEDIUM-HIGH

---

## Executive Summary

Bit2Me needs a trigger-based notification system to reactivate 72.4K dormant users holding EUR 19.5M in assets, fix the 0.12% M1 retention rate (vs. 25% Coinbase benchmark), and close the J-Post-FM gap that causes 60% D+7 drop-off with zero coverage. The research confirms that the existing stack -- CleverTap (CRM) + BigQuery (data warehouse) + Qlik (analytics) -- covers 80%+ of requirements. The only new components needed are Hightouch for Reverse ETL (EUR 350-500/mo), a Google Cloud Function for market trigger evaluation (~EUR 50/mo), and CoinGecko API for price feeds (EUR 129/mo if Pro needed). Total incremental cost: EUR 500-800/month. There is no reason to migrate from CleverTap or build custom notification infrastructure.

The recommended approach follows a dual-engine architecture: CleverTap handles real-time behavioral triggers (seconds latency) while BigQuery handles batch lifecycle triggers (hourly/daily) synced via Hightouch Reverse ETL. Market triggers use a hybrid pattern -- a Cloud Function polls CoinGecko every 5 minutes and uploads events to CleverTap for immediate campaign delivery. This mirrors the Coinbase architecture (DAG-based batch + real-time event listeners) at a fraction of the engineering cost. Phases 0-1 deliver 60%+ of trigger coverage with primarily CRM team effort (Katy), while Phases 2-3 require Engineering (Alvaro) but build on established foundations.

The dominant risk is not technical -- it is regulatory and fatigue. MiCA Article 66 requires all notifications to be "fair, clear, not misleading" with risk disclaimers. Price alerts must use only public data sources to avoid market abuse liability (MiCA Articles 87-92). Push notification fatigue destroys the channel permanently: 46% of users opt out at 2-5 pushes/week, and iOS push opt-out is effectively irreversible. The anti-fatigue formula (2/day hard cap, 5/week soft cap, priority tiers P0-P5) must be configured before any trigger goes live. The C8 whale suppression CSV must be uploaded to CleverTap immediately -- this is a blocking risk identified in the LC-OS audit that remains unresolved.

---

## Recommended Stack (What to Use)

- **CleverTap (keep):** CRM, campaign delivery, real-time Live Segments, frequency capping, Journeys (J1-J6). 2026 Gartner Leader. TesseractDB stores 2000+ data points/user. Clever.AI adds IntelliNODE, Scribe, Predictions. Migration to any alternative would cost 6+ months and reset Katy's operational knowledge. Stay.
- **BigQuery (keep):** Data warehouse, batch trigger evaluation, scoring computation. bit2me_lifecycle schema (V0a-V10) already exists. BigQuery ML available for future propensity scoring without data export.
- **Hightouch (new, EUR 350-500/mo):** Reverse ETL from BigQuery to CleverTap user profiles. Native BigQuery source + CleverTap destination (confirmed). Visual segment builder so Katy can build audiences without SQL. Incremental sync (only changed rows). Beats RudderStack on ease-of-use, beats Census on CleverTap-specific support.
- **Google Cloud Functions + Cloud Scheduler (new, ~EUR 50/mo):** Serverless market trigger evaluation. Polls CoinGecko every 5 minutes, evaluates trigger conditions, uploads events to CleverTap. Already in GCP ecosystem. No server management.
- **CoinGecko API (extend, EUR 0-129/mo):** Market data feed for price alerts. Already used by FOMO Agent. Free tier (30 calls/min) sufficient for MVP. Pro (500 calls/min) if polling 100+ assets.

**Do NOT use:** Kafka (overkill at 23K MMU -- Revolut avoided it at 50M users), Segment CDP (EUR 120K+/yr -- BigQuery IS the CDP), Braze (EUR 60-200K/yr migration), custom notification microservice (3-6 months to replicate CleverTap).

---

## Table Stakes (Build First or Users Leave)

These features exist at 4+ of 6 competitors (Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo). Missing them makes the product feel incomplete.

| Feature | Competitor Evidence | Priority |
|---------|-------------------|----------|
| **Price alerts (user-configured above/below)** | 6/6 competitors have this. Coinbase star+bell UX is the benchmark | Critical |
| **% change alerts** | 4/6 competitors. More intuitive for retail users who think in percentages | Critical |
| **Notification preference center** | 4/6 have per-category toggles. Without this, users disable ALL push to escape noise | Critical (build BEFORE any marketing trigger) |
| **Frequency capping** | Industry standard. 46% opt-out at 2-5 pushes/week | Critical (configure BEFORE any trigger) |
| **Transaction/security confirmations** | 6/6 competitors. Likely exists -- audit completeness | Audit |
| **Recurring buy confirmation + failure alerts** | 4/6 competitors. DCA = highest-retention segment | High |
| **Staking/earn reward notifications** | 4/6 competitors. Weekly digest: "You earned X this week" builds trust | High |
| **Watchlist + alert integration** | 3/6 competitors. Star + bell = Coinbase pattern. Watchlist without alerts is dead | High |

---

## Key Differentiators (Competitive Advantage)

These are blue ocean opportunities where no competitor excels, combined with Bit2Me-specific assets.

| Differentiator | Why Bit2Me Wins | Complexity |
|----------------|----------------|------------|
| **FOMO Score-driven reactivation** | 72.4K dormant users with EUR 19.5M AUC. Algorithmically timed re-engagement using urgency + social proof + market signals. FOMO Agent already designed. No competitor has this. | High (already designed) |
| **Lifecycle-aware nudges via Health Score** | Health Score formula (100-pt: Recency 30 + Frequency 20 + Product 15 + Balance 20 + Engagement 15) already defined. Proactive intervention before churn, not reactive after. | Medium |
| **Space Center gamification triggers** | "You're 200 B2M from Tier 4." Zero competitors have gamification-driven alerts. 7-tier system unique to Bit2Me. | Medium |
| **Portfolio-level alerts** | "Your portfolio is up/down X% today." Nobody does this. Blue ocean across all 6 competitors. | Medium |
| **Cross-product discovery triggers** | "You use Brokerage. Users like you earned 8.2% APY on Earn." Multi-product advantage no single-product competitor can match. | High |

---

## Architecture in One Page

Six components form the pipeline. Ownership is split between CRM team (Katy) and Engineering (Alvaro).

```
[1] EVENT INGESTION                [2] TRIGGER EVALUATION
    App SDK --> CleverTap               CleverTap Live Segments (real-time)
    Backend API --> CleverTap           BigQuery Scheduled Queries (batch)
    Backend API --> BigQuery            Cloud Function (market hybrid)
    Market Feed --> Cloud Function
         |                                    |
         v                                    v
[3] SCORING & PRIORITIZATION       [4] SUPPRESSION & FATIGUE
    Send Score = Market_Relevance       Frequency caps (CleverTap)
              * User_Relevance          C8 whale suppression
              * Fatigue_Headroom        Cooldown windows
              * Channel_Fit            Diego legal gate
    (BigQuery --> Reverse ETL)          Fatigue score (BigQuery)
         |                                    |
         v                                    v
[5] DELIVERY ORCHESTRATION         [6] MEASUREMENT & FEEDBACK
    Channel priority: Push > InApp      10% holdout per trigger
    > Email > SMS                       Per-trigger conversion tracking
    Template rendering (CleverTap)      Attribution in BigQuery
    Fallback logic                      Scoring model refinement
    (CleverTap Journeys)                (Qlik dashboards)
```

**Data flow summary:** Events flow in through CleverTap SDK (real-time) and BigQuery (batch). User attributes computed in BigQuery sync to CleverTap via Hightouch Reverse ETL every 15-60 minutes. CleverTap evaluates real-time triggers; BigQuery evaluates batch triggers. All notifications pass through the suppression layer before delivery. Measurement data flows back to BigQuery for scoring refinement.

**Four integration patterns (use all):**
1. **Batch Sync (Hightouch):** BigQuery user_profiles --> CleverTap user properties (lifecycle_stage, health_score, segment_id). Latency: 15-60 min.
2. **External Trigger API:** Cloud Function --> CleverTap (for market alerts). Latency: seconds. Rate limit: 3 req/sec, batch 1000 users/request. Public Beta -- contact CSM to enable.
3. **Live Segments:** CleverTap SDK event --> CleverTap campaign (for in-session behavioral triggers). Latency: seconds. Constraint: events must be within 2h past.
4. **API Segments:** BigQuery --> CleverTap Segment API --> "Segment Membership Change" event --> Journey entry. Converts batch computation to real-time trigger.

---

## Critical Compliance Constraints (Hard Blockers)

These are not best practices. These are legal requirements with fines up to EUR 5M or 10% of annual turnover.

| Constraint | Legal Basis | What It Means for Notifications |
|-----------|-------------|-------------------------------|
| **Separate consent per channel** | ePrivacy Directive Art. 13 + GDPR Art. 7 | OS push permission is NOT marketing consent. Must collect separate in-app consent for marketing push, email, SMS. Store per-channel flags. |
| **"Fair, clear, not misleading" copy** | MiCA Art. 66(1-3) | Every marketing notification must include or link to risk warning. Never use "pumping," "guaranteed," "risk-free," "don't miss out." APY claims must state variable rate + capital at risk. |
| **No investment advice in notifications** | MiCA Art. 66 + Title V Ch. 2 | "BTC crossed $70K" = safe. "BTC at $70K -- great entry point" = advisory = regulated service. Bright line test on all copy. |
| **Market abuse prevention** | MiCA Arts. 87-92 | Price alerts must use ONLY public data (CoinGecko). Must fire simultaneously for all eligible users -- no staggered sends by tier/balance. Maintain audit logs with timestamps. |
| **CNMV transition awareness** | Circular 1/2022 repealed; MiCA applies directly | Do NOT remove disclaimers from Circular era. Monitor draft "Ley de digitalizacion" for new requirements. Full MiCA authorization required by July 1, 2026. |
| **GDPR notification classification** | GDPR Art. 6(1)(a-f) | Transactional = Art. 6(1)(b) contractual necessity. Marketing = Art. 6(1)(a) explicit consent. User-configured alerts = Art. 6(1)(b) contract performance. Tag every template with its lawful basis. |
| **Diego legal gate** | Internal compliance control | ALL notification templates must be reviewed and approved by Diego before deployment. This is the enforcement mechanism for MiCA compliance. Non-negotiable. |

---

## Anti-Fatigue Baselines

These caps must be configured in CleverTap BEFORE any trigger goes live.

| Rule | Value | Rationale |
|------|-------|-----------|
| **Daily hard cap** | 2 notifications/user/day (all families) | 46% opt-out at 2-5/week. iOS opt-out is permanent. |
| **Weekly soft cap** | 5 notifications/user/week | Industry benchmark for finance apps |
| **Monthly ceiling** | 15 notifications/user/month | Prevents accumulation from multiple trigger families |
| **Cooldown between notifications** | 4 hours minimum (same channel) | Prevents clustering |
| **Cooldown after dismissed notification** | 24 hours (same trigger family) | Respect user signal |
| **After 3 consecutive dismissals** | 7-day cooldown for that trigger family | Decay engagement, not permission |
| **After 5 dismissals across all families** | Reduce to P0-P1 only for 14 days | Aggressive suppression before opt-out |
| **Quiet hours** | No push 22:00-08:00 user local time | 23% of apps violate this -- #1 opt-out driver |
| **Quiet hours exception** | P0 security alerts only | Login from new device, large withdrawal |

**Priority tiers (when cap is hit, lower tiers suppressed first):**
- P0: Security/transactional (never suppressed)
- P1: User-configured alerts (user asked for these)
- P2: Lifecycle critical (at-risk, pre-dormancy)
- P3: Market triggers (proactive, not user-configured)
- P4: Cross-sell / promotional
- P5: Re-engagement / generic

**Fatigue risk score (compute daily in BigQuery, sync to CleverTap):**
```
fatigue_risk = (notifications_sent_7d / 5) * 0.4
             + (notifications_dismissed_7d / notifications_sent_7d) * 0.3
             + (days_since_last_open / 7) * 0.3

If fatigue_risk > 0.7: suppress all P3+ for 48 hours
If fatigue_risk > 0.9: suppress all P2+ for 7 days
```

---

## Top 5 Pitfalls to Avoid

| # | Pitfall | Why It Hurts | Prevention Rule |
|---|---------|-------------|----------------|
| 1 | **Launching triggers without preference center + frequency caps** | Users disable ALL push to escape noise. iOS opt-out is permanent. Recovery rate <5%. | Ship preference center + caps in Phase 0, before any marketing trigger. 3 categories: Transactional (always on), Market (opt-in), Marketing (email default). |
| 2 | **Price alerts that cross into investment advice** | MiCA Art. 66 violation. Fines up to EUR 5M or 10% turnover. Personal exec liability. | Bright line test on every template. Keyword blocklist: "should," "opportunity," "don't miss," "good time to." Diego approves all. Informational only. |
| 3 | **Blast reactivation to 72.4K dormant users** | Hits invalid push tokens (deliverability damage), spam traps (email reputation), spam complaints. One spam trap hit can cut deliverability 50%. | Segment by dormancy duration. Start with most-engaged subset. Warm up 20-30% weekly over 4 weeks. Separate email subdomains (notifications vs marketing). |
| 4 | **Treating OS push permission as marketing consent** | ePrivacy Directive classifies push as electronic mail. OS permission is technical gate, not legal consent. GDPR violation. | After OS permission, show in-app consent screen per category. Record separately. Without in-app marketing consent: transactional and user-configured only. |
| 5 | **C8 whale suppression CSV not uploaded** | High-value users receive inappropriate marketing. Risk of losing top accounts. Identified in LC-OS audit as open gap. | Upload C8 CSV to CleverTap immediately. Zero engineering required. This is a Day 0 action. |

---

## Recommended Phase Order

### Phase 0: Data Foundation + Safety Rails (Weeks 1-2)

**Rationale:** Every trigger depends on events flowing correctly and suppression being active. Without this, any trigger launched risks destroying push permissions and violating compliance.

**Delivers:**
- Audited and complete event tracking (CleverTap SDK + Backend Upload Events API)
- BigQuery user_profiles table consolidated (lifecycle_stage, health_score, segment_id, holdings)
- Hightouch Reverse ETL operational (BigQuery --> CleverTap, 30-min sync)
- C8 whale suppression uploaded to CleverTap
- Frequency caps configured (2/day, 5/week, P0-P5 tiers)
- Notification preference center live (3 categories, per-channel toggles)
- InApp UTM tracking fixed (blocks measurement otherwise)

**Features addressed:** Frequency capping, preference center, C8 suppression, event tracking audit
**Pitfalls avoided:** #1 (no caps), #4 (consent), #5 (C8 gap)
**Owner:** Alvaro (BigQuery, Hightouch), Katy (CleverTap config, preference center), Diego (consent copy review)
**Research needed:** LOW -- standard CleverTap configuration + Hightouch setup docs. Audit of existing event tracking determines gap size.

---

### Phase 1: Behavioral Triggers + J-Post-FM (Weeks 3-4)

**Rationale:** These use CleverTap native capabilities. No engineering beyond Phase 0. Fastest path to revenue impact. J-Post-FM is the #1 gap from LC-OS audit (60% D+7 drop-off, zero coverage).

**Delivers:**
- 3-5 Live Action campaigns: first purchase celebration, inaction after deposit (24h), KYC abandonment (48h), reactivation welcome (7+ days inactive)
- J-Post-FM 48h journey (highest-impact new journey)
- Recurring buy confirmation + failure alerts
- Staking/earn reward weekly digest
- New listing push alerts
- FOMO Agent launch (pending Katy passcode, Diego copy, infra cron)
- 10% holdout group for measurement

**Features addressed:** J-Post-FM, recurring buy alerts, earn notifications, behavioral triggers, FOMO Agent
**Pitfalls avoided:** #2 (Diego reviews all templates), #3 (warm-up via engaged users first)
**Owner:** Katy (CleverTap campaigns), Diego (copy approval)
**Research needed:** LOW -- CleverTap Live Segments and Journeys are well-documented. Standard patterns.

---

### Phase 2: Lifecycle + Cross-sell Triggers via Reverse ETL (Weeks 5-7)

**Rationale:** Requires Hightouch operational (Phase 0) and suppression active (Phase 0-1). These are the BigQuery-computed triggers that enable lifecycle automation and cross-product discovery.

**Delivers:**
- BigQuery scheduled queries for: AT_RISK detection (Health Score < 40), near-dormancy (L3 = highest velocity segment), cross-sell eligibility (Brokerage user with Earn-eligible balance)
- Send Score computation in BigQuery (Market_Relevance * User_Relevance * Fatigue_Headroom * Channel_Fit)
- Hightouch syncs pushing trigger flags + scores to CleverTap
- CleverTap campaigns targeting synced lifecycle attributes
- Health Score-based interventions (proactive before churn)
- Dormant reactivation with balance context ("You have EUR 450 in BTC. Up 12% this month.")
- Fatigue score computation and sync

**Features addressed:** Lifecycle nudges, Health Score triggers, cross-sell discovery, dormant reactivation
**Pitfalls avoided:** #3 (warm-up dormant sends over 4 weeks), #2 (cross-sell copy through Diego)
**Owner:** Alvaro (BigQuery queries, Hightouch syncs), Katy (CleverTap campaigns), Marta (scoring validation)
**Research needed:** MEDIUM -- scoring formulas need iteration with real data; cross-sell eligibility matrix needs product team input on which assets are eligible for which products

---

### Phase 3: Market Triggers + User-Configured Price Alerts (Weeks 8-10)

**Rationale:** Most engineering-heavy component. Behavioral and lifecycle triggers deliver value while this is built. Requires app UI changes for user-configured alerts.

**Delivers:**
- Cloud Function polling CoinGecko every 5 minutes
- Proactive market alerts: "ETH is up 10% today" sent to ETH holders
- User-configured price target alerts (above/below) -- app UI + backend + CleverTap
- User-configured % change alerts (default 5/10/20%)
- Watchlist + alert integration (star + bell = Coinbase pattern)
- FOMO Agent integration with market trigger pipeline
- Per-alert cooldown: 1 alert per asset per 4 hours minimum (volatile market protection)

**Features addressed:** Price alerts, % change alerts, watchlist integration, proactive market alerts
**Pitfalls avoided:** #2 (public data only, bright line test, Diego review), market abuse (MiCA Arts. 87-92: simultaneous sends, audit logs)
**Owner:** Engineering (Cloud Function, app UI), Katy (CleverTap campaign config), Diego (market alert copy)
**Research needed:** HIGH -- CleverTap External Trigger API is in Public Beta (contact CSM to enable and test stability). App UI for price alerts needs Product team. CoinGecko rate limits need validation at scale.

---

### Phase 4: Measurement, Optimization + V2 Features (Week 11+)

**Rationale:** Requires baseline data from Phases 1-3. Cannot optimize what you cannot measure.

**Delivers:**
- notification_log table in BigQuery (full audit trail)
- Qlik dashboard: per-trigger delivery, engagement, conversion, revenue attributed
- Incremental lift measurement via holdout group analysis
- Scoring formula refinement based on actual performance
- V2 features: portfolio-level alerts, Space Center tier triggers, graduated LTV alerts (Nexo pattern), alert frequency control (one-off/daily/always), anti-phishing code in emails, smart send-time optimization (CleverTap Clever.AI), in-app notification center

**Features addressed:** Measurement framework, scoring optimization, V2 differentiators
**Owner:** Marta (analytics, lift measurement), Pablo T (Qlik dashboard), Growth team (scoring refinement)
**Research needed:** LOW for measurement (standard patterns). MEDIUM for Space Center triggers (depends on data availability in BigQuery, blocked on Maxim).

---

## Open Questions Requiring Internal Audit

These cannot be resolved from external research. They require specific internal action before proceeding.

| Question | Who Owns It | Blocks |
|----------|------------|--------|
| **What CleverTap events are currently tracked via SDK?** Full audit needed -- what exists, what is missing, what properties are attached | Katy + Engineering | Phase 0 |
| **CleverTap Account ID + Passcode for Hightouch connection** | Katy | Phase 0 |
| **CleverTap External Trigger API -- is it enabled on Bit2Me account?** Contact CSM (Public Beta) | Katy | Phase 3 |
| **Is the C8 whale suppression CSV ready to upload?** Who generates it? How often does it refresh? | Alvaro (BigQuery) + Katy (upload) | Phase 0 (Day 0) |
| **Which BigQuery Gold Layer views (V0a-V10) are production-ready?** Are lifecycle_stage, health_score, segment_id computed and current? | Alvaro + David Sales | Phase 0 |
| **InApp UTM tracking -- what is broken and what is the fix?** 13.93% CTR with 0 Qlik attribution | Alvaro + Pablo T | Phase 0 |
| **Space Center data availability in BigQuery** -- tier, points, challenges | Maxim + Alvaro | Phase 4 |
| **Diego template review throughput** -- if launching 30+ triggers, how many can Diego review per week? | Diego | All phases |
| **Email subdomain setup** -- does notifications.bit2me.com exist? SPF/DKIM/DMARC status? | Engineering/Infra | Phase 1 |
| **Current push opt-in rate baseline** -- what % of users have push enabled? Deliverable audience vs. total subscribers? | Katy (CleverTap) | Phase 0 |
| **Alvaro capacity check** -- V0a + token-holder filter + attribution already = 3 P0 on 1 person. Adding Hightouch + trigger queries. Can he absorb this? | Alvaro + Daniel | Phase 0-2 |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Existing stack covers 80%+. New components minimal, well-documented, low-risk. Pricing confirmed. |
| Features | **HIGH** | 6 competitors analyzed with official help center sources. Blue ocean gaps identified. |
| Architecture | **MEDIUM-HIGH** | Dual-engine pattern validated by Coinbase blog. All 4 CleverTap integration patterns verified via official docs. API rate limits confirmed. |
| Pitfalls | **HIGH** | Legal constraints verified against primary sources (EUR-Lex, ESMA reports). Fatigue benchmarks from multiple industry sources. |

**Overall confidence:** MEDIUM-HIGH

### Gaps Remaining

- **Scoring formula calibration:** Send Score structure is sound but weights need tuning with real Bit2Me data. Plan 2-3 iteration cycles in Phase 2.
- **CleverTap External Trigger API stability:** Public Beta, no SLA. Fallback: API Segments pattern (batch computation to real-time trigger via Segment Membership Change events).
- **Cross-sell eligibility matrix:** Which assets are eligible for which products (Earn, Pro, Card, Loan)? Internal product data not available from research. Required for Phase 2.
- **Alvaro SPOF risk:** 3 existing P0 tasks + new Hightouch + trigger queries. Capacity check before committing Phase 0-2 timelines.
- **WhatsApp channel:** Not researched in depth. Requires BSP, template approval, separate consent flow. 60-day minimum setup. Phase 4+ at earliest.

---

## Sources

### Primary -- Legal/Regulatory (HIGH confidence)
- MiCA Regulation full text (EUR-Lex): Articles 66, 86-92
- ESMA Final Report on MiCA Market Abuse Guidelines (April 2025)
- GDPR Articles 6, 7; EDPB Guidelines 1/2024 on Legitimate Interest
- ePrivacy Directive Article 13; JIPITEC 2025 academic analysis on push as electronic mail
- CNMV Circular 1/2022 (repealed) + Baker McKenzie analysis on MiCA transition

### Primary -- Platform Documentation (HIGH confidence)
- CleverTap: External Trigger API, Live Segments, API Segments, Frequency Caps, Journeys, Upload Events API, TesseractDB
- Hightouch: BigQuery-to-CleverTap integration (confirmed native connector)
- BigQuery: Scheduled queries, streaming inserts, Pub/Sub notifications
- Google Cloud Functions + Cloud Scheduler documentation

### Secondary -- Competitor Analysis (HIGH-MEDIUM confidence)
- Coinbase: Help center (price alerts) + engineering blog (notification platform, targeting engine)
- Binance: Official support docs (notifications, price alerts, customization)
- Kraken: Blog + support (chart-integrated market alerts)
- Bitpanda: Help center (price alerts, savings plans, staking, Spotlight)
- Revolut: Help center (crypto volatility toggle, watchlist alerts)
- Nexo: Support docs (notifications, loyalty tiers, AI insights, graduated LTV alerts)

### Secondary -- Industry Benchmarks (MEDIUM confidence)
- Pushwoosh 2025: Push notification opt-in rates, fatigue benchmarks, email deliverability
- MoEngage 2025: Push notification best practices and metrics
- Validity 2025: Email deliverability benchmarks (84% global inbox placement)
- Business of Apps: Push notification statistics 2025
- Retenshun: Push notification frequency sweet spot analysis

Full source lists with URLs available in: STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md.

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
