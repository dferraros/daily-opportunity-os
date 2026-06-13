"""
Competitor Intelligence -- competitor-weakness signal via review search + LLM extraction.

The Apify G2 actor's category mode returns product summaries (rating null, 404
pages), so competitor_negative_review_rate was rarely populated (2026-06-10
audit). This replaces it with a path fully under our control: Tavily searches
each direct competitor's reviews/complaints (G2, Capterra, Reddit), then a Haiku
extraction estimates a 0-1 weakness rate plus VERBATIM complaint phrases. The
rate feeds competitor_weakness_score in the scoring engine exactly as the old
field did; the verbatim phrases populate exact_customer_phrases (plan P5: real
phrases, not AI paraphrase).

Never fabricates: no Tavily key, no competitors, empty searches, or a failed/
unparseable Haiku call all leave the opportunity unchanged and log loudly.
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

COMPETITOR_RESEARCH_TTL_DAYS = 30
MAX_COMPETITORS = 2          # cost cap: Tavily credits scale with competitor count
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

EXTRACTION_SYSTEM_PROMPT = (
    "You analyze software/product reviews to gauge how WEAK incumbent competitors "
    "are -- weakness is the opportunity. From the supplied review snippets, judge "
    "how negatively users speak about these products. "
    "RUBRIC for competitor_negative_review_rate (0.0-1.0): 0.0 = users overwhelmingly "
    "satisfied (strong incumbent, hard to displace); 0.5 = mixed; 0.8+ = users "
    "frequently frustrated (weak incumbent, real opening). Base it on the evidence, "
    "not optimism. Extract complaint phrases VERBATIM from the snippets -- never "
    "paraphrase. Return ONLY valid JSON."
)


_GENERIC_NAME_WORDS = {
    "saas", "platform", "software", "app", "tool", "system", "solution", "for",
    "the", "a", "an", "and", "of", "to", "in", "mandatory", "compliance",
}


def _category_seed(opp: dict) -> str:
    """Most searchable product-space descriptor when no competitors are named.

    The opp NAME carries the real product keywords (e.g. 'E-Invoicing
    Compliance SaaS ...' -> 'E-Invoicing LATAM Regulations'), so it is the best
    search seed. Internal taxonomy labels -- the bucket ('latam_asymmetry') and
    the vertical ('smb_software') -- are NOT searchable product spaces and
    surface no real complaints, so they are last-resort fallbacks only.
    """
    name = (opp.get("name") or "").strip()
    if name:
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]+", name)
                 if w.lower() not in _GENERIC_NAME_WORDS]
        if words:
            return " ".join(words[:4])
    bucket = (opp.get("bucket") or opp.get("bucket_hypothesis") or "").strip()
    if bucket and "_" not in bucket:  # skip internal snake_case taxonomy labels
        return bucket
    return (opp.get("vertical") or "").replace("_", " ").strip()


def build_competitor_queries(opp: dict) -> list[str]:
    """Review/complaint search queries for the opp's direct competitors.

    Falls back to a product-space query (from bucket/name, not the bare
    vertical) when no competitors are named, so the signal still has a chance.
    """
    competitors = [c for c in (opp.get("direct_competitors") or []) if c][:MAX_COMPETITORS]
    if competitors:
        return [f"{c} reviews complaints problems site:g2.com OR site:capterra.com OR site:reddit.com"
                for c in competitors]
    seed = _category_seed(opp)
    if seed:
        return [f"{seed} software reviews complaints frustrations site:g2.com OR site:reddit.com"]
    return []


def _parse_extraction(raw: str) -> Optional[dict]:
    """Parse the Haiku JSON; clamp rate to 0-1, cap lists. None on malformation."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    rate = data.get("competitor_negative_review_rate")
    if rate is None:
        return None
    try:
        rate_f = max(0.0, min(1.0, float(rate)))
    except (TypeError, ValueError):
        return None

    def _str_list(value):
        if not isinstance(value, list):
            value = [value] if value else []
        return [str(v).strip() for v in value if str(v).strip()][:3]

    return {
        "competitor_negative_review_rate": round(rate_f, 3),
        "competitor_complaint_themes": _str_list(data.get("complaint_themes")),
        "exact_customer_phrases": _str_list(data.get("verbatim_phrases")),
    }


def _extract_weakness(opp: dict, digest: str) -> Optional[dict]:
    """Haiku extraction over the review digest. None on missing key / API failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from opportunity_os.ai_scorer import _load_env_key
        api_key = _load_env_key()
    if not api_key:
        logger.error("[competitor_intel] No ANTHROPIC_API_KEY -- skipping %s", opp.get("name", "?")[:50])
        return None

    competitors = ", ".join((opp.get("direct_competitors") or [])[:MAX_COMPETITORS]) or opp.get("vertical", "")
    prompt = (
        f"Competitors / category: {competitors}\n"
        f"Opportunity vertical: {opp.get('vertical', '')}\n\n"
        f"REVIEW SNIPPETS:\n{digest[:6000]}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "competitor_negative_review_rate": <float 0.0-1.0 per the rubric>,\n'
        '  "complaint_themes": ["<recurring complaint theme>", "..."],\n'
        '  "verbatim_phrases": ["<exact quote from a snippet>", "..."]\n'
        "}"
    )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = _parse_extraction(response.content[0].text)
        if parsed is None:
            logger.error("[competitor_intel] Unparseable response for %s", opp.get("name", "?")[:50])
        return parsed
    except Exception as exc:  # noqa: BLE001 -- any API failure means no signal, never a fake one
        logger.error("[competitor_intel] API call failed for %s: %s", opp.get("name", "?")[:50], exc)
        return None


def _is_fresh(opp: dict) -> bool:
    stamp = opp.get("competitor_research_at")
    if not stamp:
        return False
    try:
        return datetime.fromisoformat(stamp) > datetime.now() - timedelta(days=COMPETITOR_RESEARCH_TTL_DAYS)
    except ValueError:
        return False


def analyze_competitor_weakness(opp: dict, force: bool = False) -> dict:
    """Return field updates for one opportunity's competitor-weakness signal.

    Returns {} (and logs) when nothing can be produced: fresh within TTL,
    Tavily unavailable, no competitors/vertical, empty searches, or extraction
    failure. Never raises, never fabricates. Caller merges the returned dict.
    """
    name = opp.get("name", "?")[:50]

    if _is_fresh(opp) and not force:
        logger.info("[competitor_intel] %s fresh within %dd TTL -- skipping", name, COMPETITOR_RESEARCH_TTL_DAYS)
        return {}

    if not tavily_client.is_available():
        logger.error("[competitor_intel] Tavily unavailable -- cannot search reviews for %s", name)
        return {}

    queries = build_competitor_queries(opp)
    if not queries:
        logger.warning("[competitor_intel] No competitors or vertical for %s -- nothing to search", name)
        return {}

    snippets: list[str] = []
    for q in queries:
        results = tavily_client.search_with_content(q, max_results=3) or []
        for r in results:
            text = (r.get("raw_content") or r.get("content") or "").strip()
            if text:
                snippets.append(text[:1500])
    if not snippets:
        logger.warning("[competitor_intel] Review searches returned nothing for %s", name)
        return {}

    extracted = _extract_weakness(opp, "\n---\n".join(snippets))
    if extracted is None:
        return {}

    # Tag the basis: a rate from named competitors is grounded; one from a
    # category-keyword fallback is weaker signal (no opp currently names
    # competitors -- see STATE: populating direct_competitors upstream is the
    # real unlock). Same transparency principle as low_evidence_flag.
    has_named = bool([c for c in (opp.get("direct_competitors") or []) if c])
    updates = {
        "competitor_negative_review_rate": extracted["competitor_negative_review_rate"],
        "competitor_complaint_themes": extracted["competitor_complaint_themes"],
        "competitor_signal_basis": "named_competitors" if has_named else "category_fallback",
        "competitor_research_at": datetime.now().isoformat(),
    }
    # Only fill exact_customer_phrases if empty AND we got verbatim quotes (plan P5).
    if extracted["exact_customer_phrases"] and not opp.get("exact_customer_phrases"):
        updates["exact_customer_phrases"] = extracted["exact_customer_phrases"]

    logger.info(
        "[competitor_intel] %s -> neg_rate %.2f, %d theme(s)",
        name, updates["competitor_negative_review_rate"], len(updates["competitor_complaint_themes"]),
    )
    return updates
