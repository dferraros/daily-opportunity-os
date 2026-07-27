"""
Revenue Evidence Engine -- competitor funding, ARR, and pricing for TAM validation.

Searches for public evidence of competitor funding rounds and ARR, then scrapes
pricing pages to extract annual pricing points. Never fabricates: missing keys,
no competitors, empty searches, or failed scrapes all leave the opportunity
unchanged and log loudly.

Methods:
  search_funding_evidence(opp) -> dict: Tavily search for competitor funding/ARR
  scrape_pricing_evidence(opp) -> dict: Tavily + Firecrawl for pricing pages
  run_revenue_evidence(opp) -> dict: Orchestrator with 30-day skip guard
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from opportunity_os import tavily_client

logger = logging.getLogger(__name__)

REVENUE_EVIDENCE_TTL_DAYS = 30
MAX_COMPETITORS = 2  # cost cap: Tavily credits scale with competitor count
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

FUNDING_EXTRACTION_SYSTEM_PROMPT = (
    "Extract funding and revenue data from the search results. Be conservative: "
    "only report numbers you can cite directly from the text. Never estimate or "
    "calculate implied values. Focus on: announced funding rounds (Series A/B/C, "
    "seed), total funding raised, and any publicly disclosed ARR/revenue figures. "
    "Return ONLY valid JSON."
)

PRICING_EXTRACTION_SYSTEM_PROMPT = (
    "Extract pricing information from the webpage. Be precise: report the actual "
    "pricing model and annual/monthly costs observed. If multiple tiers exist, "
    "report the mid-market or most common tier. Estimate an annual USD price based "
    "on the observed pricing structure. Never fabricate prices. Return ONLY valid JSON."
)


def _is_fresh(opp: dict) -> bool:
    """True if opp was researched within TTL."""
    stamp = opp.get("revenue_evidence_at")
    if not stamp:
        return False
    try:
        return datetime.fromisoformat(stamp) > datetime.now() - timedelta(days=REVENUE_EVIDENCE_TTL_DAYS)
    except ValueError:
        return False


def _build_funding_queries(opp: dict) -> list[str]:
    """Build Tavily queries for competitor funding/ARR evidence.

    Falls back to a category query when no competitors are named.
    """
    competitors = [c for c in (opp.get("direct_competitors") or []) if c][:MAX_COMPETITORS]
    if competitors:
        return [
            f'"{c}" funding OR "Series A" OR "Series B" OR ARR OR "revenue" '
            f'site:techcrunch.com OR site:crunchbase.com OR site:contxto.com OR site:latamlist.com'
            for c in competitors
        ]
    # Fallback: category-level search
    vertical = (opp.get("vertical") or "").replace("_", " ")
    geography = (opp.get("geography") or "global").replace("_", " ")
    if vertical:
        return [f'{vertical} {geography} startup funding OR ARR site:techcrunch.com OR site:crunchbase.com']
    return []


def _parse_funding_extraction(raw: str) -> Optional[dict]:
    """Parse the Haiku JSON extraction; None on malformation."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    # Safely extract fields — only report if evidence-backed
    funding_raised = data.get("competitor_funding_raised")
    arr_usd = data.get("competitor_arr_usd")

    # Clamp ARR to a reasonable range if present (drop obviously fake values)
    if arr_usd is not None:
        try:
            arr_f = float(arr_usd)
            if arr_f <= 0 or arr_f > 1_000_000_000:  # 0 < ARR < $1B
                arr_usd = None
            else:
                arr_usd = round(arr_f, 2)
        except (TypeError, ValueError):
            arr_usd = None

    return {
        "competitor_funding_raised": funding_raised,
        "competitor_arr_usd": arr_usd,
    }


def _extract_funding(opp: dict, digest: str) -> Optional[dict]:
    """Haiku extraction over the funding digest. None on missing key / API failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from opportunity_os.ai_scorer import _load_env_key
        api_key = _load_env_key()
    if not api_key:
        logger.error("[revenue_evidence] No ANTHROPIC_API_KEY -- skipping %s", opp.get("name", "?")[:50])
        return None

    competitors = ", ".join((opp.get("direct_competitors") or [])[:MAX_COMPETITORS]) or opp.get("vertical", "")
    prompt = (
        f"Competitors: {competitors}\n"
        f"Opportunity: {opp.get('name', '')}\n\n"
        f"SEARCH RESULTS:\n{digest[:5000]}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "competitor_funding_raised": "<e.g. \'$50M Series B\' or null if not found>",\n'
        '  "competitor_arr_usd": <numeric ARR in USD or null if not found>\n'
        "}"
    )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=FUNDING_EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = _parse_funding_extraction(response.content[0].text)
        if parsed is None:
            logger.error("[revenue_evidence] Unparseable funding response for %s", opp.get("name", "?")[:50])
        return parsed
    except Exception as exc:  # noqa: BLE001
        logger.error("[revenue_evidence] API call failed for %s: %s", opp.get("name", "?")[:50], exc)
        return None


def search_funding_evidence(opp: dict, force: bool = False) -> dict:
    """Search for competitor funding and ARR evidence.

    Returns a dict with keys:
      competitor_funding_raised (str|None), competitor_arr_usd (float|None),
      revenue_evidence_sources (list of {url, claim})

    Returns {} (and logs) if fresh within TTL, Tavily unavailable, no
    competitors/vertical, empty searches, or extraction failure.
    """
    name = opp.get("name", "?")[:50]

    if _is_fresh(opp) and not force:
        logger.info("[revenue_evidence] %s fresh within %dd TTL -- skipping", name, REVENUE_EVIDENCE_TTL_DAYS)
        return {}

    if not tavily_client.is_available():
        logger.error("[revenue_evidence] Tavily unavailable -- cannot search funding for %s", name)
        return {}

    queries = _build_funding_queries(opp)
    if not queries:
        logger.warning("[revenue_evidence] No competitors or vertical for %s -- nothing to search", name)
        return {}

    snippets: list[dict] = []
    for q in queries:
        results = tavily_client.search_with_content(q, max_results=3) or []
        for r in results:
            text = (r.get("raw_content") or r.get("content") or "").strip()
            if text:
                snippets.append({
                    "url": r.get("url", ""),
                    "text": text[:2000],
                })

    if not snippets:
        logger.warning("[revenue_evidence] Funding searches returned nothing for %s", name)
        return {}

    # Join snippets for extraction
    digest = "\n---\n".join(s["text"] for s in snippets)
    extracted = _extract_funding(opp, digest)
    if extracted is None:
        return {}

    # Build sources list
    sources = []
    if extracted.get("competitor_funding_raised") or extracted.get("competitor_arr_usd"):
        for s in snippets[:3]:  # cite top 3 results
            sources.append({
                "url": s["url"],
                "claim": "funding/ARR evidence",
                "date": datetime.now().isoformat(),
            })

    updates = {
        "competitor_funding_raised": extracted.get("competitor_funding_raised"),
        "competitor_arr_usd": extracted.get("competitor_arr_usd"),
        "revenue_evidence_sources": sources or None,
    }

    if extracted.get("competitor_arr_usd"):
        logger.info(
            "[revenue_evidence] %s -> ARR $%.0fK from funding search",
            name, (extracted.get("competitor_arr_usd") or 0) / 1000,
        )
    else:
        logger.info("[revenue_evidence] %s -> no ARR found in funding search", name)

    return updates


def _build_pricing_queries(opp: dict) -> list[str]:
    """Build queries to find competitor pricing pages.

    No site: filter — the pricing page lives on the competitor's OWN site,
    which a site: allowlist of news/forum domains would exclude.
    """
    competitors = [c for c in (opp.get("direct_competitors") or []) if c][:MAX_COMPETITORS]
    if competitors:
        return [f'"{c}" pricing plans price per month' for c in competitors]
    return []


def _parse_pricing_extraction(raw: str) -> Optional[dict]:
    """Parse pricing extraction JSON; None on malformation."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    pricing_model = data.get("competitor_pricing_model")
    annual_price = data.get("tam_annual_price_usd")

    # Clamp annual price to reasonable range
    if annual_price is not None:
        try:
            annual_f = float(annual_price)
            if annual_f <= 0 or annual_f > 10_000_000:  # $0 < price < $10M/year
                annual_price = None
            else:
                annual_price = round(annual_f, 2)
        except (TypeError, ValueError):
            annual_price = None

    return {
        "competitor_pricing_model": pricing_model,
        "tam_annual_price_usd": annual_price,
    }


def _extract_pricing(opp: dict, digest: str) -> Optional[dict]:
    """Haiku extraction over pricing page content."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from opportunity_os.ai_scorer import _load_env_key
        api_key = _load_env_key()
    if not api_key:
        logger.error("[revenue_evidence] No ANTHROPIC_API_KEY -- skipping pricing extraction for %s", opp.get("name", "?")[:50])
        return None

    competitors = ", ".join((opp.get("direct_competitors") or [])[:MAX_COMPETITORS]) or opp.get("vertical", "")
    prompt = (
        f"Competitors: {competitors}\n"
        f"Opportunity: {opp.get('name', '')}\n\n"
        f"PRICING PAGE CONTENT:\n{digest[:5000]}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "competitor_pricing_model": "<e.g. \'SaaS $29-99/mo per location\' or null>",\n'
        '  "tam_annual_price_usd": <inferred annual USD price or null>\n'
        "}"
    )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=PRICING_EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = _parse_pricing_extraction(response.content[0].text)
        if parsed is None:
            logger.error("[revenue_evidence] Unparseable pricing response for %s", opp.get("name", "?")[:50])
        return parsed
    except Exception as exc:  # noqa: BLE001
        logger.error("[revenue_evidence] Pricing extraction failed for %s: %s", opp.get("name", "?")[:50], exc)
        return None


def scrape_pricing_evidence(opp: dict, force: bool = False) -> dict:
    """Search for and scrape competitor pricing pages.

    Returns dict with:
      competitor_pricing_model (str|None), tam_annual_price_usd (float|None)

    Gracefully handles missing Tavily/Firecrawl keys, empty searches.
    """
    name = opp.get("name", "?")[:50]

    # Skip if we already have pricing evidence (piggyback on funding TTL)
    if _is_fresh(opp) and not force:
        return {}

    if not tavily_client.is_available():
        logger.warning("[revenue_evidence] Tavily unavailable -- cannot search pricing for %s", name)
        return {}

    queries = _build_pricing_queries(opp)
    if not queries:
        logger.warning("[revenue_evidence] No competitors for pricing search in %s", name)
        return {}

    snippets: list[str] = []
    source_urls: list[str] = []
    for q in queries:
        results = tavily_client.search_with_content(q, max_results=2) or []
        for r in results:
            text = (r.get("raw_content") or r.get("content") or "").strip()
            if text:
                snippets.append(text[:2000])
                if r.get("url"):
                    source_urls.append(r["url"])

    if not snippets:
        logger.warning("[revenue_evidence] Pricing searches returned nothing for %s", name)
        return {}

    # Firecrawl pass on the top result: the search snippet often truncates the
    # pricing table; a structured scrape of the actual page beats snippets.
    # Graceful no-op without a FIRECRAWL key (scrape_structured returns None).
    if source_urls:
        from opportunity_os import firecrawl_client
        scraped = firecrawl_client.scrape_structured(
            source_urls[0],
            {
                "type": "object",
                "properties": {
                    "pricing_tiers": {"type": "string"},
                    "monthly_price_usd": {"type": "number"},
                },
            },
        )
        if scraped:
            snippets.insert(0, json.dumps(scraped)[:2000])

    digest = "\n---\n".join(snippets)
    extracted = _extract_pricing(opp, digest)
    if extracted is None:
        return {}

    pricing_sources = []
    if extracted.get("competitor_pricing_model") or extracted.get("tam_annual_price_usd"):
        pricing_sources = [
            {"url": u, "claim": "pricing evidence", "date": datetime.now().isoformat()}
            for u in source_urls[:3]
        ]

    updates = {
        "competitor_pricing_model": extracted.get("competitor_pricing_model"),
        "tam_annual_price_usd": extracted.get("tam_annual_price_usd"),
        "pricing_evidence_sources": pricing_sources,
    }

    if extracted.get("tam_annual_price_usd"):
        logger.info(
            "[revenue_evidence] %s -> annual price $%.0f detected",
            name, extracted.get("tam_annual_price_usd"),
        )
    else:
        logger.info("[revenue_evidence] %s -> pricing model: %s", name, updates["competitor_pricing_model"] or "not extracted")

    return updates


def run_revenue_evidence(opp: dict, force: bool = False) -> dict:
    """Orchestrate funding + pricing evidence search and extraction.

    Returns the opportunity dict enriched with:
      competitor_funding_raised, competitor_arr_usd, competitor_pricing_model,
      tam_annual_price_usd, revenue_evidence_sources, revenue_evidence_at,
      tam_validation_note

    Returns opp unchanged (and logs) if fresh within TTL, keys missing, or all
    searches/extractions fail. Never fabricates data.
    """
    name = opp.get("name", "?")[:50]

    if _is_fresh(opp) and not force:
        logger.info("[revenue_evidence] %s fresh within %dd -- skipping", name, REVENUE_EVIDENCE_TTL_DAYS)
        return opp

    # Search funding evidence
    funding = search_funding_evidence(opp, force=force)

    # Search pricing evidence
    pricing = scrape_pricing_evidence(opp, force=force)

    # If nothing was found, return unchanged
    if not funding and not pricing:
        logger.warning("[revenue_evidence] No revenue evidence found for %s", name)
        return opp

    # Merge results. Citations from BOTH paths land in revenue_evidence_sources:
    # a tam_annual_price_usd feeding the TAM engine without a source trail would
    # violate the no-uncited-claims rule.
    pricing = dict(pricing)
    pricing_sources = pricing.pop("pricing_evidence_sources", []) or []
    combined_sources = (funding.get("revenue_evidence_sources") or []) + pricing_sources
    updates = {
        **funding,
        **pricing,
        "revenue_evidence_sources": combined_sources or None,
        "revenue_evidence_at": datetime.now().isoformat(),
    }

    # Build validation note comparing competitor ARR to existing TAM estimate
    if funding.get("competitor_arr_usd") and opp.get("tam_usd_estimate"):
        comp_arr = funding.get("competitor_arr_usd")
        tam_estimate = opp.get("tam_usd_estimate")
        # Assume competitor has ~5% market share
        implied_tam = (comp_arr / 0.05) if comp_arr > 0 else None
        if implied_tam:
            variance_pct = abs(implied_tam - tam_estimate) / tam_estimate * 100 if tam_estimate > 0 else 0
            updates["tam_validation_note"] = (
                f"Competitor ARR ${comp_arr:.0f} implies TAM of ${implied_tam:.0f} "
                f"(vs. estimated ${tam_estimate:.0f}, variance {variance_pct:.0f}%)"
            )

    enriched = {**opp, **updates}
    logger.info("[revenue_evidence] %s enriched with revenue evidence", name)
    return enriched
