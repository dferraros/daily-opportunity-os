"""
AI Dimension Scorer — uses Claude Haiku to generate calibrated 1-10 scores
for all 16 opportunity dimensions, with one-line reasoning per dimension.

Replaces the regex heuristic estimator. Falls back to heuristic if API unavailable.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
AI_SCORER_VERSION = "haiku-4-5-v1"

DIMENSIONS = [
    "pain_severity",
    "market_size",
    "timing_tailwind",
    "willingness_to_pay",
    "monetization_clarity",
    "speed_to_mvp",
    "capital_efficiency",
    "distribution_accessibility",
    "competition_intensity",
    "defensibility",
    "regional_fit",
    "founder_fit",
    "ai_leverage",
    "operational_simplicity",
    "regulatory_simplicity",
    "revenue_speed_score",
]

RUBRIC = """
Score each dimension 1-10. Use the FULL range — 9-10 = exceptional, 1-2 = near-fatal flaw.
Do NOT cluster scores around 5-6. Differentiate clearly.

DIMENSION RUBRICS:

1. pain_severity (1-10)
   10: Emergency daily pain. People losing money/time every day. Explicit workarounds.
   7-9: Significant recurring pain. Clear frustration. Frequent complaints.
   5-6: Moderate pain. Annoyance but workarounds exist.
   3-4: Nice-to-have improvement. Low urgency.
   1-2: Unclear if pain exists. Assumed need.
   +1 signals: no existing tool, manual/Excel workflow, daily occurrence, money loss, forum complaints, Venezuela geography

2. market_size (1-10)
   10: TAM >$1B, multiple major players validate size
   7-9: TAM $100M-$1B, growing sector with VC funding
   5-6: TAM $10M-$100M, solid SMB niche
   3-4: TAM $1M-$10M, micro-niche
   1-2: <$1M TAM or unclear

3. timing_tailwind (1-10)
   10: New regulation just mandated it, or explosive growth signal, or first-mover window closing
   7-9: Strong macro tailwind (regulatory mandate, platform shift, tech cost drop)
   5-6: General market growth, no specific catalyst
   3-4: Mature market, late entry
   1-2: Contracting market or wrong timing
   +1 signals: 2025/2026 date context, mandatory/regulation keywords, "growing fast", Venezuela necessity (timing = now or never)

4. willingness_to_pay (1-10)
   10: Currently paying for worse solution, clear price point, high ROI vs alternative
   7-9: Strong WTP signal, competitive pricing benchmarks exist
   5-6: WTP assumed, needs validation
   3-4: Low WTP, price-sensitive market
   1-2: No evidence of payment willingness
   Venezuela adjustment: base -1 (WTP 0.25x US baseline, max $3-15/month SaaS)
   +1 signals: specific price points mentioned, mandatory compliance, cost savings proof

5. monetization_clarity (1-10)
   10: Specific model (X% take rate, $Y/month/user) validated by analogous businesses
   7-9: Clear model, comparable companies show it works
   5-6: Model exists but needs validation
   3-4: Unclear how money flows
   1-2: No monetization logic
   +1 signals: per-transaction/subscription/fee keywords, % rate mentioned

6. speed_to_mvp (1-10)
   10: MVP in <2 weeks. WhatsApp bot, Google Sheet + Zapier, existing API
   7-9: MVP in 2-6 weeks. Standard SaaS, no custom infrastructure
   5-6: MVP in 6-12 weeks. Some complexity
   3-4: MVP in 3-6 months. Hardware, regulatory, complex data
   1-2: >6 months. Platform play or heavy infrastructure
   +1 signals: "simple"/"lightweight"/"minimal", WhatsApp native, concierge-first

7. capital_efficiency (1-10)
   10: <$500. Phone + existing tools.
   7-9: $500-$5K. API costs, basic hosting
   5-6: $5K-$50K. Some development
   3-4: $50K-$500K. Team hire needed
   1-2: >$500K. Marketplace inventory, regulated capital, hardware
   +1 signals: bootstrap/no inventory/software-only, LATAM/VE context (lower cost)

8. distribution_accessibility (1-10)
   10: Customers visible on WhatsApp groups, LinkedIn, warm intros. Channel clear.
   7-9: Community or outreach path clear.
   5-6: Channel exists but requires work
   3-4: Distribution is the hard problem. No clear path
   1-2: No clear distribution hypothesis
   LATAM/VE +1: WhatsApp + community-based distribution always scores higher

9. competition_intensity (1-10) — INVERTED: lower competition = higher score
   8-10: No direct competitor. First-mover. Gap confirmed.
   6-7: 1-2 weak incumbents. Clear differentiation path.
   4-5: Competitive market but room for positioning
   2-3: Crowded space with strong players
   1: Dominated by large funded competitors
   Venezuela bonus: VE market has almost no software competition — typically scores 8+

10. defensibility (1-10)
    10: Data moat + network effects + switching costs. All three.
    7-9: 2 of 3 defensibility levers.
    5-6: First-mover advantage, brand trust, or community
    3-4: Replicable product. Defensibility unclear.
    1-2: No moat. Easily copied.
    Venezuela +1: First-mover data advantage in USDT/informal commerce data compounds fast

11. regional_fit (1-10)
    10: Built specifically for VE/LATAM. Leverages local infrastructure (USDT, WhatsApp, bolivar).
    7-9: Strong LATAM fit. Pricing, distribution, payment rails aligned.
    5-6: Adaptable. Global model with LATAM version.
    3-4: Western-first. Requires significant adaptation.
    1-2: Wrong market. Wrong pricing. Wrong trust model.
    +2 bonus: Venezuela geography, latam_asymmetry bucket
    +1 each: Spanish/USDT/WhatsApp/informal keywords

12. founder_fit (1-10)
    Base 4 + 1 point for each of Daniel's wedges that apply:
    1. Growth & GTM edge (lifecycle, CRM, paid, organic, A/B testing)
    2. Narrative & positioning edge (frame and sell a story fast)
    3. LATAM + Spanish intuition (VE, Spain, Colombia patterns)
    4. Fintech & crypto adjacency (Bit2Me, payment rails, USDT)
    5. Speed to prototype (Claude Code, MVP systems fast)
    6. Distribution instincts (WhatsApp funnels, performance, referral)
    Score = 4 + matching wedges. <2 matching wedges = flag "founder-fit risk".

13. ai_leverage (1-10)
    10: AI is the core product. Not buildable without AI. 10x human efficiency gain.
    7-9: AI dramatically reduces CAC, improves product quality, or enables automation
    5-6: AI useful but not core to the value prop
    3-4: Traditional software. AI nice-to-have.
    1-2: AI irrelevant or harmful to trust

14. operational_simplicity (1-10)
    10: Fully async. No physical operations. 1 person can run at scale.
    7-9: Small team (2-3). Remote. Software handles most of it.
    5-6: Requires some ops (customer support, onboarding, fulfillment)
    3-4: Ops-heavy. Requires local team or physical presence.
    1-2: Requires large team, physical logistics, or 24/7 ops

15. regulatory_simplicity (1-10)
    10: No license needed. Launch tomorrow.
    7-9: Basic business registration. No sector-specific license.
    5-6: Some compliance work (privacy policy, T&Cs, local tax registration)
    3-4: Sector license required (fintech, insurance, broker).
    1-2: Banking license, AML registration, or securities regulation required
    LATAM bonus: +2 base (informal market = less scrutiny)
    Fintech penalty: -1 (always more regulated)

16. revenue_speed_score (1-10)
    10: First revenue in <7 days. Service business, existing customer, immediate payment.
    7-9: First revenue in 7-30 days. Direct outreach + quick close.
    5-6: First revenue in 30-90 days. Need product, some sales cycle.
    3-4: First revenue in 3-6 months.
    1-2: First revenue >6 months.
    +1 signals: productized service, concierge-first, WhatsApp outreach, Venezuela urgency
"""

FOUNDER_WEDGES_CONTEXT = """
Daniel's background for founder_fit scoring:
- 10+ years lifecycle marketing, CRM, paid acquisition, A/B testing at crypto fintech (Bit2Me)
- Deep LATAM/Spanish market intuition (Venezuela, Spain, Colombia patterns)
- Crypto/fintech adjacency: Bit2Me operations, USDT payment rails, DeFi familiarity
- Can build MVP-level systems fast using Claude Code and modern tools
- Strong distribution instincts: WhatsApp funnels, performance marketing, referral programs
- Narrative & positioning: can frame and sell a story quickly
"""


def score_batch_with_ai(opps: list[dict]) -> list[dict]:
    """
    Score multiple opportunities in ONE API call instead of one call per opp.
    Costs: 1 call × (rubric + N × opp context) vs N calls × (rubric + opp context).
    For N=5 this saves ~75% of API cost. Falls back to per-opp heuristic on failure.
    """
    if not opps:
        return opps

    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_env_key()
    if not api_key:
        return [_heuristic_fallback(o) for o in opps]

    # Skip already-scored ones, only pass unscored to API
    to_score = [o for o in opps if not o.get("ai_scored_at")]
    already_done = [o for o in opps if o.get("ai_scored_at")]
    if not to_score:
        return opps

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        opp_blocks = []
        for i, opp in enumerate(to_score):
            geo = opp.get("geography", "global")
            geo_note = ""
            if geo == "venezuela":
                geo_note = " [VE: WTP=0.25x, WhatsApp-first, no competition, informal 55%]"
            elif geo == "latam":
                geo_note = " [LATAM: WTP=0.40x, WhatsApp 90%, informal 45%]"
            opp_blocks.append(
                f"OPP_{i}: {opp.get('name', '?')[:80]} | geo={geo}{geo_note}\n"
                f"  problem={str(opp.get('problem_statement', ''))[:200]}\n"
                f"  vertical={opp.get('vertical', '')} bucket={opp.get('bucket', '')}"
            )

        opps_text = "\n\n".join(opp_blocks)
        dim_list = ", ".join(DIMENSIONS)

        prompt = f"""Score these {len(to_score)} opportunities on 16 dimensions each.

{RUBRIC}

{FOUNDER_WEDGES_CONTEXT}

OPPORTUNITIES:
{opps_text}

Return ONLY a JSON array with {len(to_score)} objects (index 0 to {len(to_score)-1}).
Each object must have exactly these fields: {dim_list}
Plus _reason fields: {', '.join(d + '_reason' for d in DIMENSIONS[:4])} (first 4 dims only, to save tokens).
No prose, no markdown, no code block. Array only."""

        response = client.messages.create(
            model=MODEL,
            max_tokens=min(8000, 800 * len(to_score)),
            system=(
                "You are a hard-nosed business analyst. Score opportunities on 16 dimensions. "
                "Use the FULL 1-10 range. 30% scores ≤5 (real weaknesses), 30% above 7 (genuine strengths). "
                "Return ONLY a valid JSON array — no prose, no markdown."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Extract JSON array substring — handles prose before/after the array
        json_match = re.search(r'\[[\s\S]*\]', raw)
        if json_match:
            raw = json_match.group(0)

        scores_list = json.loads(raw)
        if not isinstance(scores_list, list) or len(scores_list) != len(to_score):
            raise ValueError(f"Expected {len(to_score)} items, got {len(scores_list) if isinstance(scores_list, list) else type(scores_list)}")

        now = datetime.now().strftime("%Y-%m-%d")
        for opp, scores in zip(to_score, scores_list):
            for dim in DIMENSIONS:
                val = scores.get(dim)
                if val is not None:
                    try:
                        opp[dim] = max(1, min(10, int(val)))
                    except (ValueError, TypeError):
                        pass
                reason = scores.get(f"{dim}_reason")
                if reason:
                    opp[f"{dim}_reason"] = str(reason)[:200]
            opp["ai_scored_at"] = now
            opp["ai_scorer_version"] = AI_SCORER_VERSION + "-batch"

        logger.info("[ai_scorer] Batch scored %d opps in 1 API call", len(to_score))
        return already_done + to_score

    except Exception as exc:
        from opportunity_os.pipeline_monitor import log_failure
        log_failure("ai_scorer.batch", exc, opp_id=f"{len(to_score)}_opps", recovered=True)
        return already_done + [_heuristic_fallback(o) for o in to_score]


def score_dimensions_with_ai(opp: dict) -> dict:
    """
    Score an opportunity on 16 dimensions using Claude Haiku.
    Returns the opp dict with all dimension fields + _reason fields populated.
    Falls back to heuristic if API unavailable or call fails.
    """
    # Skip if already AI-scored and not flagged for rescore
    if opp.get("ai_scored_at") and not opp.get("rescore_requested"):
        return opp

    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_env_key()
    if not api_key:
        logger.warning("[ai_scorer] No API key — using heuristic fallback for: %s", opp.get('name', '?')[:50])
        return _heuristic_fallback(opp)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        geo = opp.get("geography", "global")
        vertical = opp.get("vertical", "")
        bucket = opp.get("bucket") or opp.get("bucket_hypothesis", "")
        name = opp.get("name", "")
        problem = opp.get("problem_statement", "") or opp.get("description", "")
        trigger = opp.get("trigger_signal", "") or opp.get("raw_notes", "")[:300]
        notes = opp.get("raw_notes", "")[:400]

        geo_context = ""
        if geo == "venezuela":
            geo_context = (
                "\nGEOGRAPHY NOTE — Venezuela: WTP is 0.25x US baseline ($3-15/mo SaaS max). "
                "Payment rails: Zelle, USDT, Binance P2P. Distribution: WhatsApp-first. "
                "Informal commerce ~55%. Near-zero software competition. Necessity-driven entrepreneurship."
            )
        elif geo == "latam":
            geo_context = (
                "\nGEOGRAPHY NOTE — LATAM: WTP is 0.40x US baseline. "
                "Payment rails vary by country. WhatsApp penetration ~90%. Informal commerce ~45%."
            )

        json_template = "{\n" + ",\n".join(
            f'  "{d}": <int 1-10>,\n  "{d}_reason": "<one sentence max 15 words>"'
            for d in DIMENSIONS
        ) + "\n}"

        prompt = f"""Geography: {geo} | Vertical: {vertical} | Bucket: {bucket}
Name: {name}
Problem: {problem}
Signal: {trigger}
Notes: {notes}
{geo_context}
{FOUNDER_WEDGES_CONTEXT}

{RUBRIC}

Return ONLY this JSON (no prose, no markdown, no code block):
{json_template}"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=(
                "You are a hard-nosed business opportunity scoring analyst. Score on 16 dimensions. "
                "DISTRIBUTION RULE: 30% of scores must be <= 5 (real weaknesses), 40% in 5-7 (neutral), "
                "30% above 7 (genuine strengths). DO NOT cluster at 7-9. A new business idea has MANY weaknesses. "
                "Score 3-4 means this dimension is a real headwind. Score 8-9 means exceptional edge. "
                "Score 5 means neutral/unknown. When uncertain, score 5, not 7. "
                "Return ONLY valid JSON with exactly the fields requested."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Extract JSON object substring — handles prose before/after the object
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            raw = json_match.group(0)

        scores = json.loads(raw)

        # Write scores + reasons back to opp dict
        for dim in DIMENSIONS:
            val = scores.get(dim)
            if val is not None:
                try:
                    opp[dim] = max(1, min(10, int(val)))
                except (ValueError, TypeError):
                    pass
            reason = scores.get(f"{dim}_reason")
            if reason:
                opp[f"{dim}_reason"] = str(reason)[:200]

        opp["ai_scored_at"] = datetime.now().strftime("%Y-%m-%d")
        opp["ai_scorer_version"] = AI_SCORER_VERSION
        opp.pop("rescore_requested", None)

        logger.info("[ai_scorer] Scored: %s", name[:50])
        return opp

    except Exception as exc:
        from opportunity_os.pipeline_monitor import log_failure
        log_failure("ai_scorer.single", exc, opp_id=opp.get("id", "unknown"), recovered=True)
        return _heuristic_fallback(opp)


def _load_env_key() -> Optional[str]:
    """Try to read ANTHROPIC_API_KEY from .env file in project root."""
    root = _find_project_root()
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return key or None
    return None


def _find_project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])


def _heuristic_fallback(opp: dict) -> dict:
    """
    Simple regex-based fallback when AI scoring is unavailable.
    Produces plausible 1-10 estimates — not as differentiated as AI scoring.
    """
    text = " ".join([
        opp.get("name", ""),
        opp.get("problem_statement", ""),
        opp.get("description", ""),
        opp.get("raw_notes", ""),
        opp.get("trigger_signal", ""),
    ]).lower()
    geo = opp.get("geography", "global")
    bucket = opp.get("bucket") or opp.get("bucket_hypothesis", "")

    def has(*patterns):
        return any(bool(re.search(p, text)) for p in patterns)

    def clamp(val, lo=1, hi=10):
        return max(lo, min(hi, val))

    dims = {}

    # pain_severity — baseline 2 (not 5); must earn higher score
    pain_s = sum([
        has(r"no tool", r"no software", r"excel", r"manual", r"paper"),
        has(r"daily", r"every day", r"urgent"),
        has(r"losing money", r"costing", r"expensive"),
        geo == "venezuela",
        has(r"forum", r"complaint", r"frustrated"),
    ])
    dims["pain_severity"] = clamp(2 + pain_s)

    # market_size — baseline 3 (not 5)
    ms = 3
    if has(r"\$[0-9]+b", r"billion"): ms = 8
    elif has(r"\$[0-9]+m", r"million"): ms = 5
    if bucket == "venture_scale": ms += 1
    dims["market_size"] = clamp(ms)

    # timing_tailwind — baseline 3 (not 5)
    tt = 3
    if has(r"regulation", r"mandator", r"new law"): tt += 3
    if has(r"growing fast", r"2025", r"2026"): tt += 1
    if geo == "venezuela": tt += 1
    dims["timing_tailwind"] = clamp(tt)

    # willingness_to_pay — Venezuela baseline 2 (was 4); global baseline 3 (was 5)
    wtp_base = 2 if geo == "venezuela" else 3
    wtp_s = sum([
        has(r"pay", r"subscription", r"pricing"),
        has(r"currently paying", r"already pay"),
        has(r"\$[0-9]+/mo", r"per month"),
    ])
    dims["willingness_to_pay"] = clamp(wtp_base + wtp_s)

    # monetization_clarity — baseline 3 (not 5)
    mc = 3
    if has(r"subscription", r"saas", r"per month", r"per user"): mc += 2
    if has(r"take rate", r"commission", r"transaction fee"): mc += 3
    if bucket in ("fast_cash", "latam_asymmetry"): mc += 1
    dims["monetization_clarity"] = clamp(mc)

    # speed_to_mvp — baseline 3 (not 5)
    sm = 3
    if has(r"whatsapp", r"bot", r"zapier", r"no-code"): sm += 3
    if has(r"simple", r"lightweight", r"minimal"): sm += 1
    if bucket == "fast_cash": sm += 1
    dims["speed_to_mvp"] = clamp(sm)

    # capital_efficiency — baseline 4 (not 6)
    ce = 4
    if has(r"bootstrap", r"no inventory", r"software only"): ce += 2
    if bucket in ("fast_cash", "latam_asymmetry"): ce += 1
    dims["capital_efficiency"] = clamp(ce)

    # distribution_accessibility — baseline 3 (not 5)
    da = 3
    if has(r"whatsapp", r"community", r"referral"): da += 3
    if geo in ("venezuela", "latam"): da += 1
    dims["distribution_accessibility"] = clamp(da)

    # competition_intensity (inverted — higher = less competition = better) — baseline 4 (not 6)
    ci = 4
    if has(r"fragmented", r"no leader", r"no direct"): ci += 2
    if geo == "venezuela": ci += 2
    if bucket == "latam_asymmetry": ci += 1
    dims["competition_intensity"] = clamp(ci)

    # defensibility — baseline 3 (not 5)
    de = 3
    if has(r"data moat", r"network effect", r"switching cost"): de += 3
    if has(r"first mover", r"brand trust"): de += 1
    dims["defensibility"] = clamp(de)

    # regional_fit — baseline 3 (not 5)
    rf = 3
    if geo == "venezuela": rf += 3
    elif geo == "latam": rf += 2
    if bucket == "latam_asymmetry": rf += 1
    if has(r"usdt", r"bolivar", r"zelle", r"informal"): rf += 1
    dims["regional_fit"] = clamp(rf)

    # founder_fit — stays formula-based (4 + wedges); min 4 is intentional
    ff = 4
    if has(r"growth", r"crm", r"lifecycle", r"a/b", r"paid ads"): ff += 1
    if has(r"latam", r"venezuela", r"spain", r"spanish"): ff += 1
    if has(r"fintech", r"crypto", r"usdt", r"payment"): ff += 1
    if has(r"whatsapp", r"referral", r"distribution"): ff += 1
    dims["founder_fit"] = clamp(ff)

    # ai_leverage — baseline 3 (not 5)
    al = 3
    if has(r"ai", r"automation", r"machine learning", r"nlp"): al += 3
    if has(r"manual", r"human in the loop"): al += 1
    dims["ai_leverage"] = clamp(al)

    # operational_simplicity — baseline 4 (not 6)
    os_score = 4
    if has(r"async", r"automated", r"self-service"): os_score += 2
    if has(r"physical", r"local team", r"warehouse"): os_score -= 2
    dims["operational_simplicity"] = clamp(os_score)

    # regulatory_simplicity — baseline 4 (not 6)
    rs = 4
    if geo in ("venezuela", "latam") and bucket == "latam_asymmetry": rs += 2
    if has(r"fintech", r"banking", r"insurance", r"securities"): rs -= 2
    if has(r"license", r"regulated", r"compliance"): rs -= 1
    dims["regulatory_simplicity"] = clamp(rs)

    # revenue_speed_score — baseline 3 (not 5)
    pr = 3
    if has(r"service", r"consulting", r"done for you"): pr += 2
    if has(r"whatsapp", r"direct outreach"): pr += 1
    if bucket == "fast_cash": pr += 2
    if geo == "venezuela": pr += 1
    dims["revenue_speed_score"] = clamp(pr)

    result = dict(opp)
    for k, v in dims.items():
        if result.get(k) is None:
            result[k] = v

    return result
