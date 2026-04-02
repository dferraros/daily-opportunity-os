---
name: distribution-mapper
description: Map distribution reality for a scored opportunity. Answer where the buyer spends attention, what realistic CAC looks like, and what the first 10 customer path is. Run on top 5 scored opportunities after customer-pain-miner. Required before promoting any opportunity to validation stage.
tools: [WebSearch, WebFetch, Read, Write]
---

# Distribution Mapper

## When to Use

Invoke this skill in two situations:

1. **After customer-pain-miner confirms pain >= 7** — pain is real. Now confirm you can reach the buyer. Distribution mapping is the second gate.
2. **Before promoting any opportunity to validation stage** — `first_10_customer_path` must be populated before promotion. This skill produces it.

For any opportunity with `portfolio_lane = "now"`, distribution mapping is REQUIRED — not optional. "Now" opportunities must have a clear, cheap, fast channel. If distribution mapping fails, move the opportunity to "soon" or "no".

Do NOT assume distribution is viable because the pain is real. Pain existence and buyer reachability are independent gates.

---

## Workflow

### Step 1 — Read the opportunity

Read the target opportunity from `data/opportunities/opportunities.jsonl` by matching `id` or `name`.

Check for pre-built distribution helper fields:
- `_distribution_queries` — use these search queries if present
- `_recommended_channels` — channel keys to evaluate
- `_cac_benchmarks` — starting CAC estimates

If running on top 5, sort by `final_score` descending, take first 5 where `kill_decision = false` and `pain_validation_score >= 7`.

### Step 2 — Generate channel recommendations and search queries

Run the distribution intelligence module:

```python
from opportunity_os.distribution_intelligence import (
    build_distribution_queries,
    get_recommended_channels,
    CHANNEL_MAP_BY_GEO,
    TRUST_MECHANISMS_BY_GEO,
)

queries = build_distribution_queries(opp_dict)
channels = get_recommended_channels(opp_dict)
geo_channels = CHANNEL_MAP_BY_GEO.get(opp_dict["geography"], CHANNEL_MAP_BY_GEO["global"])
trust_options = TRUST_MECHANISMS_BY_GEO.get(opp_dict["geography"], TRUST_MECHANISMS_BY_GEO["global"])
```

If Python execution is unavailable:
- Read `src/opportunity_os/distribution_intelligence.py`
- Look up `CHANNEL_MAP_BY_GEO[opp["geography"]]` for ordered channel options
- Look up `TRUST_MECHANISMS_BY_GEO[opp["geography"]]` for trust signals
- Manually build 5-7 queries using the pattern: `"{vertical} marketing channels {geography}"`, `"cómo conseguir clientes {vertical} {country}"`, `"{competitor} marketing strategy"`, `"distribution {vertical} LATAM"`

### Step 3 — Search each query

Use WebSearch for each query from Step 2. Research both in Spanish and English.

Source priority order:
1. Competitor landing pages + social accounts — what channels are they visibly using?
2. Facebook Ad Library (`facebook.com/ads/library`) — what paid ads do competitors run?
3. LinkedIn company pages — B2B presence signals
4. Reddit Spanish communities — r/vzla, r/Colombia, r/mexico, r/Emprendedores
5. YouTube LATAM channels — where does this buyer consume content?
6. Trustpilot/G2 competitor reviews — how did customers find the product?

For VE-specific opportunities, also check:
- `site:reddit.com/r/vzla {vertical} marketing`
- WhatsApp group directories for Venezuelan entrepreneur communities
- TikTok search for `{vertical} Venezuela` content

### Step 4 — Apply ORB Framework

For every opportunity, map channels to the ORB model from launch-strategy skill:

**OWNED channels** — what can Daniel build and control?
- Email list for this vertical (estimate time to build: 0-6 months)
- WhatsApp broadcast list from direct outreach
- Content/blog targeting Spanish-language SEO queries
- LinkedIn personal brand for B2B

**RENTED channels** — which social platforms already have this buyer's attention?
- Rank by LATAM penetration: WhatsApp > Facebook > Instagram > TikTok > LinkedIn > Twitter/X
- For VE: WhatsApp >>> all others
- For Spain B2B: LinkedIn > Google Ads > Cold email

**BORROWED channels** — which communities, influencers, or partners already have trust?
- Entrepreneur WhatsApp groups with 1,000+ VE/LATAM members
- YouTube creators in this vertical (LATAM finance, SMB, tech)
- Complementary products (e.g. accounting software → distribution via accounting WhatsApp groups)
- Trade associations or industry groups

Document top 1-2 options per ORB layer for this opportunity.

### Step 5 — Build first_10_customer_path

This is the primary deliverable. It must be SPECIFIC.

Requirements:
- Minimum 5 steps
- Each step names a specific channel (not "social media" — name the platform)
- Each step names a specific action (not "post content" — name the content type and message)
- Steps 1-3: reach the buyer
- Steps 4-6: convert the buyer (demo, trial, close)
- Steps 7-9: activate the referral loop
- Step 10: state the MRR outcome after 10 customers

Example format:
```
1. Join 3 Venezuelan entrepreneur WhatsApp groups [name specific groups if found]
2. Post a 60-second demo video showing [exact problem solved] — daily for 5 days
3. DM 20 group members with: "Hola [name], ¿cómo manejas [exact pain]? Te muestro algo rápido"
4. Book demo calls via WhatsApp voice note — 10 calls in Week 1
5. Close first 3 paying customers at $9/mo with free 30-day trial
6. Ask each customer: "¿Conoces 2 personas que también necesiten esto?" — referral trigger
7. Build WhatsApp broadcast list from those 6 referrals — send weekly value tips
8. Close 3 more from referral list — now at 6 customers ($54/mo MRR)
9. Record a 45-second WhatsApp voice testimonial from customer 1 — post in groups
10. Repeat DM cycle using testimonial as trust signal → 10 customers = $90/mo MRR
```

### Step 6 — Estimate CAC

Pick the top channel from Step 4. Express CAC as a formula:

```
"[Channel name]: ~$[CPL] CPL × [conv%] conv = ~$[CAC] CAC"
```

Examples:
- "WhatsApp cold VE: ~$1.5 CPL × 12% conv = ~$12 CAC"
- "LinkedIn B2B LATAM: ~$15 CPL × 15% conv = ~$100 CAC"
- "WhatsApp referral: ~$0 CPL × 35% conv = ~$0 CAC (time investment only)"
- "TikTok organic: ~$0 CPL × 3% conv = ~$0 CAC (content investment only)"

Cross-reference with `CAC_BENCHMARKS_BY_CHANNEL` in `src/opportunity_os/distribution_intelligence.py` for starting estimates. Adjust based on web research findings for this specific vertical.

**CAC viability gate:** CAC must be < 3x monthly price point.
- $9/mo product → CAC must be < $27
- $15/mo product → CAC must be < $45
- $50/mo product → CAC must be < $150

If no channel meets this threshold → flag `distribution_risk = True` in the opportunity record.

### Step 7 — Write enriched fields to opportunity record

Update the opportunity dict with these 6 fields:

```python
opp["distribution_validated"] = True          # bool — False if quality gate fails
opp["top_distribution_channels"] = [          # list[str], max 3
    "WhatsApp cold outreach (referral-based)",
    "TikTok organic (short-form demo content)",
    "Instagram DM (visual products)"
]
opp["estimated_cac_logic"] = "WhatsApp cold VE: ~$1.5 CPL × 12% conv = ~$12 CAC"
opp["first_10_customer_path"] = "1. Join 3 Venezuelan WhatsApp groups → 2. ..."
opp["trust_mechanism_latam"] = "WhatsApp referral from existing customer + free 30-day trial"
opp["distribution_validated_date"] = "2026-04-01"  # today's date
```

Write the updated JSONL line back to `data/opportunities/opportunities.jsonl`. Replace the existing line for this `id`. Do not create duplicate records.

Remove `_` prefixed helper fields before writing — they are runtime scaffolding, not schema fields.

---

## VE/LATAM Rules — Apply to Every Opportunity

**1. WhatsApp first.** Always evaluate WhatsApp as the primary channel for Venezuela and all LATAM geographies before considering any other channel. If WhatsApp is ruled out, document why explicitly.

**2. Referral beats cold always.** If a referral mechanism can be designed into the first_10_customer_path, it must be there. Referral = $0 CAC + trust signal built-in.

**3. CAC must be < 3x monthly price.** For VE SaaS at $9-15/mo — CAC ceiling is $27-45. Flag anything above as distribution_risk.

**4. Trust mechanism is MANDATORY — never skip it.** Every Venezuelan and LATAM buyer needs a trust signal before paying. Options ranked by strength:
- WhatsApp referral from known contact (strongest)
- Video testimonial from recognizable local entrepreneur
- Free trial with no card required
- Visible USD pricing (not bolivares)
- Active WhatsApp support group

**5. Informal commerce buyers are WhatsApp-native, not app-store-native.** The first_10_customer_path for VE informal commerce must not assume app store discovery. Distribution must start with direct human contact.

**6. Paid advertising as primary channel for VE/LATAM at $9-15/mo = distribution_risk flag.** Paid CAC in LATAM rarely achieves the 3x rule at low price points. Note it as secondary or "future channel after 50 customers" — not primary.

---

## Output Quality Gate

**PASS** (set `distribution_validated = True`):
- `first_10_customer_path` is specific (named channels + named actions, 5+ steps)
- `estimated_cac_logic` is populated with a formula
- `trust_mechanism_latam` is populated
- Estimated CAC < 3x monthly price point

**FAIL** (set `distribution_validated = False`, add validation_notes):
- first_10_customer_path is generic (no named channels or actions)
- No channel meets CAC viability threshold

**BLOCK PROMOTION** (add `distribution_risk = True` to validation_notes):
- Estimated CAC > 3x monthly price point across ALL researched channels
- No organic or referral alternative exists
- Trust barrier is insurmountable without significant brand investment

---

## File Paths (project root relative)

| File | Purpose |
|------|---------|
| `data/opportunities/opportunities.jsonl` | Main opportunity store — read + write |
| `src/opportunity_os/distribution_intelligence.py` | Channel maps + CAC benchmarks — import or read manually |

---

## Example Invocation

```
Run distribution-mapper on opportunity: "Control de inventario para bodegueros informales Venezuela"
vertical: saas_smb
geography: venezuela
business_model_type: saas
target_customer: Dueños de bodegas y tiendas informales en Venezuela
problem_statement: No tienen forma de llevar inventario y cuentas sin papel
```

Expected output fields populated: `distribution_validated`, `top_distribution_channels`, `estimated_cac_logic`, `first_10_customer_path`, `trust_mechanism_latam`, `distribution_validated_date`.
