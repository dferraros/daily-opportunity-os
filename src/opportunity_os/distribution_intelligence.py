"""
Distribution Intelligence — maps distribution reality for each opportunity.
Answers: where does the buyer spend attention? What does CAC look like?
What is the first 10 customer path? What trust mechanism is needed?

Used by: distribution-intelligence-agent, distribution-mapper skill, daily_run.py steps 10-13

This module does NOT run outreach at runtime. It provides:
  1. CHANNEL_MAP_BY_GEO         — channels ranked by effectiveness per geography
  2. TRUST_MECHANISMS_BY_GEO    — trust-building actions by geography
  3. CAC_BENCHMARKS_BY_CHANNEL  — CPL, conversion rate, and approx CAC per channel
  4. build_distribution_queries() — generates 5-7 targeted queries for distribution research
  5. get_recommended_channels()   — returns top 3 channels for this opportunity
  6. estimate_cac()               — looks up CAC benchmark for a channel + geography pair
  7. run_distribution_intelligence() — returns a structured template for the agent to fill in

Real distribution research is performed by the distribution-intelligence-agent at runtime
using WebSearch/WebFetch tools.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from typing import Optional

MODEL = "claude-haiku-4-5-20251001"


# ─── Channel Map by Geography ─────────────────────────────────────────────────
# Channels ranked by effectiveness (highest first) for each geography.
# Primary = highest trust + lowest CAC for that market.

CHANNEL_MAP_BY_GEO: dict[str, list[str]] = {
    "venezuela": [
        "WhatsApp cold outreach (primary — referral-based)",
        "TikTok organic (secondary — short-form demo content)",
        "Instagram DM (tertiary — visual products)",
        "Telegram groups (community building)",
        "Facebook grupos de emprendedores venezolanos",
    ],
    "colombia": [
        "WhatsApp Business (primary)",
        "LinkedIn (B2B, Bogotá/Medellín)",
        "Instagram (consumer + SMB)",
        "Facebook grupos de negocios Colombia",
        "Cold email (B2B, formal sector)",
    ],
    "mexico": [
        "WhatsApp (primary)",
        "Facebook (mass market)",
        "LinkedIn (B2B CDMX/Monterrey)",
        "TikTok organic (younger SMBs)",
        "Mercado Libre seller communities",
    ],
    "latam": [
        "WhatsApp (universal primary)",
        "LinkedIn (B2B)",
        "Facebook groups (SMB communities)",
        "Content/SEO (Spanish-language organic)",
        "Performance marketing (Meta/Google)",
    ],
    "spain": [
        "LinkedIn (B2B primary)",
        "Google Ads (high intent)",
        "Cold email (B2B)",
        "Content marketing / SEO",
        "Twitter/X (tech-savvy SMBs)",
    ],
    "global": [
        "Content marketing / SEO",
        "Product Hunt",
        "LinkedIn",
        "Cold email",
        "Performance marketing",
    ],
}


# ─── Trust Mechanisms by Geography ───────────────────────────────────────────
# Ordered by trust signal strength (highest first) for each geography.
# Trust mechanism is MANDATORY output for LATAM/VE — no buyer pays without one.

TRUST_MECHANISMS_BY_GEO: dict[str, list[str]] = {
    "venezuela": [
        "WhatsApp referral from known contact (strongest signal)",
        "Video testimonial from recognizable Venezuelan entrepreneur",
        "Free trial with no card required",
        "Visible pricing in USD (not bolivares)",
        "Active WhatsApp support group",
    ],
    "colombia": [
        "Case studies from Colombian companies",
        "LinkedIn social proof",
        "Free trial",
        "Local phone support",
    ],
    "mexico": [
        "Case studies from Mexican SMBs",
        "WhatsApp support + referral program",
        "Free trial",
        "Local phone number",
    ],
    "latam": [
        "Spanish-language content",
        "Regional pricing",
        "WhatsApp support",
        "Referral program",
    ],
    "spain": [
        "EU compliance signals",
        "Spanish company registration visible",
        "Case studies",
        "Free trial",
    ],
    "global": [
        "Free trial",
        "Social proof (G2/Trustpilot)",
        "Case studies",
        "Content marketing",
    ],
}


# ─── CAC Benchmarks by Channel ────────────────────────────────────────────────
# Estimated from LATAM/VE market reality (not US benchmarks).
# cpl_usd = cost per lead | conversion_rate = lead→customer | approx_cac_usd = total CAC
# Referral and organic channels have $0 CPL but require time investment.

CAC_BENCHMARKS_BY_CHANNEL: dict[str, dict] = {
    "whatsapp_cold_ve": {
        "cpl_usd": 1.5,
        "conversion_rate": 0.12,
        "approx_cac_usd": 12,
        "notes": "Cold outreach to VE WhatsApp groups. High effort, low cash cost.",
    },
    "whatsapp_referral_ve": {
        "cpl_usd": 0,
        "conversion_rate": 0.35,
        "approx_cac_usd": 0,
        "notes": "Referral from existing VE customer. Best channel — zero CPL, high trust.",
    },
    "tiktok_organic_latam": {
        "cpl_usd": 0,
        "conversion_rate": 0.03,
        "approx_cac_usd": 0,
        "notes": "Organic TikTok for LATAM. Low conversion but zero cash cost. Scales with content volume.",
    },
    "facebook_groups_latam": {
        "cpl_usd": 2,
        "conversion_rate": 0.08,
        "approx_cac_usd": 25,
        "notes": "Facebook SMB/entrepreneur groups in LATAM. Low CPL, moderate conversion.",
    },
    "linkedin_b2b_latam": {
        "cpl_usd": 15,
        "conversion_rate": 0.15,
        "approx_cac_usd": 100,
        "notes": "LinkedIn B2B for LATAM formal sector. Higher CAC but better LTV.",
    },
    "google_ads_spain": {
        "cpl_usd": 8,
        "conversion_rate": 0.12,
        "approx_cac_usd": 67,
        "notes": "Google Ads Spain — high intent, higher CPL than LATAM.",
    },
    "cold_email_b2b": {
        "cpl_usd": 1,
        "conversion_rate": 0.05,
        "approx_cac_usd": 20,
        "notes": "Cold email B2B outreach. Low CPL but requires list building and deliverability.",
    },
    "content_seo_organic": {
        "cpl_usd": 0,
        "conversion_rate": 0.02,
        "approx_cac_usd": 0,
        "notes": "SEO/content organic. Zero cash cost but 3-6 month lag. Best for long-term compounding.",
    },
    "instagram_dm_ve": {
        "cpl_usd": 1,
        "conversion_rate": 0.10,
        "approx_cac_usd": 10,
        "notes": "Instagram DM for visual products in Venezuela. Low CPL, moderate trust.",
    },
    "telegram_groups_ve": {
        "cpl_usd": 0,
        "conversion_rate": 0.06,
        "approx_cac_usd": 0,
        "notes": "Telegram community building. Zero CPL, slow to build trust.",
    },
    "meta_ads_latam": {
        "cpl_usd": 3,
        "conversion_rate": 0.08,
        "approx_cac_usd": 37,
        "notes": "Meta/Facebook paid ads LATAM. Moderate CPL. Works for visual B2C products.",
    },
    "product_hunt_global": {
        "cpl_usd": 0,
        "conversion_rate": 0.05,
        "approx_cac_usd": 0,
        "notes": "Product Hunt launch. Zero CPL. One-time spike. Works for dev/SaaS tools.",
    },
}


# ─── Query Builder ────────────────────────────────────────────────────────────

def build_distribution_queries(opp: dict) -> list[str]:
    """
    Generate 5-7 targeted search queries to research distribution for this opportunity.

    Priority order:
      1. Vertical + geography distribution channels
      2. Competitor marketing strategy
      3. Where buyers gather (in their own language)
      4. CAC benchmarks for this vertical
      5. Specific geo distribution patterns (WhatsApp, TikTok, etc.)
      6. Organic demand signal for this vertical

    Returns a deduplicated list of 5-7 queries.
    """
    queries: list[str] = []

    vertical = opp.get("vertical") or ""
    geography = opp.get("geography") or "latam"
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()

    # 1. General distribution channels for this vertical + geography
    if vertical:
        queries.append(f"{vertical} marketing channels {geo_label}")
        queries.append(f"cómo conseguir clientes {vertical} {geo_label.lower()}")

    # 2. Competitor distribution — where are they spending?
    competitors = opp.get("direct_competitors") or []
    if competitors:
        top_competitor = competitors[0]
        queries.append(f"{top_competitor} marketing strategy distribution channels")
    else:
        # Fallback: generic competitor channel query
        queries.append(f"distribution {vertical} LATAM competitors")

    # 3. Where do these buyers gather online?
    customer = opp.get("target_customer") or ""
    if customer:
        short_customer = " ".join(customer.split()[:4])
        if geography == "venezuela":
            queries.append(f"donde se reúnen {short_customer} Venezuela online")
        else:
            queries.append(f"donde se reúnen {short_customer} {geo_label.lower()} online")

    # 4. CAC benchmarks for this vertical
    if vertical:
        queries.append(f"customer acquisition cost {vertical} LATAM benchmark")

    # 5. WhatsApp / TikTok distribution (always check for VE/LATAM)
    if geography in ("venezuela", "latam", "colombia", "mexico"):
        if vertical:
            queries.append(f"WhatsApp marketing {vertical} {geo_label.lower()} estrategia")

    # 6. Organic demand signal
    problem = opp.get("problem_statement") or ""
    if problem:
        core_words = " ".join(problem.split()[:5])
        queries.append(f"{core_words} {geo_label.lower()} solución")

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            deduped.append(q)

    # Return 5-7 queries
    return deduped[:7] if len(deduped) >= 5 else deduped


# ─── Channel Recommender ──────────────────────────────────────────────────────

def get_recommended_channels(opp: dict) -> list[str]:
    """
    Return top 3 channel keys from CAC_BENCHMARKS_BY_CHANNEL for this opportunity,
    based on geography and business_model_type.

    Logic:
    - VE geography → always start with whatsapp_cold_ve or whatsapp_referral_ve
    - LATAM → whatsapp + facebook_groups_latam as defaults
    - Spain → linkedin_b2b_latam + google_ads_spain
    - B2B business models → prioritize linkedin, cold_email
    - B2C / consumer → prioritize whatsapp, instagram, tiktok
    - Organic preference: referral > organic > paid (per CLAUDE.md VE rules)

    Returns list of 3 channel key strings (keys from CAC_BENCHMARKS_BY_CHANNEL).
    """
    geography = (opp.get("geography") or "latam").lower()
    business_model = (opp.get("business_model_type") or "").lower()

    b2b_models = {"saas", "b2b_software", "infrastructure", "data_as_a_service", "agency_plus_software"}
    b2c_models = {"consumer_app", "marketplace", "productized_service", "concierge_first", "done_for_you"}

    is_b2b = business_model in b2b_models
    is_b2c = business_model in b2c_models

    if geography == "venezuela":
        if is_b2b:
            return ["whatsapp_referral_ve", "whatsapp_cold_ve", "telegram_groups_ve"]
        return ["whatsapp_referral_ve", "whatsapp_cold_ve", "instagram_dm_ve"]

    if geography in ("colombia", "mexico"):
        if is_b2b:
            return ["whatsapp_cold_ve", "linkedin_b2b_latam", "cold_email_b2b"]
        return ["whatsapp_cold_ve", "facebook_groups_latam", "tiktok_organic_latam"]

    if geography == "latam":
        if is_b2b:
            return ["linkedin_b2b_latam", "cold_email_b2b", "whatsapp_cold_ve"]
        return ["whatsapp_cold_ve", "facebook_groups_latam", "tiktok_organic_latam"]

    if geography == "spain":
        if is_b2b:
            return ["linkedin_b2b_latam", "google_ads_spain", "cold_email_b2b"]
        return ["google_ads_spain", "content_seo_organic", "meta_ads_latam"]

    # Global fallback
    if is_b2b:
        return ["cold_email_b2b", "linkedin_b2b_latam", "content_seo_organic"]
    return ["content_seo_organic", "product_hunt_global", "meta_ads_latam"]


# ─── CAC Estimator ────────────────────────────────────────────────────────────

def estimate_cac(channel: str, geography: str) -> dict:
    """
    Look up CAC benchmark for a given channel key and geography.

    Returns the benchmark dict from CAC_BENCHMARKS_BY_CHANNEL if found,
    or a default dict with None values if the channel key is not in the table.

    Note: geography is used for context (e.g., VE channels are cheaper than Spain)
    but the primary lookup is by channel key.
    """
    benchmark = CAC_BENCHMARKS_BY_CHANNEL.get(channel)
    if benchmark:
        return {**benchmark, "channel": channel, "geography": geography}

    # Fallback: return empty benchmark with channel + geo metadata
    return {
        "channel": channel,
        "geography": geography,
        "cpl_usd": None,
        "conversion_rate": None,
        "approx_cac_usd": None,
        "notes": "No benchmark available — requires manual research for this channel.",
    }


# ─── Distribution Intelligence Runner ────────────────────────────────────────

def run_distribution_intelligence(opp: dict) -> dict:
    """
    Build the distribution intelligence template for the given opportunity.

    This function does NOT run outreach or web searches. It returns a structured
    template dict that the distribution-intelligence-agent fills in with real
    market signal at runtime.

    Returns a dict with all distribution validation fields (all Optional).
    Fields are None until populated by the agent:
      - distribution_validated: bool
      - top_distribution_channels: list[str]   (top 3 channels)
      - estimated_cac_logic: str               (e.g. "WhatsApp cold ~$1.5 CPL, 12% conv = ~$12 CAC")
      - first_10_customer_path: str            (step-by-step specific path)
      - trust_mechanism_latam: str             (how to earn trust in this market)
      - distribution_validated_date: str       (ISO date string, today)

    Also includes helper fields for the agent (prefixed with _ to distinguish):
      - _distribution_queries: list[str]       (queries to execute via WebSearch)
      - _recommended_channels: list[str]       (channel keys to evaluate)
      - _cac_benchmarks: dict                  (benchmarks for each recommended channel)
    """
    recommended_channels = get_recommended_channels(opp)
    geography = opp.get("geography") or "latam"
    trust_options = TRUST_MECHANISMS_BY_GEO.get(geography, TRUST_MECHANISMS_BY_GEO["global"])

    template: dict = {
        # Schema fields — populated by distribution-intelligence-agent
        "distribution_validated": None,
        "top_distribution_channels": recommended_channels,
        "estimated_cac_logic": None,
        "first_10_customer_path": None,
        "trust_mechanism_latam": trust_options[:2],
        "distribution_validated_date": None,

        # Agent helper fields
        "_distribution_queries": build_distribution_queries(opp),
        "_recommended_channels": recommended_channels,
        "_cac_benchmarks": {
            ch: CAC_BENCHMARKS_BY_CHANNEL.get(ch, {})
            for ch in recommended_channels
        },
        "_opportunity_id": opp.get("id"),
        "_opportunity_name": opp.get("name"),
        "_vertical": opp.get("vertical"),
        "_geography": geography,
        "_business_model_type": opp.get("business_model_type"),
        "_channel_map": CHANNEL_MAP_BY_GEO.get(geography, CHANNEL_MAP_BY_GEO["global"]),
    }

    return template


# ─── Distribution Executor (Tavily-powered) ──────────────────────────────────

def run_distribution_executor(opp: dict) -> dict:
    """
    Run dedicated distribution research using Tavily + Claude.

    Separate from run_research_executor (which focuses on pain+dist combined).
    This pass uses distribution-specific queries for sharper channel evidence.

    Returns dict with updated distribution fields, or empty dict if unavailable.
    Fields populated: distribution_validated, top_distribution_channels,
    estimated_cac_logic, first_10_customer_path, trust_mechanism_latam,
    distribution_validated_date
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_api_key()
    if not api_key:
        return {}

    template = run_distribution_intelligence(opp)
    queries = template.get("_distribution_queries") or []
    if not queries:
        return {}

    # Step 1: Tavily search with distribution-specific queries
    # max_results_per_query=2 keeps cost at ~$0.008 vs $0.016 for 4 results
    tavily_context = ""
    try:
        from opportunity_os import tavily_client
        if tavily_client.is_available():
            tavily_context = tavily_client.search_multi(queries[:3], max_results_per_query=2)
    except Exception:
        pass

    if not tavily_context:
        return {}

    # Step 2: Claude extracts distribution fields from Tavily results
    geo = opp.get("geography", "latam")
    geo_label = "Venezuela" if geo == "venezuela" else geo.upper()
    channels = template.get("_recommended_channels", [])
    benchmarks = template.get("_cac_benchmarks", {})
    channel_info = "; ".join(
        f"{ch}: ~${benchmarks.get(ch, {}).get('approx_cac_usd', '?')} CAC"
        for ch in channels
    )

    prompt = f"""You are analyzing distribution channels for a business opportunity in {geo_label}.

Opportunity: {opp.get("name", "")}
Vertical: {opp.get("vertical", "")}
Target customer: {opp.get("target_customer", "")}
Recommended channels: {channel_info}

RESEARCH RESULTS:
{tavily_context[:3000]}

Extract and return ONLY this JSON (no prose, no code block):
{{
  "distribution_validated": <true if research confirms at least 1 viable channel, else false>,
  "top_distribution_channels": [<up to 3 channels with evidence from the research>],
  "estimated_cac_logic": "<primary channel + realistic CAC estimate based on research, 1 sentence>",
  "first_10_customer_path": "<concrete step-by-step path to first 10 customers in {geo_label}, 2-3 sentences>",
  "trust_mechanism_latam": "<primary trust signal needed to convert first buyer in {geo_label}>"
}}"""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip() if response.content else ""
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {}
        data = json.loads(match.group())
    except Exception:
        return {}

    result = {"distribution_validated_date": datetime.now().date().isoformat()}

    for field, cast in [
        ("distribution_validated", bool),
        ("estimated_cac_logic", lambda v: str(v)[:300]),
        ("first_10_customer_path", lambda v: str(v)[:500]),
        ("trust_mechanism_latam", lambda v: str(v)[:300]),
    ]:
        val = data.get(field)
        if val is not None:
            try:
                result[field] = cast(val)
            except (ValueError, TypeError):
                pass

    channels_out = data.get("top_distribution_channels")
    if isinstance(channels_out, list):
        result["top_distribution_channels"] = [str(x)[:100] for x in channels_out[:3] if x]

    return result


def _load_api_key() -> Optional[str]:
    """Load ANTHROPIC_API_KEY from .env file."""
    from pathlib import Path
    for parent in [Path(__file__).resolve().parent] + list(Path(__file__).resolve().parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
            break
    return None


# ─── Convenience Helpers ──────────────────────────────────────────────────────

def is_distribution_validated(opp: dict) -> bool:
    """Return True if this opportunity has been distribution-validated by the agent."""
    return bool(opp.get("distribution_validated"))


def has_distribution_risk(opp: dict, monthly_price_usd: float) -> bool:
    """
    Return True if estimated CAC exceeds 3x the monthly price point.
    Used as a promotion blocker — do not promote to validation if True.

    monthly_price_usd: expected monthly revenue per customer.
    """
    cac_logic = opp.get("estimated_cac_logic") or ""
    # Extract numeric CAC from logic string if possible (e.g. "~$13 CAC")
    import re
    match = re.search(r"~?\$?(\d+(?:\.\d+)?)\s*CAC", cac_logic, re.IGNORECASE)
    if match:
        estimated_cac = float(match.group(1))
        return estimated_cac > (monthly_price_usd * 3)
    return False  # Cannot determine — do not block without evidence


def distribution_ease_label(score: Optional[float]) -> str:
    """Human-readable label for a distribution_ease score (0-10)."""
    if score is None:
        return "unscored"
    if score >= 9:
        return "clear cheap channel — buyer reachable in < 2 weeks"
    if score >= 7:
        return "reachable with effort — 2-4 weeks to first customer"
    if score >= 5:
        return "unclear — channel exists but conversion unproven"
    return "distribution risk — no clear path to first customer"
