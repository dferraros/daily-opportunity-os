# Technology Stack

**Project:** Trigger-Based Notification System (Bit2Me)
**Researched:** 2026-03-22
**Updated:** 2026-03-22 (enhanced with CRM ecosystem research, competitor architecture, integration specifics)

## Recommended Stack

The existing stack (BigQuery + CleverTap + Qlik) covers 80%+ of requirements. New components are minimal. This is intentional -- Bit2Me should follow Revolut's philosophy of "use managed services, avoid custom infrastructure, invest engineering time in scoring logic not delivery plumbing."

### Core Platform (Already Owned)
| Technology | Version | Purpose | Why |
|---|---|---|---|
| CleverTap | Enterprise | CRM, campaign delivery, real-time triggers, channel management | Already deployed with J1-J6 journeys. 2026 Gartner Leader in Personalization Engines. TesseractDB stores 2000+ data points/user with 10-year lookback. Native Live Segments, frequency capping, multi-channel delivery. Clever.AI adds IntelliNODE (auto-route journeys), Scribe (copy gen), Predictions (churn), Recommendations. 66% conversion lift reported. No reason to replace. |
| BigQuery | Current | Data warehouse, batch trigger evaluation, scoring computation, user profile source of truth | Already deployed with bit2me_lifecycle schema (V0a-V10). Scheduled queries + streaming inserts cover batch + near-real-time needs. BigQuery ML available for future propensity scoring without data export. |
| Qlik | Current | Analytics dashboards, campaign performance reporting | Already deployed. Pablo T building dashboards. |

### New: Data Sync Layer
| Technology | Version | Purpose | Why |
|---|---|---|---|
| Hightouch | Business ($350+/mo) | Reverse ETL: BigQuery -> CleverTap user profile sync | Native BigQuery source + CleverTap destination (confirmed). Visual segment builder for CRM team. Incremental sync (only changed rows). Schedule as frequent as every 1 minute. Beats RudderStack on ease-of-use for non-engineers; beats Census on CleverTap-specific support (Census does not explicitly list CleverTap as destination). |

### New: Market Trigger Infrastructure
| Technology | Version | Purpose | Why |
|---|---|---|---|
| Google Cloud Functions | v2 | Serverless compute for market trigger evaluation (CoinGecko polling, trigger condition checks, CleverTap event upload) | Already in GCP ecosystem (BigQuery). No server management. Pay-per-invocation (~$10-50/mo at Bit2Me scale). 5-min Cloud Scheduler trigger is trivial. |
| Google Cloud Scheduler | Current | Cron trigger for Cloud Function (every 5 min for market data) | Native GCP. Simpler than managing cron on a VM. |
| CoinGecko API | Free/Pro ($129/mo) | Market data feed (prices, volumes, trending) | Already used by FOMO Agent. Free tier: 30 calls/min (sufficient for 5-min polling of top assets). Pro: 500 calls/min (needed if polling 100+ assets or sub-minute frequency). |

### New: CleverTap External Trigger API
| Technology | Version | Purpose | Why |
|---|---|---|---|
| CleverTap External Trigger API | Public Beta | Server-initiated campaign delivery via API call | Enables BigQuery-computed triggers to fire CleverTap campaigns without waiting for Reverse ETL sync. Supports Push, Email, WhatsApp, Webhook channels. Dynamic payload personalization. Rate limit: 3 req/sec (batch up to 1000 user IDs per request). Contact CSM to enable. |

### Supporting Libraries (Cloud Function)
| Library | Purpose | When to Use |
|---|---|---|
| `@google-cloud/bigquery` | Read trigger conditions and user holdings from BigQuery | Market trigger evaluation |
| `axios` or `node-fetch` | HTTP calls to CoinGecko API and CleverTap APIs | Market data + event upload |

---

## CRM Platform Deep Comparison

Bit2Me uses CleverTap. This section documents why staying is the right call, with specific evidence.

| Criterion | CleverTap (KEEP) | Braze | Iterable | MoEngage |
|---|---|---|---|---|
| **Pricing** | From $75/mo (5K MAU), enterprise custom | $60K-$200K/yr | Premium (comparable to Braze) | $40K-$100K/yr |
| **Mobile-first** | YES (designed for mobile) | Yes (strong mobile) | Email-first, mobile second | Yes |
| **Real-time analytics** | Native TesseractDB (in-memory, 100% real-time) | Requires integration with warehouse | Requires third-party BI tools | Good but less depth |
| **AI capabilities** | Clever.AI: IntelliNODE, Scribe, Predictions, Recommendations | Advanced AI/ML | Moderate | Strong |
| **BigQuery integration** | Reverse ETL via Hightouch (confirmed). Native export to GCS->BQ. | Similar Reverse ETL options | Similar | Similar |
| **Live triggered campaigns** | Live Segments + Live Actions + External Trigger API | Attribute triggers (strong) | Workflow triggers | Event triggers |
| **Fintech fit** | Strong: funnel analytics, behavioral segmentation | Strong but costly | Moderate | Strong (value play) |
| **Gartner recognition** | Leader in 2026 Personalization Engines MQ | Leader in various MQs | Not in top quadrant | Recognized |
| **G2 rating** | 4.6/5 (highest among peers) | High | High | High |
| **Learning curve** | Moderate-Steep (needs developer support) | Steep (significant engineering) | Easy (marketer-friendly) | Moderate |
| **Switching cost from current** | $0 (already deployed) | 6-12 months migration, loss of Katy's operational knowledge | Same | Same |

**Verdict:** Stay on CleverTap. The platform covers all trigger types needed (Live Segments for real-time, API Segments for batch, External Trigger API for server-initiated, Journeys for orchestration). Migration to any alternative would cost 6+ months and reset operational knowledge. CleverTap's recent Gartner Leader recognition and Clever.AI capabilities make it a strong long-term bet.

---

## Integration Architecture: BigQuery + CleverTap

### Three Integration Patterns (use all three)

#### Pattern 1: Batch Sync via Hightouch (Segments and Scores)
```
BigQuery Scheduled Query --> Staging View --> Hightouch Sync --> CleverTap User Properties
(hourly/daily)                                (every 15-60 min)   (lifecycle_stage, health_score,
                                                                   segment_id, product_eligibility)
```
- **What syncs:** Health Score, Lifecycle Stage, Segment (SEG-01 to SEG-37), product eligibility flags, FOMO Score, fatigue score, holdings by asset
- **CleverTap side:** Journeys use these attributes as entry/exit criteria. E.g., "Enter when Health_Score drops below 40 AND lifecycle_stage = AT_RISK"
- **Best for:** Lifecycle triggers, behavioral triggers, cross-sell triggers
- **Latency:** 15-60 minutes (acceptable for these trigger types)

#### Pattern 2: External Trigger API (Real-Time Market Triggers)
```
Cloud Function (event-driven) --> CleverTap External Trigger API
                                   (user_ids + dynamic payload: asset, price, % change)
```
- **What triggers:** Price alerts (user-configured thresholds), volatility spikes, proactive market alerts
- **Rate limit:** 3 req/sec. Batch user IDs per request (up to 1000 per call). For mass events (BTC crash affecting all users), switch to campaign targeting
- **Best for:** Time-sensitive market notifications where 15-60 min sync lag is too slow

#### Pattern 3: CleverTap Native Live Triggers (In-Session Behavior)
```
CleverTap SDK (app event) --> CleverTap Live Segment evaluation --> Triggered campaign
```
- **What triggers:** Cart abandonment, feature discovery, onboarding drop-off, inaction-within-time
- **Constraint:** Events must be within 2 hours past / 2 minutes future window
- **Best for:** Onboarding nudges, in-session cross-sell, post-deposit activation (J-Post-FM)
- **Latency:** Seconds

#### Pattern 4: API Segments (BigQuery-Computed Segment Membership)
```
BigQuery Query --> Cloud Function --> CleverTap Create Segment API --> "Segment Membership Change" event
                                                                        --> Triggers Journey entry
```
- **Why this matters:** Converts batch BigQuery computation into a CleverTap system event. When a user is added/removed from an API Segment, CleverTap fires `Segment Membership Change`, which can trigger real-time Journeys
- **Best for:** FOMO Agent targeting, dormant reactivation segments, AT_RISK detection

### CleverTap API Constraints to Design Around
| Constraint | Value | Mitigation |
|---|---|---|
| Concurrent API requests | 15 | Queue with backpressure in Cloud Function |
| Create Campaign API | 3 req/sec | Batch user IDs (up to 1000 per request) |
| External Trigger API | Public Beta | Contact CSM to enable. Test thoroughly. |
| Live campaign event freshness | 2h past, 2min future | Backend events must be uploaded promptly |
| Webhook timeout | 5 seconds, 2 retries | Keep webhook endpoints fast |
| Frequency caps | Global + per-campaign configurable | Set global: 1 marketing push/day, 5/week |

---

## How Competitors Architect This

### Coinbase (confirmed via engineering blog -- MEDIUM confidence)
- **Custom notification platform** with API-first design, iterative delivery approach (shipped MVP with config files, added UI later)
- **Content platform** on headless CMS with **consensus service** (multi-reviewer approval before publish -- similar to Diego's legal gate)
- **Targeting engine** with ML: two-tower deep learning model computes user-asset affinity via dense vector embeddings. Daily batch job pre-computes user embeddings; real-time asset embedding on price change; dot-product ranking for relevance
- **Smart Targeting** for cold-start campaigns: converts holistic user activity into embeddings where similar users cluster together
- **Anti-fatigue:** ML determines "most likely interested" users before sending -- relevance scoring, not just frequency caps
- **Scale:** Custom-built because 100M+ users, hundreds of notification types, bespoke compliance requirements
- **Key lesson for Bit2Me:** Coinbase's consensus service is worth copying. Diego's legal gate should be formalized (2 of 3 approvals: content creator + legal + strategy)

### Revolut (inferred from Google Cloud case study + engineering blog -- MEDIUM confidence)
- **Event-driven microservices** but intentionally **avoided Kafka** -- uses proprietary event store on Postgres
- **Google Cloud** infrastructure (GCE, not GKE). Deploys multiple times daily
- In-house notification system tightly coupled with onboarding (introduces push permissions with value framing)
- **Philosophy:** "Engineering organization that happens to be regulated as a bank." Speed > architectural purity
- **Key lesson for Bit2Me:** You do not need Kafka. Revolut proved you can build event-driven architecture on simpler foundations. Bit2Me should use Pub/Sub (managed) not Kafka (ops burden)

### Binance (inferred -- LOW confidence)
- Likely Kafka-based event streaming given scale (150M+ users)
- Custom notification infrastructure (no evidence of third-party CRM at that scale)
- WebSocket for real-time price feeds to app, tiered alert systems
- **Key lesson for Bit2Me:** At 23K MMU, Bit2Me is 6,500x smaller than Binance. Do not copy Binance's architecture

---

## What NOT to Use (and Why)

| Technology | Why Not |
|---|---|
| **Braze** | $60K-$200K/year. Steep learning curve, significant engineering setup. CleverTap already deployed. Migration would cost 6+ months and reset Katy's knowledge. Braze attribute triggers are nice but not worth switching. |
| **Iterable** | Email-first platform. Bit2Me is mobile-first. Weaker in-app messaging and behavioral analytics vs CleverTap. Requires third-party BI tools for reporting. |
| **OneSignal** | Developer-focused push tool, not a full CRM. Would fragment the stack (OneSignal push + CleverTap journeys). |
| **MoEngage** | Viable alternative (20-40% cheaper than Braze, strong mobile). But no reason to switch from CleverTap. Switching cost exceeds savings. |
| **Apache Kafka (self-managed)** | Massive ops overhead for 1 data engineer (Alvaro). Bit2Me processes thousands of events/hour, not millions/second. Revolut avoided Kafka by choice at 50M users. |
| **Confluent Cloud (managed Kafka)** | Overkill and expensive (~$1/hr for basic cluster). Pub/Sub is cheaper and simpler at Bit2Me's volume. |
| **Segment CDP** | $120K+/year for enterprise. BigQuery IS the CDP. Adding Segment creates redundant data layer. Use Hightouch for specific BQ->CleverTap sync instead. |
| **Customer.io** | Strong for B2B/SaaS, weak for fintech mobile. No TesseractDB equivalent. |
| **Firebase Cloud Messaging (direct)** | Raw push with no journey orchestration, frequency capping, or analytics. CleverTap already wraps FCM/APNs. |
| **Custom notification microservice** | 3-6 months engineering to replicate what CleverTap does. Bit2Me should not build infrastructure; they should build intelligence (scoring, triggers, copy). |
| **Pub/Sub + Dataflow** | Dataflow is overkill for simple event routing. Pub/Sub BigQuery Subscription writes directly to BQ with no pipeline code. Only use Dataflow if you need PII masking or complex transforms before BQ write. |
| **BigQuery Continuous Queries** | Adds complexity and cost over scheduled queries. Hourly/daily batch is sufficient for lifecycle triggers. Reserve for future if sub-minute latency needed. |

---

## Estimated Incremental Monthly Cost

| Item | Cost | Notes |
|---|---|---|
| Hightouch Business | $350-500/mo | 1 destination (CleverTap), frequent syncs |
| CoinGecko Pro | $129/mo | 500 calls/min for market triggers (if free tier insufficient) |
| Cloud Functions | ~$10-50/mo | Pay per invocation, minimal at Bit2Me scale |
| Cloud Scheduler | ~$3/mo | 3 free jobs/account, $0.10/job/month after |
| Pub/Sub (if added) | ~$20-100/mo | Based on message volume. Optional for Phase 1. |
| CleverTap WhatsApp (future) | TBD | Per-message pricing, requires BSP. Phase 4. |
| **Total incremental** | **~$500-800/mo** | On top of existing CleverTap + BigQuery costs |

---

## Installation / Setup

```bash
# Phase 0: Hightouch (SaaS -- no code installation)
# 1. Sign up at hightouch.com
# 2. Connect BigQuery as source (service account key)
# 3. Connect CleverTap as destination (Account ID + Passcode from Katy)
# 4. Create first model: SELECT user_id, lifecycle_stage, health_score, segment_id FROM bit2me_lifecycle.user_profiles
# 5. Map fields, set sync schedule (every 30 min), run initial full sync

# Phase 3: Cloud Function (market triggers)
npm init -y
npm install @google-cloud/bigquery axios

# Deploy:
gcloud functions deploy marketTriggerEvaluator \
  --runtime nodejs20 \
  --trigger-http \
  --region europe-west1 \
  --memory 256MB \
  --timeout 60s

# Cloud Scheduler:
gcloud scheduler jobs create http market-trigger-job \
  --schedule "*/5 * * * *" \
  --uri "https://REGION-PROJECT.cloudfunctions.net/marketTriggerEvaluator" \
  --http-method POST

# Phase 0: Enable CleverTap External Trigger API
# Contact CleverTap CSM (Public Beta feature)
# Requires campaign pre-configuration in dashboard
```

---

## Sources

### Official Documentation (HIGH confidence)
- [CleverTap External Trigger](https://docs.clevertap.com/docs/external-trigger)
- [CleverTap External Trigger API](https://developer.clevertap.com/docs/external-trigger-api)
- [CleverTap API Request Limits](https://developer.clevertap.com/docs/api-request-limit)
- [CleverTap Messaging Frequency Caps](https://docs.clevertap.com/docs/messaging-frequency-caps)
- [CleverTap Journeys Overview](https://docs.clevertap.com/docs/journeys)
- [CleverTap API Segments](https://docs.clevertap.com/docs/api-segments)
- [CleverTap TesseractDB](https://clevertap.com/blog/tesseractdb-the-future-of-martech-is-here/)
- [CleverTap Behavioral Messaging at 100B Scale](https://clevertap.com/blog/clevertap-engineering-behavioral-messaging-at-scale/)
- [CleverTap 2026 Gartner Leader](https://clevertap.com/blog/clevertap-named-a-leader-in-2026-gartner-magic-quadrant-for-personalization-engines/)
- [Hightouch BigQuery to CleverTap](https://hightouch.com/integrations/google-bigquery-to-clevertap)
- [RudderStack BigQuery to CleverTap](https://www.rudderstack.com/integration/clevertap/integrate-your-google-bigquery-data-warehouse-with-clevertap/)
- [Google Pub/Sub BigQuery Subscriptions](https://cloud.google.com/blog/products/data-analytics/pub-sub-launches-direct-path-to-bigquery-for-streaming-analytics)
- [BigQuery Continuous Queries](https://cloud.google.com/blog/products/data-analytics/bigquery-continuous-queries-makes-data-analysis-real-time)
- [CleverTap API Overview](https://developer.clevertap.com/docs/api-overview)

### Engineering Blogs (MEDIUM confidence)
- [Coinbase: Building a Notification Platform](https://www.coinbase.com/blog/building-a-notification-platform-at-coinbase)
- [Coinbase: General-Purpose Targeting Engine](https://www.coinbase.com/blog/from-intuition-to-precision-how-coinbase-built-a-general-purpose-targeting-engine)
- [Revolut on Google Cloud](https://cloud.google.com/customers/revolut)
- [Nubank Platform Engineering](https://building.nubank.com/platform-engineering-observability-and-scaling-mobile-development/)

### Industry Benchmarks (MEDIUM confidence)
- [Pushwoosh: Fintech Push Notifications 2025](https://www.pushwoosh.com/blog/push-notifications-fintech/)
- [MoEngage: Push Notification Best Practices 2025](https://www.moengage.com/learn/push-notification-best-practices/)
- [Latinia: Push Notification Fatigue in Banking](https://latinia.com/en/resources/how-to-prevent-push-notification-fatigue-in-banking)

### Platform Comparisons (MEDIUM confidence -- each vendor's blog is biased toward their product)
- [CleverTap vs Braze](https://clevertap.com/blog/clevertap-vs-braze-customer-engagement-platform/)
- [CleverTap: Braze vs Iterable](https://clevertap.com/blog/braze-vs-iterable/)
- [MoEngage: Braze Competitors](https://www.moengage.com/blog/braze-competitors/)
- [Census vs Hightouch](https://www.polytomic.com/versus/census-vs-hightouch)
- [Plotline: Braze Alternatives 2026](https://www.plotline.so/blog/braze-alternatives-and-competitors)
