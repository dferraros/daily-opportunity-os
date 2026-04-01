# SKILL: Lark Automation for Growth Teams

## PURPOSE
Automate Lark (Feishu) for the Bit2Me growth team: daily flash reports, KPI scorecards, A/B test alerts, journey digests, bot commands, and approval workflows. Covers the full Python stack from auth to rich card messages.

---

## 1. LARK API BASICS

### App Setup (Lark Open Platform)
1. Go to https://open.larksuite.com (international) or https://open.feishu.cn (China)
2. Create an app: get **App ID** and **App Secret**
3. Add permissions (scopes) for the APIs you need
4. Publish the app to your workspace

```python
APP_ID = "cli_xxxxxxxxxxxxxxxx"
APP_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Access Token Flow
Lark uses two token types:
- **Tenant Access Token** — for bot actions (send messages, manage docs)
- **User Access Token** — for user-delegated actions (OAuth flow)

```python
import requests

def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    data = resp.json()
    if data.get("code") != 0:
        raise ValueError(f"Token error: {data}")
    return data["tenant_access_token"]  # valid for 2 hours

TOKEN = get_tenant_access_token(APP_ID, APP_SECRET)
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
```

### Key API Surfaces
| API | Base Path | Use Case |
|-----|-----------|----------|
| Messages | `/im/v1/messages` | Send/read messages in chats |
| Docs | `/docx/v1/documents` | Create/edit Lark Docs |
| Sheets | `/sheets/v3/spreadsheets` | Read/write Lark Sheets |
| Calendar | `/calendar/v4/calendars` | Create events, invites |
| Approval | `/approval/v4/approvals` | Launch approval workflows |
| Bot | `/bot/v3/info` | Bot self-info |

### Webhooks vs Polling vs Bot Commands

| Method | When to use |
|--------|-------------|
| **Incoming Webhook** | Simplest: one URL, push data to a chat. No auth needed beyond the URL. Use for alerts. |
| **Event Subscription** | React to user actions (mentions, messages, reactions). Requires a public HTTPS endpoint. |
| **Polling** | Avoid — not supported natively. Use event subscriptions instead. |
| **Bot slash commands** | Interactive: users type `/command`, bot responds. Requires event subscriptions. |

#### Incoming Webhook (fastest setup)
```python
WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/xxxxxxxx"

def send_webhook_text(text: str):
    requests.post(WEBHOOK_URL, json={"msg_type": "text", "content": {"text": text}})
```

---

## 2. PRACTICAL AUTOMATIONS FOR THE BIT2ME GROWTH TEAM

### 2.1 Daily Flash Report Bot
Runs every morning via cron. Pulls BigQuery results and posts to the #lc-daily Lark group.

```python
import schedule, time
from google.cloud import bigquery
from lark_oapi import Client
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

BQ_CLIENT = bigquery.Client(project="bit2me-prod")
LARK_CLIENT = Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
CHAT_ID = "oc_xxxxxxxxxxxxxxxxxxxxxxxx"  # #lc-daily channel

FLASH_QUERY = """
SELECT
  DATE(block_time) AS date,
  COUNTIF(stage = 'FM') AS new_fm_today,
  COUNTIF(stage IN ('ACTIVE','POWER')) AS mmu_delta,
  ROUND(SUM(revenue_eur), 2) AS revenue_eur,
  COUNTIF(stage = 'REACTIVATED') AS reactivations
FROM `bit2me_lifecycle.user_daily_snapshot`
WHERE DATE(block_time) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
"""

def build_flash_card(row) -> dict:
    return {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": f"Flash Report — {row.date}"}},
            "elements": [
                {"tag": "div", "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**New FM Users**\n{row.new_fm_today}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**MMU Delta**\n+{row.mmu_delta}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**Revenue (EUR)**\n€{row.revenue_eur:,.2f}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**Reactivations**\n{row.reactivations}"}},
                ]},
                {"tag": "hr"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "Source: BigQuery bit2me_lifecycle.user_daily_snapshot"}]}
            ]
        }
    }

def post_flash_report():
    rows = list(BQ_CLIENT.query(FLASH_QUERY).result())
    if not rows:
        return
    card = build_flash_card(rows[0])
    req = (CreateMessageRequest.builder()
           .receive_id_type("chat_id")
           .request_body(CreateMessageRequestBody.builder()
               .receive_id(CHAT_ID)
               .msg_type("interactive")
               .content(str(card))
               .build())
           .build())
    LARK_CLIENT.im.v1.message.create(req)

schedule.every().day.at("08:30").do(post_flash_report)
while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2.2 Weekly Scorecard Digest
7 core KPIs posted every Monday to the #lifecycle-team channel.

```python
SCORECARD_QUERY = """
SELECT
  SUM(CASE WHEN stage IN ('ACTIVE','POWER') THEN 1 ELSE 0 END) AS mmu,
  ROUND(AVG(m1_retention_rate), 4) AS m1_retention,
  ROUND(SUM(revenue_eur) / NULLIF(COUNT(DISTINCT user_id), 0), 2) AS arpu,
  COUNTIF(stage = 'DORMANT_BAL') AS dormant_with_bal,
  COUNTIF(stage = 'REACTIVATED') AS reactivated_week,
  ROUND(SUM(revenue_eur), 2) AS total_revenue,
  COUNTIF(stage = 'FM') AS new_fm
FROM `bit2me_lifecycle.user_weekly_snapshot`
WHERE week_start = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 WEEK), WEEK(MONDAY))
"""

TARGETS = {
    "mmu": (30000, "MMU"),
    "m1_retention": (0.25, "M1 Retention"),
    "arpu": (None, "ARPU"),
    "dormant_with_bal": (None, "Dormant w/ Balance"),
    "reactivated_week": (None, "Reactivations"),
    "total_revenue": (None, "Weekly Revenue"),
    "new_fm": (None, "New FM Users"),
}

def status_emoji(actual, target):
    if target is None:
        return "📊"
    pct = actual / target
    if pct >= 1.0:
        return "GREEN"
    if pct >= 0.8:
        return "YELLOW"
    return "RED"

def post_weekly_scorecard():
    rows = list(BQ_CLIENT.query(SCORECARD_QUERY).result())
    row = rows[0]
    lines = ["**LC Weekly Scorecard**\n"]
    for field, (target, label) in TARGETS.items():
        val = getattr(row, field)
        icon = status_emoji(val, target)
        target_str = f" / target {target}" if target else ""
        lines.append(f"{icon} **{label}**: {val}{target_str}")
    send_webhook_text("\n".join(lines))
```

### 2.3 A/B Test Significance Alert
Poll BigQuery after each test update. When p-value < 0.05, fire a Lark notification.

```python
AB_QUERY = """
SELECT
  test_id,
  test_name,
  variant,
  conversions,
  impressions,
  p_value,
  uplift_pct
FROM `bit2me_ab.test_results_live`
WHERE p_value < 0.05
  AND DATE(computed_at) = CURRENT_DATE()
  AND notified_lark = FALSE
"""

def check_ab_significance():
    rows = list(BQ_CLIENT.query(AB_QUERY).result())
    for row in rows:
        msg = (
            f"A/B TEST SIGNIFICANT\n"
            f"Test: {row.test_name} ({row.test_id})\n"
            f"Variant {row.variant}: {row.uplift_pct:+.1f}% uplift\n"
            f"p-value: {row.p_value:.4f} | Conversions: {row.conversions}/{row.impressions}\n"
            f"Action required: review and ship or kill."
        )
        send_webhook_text(msg)
        # Mark as notified to avoid duplicates
        BQ_CLIENT.query(f"""
            UPDATE `bit2me_ab.test_results_live`
            SET notified_lark = TRUE
            WHERE test_id = '{row.test_id}' AND variant = '{row.variant}'
        """).result()
```

### 2.4 Journey Performance Digest
Weekly digest of J01-J12 metrics every Friday.

```python
JOURNEY_QUERY = """
SELECT
  journey_id,
  journey_name,
  sends,
  opens,
  ROUND(opens / NULLIF(sends, 0) * 100, 1) AS open_rate_pct,
  conversions,
  ROUND(conversions / NULLIF(sends, 0) * 100, 2) AS conv_rate_pct,
  ROUND(revenue_attributed_eur, 2) AS revenue_eur
FROM `bit2me_lifecycle.journey_weekly_performance`
WHERE week_start = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 WEEK), WEEK(MONDAY))
ORDER BY revenue_eur DESC
"""

def post_journey_digest():
    rows = list(BQ_CLIENT.query(JOURNEY_QUERY).result())
    lines = ["**Journey Performance — Last 7 Days**\n"]
    for r in rows:
        lines.append(
            f"**{r.journey_id}** {r.journey_name}\n"
            f"  Sends: {r.sends:,} | Open: {r.open_rate_pct}% | Conv: {r.conv_rate_pct}% | Rev: €{r.revenue_eur:,.0f}"
        )
    send_webhook_text("\n".join(lines))
```

### 2.5 Blocker Escalation
Check TASKS.md / a BigQuery task table for items stuck > 3 days. Ping the owner.

```python
BLOCKER_QUERY = """
SELECT
  task_id,
  task_name,
  owner_lark_id,
  DATE_DIFF(CURRENT_DATE(), last_updated_date, DAY) AS days_stuck,
  status
FROM `bit2me_ops.task_tracker`
WHERE status = 'BLOCKED'
  AND DATE_DIFF(CURRENT_DATE(), last_updated_date, DAY) >= 3
"""

def escalate_blockers():
    rows = list(BQ_CLIENT.query(BLOCKER_QUERY).result())
    for r in rows:
        # Direct message the owner
        msg = (
            f"BLOCKER ESCALATION\n"
            f"Task: {r.task_name} ({r.task_id})\n"
            f"Status: {r.status} for {r.days_stuck} days\n"
            f"Please update status or request help."
        )
        send_direct_message(user_open_id=r.owner_lark_id, text=msg)

def send_direct_message(user_open_id: str, text: str):
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    payload = {
        "receive_id": user_open_id,
        "msg_type": "text",
        "content": {"text": text}
    }
    requests.post(url, headers=HEADERS, params=params, json=payload)
```

---

## 3. LARK DOCS AND SHEETS AUTOMATION

### 3.1 Write to Lark Sheets
Use this to push live data from BigQuery into the growth model spreadsheet.

```python
SPREADSHEET_TOKEN = "shtcnxxxxxxxxxxxxxxxxxx"  # from the Lark Sheet URL

def write_to_sheet(sheet_id: str, range_str: str, values: list[list]):
    """
    range_str example: "A1:D5"
    values: 2D list of cell values
    """
    url = f"https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{sheet_id}!{range_str}"
    payload = {"valueRange": {"range": f"{sheet_id}!{range_str}", "values": values}}
    resp = requests.put(url, headers=HEADERS, json=payload)
    return resp.json()

# Example: push weekly MMU to the growth model
def sync_mmu_to_sheet():
    rows = list(BQ_CLIENT.query("SELECT week, mmu FROM bit2me_lifecycle.weekly_kpis ORDER BY week").result())
    values = [["Week", "MMU"]] + [[str(r.week), r.mmu] for r in rows]
    write_to_sheet(sheet_id="Sheet1", range_str=f"A1:B{len(values)}", values=values)
```

### 3.2 Read from Lark Sheets
```python
def read_sheet(sheet_id: str, range_str: str) -> list[list]:
    url = f"https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{sheet_id}!{range_str}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    return data.get("data", {}).get("valueRange", {}).get("values", [])
```

### 3.3 Create a Lark Doc Page Programmatically
```python
def create_doc(title: str, folder_token: str = None) -> str:
    url = "https://open.larksuite.com/open-apis/docx/v1/documents"
    payload = {"title": title}
    if folder_token:
        payload["folder_token"] = folder_token
    resp = requests.post(url, headers=HEADERS, json=payload)
    data = resp.json()
    return data["data"]["document"]["document_id"]

def append_text_to_doc(document_id: str, text: str):
    """Append a paragraph block to a Lark Doc."""
    url = f"https://open.larksuite.com/open-apis/docx/v1/documents/{document_id}/blocks/batch_update"
    payload = {
        "requests": [{
            "insert_block_children": {
                "parent_block_id": document_id,  # root block
                "children": [{
                    "block_type": 2,  # paragraph
                    "paragraph": {
                        "elements": [{"text_run": {"content": text}}]
                    }
                }],
                "index": -1  # append at end
            }
        }]
    }
    requests.post(url, headers=HEADERS, json=payload)
```

### 3.4 Lark Sheets as a Lightweight Campaign Tracker
Store campaign metadata in a sheet and read/write via API. Good for tracking CleverTap campaign IDs, send dates, and results without needing a database.

Schema suggestion for the sheet:

| campaign_id | name | segment | send_date | sends | opens | conv | revenue_eur | status |
|-------------|------|---------|-----------|-------|-------|------|-------------|--------|

```python
def log_campaign_result(campaign_id, name, segment, sends, opens, conv, revenue):
    existing = read_sheet("Campaigns", "A:A")
    next_row = len(existing) + 1
    values = [[campaign_id, name, segment, str(date.today()), sends, opens, conv, revenue, "COMPLETE"]]
    write_to_sheet("Campaigns", f"A{next_row}:I{next_row}", values)
```

---

## 4. BOT DEVELOPMENT

### 4.1 Setup
1. In Lark Open Platform, enable **Bot** capability for your app
2. Set **Event Subscription** URL to your server endpoint (must be HTTPS)
3. Subscribe to: `im.message.receive_v1` (incoming messages), `im.message.mention_bot_v1`

### 4.2 Flask Event Handler (receive bot messages)
```python
from flask import Flask, request, jsonify
import hashlib, hmac, json

app = Flask(__name__)
VERIFICATION_TOKEN = "your_verification_token"
ENCRYPT_KEY = "your_encrypt_key"

@app.route("/lark/events", methods=["POST"])
def handle_event():
    body = request.get_json()

    # Lark URL verification challenge
    if "challenge" in body:
        return jsonify({"challenge": body["challenge"]})

    event_type = body.get("header", {}).get("event_type", "")
    event = body.get("event", {})

    if event_type == "im.message.receive_v1":
        handle_message(event)

    return jsonify({"code": 0})

def handle_message(event: dict):
    content = json.loads(event["message"]["content"])
    text = content.get("text", "").strip()
    chat_id = event["message"]["chat_id"]

    if text.startswith("/lifecycle-status"):
        reply_lifecycle_status(chat_id)
    elif text.startswith("/segment-size"):
        parts = text.split()
        seg = parts[1] if len(parts) > 1 else None
        reply_segment_size(chat_id, seg)
    else:
        send_text_to_chat(chat_id, "Unknown command. Try /lifecycle-status or /segment-size SEG-XX")

def send_text_to_chat(chat_id: str, text: str):
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    requests.post(url, headers=HEADERS, params={"receive_id_type": "chat_id"}, json={
        "receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": text})
    })
```

### 4.3 Command: /lifecycle-status
Returns live MMU, CURR (Current User Retention Rate), NURR (New User Retention Rate) from BigQuery.

```python
STATUS_QUERY = """
SELECT
  SUM(CASE WHEN stage IN ('ACTIVE','POWER') THEN 1 ELSE 0 END) AS mmu,
  ROUND(AVG(curr), 4) AS curr,
  ROUND(AVG(nurr), 4) AS nurr,
  ROUND(SUM(revenue_eur), 2) AS week_revenue
FROM `bit2me_lifecycle.weekly_kpis`
WHERE week_start = DATE_TRUNC(CURRENT_DATE(), WEEK(MONDAY))
"""

def reply_lifecycle_status(chat_id: str):
    rows = list(BQ_CLIENT.query(STATUS_QUERY).result())
    r = rows[0]
    text = (
        f"Lifecycle Status ({date.today()})\n"
        f"MMU: {r.mmu:,} (target: 30,000)\n"
        f"CURR: {r.curr:.1%} | NURR: {r.nurr:.1%}\n"
        f"Week Revenue: EUR {r.week_revenue:,.0f}"
    )
    send_text_to_chat(chat_id, text)
```

### 4.4 Command: /segment-size [SEG-XX]
```python
def reply_segment_size(chat_id: str, segment_id: str):
    if not segment_id or not segment_id.startswith("SEG-"):
        send_text_to_chat(chat_id, "Usage: /segment-size SEG-XX (e.g. /segment-size SEG-01)")
        return
    query = f"""
        SELECT segment_id, segment_name, user_count, pct_of_total
        FROM `bit2me_lifecycle.segment_summary`
        WHERE segment_id = '{segment_id}'
        LIMIT 1
    """
    rows = list(BQ_CLIENT.query(query).result())
    if not rows:
        send_text_to_chat(chat_id, f"Segment {segment_id} not found.")
        return
    r = rows[0]
    text = (
        f"Segment: {r.segment_id} — {r.segment_name}\n"
        f"Size: {r.user_count:,} users ({r.pct_of_total:.1f}% of total)"
    )
    send_text_to_chat(chat_id, text)
```

### 4.5 Event Subscriptions — React to Mentions and Keywords
```python
KEYWORD_TRIGGERS = {
    "fomo": "FOMO Agent status: READY. Pending: Katy (CleverTap), Diego (copy), Infra (cron).",
    "mmu": "Current MMU: ~23k. Target: 30k by Mar 31.",
    "m1": "M1 Retention: 0.12% actual vs 25% Coinbase benchmark. CRISIS level.",
}

def handle_message(event: dict):
    content = json.loads(event["message"]["content"])
    text = content.get("text", "").lower()
    chat_id = event["message"]["chat_id"]

    for keyword, response in KEYWORD_TRIGGERS.items():
        if keyword in text:
            send_text_to_chat(chat_id, response)
            return
```

---

## 5. PYTHON SDK (lark-oapi)

### Installation
```bash
pip install lark-oapi
```

### Authentication
```python
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()
```

### Send a Text Message
```python
def send_message_sdk(chat_id: str, text: str):
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(
            CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(lark.JSON.marshal({"text": text}))
                .build()
        ).build()
    resp = client.im.v1.message.create(req)
    if not resp.success():
        raise Exception(f"Lark API error: {resp.code} {resp.msg}")
```

### Send a Rich Card with Buttons
```python
def send_card_with_action(chat_id: str, title: str, body: str, action_label: str, action_url: str):
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": body}},
            {"tag": "hr"},
            {"tag": "action", "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": action_label},
                "type": "primary",
                "url": action_url
            }]}
        ]
    }
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(
            CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("interactive")
                .content(lark.JSON.marshal(card))
                .build()
        ).build()
    client.im.v1.message.create(req)

# Example: A/B test significance alert with a link to the dashboard
send_card_with_action(
    chat_id=CHAT_ID,
    title="A/B Test Reached Significance",
    body="**Test JN-01-A Variant B** achieved +12.3% uplift\np-value: 0.031 | Conversions: 847 / 6,890",
    action_label="View in AB Machine",
    action_url="https://bit2me.com/internal/ab-dashboard"
)
```

### Send a Table (as Markdown in card)
```python
def build_table_card(title: str, headers: list, rows: list) -> dict:
    # Lark Markdown table
    header_row = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    table_md = "\n".join([header_row, divider] + data_rows)
    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": title}},
        "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": table_md}}]
    }
```

---

## 6. INTEGRATION WITH BIT2ME STACK

### 6.1 BigQuery -> Python -> Lark (Daily Reporting Pipeline)

```
[BigQuery]
    |
    | (google-cloud-bigquery)
    v
[Python script]  ← runs via Cloud Scheduler or cron at 08:30 UTC+1
    |
    | (lark-oapi / requests)
    v
[Lark Group: #lc-daily]
```

Full pipeline script (`daily_flash.py`):
```python
import os
from google.cloud import bigquery
from datetime import date, timedelta

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/service-account.json"

BQ = bigquery.Client(project="bit2me-prod")
APP_ID = os.environ["LARK_APP_ID"]
APP_SECRET = os.environ["LARK_APP_SECRET"]
CHAT_ID = os.environ["LARK_LC_DAILY_CHAT"]

if __name__ == "__main__":
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    # ... run queries, build card, send
    post_flash_report()
```

Cron (runs Mon-Fri 08:30 Madrid time):
```bash
30 7 * * 1-5 /usr/bin/python3 /opt/bit2me/daily_flash.py >> /var/log/lark_flash.log 2>&1
```

### 6.2 CleverTap Webhook -> Lark Notification
CleverTap supports outbound webhooks on journey conversion events. Point them to a small Flask endpoint.

```python
@app.route("/clevrtap/journey-event", methods=["POST"])
def clevrtap_event():
    data = request.get_json()
    event_name = data.get("event_name")
    user_id = data.get("user_id")
    journey_id = data.get("journey_id", "unknown")

    if event_name == "Journey_Converted":
        # Only alert on high-value conversions
        revenue = data.get("properties", {}).get("revenue_eur", 0)
        if revenue >= 100:
            send_webhook_text(
                f"Journey Conversion Alert\n"
                f"Journey: {journey_id} | User: {user_id}\n"
                f"Revenue: EUR {revenue:.2f}"
            )
    return jsonify({"ok": True})
```

In CleverTap: Journey > Settings > Webhook > point to `https://your-server.com/clevrtap/journey-event`

### 6.3 GitHub Actions -> Lark Deployment Notification
Add to `.github/workflows/deploy.yml`:

```yaml
- name: Notify Lark on deploy
  if: success()
  run: |
    curl -X POST "${{ secrets.LARK_WEBHOOK_URL }}" \
      -H "Content-Type: application/json" \
      -d "{\"msg_type\": \"text\", \"content\": {\"text\": \"Deployed: ${{ github.repository }} @ ${{ github.sha }} by ${{ github.actor }}\"}}"
```

For failures:
```yaml
- name: Notify Lark on failure
  if: failure()
  run: |
    curl -X POST "${{ secrets.LARK_WEBHOOK_URL }}" \
      -H "Content-Type: application/json" \
      -d "{\"msg_type\": \"text\", \"content\": {\"text\": \"DEPLOY FAILED: ${{ github.repository }} — check Actions log\"}}"
```

---

## 7. LARK APPROVAL WORKFLOWS

### 7.1 Overview
Lark Approval lets you define multi-step sign-off flows with conditional routing. Ideal for the CRM legal gate (Diego must approve all messages before sending).

**Setup in Lark Admin:**
1. Go to Lark Admin > Approvals > Create Approval
2. Define approval type: "CRM Campaign Pre-Send"
3. Add form fields: campaign_name, segment, estimated_reach, copy_text, launch_date
4. Set approval nodes: Node 1 = Diego (Legal), Node 2 = Daniel (sign-off)
5. Get the **Approval Definition Code** from the URL

### 7.2 Trigger an Approval via API
```python
APPROVAL_CODE = "F0C3C1E1-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # from Lark Admin

def submit_campaign_for_approval(
    campaign_name: str,
    segment: str,
    estimated_reach: int,
    copy_text: str,
    launch_date: str,
    submitter_open_id: str
) -> str:
    url = "https://open.larksuite.com/open-apis/approval/v4/instances"
    payload = {
        "approval_code": APPROVAL_CODE,
        "user_id": submitter_open_id,
        "form": [
            {"id": "campaign_name", "type": "input", "value": campaign_name},
            {"id": "segment", "type": "input", "value": segment},
            {"id": "estimated_reach", "type": "number", "value": str(estimated_reach)},
            {"id": "copy_text", "type": "textarea", "value": copy_text},
            {"id": "launch_date", "type": "date", "value": launch_date},
        ]
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    data = resp.json()
    return data["data"]["instance_code"]  # track approval status with this

# Example: Katy submits a CRM campaign for Diego's approval
instance_code = submit_campaign_for_approval(
    campaign_name="JN-01 Second Trade Accelerator — Wave 2",
    segment="SEG-14 (Post-FM, No Second Trade)",
    estimated_reach=8420,
    copy_text="Hola {first_name}, ya tienes tu primera operación hecha...",
    launch_date="2026-03-28",
    submitter_open_id="ou_xxxxxxxxxxxxxxxx"  # Katy's open_id
)
print(f"Approval submitted: {instance_code}")
```

### 7.3 Check Approval Status
```python
def get_approval_status(instance_code: str) -> str:
    url = f"https://open.larksuite.com/open-apis/approval/v4/instances/{instance_code}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    return data["data"]["status"]  # PENDING / APPROVED / REJECTED / CANCELED

# Poll until resolved (in production, use event subscription instead)
import time
status = "PENDING"
while status == "PENDING":
    status = get_approval_status(instance_code)
    time.sleep(30)
print(f"Final status: {status}")
```

### 7.4 Approval Event Subscription
Subscribe to `approval.instance.approve_v4` to react when Diego approves:

```python
@app.route("/lark/events", methods=["POST"])
def handle_event():
    body = request.get_json()
    event_type = body.get("header", {}).get("event_type", "")

    if event_type == "approval.instance.approve_v4":
        instance = body["event"]
        if instance["status"] == "APPROVED":
            # Trigger CleverTap campaign launch
            launch_clevertap_campaign(instance["form_data"]["campaign_name"])
            send_webhook_text(
                f"Diego approved campaign: {instance['form_data']['campaign_name']}\n"
                f"Launching in CleverTap now..."
            )
        elif instance["status"] == "REJECTED":
            send_webhook_text(
                f"Campaign REJECTED by Diego: {instance['form_data']['campaign_name']}\n"
                f"Reason: {instance.get('reject_reason', 'No reason given')}"
            )
    return jsonify({"code": 0})
```

### 7.5 Conditional Routing by Campaign Type
Configure in Lark Admin or via API to route differently based on spend:

| Condition | Approval Path |
|-----------|--------------|
| Estimated reach < 5,000 | Diego only (1 node) |
| Estimated reach 5,000–50,000 | Diego + Daniel (2 nodes) |
| Estimated reach > 50,000 or paid spend | Diego + Daniel + Pablo Campos (3 nodes) |

---

## ENVIRONMENT SETUP

```bash
pip install lark-oapi google-cloud-bigquery flask schedule requests python-dotenv
```

`.env` file:
```
LARK_APP_ID=cli_xxxxxxxxxxxxxxxx
LARK_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LARK_LC_DAILY_CHAT=oc_xxxxxxxxxxxxxxxxxxxxxxxx
LARK_WEBHOOK_URL=https://open.larksuite.com/open-apis/bot/v2/hook/xxxxxxxx
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

---

## QUICK REFERENCE — API ENDPOINTS

| Action | Method | URL |
|--------|--------|-----|
| Get token | POST | `/auth/v3/tenant_access_token/internal` |
| Send message | POST | `/im/v1/messages?receive_id_type=chat_id` |
| Get chat info | GET | `/im/v1/chats/{chat_id}` |
| List chat members | GET | `/im/v1/chats/{chat_id}/members` |
| Read sheet | GET | `/sheets/v2/spreadsheets/{token}/values/{range}` |
| Write sheet | PUT | `/sheets/v2/spreadsheets/{token}/values/{range}` |
| Create doc | POST | `/docx/v1/documents` |
| Submit approval | POST | `/approval/v4/instances` |
| Get approval | GET | `/approval/v4/instances/{code}` |
| Bot info | GET | `/bot/v3/info` |

Base URL (international): `https://open.larksuite.com/open-apis`

---

## NOTES FOR BIT2ME CONTEXT

- All CRM campaigns must go through Diego approval before launch — use the Approval Workflow (Section 7) as the gate, not Slack/chat
- Katy manages CleverTap execution — the CleverTap webhook integration (Section 6.2) can auto-notify her channel when a journey hits a conversion milestone
- Pablo T owns Qlik dashboards — Lark Sheets sync (Section 6.1) can keep a live backup of key KPIs outside Qlik
- Flash report should post to #lc-daily at 08:30 Madrid (UTC+1/UTC+2 seasonal)
- Segment size commands are useful in standups — Marta can validate BQ numbers vs the bot response in real-time
