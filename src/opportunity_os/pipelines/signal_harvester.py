"""
Signal Harvester -- auto-discover opportunity signals from zero-cost sources.

Sources:
- HN Algolia: funding news, Ask HN problems (free, no auth)
- Reddit JSON: LATAM/VE subreddits for pain signals (free, no auth)
- Serper.dev: real Google results (optional, 2500 free/month -- set SERPER_API_KEY)

Output: list of signal dicts compatible with data/raw/YYYY-MM-DD-signals.jsonl
"""

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from datetime import date
from difflib import SequenceMatcher
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

USER_AGENT = "Mozilla/5.0 (compatible; OpportunityOS/1.0; harvest-bot)"
HN_ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"
REDDIT_BASE = "https://www.reddit.com"
SERPER_BASE = "https://google.serper.dev/search"

HN_STORY_QUERIES = [
    "LATAM startup funding 2025 2026",
    "Latin America fintech raised million",
    "Venezuela startup 2025 2026",
    "Latin America market opportunity SaaS",
    "LATAM remittance payment startup",
]

HN_ASK_QUERIES = [
    "Latin America problem",
    "LATAM fintech gap",
    "Ask HN Venezuela",
]

REDDIT_VE_QUERIES = [
    "negocio problema app",
    "emprendimiento tecnologia venezuela",
    "pago transferencia dolares problema",
]

REDDIT_LATAM_QUERIES = [
    "startup latinoamerica fintech problema",
    "oportunidad negocio latam saas",
    "app mercado latin america",
]

SERPER_QUERIES = [
    "LATAM startup raised funding 2026 site:techcrunch.com OR site:bloomberg.com",
    "Venezuela fintech startup 2025 2026",
    "Latin America SaaS market gap 2026",
    "remittance LATAM startup funding million 2026",
]

# Geography keyword sets
VE_KEYWORDS = frozenset({"venezuela", "vzla", "caracas", "bolivar", "venezolano", "venezolana", "maracaibo"})
LATAM_KEYWORDS = frozenset({
    "latam", "latin america", "latinoamerica", "mexico", "colombia",
    "argentina", "brazil", "chile", "peru", "brasil", "bogota", "medellin",
})

# Vertical keyword sets (checked in order -- first match wins)
VERTICAL_KEYWORDS = [
    ("fintech", frozenset({"payment", "remittance", "banking", "crypto", "wallet", "fintech", "pago",
                           "transferencia", "banco", "financial", "lending", "credit", "insurance",
                           "neobank", "exchange"})),
    ("logistics", frozenset({"logistics", "delivery", "supply chain", "shipping", "warehouse",
                              "inventory", "fulfillment", "courier", "freight", "last mile"})),
    ("healthtech", frozenset({"health", "medical", "telemedicine", "pharmacy", "doctor",
                               "clinic", "healthcare", "salud", "medico"})),
    ("ecommerce", frozenset({"ecommerce", "marketplace", "commerce", "retail", "shopping",
                              "tienda", "mercado", "checkout", "cart"})),
    ("smb_software", frozenset({"smb", "small business", "crm", "erp", "invoice", "accounting",
                                 "factura", "negocio", "pyme", "whatsapp business"})),
    ("saas", frozenset({"saas", "software", "platform", "app", "tool", "automation", "api",
                        "dashboard", "workflow"})),
]

# Keywords that suggest a signal has real market evidence
QUALITY_KEYWORDS = frozenset({
    "million", "raised", "funding", "market", "billion", "revenue", "seed", "series",
    "customers", "users", "growth", "problem", "pain", "gap", "underserved",
    "millon", "fondos", "clientes", "usuarios", "problema",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_url(url: str, headers: Optional[dict] = None, timeout: int = 10) -> Optional[str]:
    try:
        req_headers = {"User-Agent": USER_AGENT}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _classify_geography(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in VE_KEYWORDS):
        return "venezuela"
    if any(kw in text_lower for kw in LATAM_KEYWORDS):
        return "latam"
    return "global"


def _classify_vertical(text: str) -> str:
    text_lower = text.lower()
    for vertical, keywords in VERTICAL_KEYWORDS:
        if any(kw in text_lower for kw in keywords):
            return vertical
    return "other"


def _is_duplicate(name: str, existing_names: list[str], threshold: float = 0.78) -> bool:
    name_lower = name.lower().strip()
    for existing in existing_names:
        ratio = SequenceMatcher(None, name_lower, existing.lower().strip()).ratio()
        if ratio >= threshold:
            return True
    return False


def quality_score(signal: dict) -> float:
    """Heuristic quality score 0.0-1.0. Higher = more likely a real opportunity."""
    score = 0.0
    text = " ".join([
        signal.get("name", ""),
        signal.get("description", ""),
        signal.get("raw_notes", ""),
    ]).lower()

    if signal.get("geography") in ("venezuela", "latam"):
        score += 0.30
    if any(kw in text for kw in QUALITY_KEYWORDS):
        score += 0.35
    if signal.get("source_url", "").startswith("http"):
        score += 0.20
    if len(signal.get("description", "")) > 100:
        score += 0.15

    return min(score, 1.0)


# ---------------------------------------------------------------------------
# Source: Hacker News
# ---------------------------------------------------------------------------

def _harvest_hn_stories(today: str) -> list[dict]:
    signals = []
    for query in HN_STORY_QUERIES:
        try:
            encoded = urllib.parse.quote(query)
            url = f"{HN_ALGOLIA_BASE}?query={encoded}&tags=story&hitsPerPage=5"
            raw = _fetch_url(url)
            if not raw:
                continue
            data = json.loads(raw)
            for hit in data.get("hits", []):
                title = (hit.get("title") or "").strip()
                hn_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                if len(title) < 20:
                    continue
                context = f"{title}. Points: {hit.get('points', 0)}, Comments: {hit.get('num_comments', 0)}."
                signals.append({
                    "name": title[:120],
                    "description": context,
                    "geography": _classify_geography(title),
                    "vertical": _classify_vertical(title),
                    "source_url": hn_url,
                    "raw_notes": f"HN story. Points: {hit.get('points', 0)}. Search: {query}",
                    "harvested_at": today,
                })
            time.sleep(0.3)
        except Exception as exc:
            logger.debug("HN stories harvest failed '%s': %s", query, exc)
    return signals


def _harvest_hn_asks(today: str) -> list[dict]:
    signals = []
    for query in HN_ASK_QUERIES:
        try:
            encoded = urllib.parse.quote(query)
            url = f"{HN_ALGOLIA_BASE}?query={encoded}&tags=ask_hn&hitsPerPage=5"
            raw = _fetch_url(url)
            if not raw:
                continue
            data = json.loads(raw)
            for hit in data.get("hits", []):
                title = (hit.get("title") or "").strip()
                if len(title) < 15:
                    continue
                signals.append({
                    "name": title[:120],
                    "description": f"Ask HN: {title}",
                    "geography": _classify_geography(title),
                    "vertical": _classify_vertical(title),
                    "source_url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                    "raw_notes": f"Ask HN. Comments: {hit.get('num_comments', 0)}. Search: {query}",
                    "harvested_at": today,
                })
            time.sleep(0.3)
        except Exception as exc:
            logger.debug("HN ask harvest failed '%s': %s", query, exc)
    return signals


# ---------------------------------------------------------------------------
# Source: Reddit
# ---------------------------------------------------------------------------

def _harvest_reddit_subreddit(sub: str, query: str, geo: str, today: str) -> list[dict]:
    try:
        encoded = urllib.parse.quote(query)
        url = f"{REDDIT_BASE}/r/{sub}/search.json?q={encoded}&sort=top&limit=5&restrict_sr=1&t=year"
        raw = _fetch_url(url)
        if not raw:
            return []
        data = json.loads(raw)
        results = []
        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            title = (p.get("title") or "").strip()
            body = (p.get("selftext") or "")[:400].strip()
            score = p.get("score", 0)
            if not title or score < 3 or body == "[removed]":
                continue
            desc = body if body else title
            inferred_geo = _classify_geography(f"{title} {body}") if geo == "latam" else geo
            results.append({
                "name": title[:120],
                "description": desc[:300],
                "geography": inferred_geo,
                "vertical": _classify_vertical(f"{title} {body}"),
                "source_url": f"https://reddit.com{p.get('permalink', '')}",
                "raw_notes": f"Reddit r/{sub}. Upvotes: {score}. Search: {query}",
                "harvested_at": today,
            })
        time.sleep(0.5)
        return results
    except Exception as exc:
        logger.debug("Reddit harvest failed r/%s '%s': %s", sub, query, exc)
        return []


def _harvest_reddit_signals(today: str) -> list[dict]:
    signals = []
    for query in REDDIT_VE_QUERIES:
        for sub in ("vzla", "venezuela"):
            signals.extend(_harvest_reddit_subreddit(sub, query, "venezuela", today))
    for query in REDDIT_LATAM_QUERIES:
        for sub in ("latinoamerica", "Entrepreneur"):
            signals.extend(_harvest_reddit_subreddit(sub, query, "latam", today))
    return signals


# ---------------------------------------------------------------------------
# Source: Serper (optional -- needs SERPER_API_KEY)
# ---------------------------------------------------------------------------

def _harvest_serper_signals(today: str) -> list[dict]:
    api_key = os.environ.get("SERPER_API_KEY") or _load_env_key("SERPER_API_KEY")
    if not api_key:
        return []

    signals = []
    for query in SERPER_QUERIES:
        try:
            payload = json.dumps({"q": query, "num": 5}).encode()
            req = urllib.request.Request(
                SERPER_BASE,
                data=payload,
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            for result in data.get("organic", []):
                title = (result.get("title") or "").strip()
                snippet = (result.get("snippet") or "").strip()
                link = result.get("link", "")
                if len(title) < 20:
                    continue
                signals.append({
                    "name": title[:120],
                    "description": snippet[:300] or title,
                    "geography": _classify_geography(f"{title} {snippet}"),
                    "vertical": _classify_vertical(f"{title} {snippet}"),
                    "source_url": link,
                    "raw_notes": f"Serper Google result. Query: {query}",
                    "harvested_at": today,
                })
            time.sleep(0.5)
        except Exception as exc:
            logger.debug("Serper harvest failed '%s': %s", query, exc)
    return signals


def _load_env_key(key_name: str) -> Optional[str]:
    """Load an API key from .env file in project root."""
    try:
        from pathlib import Path
        env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        if not env_path.exists():
            return None
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key_name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def harvest_signals(
    today: Optional[str] = None,
    existing_names: Optional[list[str]] = None,
    min_quality: float = 0.30,
    max_signals: int = 25,
) -> list[dict]:
    """
    Harvest fresh opportunity signals from all free sources.

    Args:
        today: Date string YYYY-MM-DD. Defaults to today.
        existing_names: Names already in the system (for deduplication).
        min_quality: Minimum heuristic quality threshold 0-1.
        max_signals: Cap on signals returned.

    Returns:
        List of signal dicts ready to write to data/raw/YYYY-MM-DD-signals.jsonl.
    """
    if today is None:
        today = date.today().isoformat()
    if existing_names is None:
        existing_names = []

    logger.info("Harvesting signals for %s", today)

    all_raw: list[dict] = []

    hn_stories = _harvest_hn_stories(today)
    logger.info("  HN stories: %d raw", len(hn_stories))
    all_raw.extend(hn_stories)

    hn_asks = _harvest_hn_asks(today)
    logger.info("  HN asks: %d raw", len(hn_asks))
    all_raw.extend(hn_asks)

    reddit = _harvest_reddit_signals(today)
    logger.info("  Reddit: %d raw", len(reddit))
    all_raw.extend(reddit)

    serper = _harvest_serper_signals(today)
    if serper:
        logger.info("  Serper: %d raw", len(serper))
        all_raw.extend(serper)

    logger.info("  Total raw: %d before filtering", len(all_raw))

    # Score, filter, deduplicate (best quality first)
    scored = sorted(
        [(s, quality_score(s)) for s in all_raw],
        key=lambda x: x[1],
        reverse=True,
    )

    seen_names: list[str] = list(existing_names)
    accepted: list[dict] = []

    for signal, quality in scored:
        if len(accepted) >= max_signals:
            break
        if quality < min_quality:
            continue
        name = signal.get("name", "").strip()
        if len(name) < 15:
            continue
        if _is_duplicate(name, seen_names):
            continue
        seen_names.append(name)
        accepted.append(signal)

    logger.info("  Accepted: %d signals after filtering", len(accepted))
    return accepted
