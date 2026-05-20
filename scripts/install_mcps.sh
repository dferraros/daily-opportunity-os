#!/bin/bash
# Pre-download all MCP npm packages so Claude Code doesn't need to fetch on first use.
# Run once after cloning the repo.

echo "Installing MCP server packages..."

npm install -g @modelcontextprotocol/server-brave-search
npm install -g tavily-mcp
npm install -g firecrawl-mcp
npm install -g @apify/actors-mcp-server
npm install -g mcp-omnisearch
npm install -g research-powerpack-mcp

echo ""
echo "MCP packages installed. Now set API keys in .env:"
echo "  BRAVE_API_KEY    — https://brave.com/search/api/"
echo "  TAVILY_API_KEY   — https://tavily.com"
echo "  JINA_API_KEY     — https://jina.ai (optional)"
echo "  APIFY_TOKEN      — https://apify.com"
echo "  PERPLEXITY_API_KEY — https://perplexity.ai/settings/api"
echo ""
echo "Free sources (no key needed): HN Algolia, Reddit JSON, Google Trends"
echo "Done."
