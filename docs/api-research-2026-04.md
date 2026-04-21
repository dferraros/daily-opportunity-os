# API Research: Research Layer Candidates
**Date:** 2026-04-21
**Budget constraint:** <$50/month at 30 pipeline runs/month (~360 search queries/month)
**Baseline (current):** Tavily + Jina (free) + HN Algolia (free) + Reddit .json (free)

---

## TL;DR — Decisions

| API | Decision | Reason |
|-----|----------|--------|
| **Serper.dev** | ADD (Priority 1) | 2,500 free queries/month → effectively $0 for 6+ months; Google SERP coverage Tavily misses |
| **Exa.ai** | ADD (Priority 2) | 1,000 free queries/month; semantic/neural search finds pain signals even without exact keyword matches |
| **Reddit Official API** | ADD (Priority 3) | ~$0.09/month; replaces brittle .json scraping with authenticated, rate-limit-aware access |
| **Firecrawl** | OPTIONAL | $16/month Hobby plan; only worth it if structured competitor page extraction is needed |
| **Brave Search** | SKIP | Removed free tier (Feb 2026); $0.005/query — worse deal than Tavily ($0.003) for similar output |
| **Perplexity Sonar** | SKIP | $0.005/query; redundant — Tavily + Claude already covers cited web synthesis |
| **SerpAPI** | SKIP | $75/month minimum; credits expire monthly; no free tier worth mentioning |
| **PhantomBuster** | SKIP | $69–439/month; TOS risk; way over budget; adds no unique data not covered by others |

---

## Cost Projection at 30 Runs/Month

Assumptions: 30 daily runs × 12 queries/run = 360 queries/month across all search APIs.

| Source | Queries/month | Unit cost | Monthly cost | Notes |
|--------|--------------|-----------|--------------|-------|
| Tavily (current) | ~120 | $0.003 | ~$0.36 | Top-3 opps × 4 queries each |
| HN Algolia (current) | unlimited | $0 | $0 | Fully free, no auth |
| Jina Search (current) | ~60 | $0 | $0 | Free tier; 20 req/min |
| Reddit .json (current) | ~60 | $0 | $0 | Fragile, no auth |
| **Serper.dev (add)** | ~60 | $0 (free tier) | **$0** | 2,500 free/month; $0.001 after |
| **Exa.ai (add)** | ~60 | $0 (free tier) | **$0** | 1,000 free/month; $0.007 after |
| **Reddit Official (add)** | ~60 | $0.00024 | **~$0.01** | More reliable than .json |
| **TOTAL** | ~420 | — | **~$0.37** | Well within $50 budget |

After free tier exhaustion (month 3-4 estimated):

| Source | Monthly cost |
|--------|-------------|
| Tavily | $0.36 |
| Serper.dev | $0.06 |
| Exa.ai | $0.42 |
| Reddit Official | $0.01 |
| **TOTAL** | **~$0.85/month** |

**Budget utilization at full paid tier: ~1.7% of $50/month budget.**

---

## API Profiles

### Serper.dev (Priority 1 — ADD)

**What it does:** Google Search API — returns the actual Google SERP (organic results, news, People Also Ask, related searches). Real Google results, not a meta-search approximation.

**Why it matters for this system:**
- Google indexes Spanish-language content better than Tavily for LATAM/Venezuela searches
- "People Also Ask" box reveals exact customer language around pain points
- News tab gives fresh signals (< 24h) that Jina might miss
- Competitor pricing pages surface in Google before they appear in aggregators

**Pricing:**
- Free tier: 2,500 queries/month (resets monthly)
- Paid: $0.001/query ($50 = 50,000 queries — 139× our monthly need)
- No credit card required for free tier

**Quality vs Tavily:** Different, not better or worse. Tavily optimizes for research synthesis; Serper gives raw Google SERP structure. Use both: Tavily for top-3 deep research, Serper for broad signal scanning on opps 4-20.

**Integration path:** `free_research.py` → `serper_search(query)` function. Returns 10 organic results + snippets per call.

---

### Exa.ai (Priority 2 — ADD)

**What it does:** Neural/semantic search engine. Uses embeddings to find conceptually related pages, not just keyword matches. Trained specifically on web content with semantic understanding.

**Why it matters for this system:**
- Pain signal mining: "what problems do Venezuelan SMBs face with cash flow" → finds forum threads, blog posts, Reddit discussions that don't contain those exact words
- Finds adjacent signals: searching "informal commerce Venezuela payment problems" surfaces content about workarounds, competitor failures, community complaints
- `use_autoprompt=True` mode rewrites your query for better semantic coverage automatically

**Pricing:**
- Free tier: 1,000 queries/month (resets monthly, developer account)
- Paid: $0.007/query ($50 = 7,142 queries — 20× our monthly need)
- Free tier lasts ~5 months at our usage rate

**Key differentiator vs Tavily/Serper:** Semantic vs keyword. Tavily and Serper find pages that contain your keywords. Exa finds pages that are *about* your concept. For pain research in Spanish LATAM markets, this is a meaningful difference.

**Integration path:** `free_research.py` → `exa_search(query, use_autoprompt=True)`. Requires `exa-py` SDK or direct REST call.

---

### Reddit Official API (Priority 3 — ADD)

**What it does:** Official Reddit REST API v2. Authenticated requests — no rate-limiting surprises from Reddit's anti-scraping measures.

**Why it matters for this system:**
- Current `.json` endpoint is unauthenticated and increasingly returns 429s or empty results
- Official API allows `search` across all of Reddit, not just one subreddit at a time
- Returns `created_utc`, `score`, `num_comments`, `upvote_ratio` — better signal quality filtering
- Supports sorting by `relevance`, `top`, `new`, `hot` in one call

**Pricing:**
- Free tier: 100 queries/minute, OAuth required
- Data API: $0.24/1,000 queries = $0.00024/query
- At 60 queries/month: **~$0.01/month**

**Setup required:** Register a Reddit app at reddit.com/prefs/apps. Get `client_id`, `client_secret`. Use `praw` library or direct OAuth2 + REST calls.

**Integration path:** Replace `search_reddit()` in `free_research.py` with authenticated version using `requests-oauthlib` or `praw`. Adds `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` to `.env`.

---

### Firecrawl (OPTIONAL — not adding now)

**What it does:** Structured web scraping — converts any URL to clean Markdown or JSON. Built-in JavaScript rendering, anti-bot handling, rate limiting.

**Why it might matter later:**
- Competitor pricing pages (JavaScript-heavy)
- App store review pages
- LinkedIn company pages (with caution)

**Why skipping now:**
- Jina Reader (`r.jina.ai`) already provides free URL-to-Markdown for most use cases
- $16/month Hobby plan is a fixed cost for a capability we don't actively need yet
- Add when a specific use case requires JS rendering that Jina can't handle

**Decision gate:** Add Firecrawl when we need to scrape 3+ competitor pricing pages per week consistently.

---

### Already Covered (no action needed)

| Source | Coverage | Notes |
|--------|----------|-------|
| HN Algolia | Startup/tech community signals | Free, no auth, keep as-is |
| Jina Search (`s.jina.ai`) | Free web search | 20 req/min, keep as-is |
| Jina Reader (`r.jina.ai`) | URL → Markdown | Free URL fetcher, keep as-is |
| pytrends | Google Trends | No key required, keep as-is |
| Brave Search MCP | General web search | Native Claude Code MCP, no extra cost |
| Tavily MCP | Research with citations | Native Claude Code MCP + API key, keep as-is |

---

## Implementation Sequence

**Week 1:** Add Serper.dev
- Register at serper.dev (free, no CC required)
- Add `SERPER_API_KEY` to `.env.example`
- Implement `serper_search(query)` in `free_research.py`
- Wire into `research_opportunity_free()` — replace 1 Jina search call with Serper for "problem + geography" queries (better Google coverage)

**Week 2:** Add Exa.ai
- Register at exa.ai (free developer account)
- Add `EXA_API_KEY` to `.env.example`
- Implement `exa_search(query)` using `exa-py` SDK
- Wire into `research_opportunity_free()` — add Exa call for pain validation queries specifically

**Week 3:** Upgrade Reddit to Official API
- Register Reddit app at reddit.com/prefs/apps (Script type, personal use)
- Add `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` to `.env.example`
- Rewrite `search_reddit()` to use OAuth2 + official search endpoint
- Keep current `.json` fallback if credentials not set

**Future:** Evaluate Firecrawl when competitor research becomes a weekly workflow need.

---

## What This Stack Covers

After all additions, our research stack provides:

| Signal type | Source | Cost |
|-------------|--------|------|
| Deep research synthesis (top-3 opps) | Tavily | $0.003/query |
| Google SERP + news + PAA | Serper.dev | Free → $0.001/query |
| Semantic/conceptual pain signals | Exa.ai | Free → $0.007/query |
| Spanish-language community complaints | Reddit Official | $0.00024/query |
| HN startup/tech signals | HN Algolia | Free |
| Any URL → clean text | Jina Reader | Free |
| Trend validation | pytrends | Free |
| **Total/month at 30 runs** | | **<$1/month for 6+ months** |

---

*Researched: 2026-04-21 | Budget tested at 30 runs/month × 12 queries/run = 360 queries*
