#!/bin/bash
# Bootstrap daily-opportunity-os
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Setting up daily-opportunity-os..."

# Install Python package
pip install -e . --quiet

# Create directories
mkdir -p data/opportunities data/raw data/processed data/samples          data/customer_language exports/notion          reports/daily reports/weekly reports/deep-dives

# Create empty JSONL files
touch data/opportunities/opportunities.jsonl
touch data/opportunities/opportunity_history.jsonl
touch data/machine_metrics.jsonl

echo ""
echo "Checking API keys..."
MISSING_KEYS=()

check_key() {
    local key_name=$1
    local key_val="${!key_name}"
    if [ -z "$key_val" ] || [ "$key_val" = "your_${key_name,,}_here" ]; then
        MISSING_KEYS+=("$key_name")
    fi
}

if [ -f ".env" ]; then
    source .env
    check_key "COMPOSIO_API_KEY"
    check_key "SCRAPINGBEE_API_KEY"
    check_key "SERPAPI_KEY"
    check_key "FIRECRAWL_API_KEY"
fi

if [ ${#MISSING_KEYS[@]} -gt 0 ]; then
    echo "⚠️  Missing API keys (Pain OS and Distribution OS will run in stub mode):"
    for key in "${MISSING_KEYS[@]}"; do
        echo "   - $key"
    done
    echo "   Add keys to .env to enable full scraping. See .env.example."
else
    echo "✅ All API keys present."
fi

echo ""
echo "Bootstrap complete."
echo "  Run daily scout:   ./scripts/run_daily.sh"
echo "  Run weekly review: ./scripts/run_weekly.sh"
echo "  Show stats:        PYTHONPATH=src python3 -m opportunity_os.main stats"
echo "  Load samples:      cp data/samples/*.jsonl data/opportunities/"
