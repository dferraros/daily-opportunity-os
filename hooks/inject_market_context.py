"""
inject_market_context.py — InstructionsLoaded hook
Fetches current USDT/VES rate and crypto prices, injects as context.
Falls back silently if API unreachable. Always exits 0.

Output format (printed to stdout for Claude to see):
---
MARKET CONTEXT (auto-injected 2026-04-01 09:00):
Today's date: 2026-04-01
USDT/VES rate: 36.42 VES per USDT (from CoinGecko)
BTC: $82,450 | ETH: $3,200
---
"""
import sys
import json
import urllib.request
from datetime import datetime


def fetch_market_context() -> dict:
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=tether,bitcoin,ethereum&vs_currencies=ves,usd"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        data = json.loads(resp.read().decode())
    return data


def main():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_date = datetime.now().strftime("%Y-%m-%d")

    try:
        data = fetch_market_context()
        usdt_ves = data.get("tether", {}).get("ves", "N/A")
        btc_usd = data.get("bitcoin", {}).get("usd", "N/A")
        eth_usd = data.get("ethereum", {}).get("usd", "N/A")

        btc_fmt = f"${btc_usd:,.0f}" if isinstance(btc_usd, (int, float)) else str(btc_usd)
        eth_fmt = f"${eth_usd:,.0f}" if isinstance(eth_usd, (int, float)) else str(eth_usd)
        ves_fmt = f"{usdt_ves:.2f}" if isinstance(usdt_ves, (int, float)) else str(usdt_ves)

        print("---")
        print(f"MARKET CONTEXT (auto-injected {today}):")
        print(f"Today's date: {today_date}")
        print(f"USDT/VES rate: {ves_fmt} VES per USDT (from CoinGecko)")
        print(f"BTC: {btc_fmt} | ETH: {eth_fmt}")
        print("---")

    except Exception:
        print(f"MARKET CONTEXT: Date: {today_date}. API unavailable.")

    sys.exit(0)


if __name__ == "__main__":
    main()
