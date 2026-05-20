# Free Intelligence Stack — API Key Setup

Get all keys in ~10 minutes. All are genuinely free.

## 1. Brave Search (2000 searches/month free)
1. Go to: https://brave.com/search/api/
2. Click "Get Started Free"
3. Copy your API key
4. Add to .env: BRAVE_API_KEY=...

## 2. Tavily (research-grade search, free tier)
1. Go to: https://tavily.com
2. Sign up → Dashboard → API Keys
3. Copy your API key
4. Add to .env: TAVILY_API_KEY=...

## 3. Jina Reader (optional — works without key too)
1. Go to: https://jina.ai
2. Auto-generates API key on signup
3. Add to .env: JINA_API_KEY=...
4. Without key: 20 req/min free, just use https://r.jina.ai/<URL>

## 4. Apify (free tier, 10$/month credit included)
1. Go to: https://apify.com
2. Sign up → Settings → Integrations → API tokens
3. Add to .env: APIFY_TOKEN=...

## 5. Perplexity (free tier)
1. Go to: https://www.perplexity.ai/settings/api
2. Generate API key
3. Add to .env: PERPLEXITY_API_KEY=...

## Zero-key sources (already work, no setup needed)
- Hacker News: https://hn.algolia.com/api/v1/search?query=...
- Reddit JSON: https://reddit.com/r/vzla/search.json?q=...
- Google Trends: uv pip install pytrends (no key)
- CoinGecko: https://api.coingecko.com/api/v3/simple/price (no key)
