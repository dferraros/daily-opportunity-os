---
name: customer-pain-miner
description: Mine customer complaints and pain signals from digital sources for LATAM/Venezuela opportunities. Extracts exact complaint language, workarounds, and monetization signals. Run on top scored opportunities to validate pain before promotion to validation stage.
tools: [WebSearch, WebFetch, Read, Write]
---

# Customer Pain Miner

## When to Use

Invoke this skill in two situations:

1. **After daily scoring** — the daily pipeline identifies the top 5 opportunities. Run this skill on each before writing the final report.
2. **Before stage promotion** — before promoting any opportunity from `scout` to `validation`, pain must be validated. This skill is the gate.

Do NOT skip pain mining and assume the pain is real. The kill gate checks structure; pain mining checks market reality.

---

## Workflow

### Step 1 — Read the opportunity

Read the target opportunity from `data/opportunities/opportunities.jsonl` by matching the `id` or `name`.

If running on top 5, sort the JSONL by `final_score` descending and take the first 5 where `kill_decision = false`.

### Step 2 — Generate targeted queries

Run the query builder:

```python
from opportunity_os.pain_intelligence import build_pain_queries
queries = build_pain_queries(opp_dict)
# Returns 5-8 Spanish-language search queries
```

If Python execution is unavailable:
- Read `src/opportunity_os/pain_intelligence.py`
- Look up `PAIN_CATEGORY_QUERIES[opp["venezuela_wedge_category"]]` for the first 3 queries
- Look up `VERTICAL_QUERIES[opp["vertical"]]` for the next 3 queries
- Add `"{opp['name']} problema Venezuela"` as the final query

### Step 3 — Search each query

Use WebSearch for each query. Prioritize Spanish-language results.

Source priority order:
1. Reddit — r/vzla, r/Venezuela, r/Colombia, r/mexico, r/Emprendedores, r/finanzas
2. X/Twitter — Spanish fintech / commerce accounts
3. YouTube comment sections — LATAM finance and SMB channels
4. Google Play reviews — search `site:play.google.com {vertical} reseñas Venezuela Colombia`
5. Google search intent — use query as-is, extract autocomplete and "People Also Ask"
6. Trustpilot / G2 / Capterra — search `site:trustpilot.com {competitor}` for pain in reviews

For VE-specific opportunities, also try:
- `site:reddit.com/r/vzla {query}`
- `"{query}" site:x.com lang:es`

### Step 4 — Extract pain signals per source

For each result, extract:

| Field | What to capture |
|-------|----------------|
| Exact Spanish phrases | Verbatim complaint text, not paraphrased |
| Workarounds | What the person says they currently do instead |
| Frequency signal | How often: "todos los dias", "siempre", "a veces" |
| Emotional intensity | Frustration words: "harto", "imposible", "no sirve", "cansado" |
| Source label | Platform + community + context (e.g. "Reddit r/vzla — thread on payment rails") |

Collect up to 3 exact customer phrases total across all sources. Preserve original Spanish — do not translate.

### Step 5 — Score the pain (0-10)

Use this rubric:

| Score | Criteria |
|-------|----------|
| 9-10 | Daily urgent pain + failed workarounds + consistent complaint language across 3+ sources |
| 7-8 | Frequent pain + 2+ independent sources confirming same pain with similar language |
| 5-6 | Occasional pain + 1-2 sources + workarounds mostly adequate |
| 3-4 | Inconvenience + low frequency + no urgency signals |
| 1-2 | Minimal signal — hypothetical or anecdotal only |

**Quality gate: only score >= 7 if you found at least 2 independent sources (different platforms or communities) confirming the same pain with similar language.**

If the quality gate fails, cap the score at 6 and note "single-source confidence" in evidence_sources.

### Step 6 — Write pain fields back to opportunity record

Update the opportunity dict with these 5 fields:

```python
opp["pain_validation_score"] = 8.0          # float 0-10
opp["pain_evidence_sources"] = [            # list[str] — source descriptions
    "Reddit r/vzla — 'cobrar dolares' thread, 47 comments",
    "X/Twitter Spanish search — merchant complaints about POS failure"
]
opp["exact_customer_phrases"] = [           # list[str] — max 3, keep in Spanish
    "el punto falla todos los dias",
    "pierdo ventas porque no puedo cobrar en dolares"
]
opp["workarounds_found"] = [                # list[str] — what they use today
    "Cash in USD only",
    "Binance P2P for tech-savvy customers",
    "Zelle via US family members"
]
opp["pain_validated_date"] = "2026-04-01"   # ISO date string
```

Write the updated JSONL line back to `data/opportunities/opportunities.jsonl`. Replace the existing line for this `id`. Do not create a duplicate record.

### Step 7 — Update pain_library.jsonl

Read `data/pain_library.jsonl`. Check for an existing cluster matching:
- Same `category` (maps to `venezuela_wedge_category` or `vertical`)
- Overlapping `geographies`

**If cluster exists:** Append new evidence to `evidence_links` and new workarounds to `current_workarounds`. Do not duplicate entries already present.

**If no cluster exists:** Create a new record:

```json
{
  "pain_id": "pain_20260401_payments_venezuela",
  "category": "payments_and_collections",
  "description": "Merchants cannot reliably collect digital payments in Venezuela. POS fails daily, no viable USDT onramp for most customers.",
  "geographies": ["venezuela"],
  "affected_segments": ["retail SMBs", "informal commerce operators"],
  "severity": 9,
  "frequency": "daily",
  "current_workarounds": ["Cash USD", "Binance P2P", "Zelle via diaspora"],
  "evidence_links": [
    "Reddit r/vzla — cobrar dolares thread",
    "X/Twitter Spanish merchant complaints"
  ],
  "opportunities_mapped": ["opp_20260401_abc12345"]
}
```

Append the new record as a newline-separated JSON entry in `data/pain_library.jsonl`.

---

## Output Quality Gate

Only move an opportunity to `validation` stage if:
- `pain_validation_score >= 7`
- At least 2 independent sources in `pain_evidence_sources`
- At least 1 exact customer phrase in Spanish in `exact_customer_phrases`

If the score is < 7, leave the opportunity in `scout` stage. Add a `validation_notes` entry: `"Pain validation score {score} — insufficient signal for promotion. Re-run after 7 days."`

---

## LATAM/VE Lens — Apply to Every Opportunity

After scoring, always flag if the pain is:

1. **Informal-commerce-specific** — pain exists primarily off-platform, in the informal economy. Note: these pains are underserved by existing software precisely because the market is invisible to SaaS vendors. Flag as: `[INFORMAL]`

2. **Trust-related** — the core friction is distrust: of institutions, counterparties, digital money, or delivery systems. These require trust mechanisms (referral, escrow, community vouching) as the product wedge. Flag as: `[TRUST]`

3. **Payment-rail-specific** — pain caused by broken or absent payment infrastructure (no bank access, no card processing, USDT-only, etc.). These are structural moats for whoever solves them first. Flag as: `[PAYMENT-RAIL]`

These flags do not change the numeric score but should appear in `pain_evidence_sources` descriptions so downstream agents can use them.

---

## File Paths (project root relative)

| File | Purpose |
|------|---------|
| `data/opportunities/opportunities.jsonl` | Main opportunity store — read + write |
| `data/pain_library.jsonl` | Pain cluster library — read + append |
| `src/opportunity_os/pain_intelligence.py` | Query builder — import or read manually |

---

## Example Invocation

```
Run customer-pain-miner on opportunity: "Cobro digital para comerciantes informales Venezuela"
vertical: payments_and_collections
geography: venezuela
target_customer: Dueños de pequeños negocios informales en Venezuela
```

Expected output fields populated: `pain_validation_score`, `pain_evidence_sources`, `exact_customer_phrases`, `workarounds_found`, `pain_validated_date`.
