"""
Validation Engine — template-driven validation package builder.

Follows the exact pattern of pain_intelligence.py and distribution_intelligence.py:
- Pure computation, no I/O, no side effects
- Input: opp: dict (not Pydantic model — always a dict from the pipeline)
- Output: dict with schema fields + _-prefixed helper keys
- daily_run.py Step 14 and validation_run.py own all file writes

Public API:
  run_validation(opp, mode="auto") -> dict
  build_validation_queries(opp) -> list[str]
  is_validation_complete(opp) -> bool
  validation_status_label(status) -> str

Constants:
  AUTO_SECTION_COUNT = 7   (sections 1-7)
  FULL_SECTION_COUNT = 8   (sections 1-8, manual mode only)
  AUTO_VALIDATION_THRESHOLD = 7.0
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────

AUTO_SECTION_COUNT = 7
FULL_SECTION_COUNT = 8
AUTO_VALIDATION_THRESHOLD = 7.0

# Interview question templates keyed by geography + vertical
# Q format: past-focused, open-ended (SKILL.md quality gate)
INTERVIEW_QUESTION_BANK = {
    "venezuela": [
        "Cuéntame la última vez que tuviste un problema con [PROBLEM] — ¿qué pasó exactamente?",
        "¿Cómo estás manejando [PROBLEM] hoy? ¿Qué herramientas o procesos usas?",
        "¿Cuánto tiempo o dinero perdiste la última vez que [PROBLEM] te causó un error?",
        "¿Cuándo fue la última vez que buscaste una solución para [PROBLEM]? ¿Qué encontraste?",
        "Si [SOLUTION] existiera hoy, ¿cómo cambiaría tu semana típica?",
        "¿Quién más en tu negocio sufre este problema? ¿Cómo lo resuelven ellos?",
        "¿Has pagado por algo para resolver [PROBLEM] antes? ¿Qué fue? ¿Funcionó?",
    ],
    "latam": [
        "Tell me about the last time [PROBLEM] caused you a real headache — what happened?",
        "Walk me through how you currently handle [PROBLEM] day to day.",
        "How much time or money did you lose the last time [PROBLEM] went wrong?",
        "When did you last look for a solution to [PROBLEM]? What did you find?",
        "If [SOLUTION] existed today, what would your typical week look like?",
        "Who else in your business faces this? How do they deal with it?",
        "Have you paid for anything to solve [PROBLEM] before? What? Did it work?",
    ],
    "global": [
        "Tell me about the last time [PROBLEM] caused you a real problem — what happened?",
        "Walk me through how you currently handle [PROBLEM] day to day.",
        "How much time or money did you lose the last time [PROBLEM] went wrong?",
        "When did you last actively look for a solution to [PROBLEM]? What did you find?",
        "If [SOLUTION] existed today, how would your typical week change?",
        "Who else in your organization faces this? How do they deal with it?",
        "Have you ever paid for something to solve [PROBLEM]? What was it? Did it work?",
    ],
}

# Kill criteria templates from DecisionFilterResults
KILL_CRITERIA_TEMPLATES = {
    "can_sell_fast": (
        "Kill if: Cannot identify and contact 10 potential buyers within 7 days via "
        "direct outreach, WhatsApp, or existing network."
    ),
    "can_build_lean": (
        "Kill if: MVP requires more than 2 weeks of solo development OR costs more than "
        "$500 to test the core value proposition."
    ),
    "can_compound": (
        "Kill if: After 3 paying customers, there is no evidence of word-of-mouth, "
        "referral, data accumulation, or switching cost forming."
    ),
}

# Trust mechanisms by geography — imported logic from distribution_intelligence
TRUST_SNIPPETS = {
    "venezuela": "Reference a mutual contact or local community. Use WhatsApp voice message, not email. Mention specific VE context (USDT, P2P, Binance P2P).",
    "latam": "Mention a specific local reference or case. Lead with outcome in first message. WhatsApp preferred over email.",
    "colombia": "Use LinkedIn for B2B. Reference local industry context. Formal tone for first contact.",
    "mexico": "WhatsApp or LinkedIn. Reference shared network if possible. Short, direct first message.",
    "spain": "LinkedIn or email. Formal first contact. Reference relevant EU/fintech context.",
    "global": "LinkedIn or email. Lead with specific pain point observation. Keep first message under 100 words.",
}


# ─── Query builder ────────────────────────────────────────────────────────────

def build_validation_queries(opp: dict) -> list:
    """
    Build 5-8 customer discovery search queries from opp fields.
    Used by in-session agent to research customer pain evidence.
    """
    geo = opp.get("geography", "global").lower()
    vertical = opp.get("vertical", "").replace("_", " ")
    problem = opp.get("problem_statement", opp.get("name", ""))[:80]
    target = opp.get("target_customer", "")[:60]
    wedge = opp.get("venezuela_wedge_category", "")

    queries = []

    if geo == "venezuela":
        queries += [
            f"Venezuela {vertical} problemas {problem[:40]} Reddit OR Twitter",
            f"venezolanos {target} herramientas alternativas site:reddit.com OR site:twitter.com",
            f"USDT Venezuela {vertical} queja OR frustración 2024 OR 2025",
        ]
        if wedge:
            queries.append(f"Venezuela {wedge.replace('_', ' ')} pain complaints workaround")
    elif geo == "latam":
        queries += [
            f"LATAM {vertical} {problem[:40]} Reddit complaints",
            f"{target} {vertical} herramienta frustración OR workaround site:reddit.com",
        ]
    else:
        queries += [
            f"{vertical} {problem[:40]} reddit complaints workaround",
            f'"{target}" "{problem[:30]}" frustration OR "pain point" site:reddit.com',
        ]

    # Universal queries
    queries += [
        f"{opp.get('name', vertical)} alternatives competitors review site:g2.com OR site:capterra.com",
        f"{target} {problem[:40]} \"I wish\" OR \"why isn't there\" OR \"does anyone know\"",
        f"{vertical} {problem[:40]} \"paying for\" OR \"hired someone\" OR \"built internally\"",
    ]

    # Deduplicate and limit
    seen = set()
    result = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            result.append(q)
        if len(result) >= 8:
            break

    return result


# ─── Section renderers ────────────────────────────────────────────────────────

def _safe(val, default: str = "TBD", max_len: int = 500) -> str:
    if val is None:
        return default
    return str(val)[:max_len]


def _render_section_1_thesis(opp: dict) -> str:
    """Section 1: Thesis brief + kill criteria."""
    name = _safe(opp.get("name"), "Unknown Opportunity")
    score = opp.get("final_score", 0)
    lane = opp.get("portfolio_lane", "strategic")
    problem = _safe(opp.get("problem_statement"), "Problem not defined")
    why_now_raw = opp.get("why_now")
    if why_now_raw is None:
        ve_why = opp.get("why_now_venezuela")
        if isinstance(ve_why, dict):
            why_now_raw = ve_why.get("recent_change")
    why_now = _safe(why_now_raw, "Timing not specified")
    pain_reason = _safe(opp.get("pain_severity_reason"), "")
    filters = opp.get("decision_filter_results") or {}
    sell_fast = filters.get("can_sell_fast")
    build_lean = filters.get("can_build_lean")
    compound = filters.get("can_compound")

    filter_lines = []
    for label, val, key in [
        ("Can sell fast", sell_fast, "can_sell_fast"),
        ("Can build lean", build_lean, "can_build_lean"),
        ("Can compound", compound, "can_compound"),
    ]:
        if val is True:
            filter_lines.append(f"  - ✅ {label}")
        elif val is False:
            filter_lines.append(f"  - ❌ {label} — {KILL_CRITERIA_TEMPLATES[key]}")
        else:
            filter_lines.append(f"  - ⬜ {label} — not yet scored")

    filter_block = "\n".join(filter_lines) if filter_lines else "  - Not yet scored"

    return f"""## 1. Thesis

**{name}** | Score: {score:.2f} | Lane: {lane.upper()}

**Problem:** {problem}

**Why now:** {why_now}

**Pain evidence:** {pain_reason if pain_reason else "Run pain intelligence agent to populate."}

**Decision filters:**
{filter_block}
"""


def _render_section_2_customer(opp: dict) -> str:
    """Section 2: Customer + pain snapshot."""
    target = _safe(opp.get("target_customer"), "Not specified")
    pain_level = opp.get("customer_pain_level") or opp.get("pain_severity", "?")
    urgency = opp.get("urgency_of_need", "?")
    frequency = opp.get("frequency_of_need", "?")
    wtp = opp.get("willingness_to_pay", "?")
    phrases = opp.get("exact_customer_phrases") or []
    workarounds = opp.get("workarounds_found") or []

    phrases_block = "\n".join(f'  - "{p}"' for p in phrases[:4]) if phrases else "  - Run pain intelligence agent to collect real customer language."
    workarounds_block = "\n".join(f"  - {w}" for w in workarounds[:3]) if workarounds else "  - Not yet documented — ask in interviews."

    return f"""## 2. Customer + Pain

**Target:** {target}

**Pain dimensions (1-10):**
  - Severity: {pain_level} | Urgency: {urgency} | Frequency: {frequency} | WTP: {wtp}

**Exact customer language:**
{phrases_block}

**Current workarounds:**
{workarounds_block}
"""


def _render_section_3_interviews(opp: dict) -> str:
    """Section 3: 5 interview questions (SKILL.md quality gate: open-ended, past-focused)."""
    geo = opp.get("geography", "global").lower()
    problem = _safe(opp.get("problem_statement", opp.get("name", "this problem")), max_len=60)
    solution = opp.get("name", "this solution")[:60]
    target = _safe(opp.get("target_customer", "the customer"), max_len=40)

    bank = INTERVIEW_QUESTION_BANK.get(geo, INTERVIEW_QUESTION_BANK["global"])
    questions = []
    for q in bank[:5]:
        q = q.replace("[PROBLEM]", problem)
        q = q.replace("[SOLUTION]", solution)
        q = q.replace("[TARGET]", target)
        questions.append(q)

    q_block = "\n\n".join(f"Q{i+1}. {q}" for i, q in enumerate(questions))

    return f"""## 3. Interview Script

**Target:** {target} — aim for 5 interviews in 7 days.

**Logistics:** 20-minute call or WhatsApp voice. Record with permission. Focus on past behavior, not hypothetical intent.

{q_block}

**After each interview:** Note exact words they use. Flag any kill signal immediately.
"""


def _render_section_4_assumptions(opp: dict) -> str:
    """Section 4: 3 falsifiable assumptions from DecisionFilterResults."""
    risks = opp.get("risks") or []

    # Derive 3 assumptions from the decision filter logic
    assumptions = [
        f"**A1 — Reachability:** We can identify and contact 10 {_safe(opp.get('target_customer', 'potential buyers'), max_len=40)} within 7 days via existing channels.",
        f"**A2 — Pain is real:** At least 4 of 5 interviewees confirm the pain is severe enough that they have already tried to solve it.",
        f"**A3 — WTP exists:** At least 2 of 5 interviewees express willingness to pay {_currency_symbol(opp)}{_estimate_price(opp)}/mo or more.",
    ]

    kill_criteria = [
        KILL_CRITERIA_TEMPLATES["can_sell_fast"],
        KILL_CRITERIA_TEMPLATES["can_build_lean"],
        KILL_CRITERIA_TEMPLATES["can_compound"],
    ]

    extra_risks = [f"- {r}" for r in risks[:2]] if risks else []
    extra_block = "\n".join(extra_risks) if extra_risks else ""

    assumptions_block = "\n\n".join(assumptions)
    kill_block = "\n".join(f"{i+1}. {k}" for i, k in enumerate(kill_criteria))

    return f"""## 4. Falsifiable Assumptions

{assumptions_block}

**Kill criteria (stop if any of these trigger):**
{kill_block}
{extra_block}
"""


def _render_section_5_pricing(opp: dict) -> str:
    """Section 5: 3 pricing options — currency derived from geography."""
    base = _estimate_price(opp)
    low = max(9, int(base * 0.5))
    mid = base
    high = int(base * 2.5)
    currency = _currency_symbol(opp)

    geo = opp.get("geography", "global")
    frp = opp.get("first_revenue_path") or {}
    first_offer = _safe(
        frp.get("first_offer") if isinstance(frp, dict) else None,
        opp.get("path_to_first_revenue", "Core product access"),
        max_len=80,
    )
    model = opp.get("monetization_model", "monthly subscription")

    return f"""## 5. Pricing Test

**Model:** {model}
**First offer:** {first_offer}
**Geography:** {geo}

| Option | Price | Framing | Test signal |
|--------|-------|---------|-------------|
| **Option A — Anchor** | {currency}{high}/mo | Premium tier, full feature set | Baseline willingness to pay |
| **Option B — Target** | {currency}{mid}/mo | Standard access, core value | Primary conversion target |
| **Option C — Entry** | {currency}{low}/mo | Starter / first 10 customers discount | Remove price as objection |

**Test method:** Present all three options in interviews. Ask: "If this existed tomorrow, which would you choose?" Note hesitation, not just answer.

**Kill signal:** If Option C triggers "that's too expensive" → rethink unit economics.
"""


def _render_section_6_landing_page(opp: dict) -> str:
    """Section 6: Landing page hypothesis."""
    name = _safe(opp.get("name"), "Product Name")
    target = _safe(opp.get("target_customer"), "Your customer")
    problem = _safe(opp.get("problem_statement"), "the problem")[:120]
    phrases = opp.get("exact_customer_phrases") or []
    why_now = _safe(opp.get("why_now"), "")[:100]

    # Generate headline from customer language or problem statement
    if phrases:
        headline = f'Stop doing "{phrases[0][:60]}" manually'
    else:
        headline = f"The fastest way to solve {problem[:60]}"

    subheadline = f"Built for {target}. {why_now}" if why_now else f"Built for {target}."
    cta = "Get early access" if opp.get("stage") == "scout" else "Start free trial"

    return f"""## 6. Landing Page Hypothesis

**URL:** [create a simple Carrd or Notion page to test]

**Headline:** {headline}

**Subheadline:** {subheadline}

**CTA:** {cta}

**Conversion target:** 15% of visitors click CTA (cold traffic), 40%+ from outreach.

**Traffic source:** Direct outreach to 50 targeted contacts. Do NOT run paid ads yet.

**Pass condition:** 15+ people click CTA and leave their email within 7 days.

**Kill signal:** Less than 5 clicks from 50 targeted outreach contacts → headline/framing is wrong, or the pain is not strong enough.
"""


def _render_section_7_outreach(opp: dict) -> str:
    """Section 7: Outreach script (uses TRUST_SNIPPETS)."""
    geo = opp.get("geography", "global").lower()
    target = _safe(opp.get("target_customer"), "operators")
    problem = _safe(opp.get("problem_statement"), "manual processes")[:80]

    # Get distribution channel from flat list (populated by distribution_intelligence)
    channels = opp.get("top_distribution_channels") or []
    channel = channels[0] if channels else ("WhatsApp" if geo == "venezuela" else "LinkedIn")

    trust_note = TRUST_SNIPPETS.get(geo, TRUST_SNIPPETS["global"])

    # Template first message
    if geo == "venezuela":
        first_msg = (
            f"Hola [Nombre], soy Daniel. Vi que trabajas en [CONTEXT]. "
            f"Estoy investigando cómo los {target} manejan {problem[:50]}. "
            f"¿Tendrías 15 minutos esta semana para contarme tu experiencia? "
            f"No es una venta — solo quiero entender el problema."
        )
    else:
        first_msg = (
            f"Hi [Name], I'm Daniel. I noticed you work in [CONTEXT]. "
            f"I'm researching how {target} handle {problem[:50]}. "
            f"Would you have 15 minutes this week to share your experience? "
            f"Not a sales call — I'm trying to understand the problem."
        )

    return f"""## 7. Outreach Script

**Primary channel:** {channel}
**Trust note:** {trust_note}

**First message template:**
> {first_msg}

**List source:** LinkedIn Sales Navigator (filter: {target}, {geo.upper()}) OR local community groups OR existing network.

**Target:** 50 outreach messages → 10 replies → 5 interviews.

**Expected response rate:** 10-20% (higher if warm intro, lower if cold).

**Follow-up (48h no reply):**
> "Quick follow-up — are you the right person to talk to about this, or should I reach out to someone else on your team?"

**Kill signal:** Less than 5% reply rate from 30+ outreach messages → channel or target customer is wrong.
"""


def _render_section_8_mvp(opp: dict) -> str:
    """Section 8: MVP scope + 7-day sprint (full mode only)."""
    speed = opp.get("speed_to_mvp", 5)
    capital = opp.get("capital_intensity", 5)
    ai_leverage = opp.get("ai_leverage", opp.get("ai_leverage_potential", 5))
    first_proof = ""
    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict):
        first_proof = _safe(frp.get("first_proof_point_needed"), max_len=120)
    if not first_proof:
        first_proof = _safe(opp.get("path_to_first_revenue"), max_len=120)

    # Estimate build time
    if speed >= 8:
        build_estimate = "3-5 days"
        mvp_type = "No-code / spreadsheet + Zapier automation"
    elif speed >= 6:
        build_estimate = "5-10 days"
        mvp_type = "Lightweight webapp or Notion template + manual fulfillment"
    else:
        build_estimate = "2-4 weeks"
        mvp_type = "Minimal coded tool — defer to post-validation"

    ai_note = f"AI leverage score: {ai_leverage}/10 — " + (
        "High AI automation potential. Use Claude/GPT for core logic before writing custom code." if ai_leverage >= 7
        else "Moderate AI potential. Use for reporting/summary layer." if ai_leverage >= 5
        else "Low AI leverage. Build manually."
    )

    return f"""## 8. MVP Scope + 7-Day Sprint

**MVP type:** {mvp_type}
**Build estimate:** {build_estimate}
**Capital intensity:** {capital}/10 (lower = cheaper)

**{ai_note}**

**First proof point needed:** {first_proof if first_proof else "Confirm with 3 paying customers."}

**7-day sprint:**
- Day 1-2: 5 customer interviews (section 3 script)
- Day 3: Synthesize interviews. Kill or continue decision.
- Day 4-5: Build MVP (if continue): {mvp_type}
- Day 6: Launch landing page (section 6). Send 50 outreach messages (section 7).
- Day 7: Tally results against kill criteria (section 4). Decide: build / pivot / kill.

**Kill criteria check (Day 7):**
- [ ] 5 interviews completed with real pain confirmation
- [ ] 15+ landing page CTA clicks
- [ ] At least 2 verbal WTP signals at target price
- [ ] At least 1 "when can I use this?" response
"""


# ─── Price estimator helper ───────────────────────────────────────────────────

def _estimate_price(opp: dict) -> int:
    """Estimate mid-tier price point in EUR from schema signals."""
    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict) and frp.get("first_price_point"):
        try:
            raw = str(frp["first_price_point"]).replace("€", "").replace("$", "").replace("/mo", "").strip()
            return int(float(raw.split()[0]))
        except (ValueError, IndexError):
            pass

    # Fallback: derive from WTP score and geography
    wtp = opp.get("willingness_to_pay", 5)
    geo = opp.get("geography", "global")
    geo_multiplier = {"venezuela": 0.3, "latam": 0.6, "colombia": 0.7, "mexico": 0.7, "spain": 1.2, "global": 1.0}
    base = max(9, int(wtp * 8 * geo_multiplier.get(geo, 1.0)))
    # Round to nearest "clean" price
    for clean in [9, 19, 29, 49, 79, 99, 149, 199]:
        if base <= clean:
            return clean
    return 199


def _currency_symbol(opp: dict) -> str:
    """Return currency symbol based on geography — USD/USDT markets use $, others use €."""
    geo = (opp.get("geography") or "global").lower()
    usd_geos = {"venezuela", "latam", "colombia", "mexico", "peru", "brazil", "brasil", "argentina", "chile"}
    return "$" if geo in usd_geos else "€"


# ─── Main runner ─────────────────────────────────────────────────────────────

def run_validation(opp: dict, mode: str = "auto") -> dict:
    """
    Build a validation package for an opportunity.

    Args:
        opp: opportunity dict from pipeline or storage
        mode: "auto" (sections 1-7) or "full" (sections 1-8)

    Returns:
        dict with:
          Schema fields: stage, validation_status, validation_start_date, validation_deadline
          Helper fields (_-prefixed): _validation_markdown, _validation_queries,
                                      _opp_id, _opp_name, _mode
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")

    sections = [
        _render_section_1_thesis(opp),
        _render_section_2_customer(opp),
        _render_section_3_interviews(opp),
        _render_section_4_assumptions(opp),
        _render_section_5_pricing(opp),
        _render_section_6_landing_page(opp),
        _render_section_7_outreach(opp),
    ]
    score = float(opp.get("final_score", 0) or 0)
    if mode == "full" or (mode == "auto" and score >= AUTO_VALIDATION_THRESHOLD):
        sections.append(_render_section_8_mvp(opp))

    header = (
        f"# Validation Package: {opp.get('name', 'Unknown')}\n\n"
        f"**Generated:** {today} | **Mode:** {mode.upper()} | "
        f"**Score:** {opp.get('final_score', 0):.2f} | "
        f"**Deadline:** {deadline}\n\n---\n"
    )
    markdown = header + "\n".join(sections)

    return {
        # Schema fields (merged back by daily_run.py, filtering out _ keys)
        "stage": "validation",
        "validation_status": "in_progress",
        "validation_start_date": today,
        "validation_deadline": deadline,
        # Helper fields (stripped by _ filter in daily_run.py)
        "_validation_markdown": markdown,
        "_validation_queries": build_validation_queries(opp),
        "_opp_id": str(opp.get("id", "")),
        "_opp_name": str(opp.get("name", "")),
        "_mode": mode,
    }


# ─── Convenience helpers ──────────────────────────────────────────────────────

def is_validation_complete(opp: dict) -> bool:
    """Return True if validation has passed or failed (not in_progress or None)."""
    return opp.get("validation_status") in ("passed", "failed")


def validation_status_label(status: Optional[str]) -> str:
    """Human-readable validation status label."""
    return {
        "in_progress": "🔄 In Progress",
        "passed": "✅ Passed",
        "failed": "❌ Failed",
        None: "⬜ Not Started",
    }.get(status, "⬜ Not Started")
