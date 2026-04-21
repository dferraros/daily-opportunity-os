"""
Free Research Layer — zero-cost alternatives to Anthropic web_search.

Sources:
- Jina Reader (r.jina.ai) — any URL -> clean markdown. No key needed.
- Jina Search (s.jina.ai) — web search, no key. 20 req/min.
- HN Algolia — Hacker News search, completely free, no auth.
- Reddit JSON — add .json to any Reddit URL, no auth needed.
- Google Trends via pytrends — no key, no cost.

Usage:
    from opportunity_os.free_research import research_opportunity_free
    result = research_opportunity_free(opp_dict)
"""

import json
import os
import time
import urllib.parse
import urllib.request
from typing import Optional


JINA_SEARCH_BASE = "https://s.jina.ai/"
JINA_READER_BASE = "https://r.jina.ai/"
HN_ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"
REDDIT_BASE = "https://www.reddit.com"

USER_AGENT = "Mozilla/5.0 (compatible; OpportunityOS/1.0; research-bot)"

GEO_SUBREDDITS = {
    "venezuela": ["vzla", "venezuela", "merida"],
    "colombia": ["colombia", "medellin", "bogota"],
    "latam": ["latinoamerica", "argentina", "mexico"],
    "global": ["startups", "Entrepreneur", "SaaS"],
}


def _fetch_url(url: str, timeout: int = 8) -> Optional[str]:
    """Fetch URL, return text or None on error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def jina_search(query: str, api_key: Optional[str] = None) -> list[str]:
    """
    Search the web via Jina AI (free, no key needed).
    Returns list of result snippets.
    """
    try:
        encoded = urllib.parse.quote(query)
        url = f"{JINA_SEARCH_BASE}?q={encoded}"
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Extract meaningful lines (skip headers/boilerplate)
        lines = [l.strip() for l in raw.split("\n") if len(l.strip()) > 60]
        return lines[:5]
    except Exception:
        return []


def jina_fetch_url(url: str, api_key: Optional[str] = None) -> str:
    """
    Fetch any URL as clean markdown via Jina Reader (free).
    """
    try:
        reader_url = f"{JINA_READER_BASE}{url}"
        headers = {"User-Agent": USER_AGENT}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(reader_url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode("utf-8", errors="replace")[:3000]
    except Exception:
        return ""


def search_hn(query: str, tags: str = "story", hits: int = 10) -> list[dict]:
    """
    Search Hacker News via Algolia (completely free, no auth).
    Returns list of {title, url, points, num_comments, created_at}.
    """
    try:
        encoded = urllib.parse.quote(query)
        url = f"{HN_ALGOLIA_BASE}?query={encoded}&tags={tags}&hitsPerPage={hits}"
        raw = _fetch_url(url)
        if not raw:
            return []
        data = json.loads(raw)
        results = []
        for hit in data.get("hits", []):
            results.append({
                "title": hit.get("title", ""),
                "url": hit.get("url", ""),
                "points": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "date": hit.get("created_at", "")[:10],
                "source": "hacker_news",
            })
        return results
    except Exception:
        return []


def search_reddit(query: str, geography: str = "global", limit: int = 10) -> list[dict]:
    """
    Search Reddit without API key using the .json endpoint (free).
    Returns list of {title, selftext, score, url, subreddit}.
    """
    subreddits = GEO_SUBREDDITS.get(geography.lower(), GEO_SUBREDDITS["global"])
    results = []
    for sub in subreddits[:2]:
        try:
            encoded = urllib.parse.quote(query)
            url = f"{REDDIT_BASE}/r/{sub}/search.json?q={encoded}&sort=top&limit={limit}&restrict_sr=1"
            raw = _fetch_url(url)
            if not raw:
                continue
            data = json.loads(raw)
            for post in data.get("data", {}).get("children", []):
                p = post.get("data", {})
                text = p.get("selftext", "")[:500]
                if text and text != "[removed]":
                    results.append({
                        "title": p.get("title", ""),
                        "text": text,
                        "score": p.get("score", 0),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "subreddit": sub,
                        "source": "reddit",
                    })
            time.sleep(0.5)  # Be polite
        except Exception:
            continue
    return results


def get_google_trends(keywords: list[str], geo: str = "") -> dict:
    """
    Get Google Trends data via pytrends (free, no API key).
    Returns interest scores or empty dict if pytrends not installed.
    """
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="es-419", tz=360, timeout=(5, 10))
        kw_list = keywords[:5]  # pytrends max 5
        pytrends.build_payload(kw_list, timeframe="today 3-m", geo=geo)
        interest = pytrends.interest_over_time()
        if interest.empty:
            return {}
        # Return average interest for each keyword
        return {kw: round(float(interest[kw].mean()), 1) for kw in kw_list if kw in interest.columns}
    except ImportError:
        return {}  # pytrends not installed -- skip silently
    except Exception:
        return {}


def research_opportunity_free(opp: dict) -> dict:
    """
    Run free research on one opportunity using Jina + HN + Reddit.
    Returns dict of new fields to merge into opp (never overwrites existing non-null values).
    Zero API cost. Falls back gracefully on any error.
    """
    name = opp.get("name", "")
    geography = opp.get("geography", "global")
    vertical = opp.get("vertical", "")
    jina_key = os.environ.get("JINA_API_KEY")

    result = {}
    pain_snippets = []
    evidence_sources = []

    # 1. Jina search -- free web search
    for query in [
        f"{name} problema usuarios {geography}",
        f"{vertical} pain frustration {geography} solution",
    ]:
        snippets = jina_search(query, api_key=jina_key)
        pain_snippets.extend(snippets)
        if snippets:
            evidence_sources.append(f"Jina search: {query}")
        time.sleep(0.3)

    # 2. HN Algolia -- startup/tech signals
    hn_results = search_hn(f"{name} OR {vertical}", hits=5)
    for r in hn_results:
        if r["points"] > 10:
            pain_snippets.append(f"[HN {r['points']}pts] {r['title']}")
            evidence_sources.append(r["url"])

    # 3. Reddit -- pain complaints in Spanish
    reddit_results = search_reddit(name, geography=geography)
    reddit_phrases = []
    for r in reddit_results:
        if r["score"] > 5 and r["text"]:
            pain_snippets.append(r["text"][:200])
            reddit_phrases.append(r["title"])
            evidence_sources.append(r["url"])

    # Populate result fields (don't overwrite existing non-null values)
    if pain_snippets and not opp.get("pain_evidence_sources"):
        result["pain_evidence_sources"] = evidence_sources[:3]

    if reddit_phrases and not opp.get("exact_customer_phrases"):
        result["exact_customer_phrases"] = reddit_phrases[:3]

    # Score based on evidence volume: 3+ sources = 6+, 5+ = 7+, 8+ = 8+
    if not opp.get("pain_validation_score"):
        evidence_count = len([s for s in pain_snippets if len(s) > 50])
        score = min(6.0 + (evidence_count * 0.3), 8.5) if evidence_count >= 3 else None
        if score:
            result["pain_validation_score"] = round(score, 1)

    # Infer workarounds from Reddit complaint text (mine "currently", "have to", "use X instead")
    if not opp.get("workarounds_found") and reddit_results:
        workarounds = _extract_workarounds(reddit_results)
        if workarounds:
            result["workarounds_found"] = workarounds

    # Heuristic distribution + CAC fields from geography/vertical (no API cost)
    dist_fields = _heuristic_distribution(geography, vertical, opp)
    for field, value in dist_fields.items():
        if not opp.get(field):
            result[field] = value

    if result:
        result["free_research_at"] = __import__("datetime").datetime.now().isoformat()

    return result


def _extract_workarounds(reddit_results: list[dict]) -> list[str]:
    """
    Extract workaround signals from Reddit post titles and text.
    Looks for phrases that describe how people cope today.
    """
    workaround_keywords = [
        "use ", "using ", "currently ", "have to ", "instead ", "manually ",
        "workaround", "alternative", "instead of", "do it by", "through whatsapp",
        "uso ", "usamos ", "actualmente ", "tenemos que ", "en vez de ", "manualmente ",
    ]
    workarounds = []
    for r in reddit_results:
        combined = f"{r.get('title', '')} {r.get('text', '')}".lower()
        for kw in workaround_keywords:
            idx = combined.find(kw)
            if idx != -1:
                phrase = combined[idx:idx + 80].strip().rstrip(".,;")
                if len(phrase) > 20 and phrase not in workarounds:
                    workarounds.append(phrase.capitalize())
                    break
    return workarounds[:3]


_DISTRIBUTION_HEURISTICS = {
    "venezuela": {
        "top_distribution_channels": ["whatsapp_cold_ve", "whatsapp_referral_ve", "tiktok_organic_ve"],
        "estimated_cac_logic": "WhatsApp cold outreach at ~$2-5 CPL in VE; referral converts 3x better than cold",
        "first_10_customer_path": "Personal network + WhatsApp groups in target sector; first sale via direct demo",
        "trust_mechanism_latam": "Referral chain from known operator; video demo before commitment; pay-after-results for first client",
    },
    "latam": {
        "top_distribution_channels": ["whatsapp_cold", "referral_network", "linkedin_latam"],
        "estimated_cac_logic": "WhatsApp outreach at ~$5-15 CPL; LinkedIn enterprise at $30-80; referral near zero",
        "first_10_customer_path": "LinkedIn + WhatsApp groups in vertical; 3-5 day response cycle; monthly pricing",
        "trust_mechanism_latam": "Case study from same-country peer; 30-day free trial; community proof",
    },
    "spain": {
        "top_distribution_channels": ["linkedin_spain", "seo_spanish", "content_marketing"],
        "estimated_cac_logic": "LinkedIn Spain $20-60 CPL; Google Ads $30-120 CPL by vertical; content/SEO $5-15 CPL long-term",
        "first_10_customer_path": "LinkedIn outreach to SMB owners in target vertical; events (4YFN, SaaStr); partner referrals",
        "trust_mechanism_latam": "EU compliance signals; local case studies; free audit or consultation as lead-in",
    },
    "global": {
        "top_distribution_channels": ["content_marketing", "seo", "product_led_growth"],
        "estimated_cac_logic": "Content/SEO at $8-25 CPL (long-term); paid at $40-150 CPL by vertical",
        "first_10_customer_path": "Cold email sequences (personalized); community-led (Slack, Discord, Reddit); cold LinkedIn",
        "trust_mechanism_latam": "Social proof from beta users; G2/Capterra reviews; free tier or trial",
    },
}


def _heuristic_distribution(geography: str, vertical: str, opp: dict) -> dict:
    """
    Return heuristic distribution fields based on geography and vertical.
    These are smart defaults — overwritten by real research_executor data if/when it runs.
    """
    geo_key = geography.lower() if geography.lower() in _DISTRIBUTION_HEURISTICS else "global"
    base = _DISTRIBUTION_HEURISTICS[geo_key]

    # Vertical overrides: fintech often has WhatsApp + partnership as primary channels
    result = {k: v for k, v in base.items()}
    if vertical in ("fintech", "payments") and "whatsapp" not in str(result.get("top_distribution_channels", [])):
        channels = result.get("top_distribution_channels", [])
        result["top_distribution_channels"] = ["whatsapp_cold"] + channels[:2]

    return result
