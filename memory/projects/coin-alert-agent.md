# Coin Alert Agent — Brokerage Re-Engagement Framework
**Owner:** Daniel Ferraro | **Status:** Design phase | **Created:** Feb 25, 2026

---

## Concept
Automated agent that monitors crypto market movements (CoinGecko API) and triggers personalized CleverTap push notifications to c6/c7 users (Smart Holders) based on coins they already hold.

Based on Robinhood's model: alert on holdings, not generic market news. This is the highest-CTR trigger available for dormant users with balance.

---

## Research Backing (real benchmarks)
- Generic broadcast fintech push CTR: 2.1% iOS, 2.8% Android
- Triggered behavioral push: 6.6-7.0% CTR (~3x)
- Narrow segmented: up to 9.35% CTR (14x vs generic)
- Personalized (asset name + % change): 2x on top of triggered
- Combined triggered + personalized: ~20-30x vs generic broadcast
- Journey-based (sequence): 4.6x conversion lift vs single message
- Fintech conversion rate average: 11.6%
- Avg crypto conversion: 7-9 touchpoints

Sources: CleverTap, MoEngage, Pushwoosh benchmarks 2024-2025

---

## Architecture

### Step 1: Market Signal Layer
- **API:** CoinGecko (free tier = 30 calls/min, 10,000 calls/month, 10-min cache)
- **Endpoint top movers:** `/coins/markets?order=percent_change_24h_desc`
- **Endpoint trending:** `/search/trending` (top 7, updated every 10 min)
- **Trigger thresholds:** ±5% OR ±10% in 24h
- **Run frequency:** Every hour (24 calls/day = well within free tier)

### Step 2: User Relevance Layer (BigQuery Gold Layer)
Priority order for matching:
1. Coins user holds with current balance > €0 → HIGHEST relevance
2. Coins user traded in last 120d but no balance → Medium relevance
3. Trending coins user never held → Lowest relevance (discovery, not re-engagement)

### Step 3: Decision Framework

| Signal | Has balance in coin | Traded before, no balance | Never held |
|--------|--------------------|-----------------------------|------------|
| +10% 24h | "Tu [COIN] subió X%" → Buy/hold | "El [COIN] que operabas subió X%" | "Trending: [COIN] sube X%" |
| -10% 24h | "Tu [COIN] cayó X%. ¿Revisas?" | Skip | Skip |
| Top trending | "X está siendo buscado hoy" | Same | Same |
| Volume spike 5x | "Volumen de [COIN] 5x vs ayer" | Same | Skip |

### Step 4: Frequency Rules (mandatory)
- Max 1 push per user per day
- Max 2 pushes per user per week
- 48h cooldown after user clicks
- No sends between 23:00–08:00
- C8 suppression always active

### Step 5: CleverTap Execution
- Properties to pass: `coin_name`, `percent_change`, `coin_symbol`, `user_id`, `direction` (up/down)
- Push template: `Tu {{coin_name}} subió {{percent_change}}% en 24h`
- Deep link: `appbit2me://bit2me.com/trade/{{coin_symbol}}`
- Conversion event: `transaction_api` (14d window — NOT 7d)
- Labels: `brokerage|coin-alert|triggered`

---

## Copy Templates

### Holdings — Price Up
- **Push title:** Tu {{coin_name}} subió {{percent_change}}%
- **Push body:** En las últimas 24h. ¿Quieres operar o revisar tu posición?
- **CTA deep link:** trade screen for that coin

### Holdings — Price Down
- **Push title:** Tu {{coin_name}} cayó {{percent_change}}%
- **Push body:** El mercado se mueve. Revisa tu cartera y decide tu próximo paso.
- **CTA deep link:** wallet

### Previously Traded (no balance)
- **Push title:** {{coin_name}} se está moviendo
- **Push body:** Subió {{percent_change}}% hoy. La última vez que operaste fue hace X días.
- **CTA deep link:** trade screen

### Trending Discovery
- **Push title:** {{coin_name}} está trending hoy
- **Push body:** Es el más buscado en las últimas 24h. ¿Quieres ver por qué?
- **CTA deep link:** prices list

---

## Key Insight (Robinhood model)
Robinhood sends alerts for:
- Assets user HOLDS: on by default, 5% or 10% threshold
- Assets on watchlist: off by default
- Frequency: "Less" = max 3 per coin per 24h, "More" = unlimited
This is why they outperform: relevance = user's own assets.

---

## What to Build First (priority order)
1. CoinGecko connector (free API, pull movers every hour)
2. Holdings lookup from BigQuery Gold Layer for c6+c7 users
3. Match movers × holdings → build trigger list
4. CleverTap triggered campaign setup (Katy)
5. Frequency cap logic
6. Measure: CTR, influenced conversions, unsubscribes

---

## Measurement Plan
- Primary: transaction_api conversions (14d window)
- Secondary: CTR push, influenced conversions
- Benchmark to beat: triggered baseline 6.6% CTR
- Control group: 10% holdout (no alert sent)
- Decision cycle: 9 days per sprint

---

## Open Questions
- Does BigQuery Gold Layer expose per-user coin holdings in real-time or batch?
- Does CleverTap support dynamic deep links with coin symbols?
- Is there a minimum % move threshold that avoids notification fatigue without sacrificing relevance?
- Can N8N be used as the orchestration layer (CoinGecko → BigQuery match → CleverTap API)?
