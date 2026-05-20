"""
Research Executor — validates pain and distribution fields for each opportunity.

Search strategy (in priority order):
1. Tavily API  — primary, structured results, ~$0.004/search
2. Firecrawl   — Reddit/forum crawl for exact customer phrases
3. Anthropic web_search_20250305 — fallback if Tavily unavailable

Follows ai_scorer.py patterns exactly:
- _load_env_key() and _find_project_root() helpers
- Falls back gracefully (returns opp unchanged) if API unavailable or call fails
- Writes research_executed_at timestamp on success

Input: opp dict (optionally pre-enriched by pain_intelligence + distribution_intelligence)
Output: opp dict with these fields populated:
  Pain: pain_validation_score, exact_customer_phrases, pain_evidence_sources, workarounds_found
  Distribution: distribution_validated, top_distribution_channels, estimated_cac_logic,
                first_10_customer_path, trust_mechanism_latam
  Meta: research_executed_at
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

from opportunity_os.pipeline_monitor import log_failure

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
MAX_SEARCH_USES = 1  # fallback: 1 search per call — web_search is $10/1000 searches


def run_research_executor(opp: dict) -> dict:
    """
    Execute web research for pain + distribution validation on one opportunity.
    Returns opp dict with populated research fields (or unchanged if API unavailable).
    """
    if opp.get("research_executed_at"):
        return opp  # Skip already-researched opps

    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_env_key()
    if not api_key:
        logger.debug("[research_executor] No API key — skipping: %s", opp.get("name", "?")[:50])
        return opp

    name = opp.get("name", "unknown")

    # Step 1: Tavily search (primary — structured results, cheap)
    tavily_context = ""
    try:
        from opportunity_os import tavily_client
        if tavily_client.is_available():
            pain_queries = opp.get("_pain_queries") or []
            dist_queries = opp.get("_distribution_queries") or []
            all_queries = (pain_queries + dist_queries)[:3]
            if not all_queries:
                geo_label = "Venezuela" if opp.get("geography") == "venezuela" else (opp.get("geography") or "LATAM").upper()
                all_queries = [
                    f"{name} {geo_label} customers complaints demand",
                    f"{opp.get('vertical', '')} distribution channels {geo_label}",
                ]
            # 3 results/query → ~$0.012 Tavily cost (better context depth, was 2 at $0.008)
            tavily_context = tavily_client.search_multi(all_queries, max_results_per_query=3)
            if tavily_context:
                logger.debug("Tavily: %d chars of research context", len(tavily_context))
    except Exception as e:
        log_failure("tavily_search", e, opp_id=opp.get("id", "unknown"))

    # Step 2: Firecrawl Reddit pain phrases (complements Tavily)
    firecrawl_phrases = []
    try:
        from opportunity_os.firecrawl_client import crawl_pain_evidence
        query = opp.get("problem_statement", opp.get("name", ""))[:100]
        geo = opp.get("geography", "global")
        found = crawl_pain_evidence(query, geography=geo)
        if found:
            firecrawl_phrases = found
            logger.debug("Firecrawl: %d pain phrases found", len(found))
    except Exception as e:
        log_failure("firecrawl_pain_evidence", e, opp_id=opp.get("id", "unknown"))

    # Step 3: Extract structured fields via Claude (with or without Tavily context)
    try:
        if tavily_context:
            combined = _extract_from_tavily_results(opp, api_key, tavily_context)
        else:
            combined = _execute_combined_research(opp, api_key)
        opp = {**opp, **combined}
    except Exception as exc:
        log_failure("research_executor.combined", exc, opp_id=opp.get("id", "unknown"))

    # Merge Firecrawl phrases into exact_customer_phrases
    if firecrawl_phrases:
        existing = opp.get("exact_customer_phrases") or []
        merged = list(dict.fromkeys(existing + firecrawl_phrases))[:5]
        opp["exact_customer_phrases"] = merged

    opp["research_executed_at"] = datetime.now().isoformat()
    logger.info("[research_executor] Research complete: %s", name[:50])
    return opp


def _execute_combined_research(opp: dict, api_key: str) -> dict:
    """
    Pain + distribution in ONE API call with ONE web search.
    Replaces two separate _execute_pain_research + _execute_distribution_research calls.
    Cost: 1 web search ($0.01) + 1 API call vs 2 searches ($0.02) + 2 API calls.
    """
    import anthropic

    name = opp.get("name", "")
    problem = opp.get("problem_statement", "") or opp.get("description", "")
    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()
    vertical = opp.get("vertical", "")

    # Build best available search query from pre-computed queries
    pain_queries = opp.get("_pain_queries") or []
    dist_queries = opp.get("_distribution_queries") or []
    all_queries = (pain_queries + dist_queries)[:2]
    if not all_queries:
        all_queries = [f"{name} {geo_label} market demand customers"]

    query_list = "\n".join(f"- {q}" for q in all_queries)

    prompt = f"""Research this opportunity in {geo_label}: {name}
Problem: {problem}
Vertical: {vertical}

Search queries to execute:
{query_list}

After searching, return ONLY this JSON (no prose, no code block):
{{
  "pain_validation_score": <float 0-10>,
  "exact_customer_phrases": [<up to 2 complaint phrases in local language>],
  "pain_evidence_sources": [<up to 2 source descriptions>],
  "workarounds_found": [<1-2 current workarounds people use>],
  "distribution_validated": <true/false>,
  "top_distribution_channels": [<up to 2 confirmed channels>],
  "estimated_cac_logic": "<channel + estimated CAC in one line>",
  "first_10_customer_path": "<how to get first 10 customers, max 2 sentences>",
  "trust_mechanism_latam": "<primary trust signal for this geography>"
}}"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 1,  # 1 search covers both pain + distribution
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [b.text for b in response.content if hasattr(b, "text") and getattr(b, "type", "") == "text"]
    raw = " ".join(text_blocks).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    data = json.loads(match.group())
    result = {}

    for field, cast, cap in [
        ("pain_validation_score", lambda v: max(0.0, min(10.0, float(v))), None),
        ("distribution_validated", bool, None),
        ("estimated_cac_logic", lambda v: str(v)[:300], None),
        ("first_10_customer_path", lambda v: str(v)[:500], None),
        ("trust_mechanism_latam", lambda v: str(v)[:300], None),
    ]:
        val = data.get(field)
        if val is not None:
            try:
                result[field] = cast(val)
            except (ValueError, TypeError):
                pass

    for list_field, max_items, item_len in [
        ("exact_customer_phrases", 2, 200),
        ("pain_evidence_sources", 2, 300),
        ("workarounds_found", 2, 200),
        ("top_distribution_channels", 2, 100),
    ]:
        items = data.get(list_field)
        if isinstance(items, list):
            result[list_field] = [str(x)[:item_len] for x in items[:max_items] if x]

    return result


def _extract_from_tavily_results(opp: dict, api_key: str, tavily_context: str) -> dict:
    """
    Use Claude to extract structured fields from pre-fetched Tavily search results.
    No web_search tool needed — Claude processes the context directly.
    Cheaper: no tool-use overhead, just text input → JSON output.
    """
    import anthropic

    name = opp.get("name", "")
    problem = opp.get("problem_statement", "") or opp.get("description", "")
    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()

    prompt = f"""You are analyzing research results for a business opportunity in {geo_label}.

Opportunity: {name}
Problem: {problem}

RESEARCH RESULTS:
{tavily_context[:3000]}

Based on the research above, extract and return ONLY this JSON (no prose, no code block):
{{
  "pain_validation_score": <float 0-10, based on evidence of real demand>,
  "exact_customer_phrases": [<up to 3 real complaint phrases from the results>],
  "pain_evidence_sources": [<up to 2 source names/URLs from above>],
  "workarounds_found": [<1-2 workarounds people currently use>],
  "distribution_validated": <true if clear distribution channel found, else false>,
  "top_distribution_channels": [<up to 3 channels with evidence>],
  "estimated_cac_logic": "<channel + estimated CAC in one line>",
  "first_10_customer_path": "<how to reach first 10 customers given this evidence, max 2 sentences>",
  "trust_mechanism_latam": "<primary trust signal for {geo_label}>"
}}"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=600,  # JSON output is ~300-400 tokens; 600 leaves headroom
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip() if response.content else ""
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    data = json.loads(match.group())
    result = {}

    for field, cast in [
        ("pain_validation_score", lambda v: max(0.0, min(10.0, float(v)))),
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

    for list_field, max_items, item_len in [
        ("exact_customer_phrases", 3, 200),
        ("pain_evidence_sources", 2, 300),
        ("workarounds_found", 2, 200),
        ("top_distribution_channels", 3, 100),
    ]:
        items = data.get(list_field)
        if isinstance(items, list):
            result[list_field] = [str(x)[:item_len] for x in items[:max_items] if x]

    return result


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
