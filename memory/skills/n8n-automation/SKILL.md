# SKILL: n8n Workflow Automation

## PURPOSE
Build and maintain n8n automation workflows connecting BigQuery, CleverTap, Lark, Notion, and Google Sheets for the Bit2Me Growth team. Use this skill whenever you need to automate data pipelines, alerts, digests, or cross-tool syncs.

---

## 1. WHAT IS N8N

n8n is an open-source, self-hostable workflow automation platform — a fully owned alternative to Zapier/Make.

Key facts:
- 400+ native integrations (nodes)
- Visual drag-and-drop workflow builder
- All logic runs on your infra — no data leaves your environment
- Free self-hosted tier (Community Edition). Paid cloud option available.
- Webhooks, cron, manual, and app-event triggers
- Full code escape hatch: Code node (JS/Python), HTTP Request node for any REST API
- Workflow JSON is exportable and version-controllable

---

## 2. CORE CONCEPTS

### 2.1 Workflow Anatomy

```
[Trigger] → [Node A] → [Node B] → [Node C] → [Output]
                ↓ (on error)
          [Error Handler]
```

Every workflow starts with exactly one trigger node. Data flows as an **items array** — each item is a JSON object representing one record.

### 2.2 Trigger Types

| Trigger | Use case |
|---|---|
| Schedule (Cron) | Daily reports, weekly digests |
| Webhook | Receive POST from BigQuery scheduled query, external system |
| Manual | One-off runs, testing |
| App event | CleverTap webhook, Notion database change |
| Polling | Check a Google Sheet row every N minutes |

Cron syntax for Madrid time (UTC+1 / UTC+2 DST):
```
# 8am Madrid (UTC+1 winter)
0 7 * * *

# 8am Madrid (UTC+2 summer)
0 6 * * *
```
Best practice: use `Europe/Madrid` timezone in the Schedule node settings rather than hardcoding UTC offsets.

### 2.3 Core Nodes

| Node | Purpose |
|---|---|
| **Schedule Trigger** | Cron-based execution |
| **Webhook** | HTTP endpoint — receive external calls |
| **HTTP Request** | Call any REST API (CleverTap, CoinGecko, internal) |
| **Google Sheets** | Read/write/append sheet data |
| **BigQuery** | Run queries, fetch results |
| **Notion** | Create/update pages and database entries |
| **Lark / Feishu** | Post messages to Lark Bot groups |
| **Code** | JS or Python logic node — transform data, compute values |
| **IF** | Branch on a condition |
| **Switch** | Multi-branch routing |
| **Merge** | Join multiple branches |
| **Set** | Create or overwrite fields on each item |
| **Split In Batches** | Paginate large arrays |
| **Wait** | Pause execution (rate limiting) |
| **Execute Workflow** | Call a sub-workflow |
| **Error Trigger** | Catch errors from any workflow |
| **Stop And Error** | Force-fail a workflow with a message |

### 2.4 Data Flow — Items Array

Every node receives and outputs an **items array**:

```json
[
  { "json": { "user_id": "abc", "revenue": 42.5 } },
  { "json": { "user_id": "def", "revenue": 18.0 } }
]
```

Reference fields in expressions using `{{ $json.field_name }}`.

Access previous node output: `{{ $node["Node Name"].json.field }}`.

Loop implicitly: most nodes run once per item. Use **Split In Batches** for explicit batching.

### 2.5 Expressions and JSONata

n8n uses two expression modes:

**n8n expressions** (default):
```
{{ $json.revenue }}
{{ $json.revenue.toFixed(2) }}
{{ new Date().toISOString() }}
{{ $node["BigQuery"].json.row_count > 0 ? "yes" : "no" }}
```

**JSONata** (toggle in expression editor):
```jsonata
$sum(items.revenue)
$formatNumber(total, "0,000.00")
items[status = "active"].user_id
```

Use JSONata when aggregating across the full items array (not available in standard expressions).

### 2.6 Error Handling

**Workflow-level error handler:**
1. Create a separate "Error Handler" workflow.
2. In main workflow: Settings → Error Workflow → select it.
3. Error workflow receives `{{ $json.execution.error.message }}` and `{{ $json.workflow.name }}`.

**Node-level try/catch:**
- Right-click any node → "Continue On Fail"
- Add IF node after: check `{{ $json.error }}` is not empty

**Retry logic:**
- Right-click node → Retry On Fail → set max retries + wait interval
- Use for flaky APIs (CleverTap, external webhooks)

---

## 3. KEY WORKFLOWS FOR BIT2ME GROWTH TEAM

### 3.1 Daily Flash Report (8am Madrid)

**Purpose:** Post daily revenue + user metrics to Lark "LC Daily" group.

**Flow:**
```
Schedule (8am Madrid) → BigQuery Query → Code (format) → Lark Bot Post
```

**Schedule node config:**
```json
{
  "rule": {
    "interval": [{ "field": "cronExpression", "expression": "0 7 * * *" }]
  },
  "timezone": "Europe/Madrid"
}
```

**BigQuery node — SQL:**
```sql
SELECT
  DATE(CURRENT_DATE() - 1) AS report_date,
  COUNTIF(lifecycle_stage = 'ACTIVE') AS active_users,
  COUNTIF(lifecycle_stage = 'FM') AS fm_completers_yesterday,
  ROUND(SUM(revenue_eur), 2) AS total_revenue_eur,
  COUNTIF(lifecycle_stage IN ('DORMANT_BAL','DORMANT_ZERO')) AS dormant_users
FROM `bit2me-prod.bit2me_lifecycle.v_user_daily_snapshot`
WHERE snapshot_date = DATE(CURRENT_DATE() - 1)
```

**Code node (JS) — format message:**
```javascript
const d = items[0].json;

const msg = `*Flash Report — ${d.report_date}*

Active Users: ${d.active_users.toLocaleString()}
FM Completers (yesterday): ${d.fm_completers_yesterday.toLocaleString()}
Revenue: €${parseFloat(d.total_revenue_eur).toFixed(2)}
Dormant (total): ${d.dormant_users.toLocaleString()}

_Posted by n8n @ 08:00 Madrid_`;

return [{ json: { message: msg } }];
```

**Lark HTTP Request node:**
- Method: POST
- URL: `https://open.larksuite.com/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN`
- Body (JSON):
```json
{
  "msg_type": "text",
  "content": {
    "text": "{{ $json.message }}"
  }
}
```

---

### 3.2 A/B Test Significance Alert

**Purpose:** When a BigQuery scheduled query detects p-value < 0.05, fire a Lark alert and create a Notion action task.

**Flow:**
```
Webhook → IF (p_value < 0.05) → Lark Alert
                               → Notion Task
```

**Webhook trigger:**
- Method: POST
- Path: `/ab-test-result`
- BigQuery scheduled query POSTs to this URL on completion

**Expected payload from BigQuery:**
```json
{
  "test_id": "AB-047",
  "test_name": "Onboarding CTA Color",
  "variant": "B",
  "p_value": 0.032,
  "lift_pct": 12.4,
  "conversions_control": 340,
  "conversions_variant": 381,
  "run_date": "2026-03-25"
}
```

**IF node condition:**
```
{{ $json.p_value }} < 0.05
```

**Lark message (Code node):**
```javascript
const d = items[0].json;
const significance = d.p_value < 0.01 ? "HIGHLY SIGNIFICANT" : "SIGNIFICANT";

const msg = `*A/B Test Result: ${significance}*

Test: ${d.test_id} — ${d.test_name}
Winning Variant: ${d.variant}
Lift: +${d.lift_pct}%
p-value: ${d.p_value}
Control conversions: ${d.conversions_control}
Variant conversions: ${d.conversions_variant}
Date: ${d.run_date}

Action required — see Notion task.`;

return [{ json: { message: msg } }];
```

**Notion node — create task:**
- Operation: Create Page
- Database ID: `YOUR_NOTION_AB_DATABASE_ID`
- Properties:
```json
{
  "Name": "Act on {{ $json.test_id }}: {{ $json.test_name }}",
  "Status": "To Do",
  "Priority": "High",
  "Test ID": "{{ $json.test_id }}",
  "Lift": "{{ $json.lift_pct }}%",
  "Date": "{{ $json.run_date }}"
}
```

---

### 3.3 Journey Conversion Weekly Digest (Monday 9am)

**Purpose:** Every Monday, pull CleverTap journey stats for J01-J12 and post a table to Lark + append to Google Sheet.

**Flow:**
```
Schedule (Mon 9am) → Code (date range) → HTTP Request (CleverTap API) → Code (format table) → Lark Post
                                                                                              → Google Sheets Append
```

**Schedule node:**
```json
{ "expression": "0 8 * * 1", "timezone": "Europe/Madrid" }
```

**Code node — compute date range:**
```javascript
const today = new Date();
const monday = new Date(today);
monday.setDate(today.getDate() - 7);

const fmt = d => d.toISOString().split('T')[0].replace(/-/g, '');

return [{ json: {
  from: fmt(monday),
  to: fmt(today)
}}];
```

**CleverTap API — HTTP Request node:**
- Method: GET
- URL: `https://eu1.api.clevertap.com/1/stats/journeys.json`
- Headers:
  ```
  X-CleverTap-Account-Id: YOUR_ACCOUNT_ID
  X-CleverTap-Passcode: YOUR_PASSCODE
  ```
- Query params: `from={{ $json.from }}&to={{ $json.to }}`

**Code node — format digest:**
```javascript
const journeys = items[0].json.records || [];

let table = "*Journey Conversion Digest — Week ending " + new Date().toISOString().split('T')[0] + "*\n\n";
table += "Journey | Entered | Converted | Conv%\n";
table += "--------|---------|-----------|------\n";

for (const j of journeys) {
  const pct = j.entered > 0 ? ((j.converted / j.entered) * 100).toFixed(1) : "0.0";
  table += `${j.journey_name} | ${j.entered} | ${j.converted} | ${pct}%\n`;
}

return [{ json: { message: table, journeys } }];
```

**Google Sheets node:**
- Operation: Append Row
- Sheet: "Journey Digest Log"
- Map columns: `week_ending`, `journey_name`, `entered`, `converted`, `conv_pct`

---

### 3.4 Dormant Segment Daily Sync to CleverTap

**Purpose:** Each morning, identify users who entered DORMANT status yesterday, push them to a CleverTap segment, and enroll them in J04 (reactivation journey).

**Flow:**
```
Schedule (6am) → BigQuery (new dormants) → Code (build payload) → Split In Batches (100) → CleverTap Upload API → Wait (1s) → [loop]
```

**BigQuery query:**
```sql
SELECT
  user_id,
  email,
  lifecycle_stage,
  balance_eur,
  days_since_last_trade
FROM `bit2me-prod.bit2me_lifecycle.v_user_daily_snapshot`
WHERE snapshot_date = DATE(CURRENT_DATE() - 1)
  AND lifecycle_stage IN ('DORMANT_BAL', 'DORMANT_ZERO')
  AND previous_stage NOT IN ('DORMANT_BAL', 'DORMANT_ZERO')
-- Only users who NEWLY became dormant yesterday
```

**Split In Batches node:**
- Batch size: 100 (CleverTap upload limit per call)

**Code node — build CleverTap payload:**
```javascript
const users = items.map(item => ({
  type: "profile",
  identity: item.json.user_id,
  ts: Math.floor(Date.now() / 1000),
  profileData: {
    Email: item.json.email,
    lifecycle_stage: item.json.lifecycle_stage,
    dormant_balance_eur: item.json.balance_eur,
    days_since_last_trade: item.json.days_since_last_trade,
    segment_tag: "dormant_new_batch"
  }
}));

return [{ json: { d: users } }];
```

**CleverTap Upload — HTTP Request node:**
- Method: POST
- URL: `https://eu1.api.clevertap.com/1/upload`
- Headers:
  ```
  X-CleverTap-Account-Id: YOUR_ACCOUNT_ID
  X-CleverTap-Passcode: YOUR_PASSCODE
  Content-Type: application/json
  ```
- Body: `{{ $json }}`

**Wait node:** 1 second between batches (rate limit protection).

---

## 4. INSTALLATION AND SETUP

### 4.1 Self-Hosted via Docker Compose (recommended)

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Europe/Madrid
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

`.env` file:
```
N8N_HOST=n8n.your-domain.com
N8N_ENCRYPTION_KEY=generate-a-32-char-random-string
DB_PASSWORD=strong-random-password
```

Start: `docker-compose up -d`

Access at `http://localhost:5678` (or your domain).

### 4.2 n8n Cloud vs Self-Hosted

| | Cloud | Self-Hosted |
|---|---|---|
| Setup | Zero | Docker / VPS |
| Cost | From $20/mo | VPS cost only |
| Data residency | n8n servers | Your infra |
| Control | Limited | Full |
| Recommendation for Bit2Me | — | Self-hosted (data sensitivity) |

### 4.3 Credential Storage

All credentials stored encrypted using `N8N_ENCRYPTION_KEY`. Never hardcode secrets in workflow nodes — always use the **Credentials** panel.

Create credentials via: Settings → Credentials → New Credential

Types needed for Bit2Me stack:
- **Google Service Account** (BigQuery + Sheets)
- **HTTP Header Auth** (CleverTap: Account ID + Passcode as custom headers)
- **Notion API** (Internal Integration Token)
- **HTTP Request Generic** (Lark webhook URL)

### 4.4 Webhook URL Setup

When self-hosting, set `WEBHOOK_URL` to your public HTTPS URL. n8n generates webhook URLs in this format:
```
https://n8n.your-domain.com/webhook/YOUR-WORKFLOW-UUID
```

Test webhooks use: `https://n8n.your-domain.com/webhook-test/UUID` (only active during manual test runs — switch to production URL before deploying).

---

## 5. BIGQUERY INTEGRATION

### 5.1 Service Account Setup

1. GCP Console → IAM → Service Accounts → Create
2. Grant roles: `BigQuery Data Viewer` + `BigQuery Job User`
3. Create JSON key → download
4. In n8n: Credentials → Google Service Account → paste JSON key contents

### 5.2 BigQuery Node Configuration

- **Operation:** Execute Query
- **Project ID:** `bit2me-prod`
- **SQL:** paste query directly or reference `{{ $json.query }}` from a Set node upstream

The node returns results as items array — each row becomes one item:
```json
{ "json": { "user_id": "abc", "revenue": 42.5, "stage": "ACTIVE" } }
```

### 5.3 Handling Large Result Sets

BigQuery node fetches all rows by default. For large queries:

**Option A — Aggregate in SQL (preferred):**
Always aggregate in BigQuery. Never pull row-level data for 100k+ users into n8n for processing.

**Option B — Pagination via LIMIT/OFFSET:**
```javascript
// Code node to build paginated query
const offset = $node["Set"].json.offset || 0;
const limit = 1000;
return [{ json: {
  query: `SELECT * FROM table LIMIT ${limit} OFFSET ${offset}`
}}];
```

Use a Merge node (Wait for All mode) + IF (check if results < limit) to stop the loop.

**Option C — Export to GCS first:**
For very large exports, use BigQuery → GCS export → n8n reads GCS file via HTTP Request.

### 5.4 Common BigQuery Patterns

```sql
-- Daily snapshot query pattern (always prefer snapshot table over live)
SELECT * FROM `bit2me-prod.bit2me_lifecycle.v_user_daily_snapshot`
WHERE snapshot_date = DATE(CURRENT_DATE() - 1)

-- Pass date as expression from upstream node
WHERE snapshot_date = '{{ $json.report_date }}'

-- Segment filter
WHERE lifecycle_stage IN ('DORMANT_BAL', 'DORMANT_ZERO')
  AND health_score < 30
```

---

## 6. ERROR HANDLING AND MONITORING

### 6.1 Global Error Workflow

Create one workflow called "Error Handler — Global":

**Error Trigger node** (catches all workflow errors)

**Code node — format error message:**
```javascript
const err = items[0].json;
const msg = `*n8n Workflow Error*

Workflow: ${err.workflow.name}
Node: ${err.execution.lastNode}
Error: ${err.execution.error.message}
Time: ${new Date().toISOString()}
Execution ID: ${err.execution.id}

Check: https://n8n.your-domain.com/execution/${err.execution.id}`;

return [{ json: { message: msg } }];
```

**Lark HTTP Request node** → posts to "#alerts-n8n" Lark group.

Assign this workflow as the Error Workflow in every production workflow: Workflow Settings → Error Workflow → select "Error Handler — Global".

### 6.2 Per-Node Error Handling

For nodes that interact with external APIs (CleverTap, Lark):
1. Right-click node → Settings → "Continue On Fail: ON"
2. Add IF node after: check `{{ $json.error }}` is not empty
3. Error branch: Set node to log details → either stop or merge back

### 6.3 Retry Logic

For HTTP Request nodes calling flaky external APIs:
- Right-click → Settings → Retry On Fail: ON
- Max Tries: 3
- Wait Between Tries: 5000ms

For CleverTap upload batches, always add a **Wait node** (1-2s) between iterations to avoid HTTP 429 errors.

### 6.4 Execution History

- UI: Executions tab (left sidebar) — see all past runs, status, duration
- Filter by: workflow name, status (success/error), date range
- Click any execution → full node-by-node data inspection
- Configure retention: `EXECUTIONS_DATA_MAX_AGE=720` (hours) in environment variables

### 6.5 Monitoring Checklist

| Check | Frequency | Method |
|---|---|---|
| Flash Report delivered | Daily | Verify Lark message received by 8:10am Madrid |
| Dormant sync row count | Daily | Append count to Google Sheet in the workflow |
| A/B alert accuracy | Weekly | Review Notion tasks, check for false positives |
| Workflow error count | Weekly | Executions tab filtered by "Error" |
| CleverTap upload success | Daily | Check API response `status: "success"` in execution log |

---

## 7. WORKFLOW EXPORT AND VERSION CONTROL

Export any workflow as JSON:
- Workflow menu (top-right) → Download → saves `.json`

Store in a git repo alongside SQL and other automation files:
```
/n8n-workflows/
  flash-report.json
  ab-test-alert.json
  journey-digest.json
  dormant-sync.json
  error-handler-global.json
```

Import: New Workflow → Import from File → select JSON.

Commit convention: `feat(n8n): add dormant sync retry logic`

---

## 8. QUICK REFERENCE

### Lark Bot Webhook — plain text
```json
POST https://open.larksuite.com/open-apis/bot/v2/hook/YOUR_TOKEN
{
  "msg_type": "text",
  "content": { "text": "your message here" }
}
```

### Lark Bot Webhook — rich card (markdown)
```json
{
  "msg_type": "interactive",
  "card": {
    "elements": [{
      "tag": "div",
      "text": { "content": "**Bold** and _italic_ and `code`", "tag": "lark_md" }
    }]
  }
}
```

### CleverTap API Base URLs (EU cluster)
```
Base:    https://eu1.api.clevertap.com/1/
Upload:  POST /upload
Journeys: GET /stats/journeys.json
Segment: POST /segments/create.json
```

### n8n Expression Cheatsheet
```
{{ $json.field }}                        -- current item field
{{ $node["NodeName"].json.field }}       -- specific node output
{{ $items("NodeName")[0].json.field }}   -- first item from node
{{ new Date().toISOString() }}           -- current timestamp ISO
{{ $json.value.toString() }}             -- type cast to string
{{ Math.round($json.pct * 100) / 100 }} -- round to 2 decimals
{{ $json.arr.length }}                   -- array length
```

### Cron Quick Reference (set timezone to Europe/Madrid in node)
```
0 6 * * *    -- 6am daily (dormant sync)
0 7 * * *    -- 7am UTC = 8am Madrid (winter)
0 8 * * 1    -- 8am UTC Monday = 9am Madrid Monday
0 */6 * * *  -- every 6 hours
*/15 * * * * -- every 15 minutes
```

### Docker Compose — start/stop/restart
```bash
docker-compose up -d          # start in background
docker-compose down           # stop
docker-compose restart n8n    # restart only n8n service
docker-compose logs -f n8n    # follow logs
```
