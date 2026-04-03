"""
Research Executor — fires real Anthropic web_search_20250305 calls to validate
pain and distribution fields for each opportunity.

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
import os
import re
import time
from datetime import datetime
from typing import Optional

MODEL = "claude-haiku-4-5-20251001"
MAX_SEARCH_USES = 3


def run_research_executor(opp: dict) -> dict:
    """
    Execute web research for pain + distribution validation on one opportunity.
    Returns opp dict with populated research fields (or unchanged if API unavailable).
    """
    if opp.get("research_executed_at"):
        return opp  # Skip already-researched opps

    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_env_key()
    if not api_key:
        print(f"  [research_executor] No API key — skipping: {opp.get('name', '?')[:50]}")
        return opp

    name = opp.get("name", "unknown")

    try:
        pain_result = _execute_pain_research(opp, api_key)
        opp.update(pain_result)
    except Exception as exc:
        print(f"  [research_executor] Pain research failed ({type(exc).__name__}: {exc}) for: {name[:40]}")

    try:
        dist_result = _execute_distribution_research(opp, api_key)
        opp.update(dist_result)
    except Exception as exc:
        print(f"  [research_executor] Distribution research failed ({type(exc).__name__}: {exc}) for: {name[:40]}")

    opp["research_executed_at"] = datetime.now().isoformat()
    print(f"  [research_executor] Research complete: {name[:50]}")
    return opp


def _execute_pain_research(opp: dict, api_key: str) -> dict:
    """Use web_search_20250305 to validate pain signals. Returns dict with pain fields."""
    import anthropic

    queries = opp.get("_pain_queries") or []
    if not queries:
        try:
            from opportunity_os.pain_intelligence import build_pain_queries
            queries = build_pain_queries(opp)
        except Exception:
            pass

    if not queries:
        name = opp.get("name", "")
        geo = opp.get("geography", "latam")
        geo_label = "Venezuela" if geo == "venezuela" else geo.upper()
        queries = [
            f"{name} problem complaints {geo_label}",
            f"{opp.get('vertical', '')} pain frustration {geo_label}",
        ]

    name = opp.get("name", "")
    problem = opp.get("problem_statement", "") or opp.get("description", "")
    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()
    search_queries = queries[:3]
    query_list = "\n".join(f"- {q}" for q in search_queries)

    prompt = f"""Research pain validation for this business opportunity:

Opportunity: {name}
Problem: {problem}
Geography: {geo_label}

Execute web searches using these queries to find real evidence:
{query_list}

After searching, return ONLY this JSON (no prose, no markdown, no code block):
{{
  "pain_validation_score": <float 0-10, where 10=daily urgent pain with failed workarounds>,
  "exact_customer_phrases": [<up to 3 exact complaint phrases found in local language>, ...],
  "pain_evidence_sources": [<up to 3 source descriptions or URLs>, ...],
  "workarounds_found": [<what people actually do today to solve this>, ...]
}}

Score guide: 9-10=emergency daily pain, 7-8=frequent recurring pain, 5-6=moderate annoyance, 3-4=nice-to-have, 1-2=assumed pain not confirmed.
Return null values if no evidence found for a field."""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCH_USES,
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

    score = data.get("pain_validation_score")
    if score is not None:
        try:
            result["pain_validation_score"] = max(0.0, min(10.0, float(score)))
        except (ValueError, TypeError):
            pass

    phrases = data.get("exact_customer_phrases")
    if isinstance(phrases, list):
        result["exact_customer_phrases"] = [str(p)[:200] for p in phrases[:3] if p]

    sources = data.get("pain_evidence_sources")
    if isinstance(sources, list):
        result["pain_evidence_sources"] = [str(s)[:300] for s in sources[:3] if s]

    workarounds = data.get("workarounds_found")
    if isinstance(workarounds, list):
        result["workarounds_found"] = [str(w)[:200] for w in workarounds if w]

    return result


def _execute_distribution_research(opp: dict, api_key: str) -> dict:
    """Use web_search_20250305 to validate distribution channels. Returns dict with distribution fields."""
    import anthropic

    queries = opp.get("_distribution_queries") or []
    recommended = opp.get("_recommended_channels") or []

    if not queries:
        try:
            from opportunity_os.distribution_intelligence import build_distribution_queries, get_recommended_channels
            queries = build_distribution_queries(opp)
            recommended = get_recommended_channels(opp)
        except Exception:
            pass

    if not queries:
        name = opp.get("name", "")
        geo = opp.get("geography", "latam")
        geo_label = "Venezuela" if geo == "venezuela" else geo.upper()
        queries = [
            f"how to acquire first customers {name} {geo_label}",
            f"marketing channel {opp.get('vertical', '')} {geo_label} CAC cost",
        ]

    name = opp.get("name", "")
    geography = opp.get("geography", "latam")
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()
    vertical = opp.get("vertical", "")
    search_queries = queries[:3]
    query_list = "\n".join(f"- {q}" for q in search_queries)
    channels_hint = ", ".join(recommended[:3]) if recommended else "unknown"

    prompt = f"""Research customer acquisition and distribution for this business opportunity:

Opportunity: {name}
Geography: {geo_label}
Vertical: {vertical}
Likely channels: {channels_hint}

Execute web searches to find real evidence about how to reach customers:
{query_list}

After searching, return ONLY this JSON (no prose, no markdown, no code block):
{{
  "distribution_validated": <true if at least one clear channel confirmed, false otherwise>,
  "top_distribution_channels": [<up to 3 channels confirmed by evidence>, ...],
  "estimated_cac_logic": "<one line: channel + estimated CAC, e.g. 'WhatsApp cold outreach ~$12 CAC'>",
  "first_10_customer_path": "<step-by-step path to first 10 paying customers, max 2 sentences>",
  "trust_mechanism_latam": "<primary trust-building mechanism for this geography>"
}}

For LATAM/Venezuela: WhatsApp, referral networks, and community trust typically dominate.
Return null values if no evidence found."""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCH_USES,
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

    dist_validated = data.get("distribution_validated")
    if dist_validated is not None:
        result["distribution_validated"] = bool(dist_validated)

    channels = data.get("top_distribution_channels")
    if isinstance(channels, list):
        result["top_distribution_channels"] = [str(c)[:100] for c in channels[:3] if c]

    cac_logic = data.get("estimated_cac_logic")
    if cac_logic:
        result["estimated_cac_logic"] = str(cac_logic)[:300]

    path = data.get("first_10_customer_path")
    if path:
        result["first_10_customer_path"] = str(path)[:500]

    trust = data.get("trust_mechanism_latam")
    if trust:
        result["trust_mechanism_latam"] = str(trust)[:300]

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
