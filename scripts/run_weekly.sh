#!/bin/bash
# Daily Opportunity OS -- weekly review
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH="$PROJECT_ROOT/src"
echo "Running weekly opportunity review -- $(date '+%Y-%m-%d')"
python3 -m opportunity_os.main weekly "$@"
