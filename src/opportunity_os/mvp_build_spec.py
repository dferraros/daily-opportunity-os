"""Generate an MVP build specification from a scored opportunity.

`opp-os build-spec <opp_id>` writes two files designed for the build phase:

- YYYY-MM-DD-{id}-mvp-build-spec.md  -- detailed 7-section build specification
- YYYY-MM-DD-{id}-build-prompt.md    -- self-contained prompt for Claude Code

Pure templating: no API calls, no key requirements. Mirrors kickoff.py and validation_engine.py.

Sections A-G:
  A. Feature Scope (must-have from first_revenue_path; explicit OUT-OF-SCOPE)
  B. Tech Architecture (vertical/geography-keyed skeleton with hour estimates)
  C. 4-Week Sprint Plan (weekly definition-of-done)
  D. Resource Plan (table)
  E. Unit Economics (scenarios: conservative/base/ambitious; break-even at $8K/mo)
  F. Weekly Metrics + Kill Conditions
  G. Week-4 Go/No-Go Criteria
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from opportunity_os.kickoff import GEO_WTP_ANCHORS, _slugify, _text_or
from opportunity_os.storage import get_opportunity_by_id, get_project_root


# ─── Architecture templates by vertical/geography ───────────────────────────

ARCHITECTURE_TEMPLATES = {
    "venezuela_fintech": {
        "stack": "Python FastAPI + Postgres + Celery, WhatsApp webhook integration via Twilio",
        "key_components": ["payment rail detector", "transaction importer", "reconciliation engine", "WhatsApp bot"],
        "infrastructure": "AWS or Heroku (< $50/mo initially), Twilio for WhatsApp ($0.0075/msg)",
        "estimated_hours": 80,
        "critical_path": "Payment detection (20h) → Importer (20h) → WhatsApp bot (15h) → Testing (25h)",
    },
    "venezuela_smb": {
        "stack": "No-code (Zapier) + Airtable + Whatsapp via Zapier, or lightweight Node.js + SQLite for offline",
        "key_components": ["workflow automation", "data sync", "mobile-friendly UI", "WhatsApp responder"],
        "infrastructure": "Zapier (< $40/mo) OR self-hosted Node.js ($10-20/mo VPS), WhatsApp Business API",
        "estimated_hours": 60,
        "critical_path": "Zapier automation (10h) → Manual testing (15h) → WhatsApp integration (20h) → Launch (15h)",
    },
    "latam_fintech": {
        "stack": "Python FastAPI + Postgres + Celery, SMS/WhatsApp notification layer",
        "key_components": ["payment orchestration", "local payment method support", "audit trail", "SMS alerts"],
        "infrastructure": "AWS/GCP ($100-150/mo), Twilio ($0.005-0.02/SMS), local payment provider SDKs",
        "estimated_hours": 120,
        "critical_path": "Payment adapter (30h) → Database (15h) → API (25h) → SMS layer (20h) → Testing (30h)",
    },
    "latam_smb": {
        "stack": "React + Node.js + Postgres OR Supabase, mobile-responsive",
        "key_components": ["dashboard", "inventory sync", "report generation", "local payment methods"],
        "infrastructure": "Vercel + Supabase ($30-50/mo) OR self-hosted ($20-30/mo)",
        "estimated_hours": 100,
        "critical_path": "API (25h) → Frontend (30h) → Local payment integration (20h) → Mobile (15h) → Testing (10h)",
    },
    "global_saas": {
        "stack": "React + Node.js + Postgres + Stripe, standard SaaS stack",
        "key_components": ["user auth", "core feature", "billing", "support channels"],
        "infrastructure": "Vercel + Heroku/Railway ($50-100/mo), Stripe billing",
        "estimated_hours": 140,
        "critical_path": "Auth (15h) → Core feature (50h) → Billing (20h) → Polish (30h) → Testing (25h)",
    },
    "default": {
        "stack": "Language-agnostic. Start with the simplest possible tech (no-code, spreadsheet, or single-file script).",
        "key_components": ["core logic", "manual fulfillment", "customer interface", "reporting"],
        "infrastructure": "Minimal: GitHub, Notion, or local machine for first 3 customers",
        "estimated_hours": 50,
        "critical_path": "MVP logic (20h) → Manual test (10h) → Customer delivery (15h) → Iterate (5h)",
    },
}


def _get_architecture_key(opp: dict) -> str:
    """Determine architecture template key from geography + vertical."""
    geo = (opp.get("geography") or "global").lower()
    vertical = (opp.get("vertical") or "").lower().replace(" ", "_")

    # Priority: geography_vertical, geography fallback, vertical fallback, default
    if geo == "venezuela":
        if "fintech" in vertical or "payment" in vertical:
            return "venezuela_fintech"
        return "venezuela_smb"
    elif geo in ("latam", "colombia", "mexico", "peru", "argentina", "chile"):
        if "fintech" in vertical or "payment" in vertical:
            return "latam_fintech"
        return "latam_smb"
    elif geo == "global":
        if "saas" in vertical or "software" in vertical:
            return "global_saas"

    return "default"


def _estimate_price(opp: dict) -> int:
    """Estimate mid-tier monthly price in local currency."""
    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict) and frp.get("first_price_point"):
        try:
            raw = str(frp["first_price_point"]).replace("€", "").replace("$", "").replace("/mo", "").strip()
            return int(float(raw.split()[0]))
        except (ValueError, IndexError):
            pass

    wtp = opp.get("willingness_to_pay", 5)
    geo = opp.get("geography", "global")
    geo_multiplier = {"venezuela": 0.3, "latam": 0.6, "colombia": 0.7, "mexico": 0.7, "spain": 1.2, "global": 1.0}
    base = max(9, int(wtp * 8 * geo_multiplier.get(geo, 1.0)))
    for clean in [9, 19, 29, 49, 79, 99, 149, 199]:
        if base <= clean:
            return clean
    return 199


def _currency_symbol(opp: dict) -> str:
    """Return currency symbol based on geography."""
    geo = (opp.get("geography") or "global").lower()
    usd_geos = {"venezuela", "latam", "colombia", "mexico", "peru", "brazil", "brasil", "argentina", "chile"}
    return "$" if geo in usd_geos else "€"


# ─── Section renderers ───────────────────────────────────────────────────────

def _render_section_a_feature_scope(opp: dict) -> str:
    """Section A: Feature scope (must-have and explicit OUT-OF-SCOPE)."""
    frp = opp.get("first_revenue_path") or {}
    first_offer = _text_or(
        frp if isinstance(frp, dict) else {"first_offer": None},
        "first_offer",
        opp.get("path_to_first_revenue", "[NEEDS INPUT: first_revenue_path]")
    )

    vertical = opp.get("vertical", "").lower()
    is_fintech = "fintech" in vertical or "payment" in vertical

    # OUT-OF-SCOPE rules for fintech
    out_of_scope_fintech = (
        "\n- **No customer fund custody** — avoid regulated custody roles; use pass-through APIs\n"
        "- **No transfer initiation** — customers manage transfers themselves; tool monitors/reconciles\n"
        "- **No settlement** — defer settlement to existing infrastructure (bank, Zelle, USDT P2P)\n"
    ) if is_fintech else ""

    must_haves = opp.get("assumptions") or [
        "Core problem solved for 1 customer",
        "Documented first revenue path",
        "Repeatable onboarding (< 15 min per customer)"
    ]
    must_have_lines = "\n".join(f"- {m}" for m in must_haves[:5]) if must_haves else "- (populate from assumptions)"

    return f"""## A. Feature Scope

**First offer:** {first_offer}

**Must-have (MVP):**
{must_have_lines}

**Out of scope (first 3 customers):**
- Analytics dashboards
- Admin tools
- Bulk import/export
- Mobile app (unless WhatsApp for Venezuela)
- Email notifications (WhatsApp only for Venezuela/LATAM)
- Role-based access control{out_of_scope_fintech}

**User flow (single customer, end-to-end):**
[NEEDS INPUT: describe 5-step flow from signup to first successful transaction/result]

**Acceptance criteria for "done":**
- Customer can complete the core workflow without support
- At least 1 paying customer has used it for 2 weeks
- Zero critical bugs in that usage
"""


def _render_section_b_tech_architecture(opp: dict) -> str:
    """Section B: Tech architecture skeleton with hour estimates."""
    arch_key = _get_architecture_key(opp)
    template = ARCHITECTURE_TEMPLATES.get(arch_key, ARCHITECTURE_TEMPLATES["default"])

    return f"""## B. Tech Architecture

**Tech stack:** {template['stack']}

**Key components:**
{chr(10).join(f'- {c}' for c in template['key_components'])}

**Infrastructure costs (first 3 months):**
{template['infrastructure']}

**Build estimate:** {template['estimated_hours']} hours solo (4-5 weeks at 20h/week)

**Critical path:**
{template['critical_path']}

**Deployment target:** [NEEDS INPUT: Vercel | Heroku | Railway | Self-hosted VPS | No-code platform]

**Key dependencies to validate:**
- Payment provider API availability (latency, rate limits, cost)
- WhatsApp Business API approval (if VE/LATAM: 5-10 business days)
- Third-party integrations stable and documented
"""


def _render_section_c_sprint_plan(opp: dict) -> str:
    """Section C: 4-week sprint plan with weekly definition-of-done."""
    return """## C. 4-Week Sprint Plan

**Week 1: Foundation + Customer Interviews**
- Days 1-2: Set up local dev environment, database schema, basic auth
- Days 3-4: Conduct 5 customer discovery interviews (validate problem severity)
- Day 5: Refine MVP scope based on interviews; drop non-essentials
- Definition of done: Local dev works, 5 interviews documented, scope frozen

**Week 2: Core Feature**
- Days 1-3: Build core logic (the 80% that matters)
- Days 4-5: Manual end-to-end test with real data
- Definition of done: Core feature works locally, tested with 1 internal user

**Week 3: Polish + Deployment**
- Days 1-2: UI/UX polish, error messages, basic docs
- Days 3-4: Deploy to staging; test payment/webhook integrations
- Day 5: Security audit (OWASP top 3), fix critical issues
- Definition of done: Staging environment live, 2 customers invited to test

**Week 4: Beta Launch + Iterate**
- Days 1-2: Onboard first 2 paying customers (or pilot customers)
- Days 3-4: Fix bugs, respond to customer feedback
- Day 5: Evaluate go/no-go criteria (section G)
- Definition of done: 1-2 customers using production, revenue running, metrics recorded

**Daily standdown (async):**
- 1 line: What shipped today?
- 1 line: What blocks progress?
- 1 number: Hours burned vs. plan
"""


def _render_section_d_resource_plan(opp: dict) -> str:
    """Section D: Resource plan table."""
    return """## D. Resource Plan

| Role | Responsibility | % Allocation | Duration |
|------|---|---|---|
| **Founder** | Architecture, core feature, customer interviews | 100% | 4 weeks |
| **Customer #1** | Beta tester, feedback loop | Async (2-3h/week) | Weeks 2-4 |
| **Customer #2** | Beta tester, edge-case discovery | Async (2-3h/week) | Week 4+ |
| **Claude Code** | Pair programming on implementation | On-demand | Weeks 1-4 |

**Cost breakdown (pre-revenue):**
- Infrastructure: $50-150/mo
- APIs (Twilio, payment gateways, etc.): $20-100/mo
- Tools (GitHub, etc.): $0-50/mo
- **Total pre-revenue burn:** $70-300/mo (hypothesis — adjust per actuals)

**Funding needed before first revenue:**
- Conservative: $2,000 (assume 6-week timeline, $300/mo burn)
- Base: $1,000 (assume 4-week timeline with existing resources)
- Ambitious: $500 (assume co-founder or existing infrastructure)
"""


def _render_section_e_unit_economics(opp: dict) -> str:
    """Section E: Unit economics with 3 scenarios (conservative/base/ambitious)."""
    mid_price = _estimate_price(opp)
    currency = _currency_symbol(opp)
    setup_fee = max(0, mid_price // 3)  # Default: ~1 month MRR

    geo = opp.get("geography", "global").lower()
    monthly_burn = 300 if geo == "venezuela" else (200 if geo in ("latam", "colombia") else 400)
    break_even_customers = max(1, int(8000 / mid_price))

    return f"""## E. Unit Economics

**Hypothetical setup:**
- Setup fee: {currency}{setup_fee} (hypothesis — validate in interviews)
- Monthly MRR per customer: {currency}{mid_price} (hypothesis from WTP anchor: {GEO_WTP_ANCHORS.get(geo, GEO_WTP_ANCHORS["global"])})
- Customer CAC (via cold outreach): {currency}{mid_price * 3} (hypothesis — 3x MRR from first 3 months outreach)
- Customer LTV (24-month horizon): {currency}{mid_price * 24} (assumption: 2-year retention)

**Payback period:** {max(1, int((mid_price * 3) / mid_price))} months (CAC ÷ MRR)

**Break-even analysis (monthly burn {currency}{monthly_burn}):**
- Conservative (50% attach): {break_even_customers * 2} customers to cover burn
- Base (100% attach): {break_even_customers} customers to cover burn
- Ambitious (150% attach): {max(1, int(break_even_customers * 0.67))} customers to cover burn

**3-Customer Scenarios (end of Week 4):**

| Metric | Conservative | Base | Ambitious |
|--------|---|---|---|
| **Pricing** | {currency}{int(mid_price * 0.75)}/mo | {currency}{mid_price}/mo | {currency}{int(mid_price * 1.25)}/mo |
| **Customers** | 1 | 3 | 5 |
| **Monthly Revenue** | {currency}{int(mid_price * 0.75)} | {currency}{mid_price * 3} | {currency}{int(mid_price * 1.25 * 5)} |
| **Setup Fees** | {currency}{setup_fee} | {currency}{setup_fee * 3} | {currency}{setup_fee * 5} |
| **Total Collected** | {currency}{int(mid_price * 0.75) + setup_fee} | {currency}{mid_price * 3 + setup_fee * 3} | {currency}{int(mid_price * 1.25 * 5 + setup_fee * 5)} |
| **Gross Margin** | 80% | 80% | 80% |
| **Burn (4 weeks)** | {currency}{monthly_burn * 1} | {currency}{monthly_burn * 1} | {currency}{monthly_burn * 1} |
| **Net Position** | [NEEDS INPUT] | [NEEDS INPUT] | [NEEDS INPUT] |

**Key hypotheses to test:**
1. {currency}{mid_price}/mo is acceptable to customers (vs. {GEO_WTP_ANCHORS.get(geo, GEO_WTP_ANCHORS["global"])})
2. CAC will be {currency}{mid_price * 3} or lower via cold outreach
3. Customer acquisition will take 2-4 weeks, not 8-12 weeks
4. No unexpected infrastructure costs beyond {currency}{monthly_burn}/mo

**Profit model at scale (12 customers, month 6):**
- MRR: {currency}{mid_price * 12} (hypothesis)
- Burn: {currency}{monthly_burn} (fixed + variable)
- Net: {currency}{mid_price * 12 - monthly_burn} (hypothesis: break-even or profitable)
"""


def _render_section_f_metrics_and_kills(opp: dict) -> str:
    """Section F: Weekly metrics and kill conditions."""
    return """## F. Weekly Metrics + Kill Conditions

**Track these metrics daily (Notion or spreadsheet):**
- Interviews completed: [target: 5 by end Week 1]
- Landing page CTA clicks: [target: 15+ per 50 outreach]
- Customer conversations leading to LOI: [target: 1+ per week]
- Churn: [target: 0 in first month]
- Feature requests vs. complaints: [ratio to watch]

**Weekly kill criteria — stop if ANY trigger:**

| Week | Kill Signal | Action |
|---|---|---|
| **End Week 1** | Fewer than 3 interviews scheduled OR all interviews reject pain severity | Pivot problem angle or target customer |
| **End Week 2** | Landing page < 5% CTA rate from 50+ outreach OR core feature incomplete | Scope cut aggressively; consider no-code pivot |
| **End Week 3** | Zero LOIs (letters of interest) or commitment to pay | Rethink pricing/offer; test lower price point |
| **End Week 4** | Zero paying customers after outreach to 50+ targets | Declare discovery complete; move to pivot candidates |

**Pass criteria (promotion to Week 5+):**
- [ ] Minimum 2 paying customers (recurring billing set up)
- [ ] At least 1 customer using product 3+ times/week
- [ ] 0 critical bugs in production
- [ ] Revenue > 30% of projected conservative scenario (Week 4 table)
- [ ] Strong qualitative signal: at least 1 customer unsolicited referral or "when can I pay more"
"""


def _render_section_g_go_no_go(opp: dict) -> str:
    """Section G: Week-4 go/no-go criteria."""
    currency = _currency_symbol(opp)
    mid_price = _estimate_price(opp)

    return f"""## G. Week-4 Go/No-Go Decision

**Data to gather by end of Week 4:**
- [ ] Total customers (trial + paying): [NEEDS INPUT: target: 2-5]
- [ ] Total revenue collected (setup + MRR): {currency}[NEEDS INPUT]
- [ ] Customer satisfaction (NPS or simple poll): [NEEDS INPUT: target: +30 or higher]
- [ ] Time spent on support vs. building: [NEEDS INPUT: target: <20% of time]
- [ ] Roadmap clarity for next 4 weeks: [NEEDS INPUT: 3-5 clear next features]

**GO Decision (promotion to scale):**
✅ Proceed to Week 5-8 focused build if:
- 2+ paying customers with MRR {currency}{mid_price}+
- Revenue trajectory suggests path to {currency}1K/mo MRR within 8 weeks
- At least 1 strong customer signal (referral, feature request, "when is X ready?")
- Founder confidence in problem-solution fit is HIGH

**PIVOT Decision (narrow or shift):**
⚠️ Pivot to neighbor opportunity if:
- Core problem confirmed but current positioning misses majority WTP
- Customer segment wrong; different segment has stronger urgency
- Distribution channel different than assumed
- Monetization model needs rethink (per-user vs. per-org, etc.)

**NO-GO Decision (kill and move on):**
❌ Kill and move on if:
- Fewer than 2 LOIs (letters of interest) from 50+ outreach
- No customer willingness to pay at target price point
- Founder loss of conviction due to discovered blockers (legal, technical, market)
- Better opportunity emerged in parallel validation queue

**If NO-GO:** Document kill reason in 1-2 sentences for future reference.
Preserve all customer feedback and pain evidence in vault for similar future ideas.
"""


def build_mvp_spec(opp: dict) -> str:
    """
    Build a complete MVP build specification from an opportunity.

    Args:
        opp: opportunity dict from storage

    Returns:
        markdown string with sections A-G
    """
    name = opp.get("name", "Unnamed Opportunity")
    score = opp.get("final_score", 0)
    score_str = f"{float(score):.1f}/10" if score is not None else "unscored"

    header = f"""# MVP Build Specification: {name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
**Opportunity ID:** {opp.get('id', 'unknown')}
**Score:** {score_str} | **Lane:** {opp.get('portfolio_lane', 'unknown').upper()}
**Geography:** {opp.get('geography', 'global').upper()}

---

This specification is a **build contract** for the next 4 weeks. Every number is labeled **hypothesis** —
validate or discard during execution. Missing inputs are marked **[NEEDS INPUT: field]** — fill these before starting Week 1.

"""

    sections = [
        _render_section_a_feature_scope(opp),
        _render_section_b_tech_architecture(opp),
        _render_section_c_sprint_plan(opp),
        _render_section_d_resource_plan(opp),
        _render_section_e_unit_economics(opp),
        _render_section_f_metrics_and_kills(opp),
        _render_section_g_go_no_go(opp),
    ]

    return header + "\n".join(sections)


def build_claude_code_prompt(opp: dict, spec_md: str) -> str:
    """
    Build a self-contained Claude Code prompt for the build phase.

    Composes with kickoff.py's starter pack + the spec generated above.

    Args:
        opp: opportunity dict from storage
        spec_md: the MVP spec markdown (output of build_mvp_spec)

    Returns:
        self-contained prompt string
    """
    name = opp.get("name", "this opportunity")
    slug = _slugify(name)
    geo = (opp.get("geography") or "global").lower()

    frp = opp.get("first_revenue_path") or {}
    first_offer = _text_or(
        frp if isinstance(frp, dict) else {"first_offer": None},
        "first_offer",
        opp.get("path_to_first_revenue", "a core product or service")
    )

    target_customer = opp.get("target_customer", "the target customer")
    problem = opp.get("problem_statement", "the problem they face")

    return f"""# Claude Code Build Prompt — {name}

**READ THIS FIRST:** The MVP Build Specification (attached/pasted below) is your build contract for the next 4 weeks.
Use /spec and /plan to break down implementation into tasks.
Every number is a hypothesis — validate during execution.

---

## The Ask

Build an MVP for **{name}** in 4 weeks, solo + AI tooling.

**Problem:** {problem}

**Customer:** {target_customer}

**First offer:** {first_offer}

**Success metric:** 1-2 paying customers using the product by end of Week 4.

**Kill condition:** If you cannot confirm the problem with 5 customer interviews by end of Week 1,
or if zero customers will pay for the solution by end of Week 4, stop and move to the next candidate.

---

## Workflow

1. **Read the spec** — every section A-G
2. **Fill [NEEDS INPUT] gaps** — specifically:
   - Section A: 5-step user flow for your first customer
   - Section B: Deployment target (Vercel, Heroku, self-hosted, no-code platform)
   - Section D: Verify resource plan; adjust timeline if solo time is different
   - Section E: Validate pricing with 5 customers; adjust MRR assumptions
3. **Run /spec** — propose detailed implementation spec to your Claude Code session
4. **Run /plan** — break spec into weekly tasks
5. **Execute** — commit daily progress; track metrics (Section F)
6. **Week 4 decision** — evaluate go/no-go criteria (Section G); document decision

---

## Key Constraints

- **Budget:** < $2,000 pre-revenue (APIs, hosting, tools)
- **Timeline:** MVP shippable in <= 4 weeks, 20-25 hours/week
- **Scope:** Customer can complete the core workflow in < 5 minutes without support
- **Distribution:** First 10 customers via {GEO_WTP_ANCHORS.get(geo, GEO_WTP_ANCHORS['global'])} pricing + direct outreach
- **Geography:** {geo.upper()} market reality — pricing, trust, payment rails, distribution all region-specific

---

## Acceptance Criteria (End of Week 4)

- [ ] Core feature deployed and live for paying customers
- [ ] 1-2 paying customers running on production (recurring billing)
- [ ] Daily metrics tracked (interviews, revenue, churn, feature requests)
- [ ] Week-4 go/no-go decision documented
- [ ] If GO: roadmap for Week 5-8 is clear
- [ ] If PIVOT: neighbor candidate identified with same research
- [ ] If NO-GO: kill reason recorded for future reference

---

## Full Build Specification

Below is the complete specification. Fill all [NEEDS INPUT] sections before you start Week 1.

{spec_md}

---

**Generated by Daily Opportunity OS**
This prompt composes with the standard Claude Code workflow: /spec → /plan → /build → /ship.
"""


def write_build_package(opp: dict, out_dir: Optional[str] = None) -> dict:
    """
    Write MVP build spec + prompt files to disk.

    Args:
        opp: opportunity dict from storage
        out_dir: optional override directory (used by tests)

    Returns:
        dict with {"spec_path", "prompt_path"} on success, or {"error": msg} on failure
    """
    opp_id = opp.get("id")
    if not opp_id:
        return {"error": "Opportunity missing id field."}

    # Determine output directory (mirrors kickoff.py pattern)
    if out_dir:
        target = Path(out_dir)
    else:
        project_root = get_project_root()
        date_str = datetime.now().strftime("%Y-%m-%d")
        target = Path(project_root) / "reports" / "deep-dives" / date_str

    target.mkdir(parents=True, exist_ok=True)

    # Generate content
    spec_md = build_mvp_spec(opp)
    prompt_md = build_claude_code_prompt(opp, spec_md)

    # Write atomically (temp + rename pattern)
    files = []
    opp_slug = _slugify(opp.get("name", "opp"))
    date_str = datetime.now().strftime("%Y-%m-%d")

    for filename_template, content in [
        (f"{date_str}-{opp_id[:20]}-mvp-build-spec.md", spec_md),
        (f"{date_str}-{opp_id[:20]}-build-prompt.md", prompt_md),
    ]:
        path = target / filename_template
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
        files.append(str(path))

    return {"spec_path": files[0], "prompt_path": files[1]}
