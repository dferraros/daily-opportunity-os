#!/bin/bash
# Daily Opportunity OS -- daily run
# Usage: ./scripts/run_daily.sh [--dry-run] [--date YYYY-MM-DD]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH="$PROJECT_ROOT/src"

# Log automation run start (proof of execution)
RUN_DATE="$(date '+%Y-%m-%d %H:%M:%S')"
echo "{\"run_date\": \"$RUN_DATE\", \"status\": \"started\", \"trigger\": \"automation\"}" >> "$PROJECT_ROOT/data/automation_runs.jsonl"

echo "Running daily opportunity scout -- $RUN_DATE"
uv run python -m opportunity_os.main daily "$@"
EXIT_CODE=$?

# Log completion status
echo "{\"run_date\": \"$RUN_DATE\", \"status\": \"completed\", \"exit_code\": $EXIT_CODE}" >> "$PROJECT_ROOT/data/automation_runs.jsonl"
exit $EXIT_CODE
