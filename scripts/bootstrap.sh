#!/bin/bash
set -e
echo "Bootstrapping Daily Opportunity OS..."
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python -m venv .venv
source .venv/bin/activate || .venv/Scripts/activate
pip install -e .
echo "Setup complete. Run: python -m opportunity_os.main --daily"
echo "Or: opp-os --daily (after pip install -e .)"
