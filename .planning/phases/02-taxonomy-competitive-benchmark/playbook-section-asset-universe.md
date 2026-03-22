# Section 7: Asset Universe Mapping

> **Purpose:** This section defines how Bit2Me's 420+ listed crypto assets are classified, which assets are eligible for each product, and which assets are in scope for each trigger family. Every trigger definition in the Master Trigger Table (Phase 3) references this section via its `asset_scope` field.
>
> **Owners:** Alvaro (BigQuery views, asset eligibility data), Katy (CleverTap asset-related segments), Product (listing decisions)
>
> **Dependencies:** Phase 1 consent categories (CAT-SEC through CAT-PRO), trigger family definitions (Section 6)

---

## 7.1 Asset Classification Tiers

Every crypto asset listed on Bit2Me belongs to exactly one of four classification tiers. Tier assignment is based on market cap rank on Bit2Me, daily trading volume on the platform, and asset risk profile. Tier assignment is reviewed quarterly and stored in the BigQuery view `bit2me_lifecycle.asset_classification`.

| Tier | Name | Examples | Criteria | Approx. Count | Default Notification Behavior |
|------|------|----------|----------|----------------|-------------------------------|
| T1 | Major | BTC, ETH, SOL, BNB, XRP, ADA | Top 10 by market cap on Bit2Me; daily volume > EUR 100K on platform | ~10 | All trigger families eligible. Market triggers (Family B) fire at default thresholds. Cross-sell triggers reference these first. Highest signal-to-noise ratio. |
| T2 | Stablecoin | USDT, USDC, DAI, EUROC | Pegged to fiat currency (USD, EUR, or other sovereign currency) | ~5-8 | Cross-sell (Earn) eligible -- stablecoins in Wallet are prime Earn cross-sell targets. Volatility triggers SUPPRESSED (intentionally stable assets). De-peg alert at >2% deviation from peg for >1 hour triggers Family F (Risk/Protective) alert. Price alerts (Family A) still allowed if user configures them. |
| T3 | Mid-cap / Long-tail | DOT, LINK, AVAX, ATOM, MATIC, UNI, and ~100-200 others | Listed on Bit2Me; daily volume EUR 1K-100K on platform | ~100-200 | User-configured alerts (Family A) eligible with no restrictions. Market triggers (Family B) only if daily volume > EUR 10K on day of evaluation -- prevents noise from illiquid assets. Behavioral triggers (Family C) eligible if user has interacted with the asset. |
| T4 | Micro-cap / Memecoin | PEPE, BONK, FLOKI, SHIB, WIF, and ~200+ others | Listed on Bit2Me; daily volume < EUR 1K on platform | ~200+ | User-configured alerts (Family A) only -- user explicitly opted in. NO proactive market triggers (Family B) -- volume too low, signals too noisy. New listing announcement (one-time, CAT-MKT) eligible. Behavioral triggers (Family C) eligible only for assets user already holds. |

**Tier assignment rules:**
- Tier is determined by trailing 30-day median daily volume on Bit2Me, not by external market cap alone
- An asset can move between tiers at the quarterly review (e.g., a memecoin that gains sustained volume could promote from T4 to T3)
- Stablecoins are always T2 regardless of volume (classification by function, not volume)
- New listings enter at T4 by default; they promote based on volume data after 30 days of trading

**BigQuery implementation:**
```sql
-- View: bit2me_lifecycle.asset_classification
-- Updated: daily via scheduled query
-- Columns: asset_id, asset_symbol, asset_name, tier (T1|T2|T3|T4),
--          median_daily_volume_eur_30d, is_stablecoin, last_tier_review_date,
--          listed_date, is_active
```

---

## 7.2 Product-Asset Eligibility Matrix

Each Bit2Me product supports a different subset of the total asset universe. This matrix determines which assets can appear in cross-sell triggers (Family E), which assets are relevant for product-specific behavioral triggers (Family C), and which products a given asset can be promoted to.

| Product | Asset Scope | Approx. Count | Scope Description | Notes |
|---------|------------|----------------|-------------------|-------|
| **Wallet** | All listed assets | ~420+ | Every asset listed on Bit2Me can be held in Wallet (buy, hold, send, receive) | Wallet is the universal container. All assets are Wallet-eligible by definition. |
| **Brokerage** (Buy & Sell) | All listed assets | ~420+ | Simple buy/sell for all listed crypto. Brokerage and Wallet share the same asset scope. | Primary entry point for retail users. Family A (price alerts) and Family B (market triggers) both reference Brokerage-eligible assets. |
| **Pro** (Order Book) | Liquidity-sufficient subset | ~50-100 | Assets with active order book trading pairs. Requires sufficient liquidity for limit/stop orders. | Pro-eligible is a strict subset of Brokerage-eligible. Family E cross-sell: "This asset is available on Pro with limit orders." |
| **Earn** | Staking/earn-program subset | ~20-50 | Assets with active staking, lending, or yield programs. Changes as programs are added/removed. | Earn-eligible is the most dynamic subset -- changes weekly as programs launch/end. Family E cross-sell is highest value here: "Your USDT could earn X% APY." |
| **Card** | All held assets (spend) | ~420+ | Users can spend any crypto they hold via the Bit2Me Card. Asset scope = user's current holdings. | Card triggers are user-specific ("Spend your BTC at any merchant"), not asset-catalog-wide. |
| **Loan** | Collateral-eligible assets | ~5-15 | Typically BTC, ETH, and major stablecoins. Conservative collateral policy. | Loan-eligible is the smallest subset. Family F (Risk/Protective) triggers for LTV thresholds reference only Loan-collateralized assets. |
| **Launchpad** | New token launches | Event-driven | Not a persistent asset catalog. Each launchpad event introduces a new asset for a limited period. | Trigger type: one-time announcement (CAT-MKT or CAT-PRD). Not included in persistent asset scope rules. |
| **Space Center** | B2M token primarily | 1 (B2M) | Gamification/loyalty program centered on B2M token holdings. Tier advancement based on B2M balance. | Family E cross-sell: "Hold X more B2M to reach Tier N." Family D (lifecycle): Space Center mission triggers. |
| **Pay** | Payment-eligible assets | ~10-50 | Assets accepted for payment processing. Subset determined by payment processor integrations. | Pay-eligible scope depends on merchant acceptance and payment rails. Cross-sell: "Pay with crypto at 10,000+ merchants." |
| **Wealth** | TBD (not yet launched) | TBD | Managed portfolio / wealth management product. Asset scope will be defined at product launch. | Include in eligibility matrix structure now; populate when product specifications are finalized. |
| **API** | All listed assets | ~420+ | API access mirrors Wallet/Brokerage scope. All listed assets accessible via API endpoints. | API triggers are typically not notification-relevant (developer audience uses webhooks, not push). |

**Dynamic reference rule:** All trigger definitions and cross-sell logic must reference eligibility dynamically (e.g., "Earn-eligible assets" or `WHERE product_earn_eligible = true`) rather than hard-coding asset lists. This ensures triggers automatically adapt when assets are added to or removed from product programs.

**BigQuery implementation:**
```sql
-- View: bit2me_lifecycle.asset_product_eligibility
-- Updated: daily via scheduled query (or event-driven when product catalogs change)
-- Columns: asset_id, asset_symbol, tier,
--          wallet_eligible, brokerage_eligible, pro_eligible, earn_eligible,
--          card_eligible, loan_eligible, launchpad_eligible, space_center_eligible,
--          pay_eligible, wealth_eligible, api_eligible,
--          earn_apy_current, loan_max_ltv, last_updated
```

---

## 7.3 Trigger-Family Asset Scope Rules

Each of the 6 trigger families (defined in Section 6: Trigger Taxonomy) has a distinct asset scope rule. This table defines which assets each family can reference when firing triggers. The `asset_scope` field in every trigger definition (Phase 3 Master Trigger Table) must conform to one of these rules.

| Family | Family Name | Asset Scope Rule | Layer Reference | Volume Minimum | Stablecoin Behavior | Example |
|--------|------------|-----------------|-----------------|----------------|---------------------|---------|
| **A** | User Configured | All listed assets (Layer 1) | Layer 1: Full catalog | None -- user chooses | Allowed (user may want stable price alerts) | User sets alert: "BTC > EUR 80,000" -- any asset the user selects |
| **B** | Market Triggered | Top 50-100 by daily volume (T1 + top T3) | Layer 1 filtered by volume | EUR 10K/day minimum | Excluded from volatility triggers (intentionally stable); included in volume-anomaly triggers | "SOL is up 12% in 4 hours" -- only fires for assets above volume threshold |
| **C** | Behavioral | Assets the user has interacted with (viewed, traded, held, watchlisted) | Layer 3: Per-user interaction history | None -- scoped to user behavior | Included if user has interacted | "You viewed ETH 3 times this week but haven't bought" -- scoped to user's browsing/trading history |
| **D** | Lifecycle | Not asset-specific (lifecycle stage-based) | N/A | N/A | N/A | "You haven't traded in 30 days" -- targets user state, not specific assets. May reference user's top held asset for personalization but scope rule is lifecycle, not asset. |
| **E** | Product Cross-sell | Product-specific subsets (Earn-eligible, Loan-eligible, Pro-eligible) | Layer 2: Product catalogs | None (product eligibility determines scope) | Prime targets for Earn cross-sell (stablecoins in Wallet earning 0% = highest-value trigger) | "Your USDT could earn 3.2% APY in Earn" -- only fires for assets in Earn-eligible AND in user's Wallet |
| **F** | Risk / Protective | Assets the user currently holds or has collateralized | Layer 3: Per-user holdings + collateral | None (user holdings determine scope) | De-peg alert: >2% deviation for >1 hour | "Your BTC collateral LTV is at 71.4%" -- only fires for assets the user has at risk |

**Scope evaluation logic (pseudocode for BigQuery WHERE clauses):**

- **Family A:** No filtering needed -- user selects the asset explicitly
- **Family B:** `WHERE tier IN ('T1') OR (tier = 'T3' AND median_daily_volume_eur_30d > 10000)` -- stablecoins excluded from volatility signals via `AND is_stablecoin = false`
- **Family C:** `WHERE asset_id IN (SELECT asset_id FROM user_asset_interactions WHERE user_id = :user_id AND interaction_date > DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY))`
- **Family D:** No asset filtering (lifecycle triggers are user-state-based)
- **Family E:** `WHERE [product]_eligible = true AND asset_id IN (SELECT asset_id FROM user_holdings WHERE user_id = :user_id)` -- intersection of product eligibility and user holdings
- **Family F:** `WHERE asset_id IN (SELECT asset_id FROM user_holdings WHERE user_id = :user_id) OR asset_id IN (SELECT collateral_asset_id FROM user_loans WHERE user_id = :user_id AND status = 'active')`

---

## 7.4 Asset Scope Governance

Rules for maintaining the asset universe mapping over time. The asset landscape changes frequently (new listings, delistings, product eligibility changes), so governance ensures trigger accuracy without manual intervention.

### 7.4.1 Dynamic vs. Static

**Rule:** Asset scope is ALWAYS dynamic (BigQuery views), NEVER hard-coded lists.

| Approach | Used For | Update Mechanism |
|----------|---------|-----------------|
| Dynamic BigQuery view | All asset scope rules | Scheduled daily query recalculates tier assignments and product eligibility from source tables |
| Event-driven update | Earn program launches/ends, new listings, delistings | Source system change triggers view refresh within 1 hour |
| Hard-coded list | NEVER | Unmaintainable with 420+ assets and frequent changes |

### 7.4.2 Volume Threshold Maintenance

- **Review cadence:** Quarterly (aligned with tier review)
- **Owner:** Alvaro (data), with input from Product (listing strategy)
- **Current thresholds:**
  - T1 entry: daily volume > EUR 100K (trailing 30-day median)
  - T3/T4 boundary: daily volume EUR 1K
  - Family B minimum: daily volume EUR 10K
- **Adjustment criteria:** If >20% of Family B triggers fire for assets with <5 trades/day, thresholds are too low. If <10 assets qualify for Family B, thresholds may be too high.
- **Threshold changes require:** Written justification in the governance log, review by Alvaro, and a 7-day monitoring period after change

### 7.4.3 Stablecoin De-Peg Monitoring

Stablecoins are designed to maintain a 1:1 peg with their reference fiat currency. A sustained deviation from peg is a risk event that affects users holding or earning yield on that stablecoin.

- **Trigger condition:** >2% deviation from peg price sustained for >1 hour
- **Trigger family:** Family F (Risk/Protective)
- **Consent category:** CAT-SEC (security/protective -- no consent required, contractual necessity)
- **Priority tier:** P0 (highest -- financial risk to user)
- **Channels:** Push + Email (dual delivery for risk alerts)
- **Asset scope:** All T2 (stablecoin) assets
- **Data source:** Price feed comparison between stablecoin price on Bit2Me and reference fiat value. Cross-referenced with external price feeds (CoinGecko, CoinMarketCap) to avoid false positives from Bit2Me-specific liquidity issues.
- **False positive protection:** Deviation must persist for >1 hour AND be confirmed on at least 2 price sources. Single-source spikes are not actionable.
- **Cooldown:** 24 hours per stablecoin per user (avoid repeated alerts during extended de-peg events)

### 7.4.4 New Listing Process

When a new asset is listed on Bit2Me, it must be integrated into the asset universe mapping.

| Step | Action | Timeline | Owner |
|------|--------|----------|-------|
| 1 | Asset listed on Bit2Me platform | T+0 | Product/Engineering |
| 2 | Asset auto-enters Wallet and Brokerage eligibility (all listed assets are Wallet/Brokerage-eligible) | T+0 (automatic) | BigQuery view refresh |
| 3 | Asset assigned to T4 (Micro-cap/Memecoin) by default | T+0 (automatic) | BigQuery scheduled query |
| 4 | New listing announcement trigger fires (one-time, CAT-MKT) for users who have opted into Market Alerts | T+0 to T+24h | CleverTap campaign (Katy) |
| 5 | Manual review for other product eligibility (Pro, Earn, Loan, Pay) | T+7 to T+30 | Product team |
| 6 | Tier re-evaluation based on 30-day trading data | T+30 | Automatic (BigQuery scheduled query) |
| 7 | If volume warrants, asset promotes from T4 to T3 (or higher) | T+30+ | Automatic with quarterly governance review |

### 7.4.5 Delisting Process

When an asset is delisted from Bit2Me:

1. All active Family A (user-configured) alerts for the asset are deactivated with a notification to the user (CAT-TXN, P1)
2. Asset is removed from all product eligibility flags in the BigQuery view
3. Family B, C, and E triggers can no longer fire for this asset
4. Family F triggers remain active until the user has zero balance of the asset (protective alerts for held assets)
5. Asset remains in historical data for analytics but is flagged `is_active = false`

---

## 7.5 Cross-References

This section is referenced by and references the following playbook sections:

| Reference | Direction | Connection |
|-----------|-----------|------------|
| **Section 6: Trigger Taxonomy** | Referenced BY | Every trigger family definition references this section for its `asset_scope` rule. The trigger template field `asset_scope` must conform to one of the 6 family scope rules defined in Section 7.3. |
| **Phase 3: Master Trigger Table** | Referenced BY | Each trigger row in the Master Trigger Table includes an `asset_scope` column. Valid values are: "Layer 1 (all listed)", "Layer 2 ([product]-eligible)", "Layer 3 (user holdings/interactions)", or "N/A (lifecycle)". |
| **Section 1: Preference Center** | References | Asset-related triggers require consent: Family A = CAT-USR, Family B = CAT-MKT, Family E = CAT-PRO. Stablecoin de-peg = CAT-SEC (no consent needed). |
| **Phase 1: Hightouch Reverse ETL** | References | User properties synced via Hightouch include `assets_held` (list), `products_active` (list), and `lifecycle_stage` -- all needed for per-user asset scope evaluation in Families C, E, and F. |
| **Phase 1: Event Schema** | References | Events like `Asset Viewed`, `Trade Completed`, `Deposit Received` generate the interaction history used by Family C (behavioral) and Family F (protective) scope rules. |
| **BigQuery Views** | Provides | `bit2me_lifecycle.asset_classification` (tier assignments) and `bit2me_lifecycle.asset_product_eligibility` (product eligibility matrix) are the canonical data sources for all asset scope evaluation. |

---

## Appendix 7A: Tier Assignment Decision Tree

```
Is the asset pegged to a fiat currency?
  YES -> T2 (Stablecoin)
  NO  -> Is the asset in the Top 10 by market cap on Bit2Me
         AND does it have daily volume > EUR 100K?
    YES -> T1 (Major)
    NO  -> Does it have daily volume EUR 1K-100K?
      YES -> T3 (Mid-cap / Long-tail)
      NO  -> T4 (Micro-cap / Memecoin)
```

## Appendix 7B: High-Value Cross-Sell Asset Patterns

These are the highest-value asset-product combinations for Family E (Cross-sell) triggers, based on the intersection of user holdings and product eligibility:

| Pattern | User Has | Product Target | Why High Value | Example Trigger |
|---------|----------|---------------|---------------|-----------------|
| Idle stablecoin | USDT/USDC in Wallet, earning 0% | Earn | Zero opportunity cost to user; guaranteed yield improvement | "Your 500 USDT is earning 0%. Earn offers 3.2% APY." |
| BTC/ETH without Loan | BTC or ETH in Wallet, no active loan | Loan | Major assets = best collateral; user already holds eligible asset | "Need liquidity without selling? Use your BTC as collateral." |
| Brokerage-only trader | Trades on Brokerage, never used Pro | Pro | Lower fees, limit orders = value-add for active traders | "Save on fees with limit orders on Pro." |
| Holder without Card | Holds crypto, no Card activated | Card | Spend utility increases perceived value of holdings | "Spend your crypto at any merchant with Bit2Me Card." |
| Active trader, low Space Center | Regular trades, Space Center Tier 1-2 | Space Center | Trading activity should convert to loyalty tier advancement | "You traded 15 times this month. Hold B2M to advance 100x faster." |
