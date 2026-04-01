#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR/src"
python -m opportunity_os.main --daily
echo "Daily run complete: $(date)"
