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
echo "Bootstrap complete."
echo "  Run daily scout:   ./scripts/run_daily.sh"
echo "  Run weekly review: ./scripts/run_weekly.sh"
echo "  Show stats:        PYTHONPATH=src python3 -m opportunity_os.main stats"
echo "  Load samples:      cp data/samples/*.jsonl data/opportunities/"
