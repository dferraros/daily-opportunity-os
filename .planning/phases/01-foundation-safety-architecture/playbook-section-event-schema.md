## 4. Event Schema

### 4.1 Event Ingestion Architecture

Two ingestion paths feed events into CleverTap: the **CleverTap SDK** (client-side, auto-tracked + custom events) and the **Upload Events API** (server-side, backend events). SDK events reach CleverTap in real-time and are available immediately for Live campaign triggers. Upload Events must arrive within **2 hours** of occurrence for Live campaign triggers to fire -- stale events are stored but cannot activate time-sensitive campaigns.

All events also flow to BigQuery (via CleverTap export or parallel backend writes) for scoring, attribution, fatigue computation, and reporting. The event schema below defines the minimum viable set of events required for the trigger-based notification system to function.

---

### 4.2 SDK Events (Tracked in App)

| Event Name | Properties | Property Types | Trigger Use | Notes |
|---|---|---|---|---|
| **Product_Viewed** | `{product_name, duration_sec}` | `product_name: string, duration_sec: integer` | Cross-sell intent detection | Auto-tracked if CleverTap SDK Page Viewed is enabled |
| **Price_Alert_Set** | `{asset, target_price, direction}` | `asset: string, target_price: float, direction: string ("above"/"below")` | User-configured alert activation | `direction` must be exactly "above" or "below" |
| **Asset_Added_Watchlist** | `{asset}` | `asset: string` | Market alert eligibility | Tracks user interest signals for asset-specific notifications |
| **Preference_Changed** | `{category, channel, new_status}` | `category: string, channel: string, new_status: boolean` | Consent tracking | Fires when user toggles notification preference in-app |
| **App_Opened** | `{session_count, days_since_last}` | `session_count: integer, days_since_last: integer` | Engagement tracking, reactivation trigger | Auto-tracked by CleverTap SDK |
| **Push_Permission_Changed** | `{new_status}` | `new_status: boolean` | Channel availability tracking | Auto-tracked by CleverTap SDK |
| **Notification_Clicked** | `{campaign_id, trigger_type, channel}` | `campaign_id: string, trigger_type: string, channel: string` | Feedback loop, fatigue reset (resets escalating cooldown) | Auto-tracked by CleverTap SDK |

---

### 4.3 Backend Upload Events (via Upload Events API)

| Event Name | Properties | Property Types | Trigger Use | Notes |
|---|---|---|---|---|
| **Charged** | `{Amount, currency, Items}` | `Amount: float, currency: string ("EUR"), Items: [{name: string, quantity: integer, price: float}]` | Revenue tracking, purchase triggers | MUST use "Charged" (CleverTap built-in for revenue/LTV). Do NOT use custom event names for purchases. |
| **Deposit_Completed** | `{amount_eur, method, is_first_deposit}` | `amount_eur: float, method: string, is_first_deposit: boolean` | Activation triggers, post-deposit nudge | `is_first_deposit` enables onboarding journey trigger (J-Post-FM) |
| **Withdrawal_Completed** | `{amount_eur, asset}` | `amount_eur: float, asset: string` | Risk/churn signal | Large withdrawals may trigger protective alerts (P0 for security, P2 for retention) |
| **KYC_Step_Completed** | `{step_number, total_steps}` | `step_number: integer, total_steps: integer` | Onboarding nudges, abandonment detection | Track each step for funnel analysis; trigger nudge if started but not completed in 48h |
| **Earn_Subscribed** | `{asset, amount, apy}` | `asset: string, amount: float, apy: float` | Product adoption tracking | Cross-sell trigger (user adopted Earn -- do not send Earn cross-sell) |
| **Order_Filled** | `{asset, amount_eur, side, product}` | `asset: string, amount_eur: float, side: string ("buy"/"sell"), product: string ("brokerage"/"pro")` | Trading activity, frequency tracking | Use alongside "Charged" for trade-specific properties |

---

### 4.4 Cloud Function Events (via Upload Events API)

| Event Name | Properties | Property Types | Trigger Use | Notes |
|---|---|---|---|---|
| **Market_Trigger_Fired** | `{asset, change_pct, direction, trigger_type}` | `asset: string, change_pct: float, direction: string ("up"/"down"), trigger_type: string ("volatility"/"momentum"/"volume")` | Proactive market alerts | Cloud Function generates these on CoinGecko polling (every 5 min) |
| **Price_Alert_Triggered** | `{asset, current_price, target_price, direction}` | `asset: string, current_price: float, target_price: float, direction: string ("above"/"below")` | User-configured price alert delivery | Matches against user's Price_Alert_Set events |

---

### 4.5 Upload Events API Constraints

| Constraint | Value | Impact |
|---|---|---|
| Max records per API call | **1000** | Batch uploads; do not send one event per call |
| Max concurrent requests | **15** | Queue with backpressure in Cloud Function / backend |
| Max event types per account | **512** | Plan event naming carefully; do not create variants |
| Max properties per event | **256** | More than sufficient for all events above |
| Event name case sensitivity | **Case-INSENSITIVE** | "Purchase" and "purchase" are the same event. Standardize to Title_Case with underscores. |
| Prohibited characters in event names | `% > < ! | & . : ; $ ' " \` | Validate before sending; any prohibited char causes silent rejection |
| Timestamp format | **Unix epoch (seconds)** | Must be within 2 hours of current time for Live campaigns |
| Test mode | **dryRun=1 parameter** | Always test with dryRun before production upload |

---

### 4.6 Reserved Event Names (NEVER Use for Custom Events)

The following event names are reserved by CleverTap for system tracking. If a backend developer accidentally uses a reserved event name, **CleverTap silently drops the event with no error**. Always check this list before creating a new event type.

- Notification Sent
- Notification Viewed
- Notification Clicked (system version -- but our custom `Notification_Clicked` with underscore is safe)
- App Launched
- App Installed
- UTM Visited
- Push Impressions
- **Charged** (RESERVED for purchase tracking -- use it for all purchases, do not rename it)

**Important:** "Charged" is the only reserved name you SHOULD use. It is CleverTap's built-in event for revenue analytics and LTV calculation. All purchase/trade events must use "Charged" with the `Items` array. Custom event names for purchases (e.g., "Purchase_Made", "Trade_Executed") will NOT feed into CleverTap's revenue dashboards.

---

### 4.7 Upload Events API Example

```json
POST https://api.clevertap.com/1/upload
Headers:
  X-CleverTap-Account-Id: {ACCOUNT_ID}
  X-CleverTap-Passcode: {PASSCODE}
  Content-Type: application/json

{
  "d": [
    {
      "identity": "user_12345",
      "type": "event",
      "evtName": "Deposit_Completed",
      "evtData": {
        "amount_eur": 500.00,
        "method": "bank_transfer",
        "is_first_deposit": true
      },
      "ts": 1711152000
    },
    {
      "identity": "user_12345",
      "type": "event",
      "evtName": "Charged",
      "evtData": {
        "Amount": 250.00,
        "Items": [
          {
            "name": "BTC",
            "quantity": 1,
            "price": 250.00
          }
        ]
      },
      "ts": 1711152300
    }
  ]
}
```

**Testing:** Before production upload, add `"dryRun": 1` to the request body to validate the payload without persisting events. Check the response for per-record status codes.

---

### 4.8 Event-to-Trigger Mapping

This table shows which triggers each event enables and the priority tier for suppression decisions (see Section 2.5 Fatigue Risk Score and Section 3.5 Escalating Cooldowns).

| Event | Enables Trigger Type | Trigger Family | Priority Tier |
|---|---|---|---|
| **Charged** | First purchase celebration, repeat purchase nudge | Behavioral / Lifecycle | P2 |
| **Deposit_Completed** | Post-deposit activation (no trade in 24h) | Behavioral | P2 |
| **Withdrawal_Completed** | Large withdrawal protective alert | Risk | P0 (security) / P2 (retention) |
| **KYC_Step_Completed** | KYC abandonment nudge (started, not finished in 48h) | Lifecycle | P2 |
| **Product_Viewed** | Cross-sell intent (viewed Earn page 3x, never subscribed) | Cross-sell | P4 |
| **Price_Alert_Set** | User-configured price alert activation | User-Configured | P1 |
| **Market_Trigger_Fired** | Proactive market alert delivery | Market | P3 |
| **App_Opened** (after 7+ days) | Reactivation welcome | Lifecycle | P2 |

**Cross-references:**
- Section 2.5: Priority tiers P0-P5 and fatigue score thresholds
- Section 3.5: Escalating cooldowns (Notification_Clicked resets cooldown levels)
- Section 5: Hightouch Reverse ETL (notification_fatigue_score synced from BigQuery)
