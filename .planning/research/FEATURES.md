# Feature Landscape: Trigger-Based Notifications for Crypto/Fintech

**Domain:** Crypto exchange CRM notifications
**Researched:** 2026-03-22 (updated with full competitor matrix)

---

## Part A: Competitor Features Research

### Comparative Matrix: Notification Types by Competitor

| Feature | Coinbase | Binance | Kraken | Bitpanda | Revolut | Nexo | Bit2Me (current) |
|---------|----------|---------|--------|----------|---------|------|-------------------|
| **Price target alerts** (above/below) | YES | YES | YES | YES | YES (stocks only) | YES | NO |
| **% change alerts** | YES | YES | YES (% buttons) | NO | YES (fixed 2% only) | NO | NO |
| **Volatility alerts** (auto) | NO | NO | NO | NO | YES (fixed 2% toggle) | YES (AI-driven) | NO |
| **Watchlist alerts** | YES (star + bell) | NO (separate) | YES (favorites sync) | NO | YES (5% move) | NO | NO |
| **Portfolio value alerts** | NO | NO | NO | NO | NO | YES (dashboard) | NO |
| **Order fill notifications** | YES | YES | YES | YES | YES | N/A | YES (assumed) |
| **Recurring buy confirmation** | YES | YES (Auto-Invest) | NO | YES (Savings Plan) | YES (Auto-Buy) | NO | NO |
| **Recurring buy failure** | YES | YES | NO | YES (email) | YES | NO | NO |
| **Staking reward payout** | YES (email) | NO (native) | YES | YES (weekly) | NO | YES (daily) | NO |
| **Earn/yield rate changes** | NO | NO | NO | NO | NO | NO | NO |
| **New listing alerts** | NO (native) | YES | NO (native) | YES (Spotlight) | NO | NO | NO |
| **Loyalty/tier alerts** | NO | NO | NO | NO | NO | YES (tier changes) | NO |
| **LTV/margin call alerts** | N/A | YES (liquidation) | YES | YES (margin) | N/A | YES (3-tier) | NO |
| **Security alerts** | YES | YES | YES | YES | YES | YES (anti-phishing) | YES (assumed) |
| **AI market insights** | NO | NO | NO | NO | NO | YES | NO |
| **Gamification/rewards alerts** | YES (Learn) | YES (Launchpad) | NO | YES (Spotlight) | NO | NO | NO |

### Channels by Competitor

| Channel | Coinbase | Binance | Kraken | Bitpanda | Revolut | Nexo |
|---------|----------|---------|--------|----------|---------|------|
| **Push** | YES | YES | YES | YES | YES | YES |
| **Email** | YES | YES | NO (web only) | YES | YES | YES |
| **In-App** | YES | YES (inbox) | YES | NO | YES | YES |
| **SMS** | NO | NO | NO | NO | NO | YES (security) |
| **Browser** | NO | YES (sound) | YES (sound + pop) | NO | NO | NO |

### Preference Center Granularity

| Capability | Coinbase | Binance | Kraken | Bitpanda | Revolut | Nexo |
|------------|----------|---------|--------|----------|---------|------|
| **Per-channel toggle** | YES | YES | YES | NO | YES | YES |
| **Per-category toggle** | YES | YES (marketing/ops/risk) | NO | NO | YES | YES |
| **Alert frequency** | YES (dropdown) | YES (one-off/daily/always) | NO | NO | NO | NO |
| **Alert limits** | Unlimited | 50 total, 10/pair, 90d expiry | Undocumented | Undocumented | Undocumented | Undocumented |
| **Notification language** | NO | YES | NO | NO | NO | NO |
| **Mute/snooze** | NO | YES (per alert) | NO | NO | NO | NO |

### Asset Scope for Alerts

| Scope | Coinbase | Binance | Kraken | Bitpanda | Revolut | Nexo |
|-------|----------|---------|--------|----------|---------|------|
| **Crypto** | All listed | All pairs (Pro only) | All spot + futures | All listed | 280+ (limited alerts) | All listed |
| **Stocks/ETFs** | YES | NO | NO | YES | YES (4000+) | NO |
| **Commodities** | NO | NO | NO | YES (metals) | YES | NO |

---

### Per-Competitor Deep Dives

#### Coinbase
**Confidence:** HIGH (official help center + engineering blog)

**Strengths:**
- Watchlist-first UX: star an asset, tap bell icon. Clean two-step mental model.
- Per-alert channel selection: each alert independently chooses push, email, or in-app.
- Frequency dropdown per alert (not global).
- Staking milestone emails at key unbonding stages.
- Real-time price alerts launched 2024 with smart defaults for portfolio holdings.
- Documented "responsive alerts" approach: studied which alerts drive trades vs. cause fatigue, removed automated ones, made rest opt-in, improving push retention.

**Weaknesses:**
- No volatility alerts (price target only).
- No portfolio-level alerts (e.g., "portfolio dropped 10%").
- No AI-driven or contextual alerts.
- Previously had more robust alerting that was downgraded -- cautionary tale about over-building.

**Sources:** [Price Alerts](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/what-are-price-alerts) | [Notification Platform Blog](https://www.coinbase.com/blog/building-a-notification-platform-at-coinbase) | [Real-Time Alerts Blog](https://www.coinbase.com/blog/new-real-time-price-alerts-for-the-coinbase-app)

#### Binance
**Confidence:** HIGH (official support docs)

**Strengths:**
- Most flexible alert creation: price target OR % change, one-off/daily/always frequency.
- Desktop app with sound alerts.
- Clean notification categories: Marketing, Operational, Transaction Risk.
- P2P-specific price alerts (unique).
- Per-alert mute toggle (granular fatigue control).
- Multi-language notification support.

**Weaknesses:**
- Price alerts restricted to Pro mode (Lite users get nothing).
- Hard limits: 50 alerts, 10/pair, 90-day expiry.
- No native staking notifications (third-party bots fill the gap).
- Watchlist and alerts are separate, unconnected flows.

**Sources:** [Customize Notifications](https://www.binance.com/en/support/faq/how-to-customize-your-binance-app-settings-and-notifications-0a498da1689f4f56982b50a75721f310) | [Set Price Alert](https://www.binance.com/en/support/faq/how-to-set-a-price-alert-on-binance-53349d11525b42f79ff20d3ea1dc312b)

#### Kraken
**Confidence:** MEDIUM-HIGH (blog + support article)

**Strengths:**
- Chart-integrated alerts: right-click chart to set alert at that price. Best-in-class for traders.
- Active alerts visible as horizontal lines on chart.
- Cross-platform sync: alerts sync between Pro web and Pro mobile.
- Alert history alongside active alerts.

**Weaknesses:**
- No email channel (push and browser only).
- No frequency control.
- No staking, earn, or portfolio alerts.
- Split app ecosystem (Kraken vs. Kraken Pro) creates confusion.

**Sources:** [Market Alerts](https://support.kraken.com/articles/price-alerts) | [Price Alerts Blog](https://blog.kraken.com/product/now-live-price-alerts-on-kraken-pro)

#### Bitpanda
**Confidence:** MEDIUM (help center confirmed features; notification settings sparse)

**Strengths:**
- Savings Plan failure emails (proactive DCA failure alerts).
- Spotlight launch push (new coin countdown + go-live notification).
- Weekly staking reward distribution with trackable history.
- Margin pre-liquidation alerts.
- Multi-asset scope: crypto, stocks, ETFs, metals, indices.

**Weaknesses:**
- Price alerts are email-only (no push for price targets).
- No in-app notification center.
- No % change alerts, no watchlist integration.
- No preference center for notification categories.

**Sources:** [Price Alerts](https://support.bitpanda.com/hc/en-us/articles/360000902305-What-is-the-price-alert-feature) | [Savings Plans](https://support.bitpanda.com/hc/en-us/articles/360003576300-How-do-I-create-a-savings-plan) | [Staking](https://support.bitpanda.com/hc/en-us/articles/4824180360092-Bitpanda-Staking)

#### Revolut
**Confidence:** MEDIUM (help center confirmed; crypto alerts notably basic vs. stocks)

**Strengths:**
- Volatility toggle: simple on/off for "crypto moved >2%." Zero setup friction.
- Watchlist auto-alerts: stocks on watchlist trigger at 5% move (no setup needed).
- ML-driven fraud detection with instant alerts.
- Cross-asset consistency in UX.

**Weaknesses:**
- Crypto alerts are extremely basic: only the 2% volatility toggle (NOT customizable).
- Stock alerts far more advanced than crypto alerts.
- No custom price targets for crypto.
- Fixed 2% threshold generates daily spam for any crypto asset. Community forums full of complaints. This is an anti-pattern.

**Sources:** [Crypto Volatility](https://help.revolut.com/en-SE/help/wealth/cryptocurrencies/getting-cryptocurrency-exposure/can-i-be-notified-of-price-volatility/) | [Watchlist & Alerts](https://help.revolut.com/help/wealth/stocks/getting-started-with-trading/managing-your-trading-account/trading-alerts/managing-my-trading-watchlist-and-price-alerts/)

#### Nexo
**Confidence:** MEDIUM (reviews + partial support docs; some inferred)

**Strengths:**
- AI Insights: daily market digest pushed to all users. Zero config. Unique differentiator.
- Graduated LTV alerts at 71.4%, 74.1%, 76.9% -- progressive urgency, not binary.
- Daily earn interest payout confirmations.
- Loyalty tier change notifications (Base/Silver/Gold/Platinum).
- Anti-scam engine: contextual warnings that adapt to risk level.
- Anti-phishing code in all emails (unique code users verify).

**Weaknesses:**
- No custom price target alerts.
- No watchlist functionality.
- No recurring buy product.
- Limited preference center documentation.

**Sources:** [Manage Notifications](https://support.nexo.com/article/how-do-i-manage-my-notifications) | [Nexo Review (Coin Bureau)](https://coinbureau.com/review/nexo-review) | [Loyalty Program](https://support.nexo.com/article/nexo-loyalty-program-explained)

---

### Blue Ocean Gaps (No Competitor Excels Here)

1. **Portfolio-level alerts**: Nobody sends "Your portfolio is up/down X% today."
2. **Cross-product notifications**: No exchange connects products via alerts (e.g., "SOL unlocked. Trade on Pro or move to Earn?").
3. **Earn rate change alerts**: When APY changes, nobody proactively notifies.
4. **Gamification-driven alerts**: Space Center is unique to Bit2Me. No competitor has tier/challenge/reward triggers.
5. **Personalized alert suggestions**: "Based on your holdings, set an alert for ETH at $X" -- nobody does this.
6. **Alert-to-action flow**: All competitors land alerts on generic page. None have "trigger > one-tap trade."

---

## Part B: Bit2Me Feature Landscape

### Table Stakes

Features users expect. Missing = product feels incomplete or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Price alerts (user-configured)** | Every competitor has them. Users expect "alert me when BTC hits $X." Coinbase/Binance UX is the benchmark | Medium | Requires price feed + user preference storage + real-time evaluation |
| **% change alerts** | 4 of 6 competitors offer this. More intuitive than price targets for retail users who think in % | Medium | Default suggestions: 5%, 10%, 20%. Let user type custom % |
| **Transaction confirmations** | Regulatory + trust requirement | Low | Likely exists via CleverTap. Audit completeness |
| **Security alerts** | Non-negotiable for fintech. All 6 competitors have comprehensive security alerts | Low | Likely exists. Enhance with IP geolocation |
| **KYC status updates** | Users waiting for verification expect progress visibility | Low | Lifecycle trigger on KYC state change |
| **Deposit/withdrawal confirmations** | Money movement = mandatory notification | Low | Transactional, likely implemented |
| **New listing announcements** | Binance and Bitpanda do this. Users expect to know when new assets appear | Low | Manual or automated from listing event |
| **Frequency capping** | 46% opt-out at 2-5 pushes/week. 1 marketing push/day max | Medium | CleverTap Global Frequency Caps. Configure, don't build |
| **Notification preference center** | 4 of 6 competitors have per-category toggles. Without this, users disable ALL push to stop noise. Kills channel permanently | Medium | 3 categories: Transactional (always on), Market (opt-in), Marketing (email default). Copy Binance 3-tier model |
| **Opt-in/opt-out granularity** | GDPR + MiCA requirement. Per-channel, per-type control | Medium | Push/email/in-app per notification category |
| **Watchlist + alert integration** | 3 of 6 competitors tie these together. Watchlist without alerts = dead feature | Medium | Star + bell = Coinbase pattern |
| **Recurring buy confirmations + failures** | 4 of 6 competitors. DCA = highest-retention segment. They NEED execution confirmation | Low | Email + push for failures. Push only for confirmations |
| **Staking/earn reward notifications** | 4 of 6 competitors. Builds trust, reminds users value is growing | Low | Weekly digest: "You earned X this week" |

### Differentiators

Features that set Bit2Me apart. Not universally expected, but create competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **FOMO Score-driven reactivation** | Algorithmically timed re-engagement using urgency + social proof + market signals. 72.4K dormant users with EUR19.5M AUC | High | Bit2Me unique IP. FOMO Agent already designed |
| **Proactive market alerts** (not user-configured) | "ETH is up 10% today" sent to ETH holders. Drives dormant re-engagement | Medium | Cloud Function + CoinGecko + CleverTap |
| **Lifecycle-aware nudges** | "You deposited 3 days ago but haven't purchased." Triggered by lifecycle stage | Medium | BigQuery lifecycle + Reverse ETL + CleverTap |
| **Cross-product discovery triggers** | "You use Brokerage. Users like you earned 8.2% APY on Earn" | High | Product eligibility matrix + usage patterns |
| **Health Score-based interventions** | Proactive before churn, not reactive after. Alert when health drops | Medium | Health Score formula already defined |
| **Whale protection (C8 suppression)** | High-value users receive NO marketing push. Only transactional | Low | C8 segment suppression. Upload to CleverTap |
| **Space Center gamification triggers** | "You're 200 B2M from Tier 4." NO competitor has gamification-driven alerts | Medium | Depends on Space Center data in BigQuery |
| **Portfolio-level alerts** | "Portfolio dropped 10% today." Blue ocean -- zero competitors do this well | Medium | BigQuery portfolio value calculation |
| **Graduated LTV alerts** (copy Nexo) | 3-tier progressive warnings for Loan product | Low | Critical for Loan trust |
| **New listing FOMO alerts** (copy Binance/Bitpanda) | FOMO driver for dormant users. Launchpad fit | Low | Push + in-app. Manual trigger |
| **Alert frequency control** (copy Binance) | Anti-fatigue: one-off / daily / always | Low | Big impact on quality |
| **Post-first-trade 48h journey (J-Post-FM)** | #1 gap from LC-OS audit. 60% D+7 drop-off, ZERO coverage | Medium | Highest-impact new journey |
| **Anti-phishing code in emails** (copy Nexo) | Unique code users verify. Low cost, high trust | Low | Email template update |
| **Smart send-time optimization** | Send at each user's peak engagement time | Low | CleverTap Clever.AI. Enable, don't build |
| **Incremental lift measurement** | A/B holdouts per trigger to prove causal revenue | High | CleverTap supports control groups |
| **Dormant reactivation with balance context** | "You have EUR 450 in BTC. Up 12% this month." Combines holdings + market | High | Market trigger pipeline + balance data |

### Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Who Does It Wrong | Why Avoid | What to Do Instead |
|--------------|-------------------|-----------|-------------------|
| **Fixed-threshold volatility** (2%) | Revolut | BTC moves 2% daily = daily spam = push opt-out. Community complaints | User-set % (5/10/20%). Default 5% for crypto |
| **Marketing + transactional same channel** | Binance (pre-toggle era) | Users disable push to stop promos, lose trade confirmations | Separate at system level. Marketing = email default |
| **Alert limits with expiry** | Binance (50 max, 90d) | Power users hit limits. Expired alerts need re-creation | No artificial limits. Archive inactive |
| **Pro-only alerts** | Binance Lite | Excludes largest segment from engagement | Alerts for ALL. Pro gets chart integration |
| **"Buy now" price pumps** | Common mistake | MiCA prohibits investment advice. CNMV will flag | Informational: "BTC reached $X" + disclaimer. Diego approves all |
| **Daily marketing blasts** | Common | 46% opt-out at 2-5/week. Destroys push permanently | 1 marketing/day max, 3-4/week |
| **SMS for marketing** | N/A | EUR0.03-0.08/msg, low ROI in Spain, GDPR complexity | SMS = 2FA/security only |
| **Auto-opt-in all types** | Common | Day-1 spam = all permissions disabled. Recovery <5% | Progressive: transactional first. Market after first trade |
| **Automated portfolio advice** | N/A | "Consider buying X" = investment advice under MiCA | Informational triggers only |
| **Re-permission nagging** | Common | Repeated asks after decline | Once onboarding, once after value moment. Max 2 ever |
| **Sound alerts by default** | Kraken, Binance desktop | Sound during meetings = negative association | Sound off default. User opts in |
| **Real-time P&L push** | N/A | "Portfolio down 15%" causes panic + support tickets | P&L in-app only. Never push negative performance |
| **"We miss you" guilt messaging** | Common | Negative framing increases unsubscribe rate | Positive: "Your portfolio is up 8% since last visit" |
| **Complex preference UI (V1)** | Over-engineering trap | Delays launch. You don't know what triggers work yet | V1: simple on/off per category. V2: granular per asset/threshold |

### Feature Dependencies

```
Event Tracking (Phase 0) --> ALL triggers depend on this
    |
    +--> Behavioral Triggers (Phase 1) --> No dependencies beyond events
    |
    +--> Reverse ETL Setup (Phase 0) --> Lifecycle Triggers (Phase 2)
    |                                     |
    |                                     +--> Cross-sell Triggers (Phase 2)
    |                                     |
    |                                     +--> Health Score Triggers (Phase 2)
    |
    +--> Cloud Function (Phase 3) --> Market Triggers (Phase 3)
    |                                  |
    |                                  +--> User Price Alerts (Phase 3) [requires app UI]
    |
    +--> Notification Log (Phase 4) --> Measurement Dashboard (Phase 4)
                                        |
                                        +--> Scoring Optimization (Phase 4+)

User Notification Preferences --> Frequency Capping (preferences feed cap logic)
BigQuery Gold Layer (V0a-V10) --> Health Score --> Health Score Triggers
BigQuery Gold Layer --> FOMO Score --> FOMO Agent Triggers
CoinGecko Price Feed --> Price Alert Evaluation --> User-Configured Alerts
CleverTap External Trigger API --> Market Triggers (server-side push)
Hightouch Sync --> Segment Membership --> Lifecycle Journey Entry
C8 Suppression Upload --> Whale Protection (prerequisite for ANY marketing push)
J-Post-FM Journey --> Cross-Product Discovery (retain first, then cross-sell)
```

---

## Part C: Implementation Roadmap by Priority

### Copy Now -- MVP (30 Days)

**Week 1-2: Foundation (ship before ANY market alerts)**

| # | What | Why | How |
|---|------|-----|-----|
| 1 | **Notification Preference Center** | Container first. Every alert added without this risks push opt-out | 3 categories: Transactional (on), Market (opt-in), Marketing (email default). Per-channel toggles. Copy Binance 3-tier |
| 2 | **C8 whale suppression** | Risk mitigation. Upload CSV NOW. Zero engineering | CleverTap exclusion segment |
| 3 | **Event tracking audit** | Foundation for all triggers. Verify completeness | Audit existing events, gap-fill |
| 4 | **Security alerts audit** | Ensure login/withdrawal/2FA coverage | Verify, add IP geolocation |
| 5 | **Frequency capping config** | Anti-fatigue foundation | CleverTap Global Frequency Caps |

**Week 2-3: Market Alerts (Activation Driver)**

| # | What | Why | How |
|---|------|-----|-----|
| 6 | **Price target alerts** (above/below) | #1 expected feature. Coinbase/Binance benchmark | Asset page > bell > set price > choose channel. Top 20 assets by volume |
| 7 | **% change alerts** (user-defined) | More intuitive for retail. 4/6 competitors | Default 5/10/20%. Custom %. Complement to price targets |
| 8 | **Watchlist + alert integration** | Star + bell = Coinbase pattern. Watchlist without alerts is dead | Add alert integration to existing watchlist |

**Week 3-4: Lifecycle Alerts (Retention Driver)**

| # | What | Why | How |
|---|------|-----|-----|
| 9 | **J-Post-FM 48h journey** | #1 gap from LC-OS audit. 60% D+7 drop-off | Highest-impact new journey |
| 10 | **Recurring buy confirmation + failure** | DCA = highest-retention. Need execution confirmation | Email + push failures. Push confirmations |
| 11 | **Earn/staking reward notification** | 4/6 competitors. Trust + retention | Weekly digest: "You earned X" |
| 12 | **New listing alert** | FOMO driver. Launchpad fit. Low complexity | Push + in-app. Manual trigger |
| 13 | **FOMO Agent launch** | Already designed. 72.4K dormant, EUR19.5M AUC | Pending Katy, Diego, Infra |
| 14 | **3-5 behavioral triggers** | Quick revenue wins via CleverTap Live Segments | Session-based triggers |
| 15 | **Reverse ETL setup** (Hightouch) | Enables Phase 2 lifecycle triggers | Foundation for V2 |

### Build Later -- V2 (90 Days)

| # | What | Why V2 | Dependency |
|---|------|--------|------------|
| 1 | Alert frequency control (one-off/daily/always) | Anti-fatigue. Needs preference infra stable | Pref Center V1 |
| 2 | Portfolio-level alerts | Blue ocean. No competitor | BigQuery portfolio calc |
| 3 | Space Center tier change alerts | Gamification + notification = engagement | Space Center API |
| 4 | Graduated LTV alerts for Loan | Copy Nexo 3-tier | Loan LTV calculation |
| 5 | Health Score sync + triggers | Foundation for lifecycle automation | Gold Layer + Hightouch |
| 6 | Cross-product nudges | Multi-product advantage | MiCA review (Diego) |
| 7 | Smart send-time | Enable CleverTap Clever.AI | Configuration only |
| 8 | Anti-phishing code in emails | Copy Nexo. Low cost, high trust | Email template update |
| 9 | In-app notification center (inbox) | Persistent alert record | Frontend component |
| 10 | Dormant reactivation with balance context | Holdings + market combo | Market pipeline + balance data |

### Build Later -- V3 (180 Days)

| # | What | Why V3 |
|---|------|--------|
| 1 | AI market insights digest | Nexo-like daily curated summary. Needs content pipeline + ML |
| 2 | Chart-integrated alerts (Kraken-style) | Right-click chart. Needs Pro product investment |
| 3 | Technical indicator alerts (RSI, MA) | No competitor offers natively. Power user differentiator |
| 4 | Per-alert multi-channel selection | Coinbase-level granularity |
| 5 | WhatsApp channel | BSP setup, template approval, consent. 60d minimum |
| 6 | Cross-product ML recommendations | User embedding model. Complex |
| 7 | Scoring optimization | Need baseline data first |

---

## Sources

### Official Help Centers (HIGH confidence)
- [Coinbase: Price Alerts](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/what-are-price-alerts)
- [Coinbase: Notification Platform Blog](https://www.coinbase.com/blog/building-a-notification-platform-at-coinbase)
- [Coinbase: Real-Time Price Alerts](https://www.coinbase.com/blog/new-real-time-price-alerts-for-the-coinbase-app)
- [Binance: Customize Notifications](https://www.binance.com/en/support/faq/how-to-customize-your-binance-app-settings-and-notifications-0a498da1689f4f56982b50a75721f310)
- [Binance: Set Price Alert](https://www.binance.com/en/support/faq/how-to-set-a-price-alert-on-binance-53349d11525b42f79ff20d3ea1dc312b)
- [Kraken: Market Alerts](https://support.kraken.com/articles/price-alerts)
- [Kraken: Price Alerts Blog](https://blog.kraken.com/product/now-live-price-alerts-on-kraken-pro)
- [Bitpanda: Price Alerts](https://support.bitpanda.com/hc/en-us/articles/360000902305-What-is-the-price-alert-feature)
- [Bitpanda: Savings Plans](https://support.bitpanda.com/hc/en-us/articles/360003576300-How-do-I-create-a-savings-plan)
- [Bitpanda: Staking](https://support.bitpanda.com/hc/en-us/articles/4824180360092-Bitpanda-Staking)
- [Revolut: Crypto Volatility](https://help.revolut.com/en-SE/help/wealth/cryptocurrencies/getting-cryptocurrency-exposure/can-i-be-notified-of-price-volatility/)
- [Revolut: Watchlist & Alerts](https://help.revolut.com/help/wealth/stocks/getting-started-with-trading/managing-your-trading-account/trading-alerts/managing-my-trading-watchlist-and-price-alerts/)
- [Revolut: Manage Notifications](https://help.revolut.com/help/profile-and-plan/profile-plan/notifications/how-do-i-manage-my-notifications/)
- [Nexo: Manage Notifications](https://support.nexo.com/article/how-do-i-manage-my-notifications)
- [Nexo: Loyalty Program](https://support.nexo.com/article/nexo-loyalty-program-explained)
- [CleverTap: Live User Segments](https://clevertap.com/segmentation/live-user-segments/)

### Reviews & Analysis (MEDIUM confidence)
- [Coin Bureau: Nexo Review 2025](https://coinbureau.com/review/nexo-review)
- [BrokerChooser: Revolut Price Alerts](https://brokerchooser.com/invest-long-term/risk-management/price-alerts-revolut)
- [Bitcompare: Revolut Crypto Review](https://bitcompare.net/post/revolut-crypto-review)

### Push Notification Best Practices (MEDIUM confidence)
- [Pushwoosh: Opt-In Rates 2025](https://www.pushwoosh.com/blog/increase-push-notifications-opt-in/)
- [HostAdvice: Push Notification Best Practices](https://hostadvice.com/blog/digital-marketing/push-notifications/push-notifications-best-practices/)
- [Anstrex: Push Notification Consent 2025](https://www.anstrex.com/blog/the-ultimate-guide-to-push-notification-consent-in-2025)

### Confidence Assessment
| Competitor | Confidence | Reason |
|------------|------------|--------|
| Coinbase | HIGH | Multiple official docs + engineering blog |
| Binance | HIGH | Official support docs, detailed FAQ |
| Kraken | MEDIUM-HIGH | Official blog + support article |
| Bitpanda | MEDIUM | Help center confirmed some; notification settings sparse |
| Revolut | MEDIUM | Crypto alerts confirmed basic; stocks more developed |
| Nexo | MEDIUM | Reviews + partial support docs; some inferred |
