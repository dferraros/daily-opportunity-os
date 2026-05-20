#!/bin/bash
# Weekly Ritual -- run every Friday
# Produces: weekly report, top 3 to validate, top 3 to discard, top 3 rising, 1 conviction area
# Usage: bash scripts/run_weekly_ritual.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=============================="
echo "   WEEKLY RITUAL -- $(date +%Y-%m-%d)"
echo "=============================="

# Step 1: Run weekly pipeline
echo ""
echo "[1/3] Running opp-os weekly pipeline..."
PYTHONPATH=src uv run python -m opportunity_os.main weekly

# Step 2: Show latest weekly report
echo ""
echo "[2/3] Latest weekly report:"
WEEKLY_DIR="$PROJECT_ROOT/reports/weekly"
if [ -d "$WEEKLY_DIR" ]; then
    LATEST=$(ls -t "$WEEKLY_DIR"/*.md 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        echo "  -> $LATEST"
        echo ""
        head -50 "$LATEST"
    else
        echo "  No weekly reports found."
    fi
fi

# Step 3: Show notion sync status
echo ""
echo "[3/3] Notion sync status:"
PYTHONPATH=src uv run python scripts/notion_push.py --summary-only 2>/dev/null || echo "  No sync payload found."

echo ""
echo "=============================="
echo "Weekly ritual complete."
echo ""
echo "Next steps:"
echo "  1. Review the weekly report above"
echo "  2. Promote top 3 to validation: opp-os validate --id <id>"
echo "  3. Log kill reasons for bottom 3"
echo "  4. Run Notion sync: uv run python scripts/notion_push.py --execute"
echo "  5. Set 1 conviction area as 30-day focus in STATE.md"
echo "=============================="
