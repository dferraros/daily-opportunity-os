"""
Free Research Layer — zero-cost alternatives to Anthropic web_search.

Sources (no API key required):
- Jina Reader (r.jina.ai) — any URL -> clean markdown.
- Jina Search (s.jina.ai) — web search. 20 req/min.
- HN Algolia — Hacker News search, no auth.
- Reddit JSON — add .json to any Reddit URL, no auth.
- Google Trends via pytrends — no key, no cost.

Sources (optional API key — free tiers are generous):
- Serper.dev — real Google SERP results. 2,500 free/month. Set SERPER_API_KEY.
- Exa.ai — semantic/neural search. 1,000 free/month. Set EXA_API_KEY.
- Reddit Official API — authenticated, reliable. Set REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET.

Usage:
    from opportunity_os.free_research import research_opportunity_free
    result = research_opportunity_free(opp_dict)
"""

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Optional

from opportunity_os import tavily_client

logger = logging.getLogger(__name__)

JINA_SEARCH_BASE = "https://s.jina.ai/"
JINA_READER_BASE = "https://r.jina.ai/"
HN_ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"
REDDIT_BASE = "https://www.reddit.com"
REDDIT_API_BASE = "https://oauth.reddit.com"
SERPER_BASE = "https://google.serper.dev/search"
EXA_BASE = "https://api.exa.ai/search"

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
    except Exception as exc:
        logger.warning("[free_research] fetch failed for %s: %s", url[:80], exc)
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
    except Exception as exc:
        logger.warning("[free_research] Jina search failed for %r: %s", query[:60], exc)
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
    except Exception as exc:
        logger.warning("[free_research] Jina reader failed for %s: %s", url[:80], exc)
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
    except Exception as exc:
        logger.warning("[free_research] HN search failed for %r: %s", query[:60], exc)
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
        except Exception as exc:
            logger.warning("[free_research] Reddit .json search failed for r/%s: %s", sub, exc)
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
    except Exception as exc:
        logger.warning("[free_research] Google Trends failed for %s: %s", keywords[:2], exc)
        return {}


def serper_search(query: str, api_key: Optional[str] = None) -> list[str]:
    """
    Search Google via Serper.dev (2,500 free queries/month, then $0.001/query).
    Returns list of result snippets. Falls back silently if no key or on error.

    Set SERPER_API_KEY in .env to enable. Returns [] if key not set.
    """
    key = api_key or os.environ.get("SERPER_API_KEY")
    if not key:
        return []
    try:
        payload = json.dumps({"q": query, "num": 10}).encode("utf-8")
        headers = {
            "X-API-KEY": key,
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(
            SERPER_BASE,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        snippets: list[str] = []
        # Organic results
        for r in data.get("organic", []):
            snippet = r.get("snippet", "")
            if len(snippet) > 40:
                snippets.append(snippet)
        # People Also Ask — reveals exact customer language
        for paa in data.get("peopleAlsoAsk", []):
            question = paa.get("question", "")
            if question and len(question) > 20:
                snippets.append(f"[PAA] {question}")
        return snippets[:8]
    except Exception as exc:
        logger.warning("[free_research] Serper search failed for %r: %s", query[:60], exc)
        return []


def exa_search(query: str, api_key: Optional[str] = None, num_results: int = 5) -> list[str]:
    """
    Semantic/neural web search via Exa.ai (1,000 free queries/month, then $0.007/query).
    Finds conceptually related content even without exact keyword matches.
    Ideal for pain signal research: "what problems do Venezuelan SMBs face" finds
    forum threads even when they don't contain those exact words.

    Set EXA_API_KEY in .env to enable. Returns [] if key not set.
    """
    key = api_key or os.environ.get("EXA_API_KEY")
    if not key:
        return []
    try:
        payload = json.dumps({
            "query": query,
            "numResults": num_results,
            "useAutoprompt": True,          # Exa rewrites query for better semantic coverage
            "type": "neural",               # Embedding-based, not keyword
            "contents": {"text": {"maxCharacters": 500}},
        }).encode("utf-8")
        headers = {
            "x-api-key": key,
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(
            EXA_BASE,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        snippets: list[str] = []
        for result in data.get("results", []):
            text = (result.get("text") or "").strip()
            title = (result.get("title") or "").strip()
            if text and len(text) > 40:
                snippets.append(text[:300])
            elif title and len(title) > 20:
                snippets.append(title)
        return snippets[:5]
    except Exception as exc:
        logger.warning("[free_research] Exa search failed for %r: %s", query[:60], exc)
        return []


def search_reddit_official(
    query: str,
    geography: str = "global",
    limit: int = 10,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> list[dict]:
    """
    Search Reddit via the official OAuth2 API (more reliable than .json scraping).
    Cost: $0.00024/query (~$0.01/month at 30 runs). Set REDDIT_CLIENT_ID +
    REDDIT_CLIENT_SECRET in .env to enable. Falls back to search_reddit() if
    credentials not set.

    Returns same shape as search_reddit(): list of {title, text, score, url, subreddit, source}.
    """
    cid = client_id or os.environ.get("REDDIT_CLIENT_ID")
    csecret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
    if not cid or not csecret:
        return search_reddit(query, geography=geography, limit=limit)

    try:
        # Step 1: Get access token (application-only OAuth2)
        credentials = f"{cid}:{csecret}".encode("utf-8")
        import base64
        encoded = base64.b64encode(credentials).decode("utf-8")
        token_req = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {encoded}",
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(token_req, timeout=8) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
        access_token = token_data.get("access_token")
        if not access_token:
            return search_reddit(query, geography=geography, limit=limit)

        # Step 2: Search across Reddit with official API
        encoded_query = urllib.parse.quote(query)
        subreddits = GEO_SUBREDDITS.get(geography.lower(), GEO_SUBREDDITS["global"])
        subreddit_filter = "+".join(subreddits[:3])
        search_url = (
            f"{REDDIT_API_BASE}/r/{subreddit_filter}/search"
            f"?q={encoded_query}&sort=top&limit={limit}&restrict_sr=1&t=year"
        )
        search_req = urllib.request.Request(
            search_url,
            headers={
                "Authorization": f"bearer {access_token}",
                "User-Agent": USER_AGENT,
            },
        )
        with urllib.request.urlopen(search_req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results: list[dict] = []
        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            text = (p.get("selftext") or "")[:500]
            if text and text not in ("[removed]", "[deleted]"):
                results.append({
                    "title": p.get("title", ""),
                    "text": text,
                    "score": p.get("score", 0),
                    "url": f"https://reddit.com{p.get('permalink', '')}",
                    "subreddit": p.get("subreddit", ""),
                    "source": "reddit_official",
                })
        return results
    except Exception as exc:
        logger.warning(
            "[free_research] Reddit official API failed (%s) -- falling back to .json scraping", exc
        )
        return search_reddit(query, geography=geography, limit=limit)


def get_unavailable_sources() -> list[str]:
    """Return names of optional research sources that are not configured.

    Surfaced by the free-research CLI before running, so "news=0 pain=0"
    reads as "sources not configured" instead of "no demand signal".
    Jina and HN are keyless and always available, so they are not listed.
    """
    missing = []
    if not tavily_client.is_available():
        missing.append("tavily (TAVILY_API_KEY)")
    if not os.environ.get("SERPER_API_KEY"):
        missing.append("serper (SERPER_API_KEY)")
    if not os.environ.get("EXA_API_KEY"):
        missing.append("exa (EXA_API_KEY)")
    if not (os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")):
        missing.append("reddit-official (REDDIT_CLIENT_ID/SECRET)")
    return missing


def research_opportunity_free(opp: dict) -> dict:
    """
    Run free research on one opportunity using Jina + Serper + Exa + HN + Reddit.

    Sources used (in priority order):
    1. Serper.dev — Google SERP + People Also Ask (if SERPER_API_KEY set; free 2,500/mo)
    2. Exa.ai — semantic pain signal search (if EXA_API_KEY set; free 1,000/mo)
    3. Jina Search — free web search fallback (no key required)
    4. HN Algolia — startup/tech signals (no key required)
    5. Reddit — official OAuth2 if REDDIT_CLIENT_ID/SECRET set, else .json fallback

    Returns dict of new fields to merge into opp (never overwrites existing non-null values).
    Falls back gracefully on any error.
    """
    name = opp.get("name", "")
    geography = opp.get("geography", "global")
    vertical = opp.get("vertical", "")
    jina_key = os.environ.get("JINA_API_KEY")

    result: dict = {}
    pain_snippets: list[str] = []
    evidence_sources: list[str] = []

    # 1. Serper.dev -- real Google SERP results (covers Spanish-language content better)
    serper_snippets = serper_search(
        f"{name} problema clientes {geography} alternativas",
    )
    if serper_snippets:
        pain_snippets.extend(serper_snippets)
        evidence_sources.append(f"Serper: {name} problema clientes {geography}")
    else:
        # Fallback: Jina search when Serper key not set
        for query in [
            f"{name} problema usuarios {geography}",
            f"{vertical} pain frustration {geography} solution",
        ]:
            snippets = jina_search(query, api_key=jina_key)
            pain_snippets.extend(snippets)
            if snippets:
                evidence_sources.append(f"Jina search: {query}")
            time.sleep(0.3)

    # 2. Exa.ai -- semantic search for pain signals (finds conceptual matches, not just keywords)
    exa_pain_snippets = exa_search(
        f"problems challenges {vertical} {geography} customers complain",
        num_results=5,
    )
    if exa_pain_snippets:
        pain_snippets.extend(exa_pain_snippets)
        evidence_sources.append(f"Exa semantic: {vertical} pain {geography}")
    time.sleep(0.2)

    # 3. HN Algolia -- startup/tech signals (always free)
    # Use a shorter, more searchable query — long opp names get zero HN hits
    hn_query = f"{vertical} {geography}" if vertical else name[:40]
    hn_results = search_hn(hn_query, hits=8)
    for r in hn_results:
        if r["points"] > 3:  # lowered from 10 — niche topics score lower but are still signal
            pain_snippets.append(f"[HN {r['points']}pts] {r['title']}")
            evidence_sources.append(r["url"])

    # 4. Reddit -- official API if credentials set, .json fallback otherwise
    reddit_results = search_reddit_official(name, geography=geography)
    reddit_phrases: list[str] = []
    for r in reddit_results:
        if r["score"] > 5 and r["text"]:
            pain_snippets.append(r["text"][:200])
            reddit_phrases.append(r["title"])
            evidence_sources.append(r["url"])

    # 5. Tavily news signal -- count of news articles in last 30 days (zero cost, existing key)
    news_query = f"{name} {vertical}".strip() or name
    news_count = tavily_client.search_news(news_query)
    result["news_signal_count"] = news_count

    # Count meaningful evidence pieces (>50 chars) — the only real-data signal
    # this function produces. Always stored regardless of existing pain scores.
    evidence_count = len([s for s in pain_snippets if len(s) > 50])
    result["pain_signal_count"] = evidence_count

    # Populate result fields (don't overwrite existing non-null values)
    if pain_snippets and not opp.get("pain_evidence_sources"):
        result["pain_evidence_sources"] = evidence_sources[:3]

    if reddit_phrases and not opp.get("exact_customer_phrases"):
        result["exact_customer_phrases"] = reddit_phrases[:3]

    # Score based on evidence volume only when pain_validation_score is unset
    # (i.e., no paid research ran). Already-researched opps keep their real score.
    if opp.get("pain_validation_score") is None:
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

    # Always stamp free_research_at — this is an idempotency marker, not a "something changed"
    # marker. Without it, the enrichment pipeline re-runs expensively on every daily cycle for
    # fully-enriched opps that correctly produce no new fields.
    result["free_research_at"] = datetime.now().isoformat()

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
