#!/bin/bash
# Daily Opportunity OS -- daily run
# Usage: ./scripts/run_daily.sh [--dry-run] [--date YYYY-MM-DD]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH="$PROJECT_ROOT/src"
echo "Running daily opportunity scout -- $(date '+%Y-%m-%d %H:%M')"
uv run python -m opportunity_os.main daily "$@"
