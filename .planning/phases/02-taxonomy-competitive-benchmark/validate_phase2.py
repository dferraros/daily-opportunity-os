#!/usr/bin/env python3
"""Validation script for Phase 2: Taxonomy + Competitive Benchmark."""
import os
import sys

PHASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = []

def check_file(filename, required_strings, req_id, description):
    filepath = os.path.join(PHASE_DIR, filename)
    if not os.path.exists(filepath):
        RESULTS.append(f"FAIL [{req_id}] {description}: file {filename} not found")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    missing = [s for s in required_strings if s.lower() not in content.lower()]
    if missing:
        RESULTS.append(f"FAIL [{req_id}] {description}: missing: {missing}")
    else:
        RESULTS.append(f"PASS [{req_id}] {description}")

# TAX-01: Taxonomy overview with 6 families
check_file("playbook-section-trigger-taxonomy.md",
    ["Family A", "Family B", "Family C", "Family D", "Family E", "Family F",
     "trigger_id", "eligibility", "consent_category", "priority_tier"],
    "TAX-01", "Trigger taxonomy with 6 families and template fields")

# TAX-02 through TAX-07: Family content in combined taxonomy file
families = [
    ("TAX-02", "playbook-section-trigger-taxonomy.md", "Family A",
     ["price target", "who_receives", "who_never_receives", "cooldown", "CAT-USR"]),
    ("TAX-03", "playbook-section-trigger-taxonomy.md", "Family B",
     ["volatility", "who_receives", "who_never_receives", "cooldown", "CAT-MKT"]),
    ("TAX-04", "playbook-section-trigger-taxonomy.md", "Family C",
     ["watched not bought", "who_receives", "who_never_receives", "cooldown"]),
    ("TAX-05", "playbook-section-trigger-taxonomy.md", "Family D",
     ["at_risk", "who_receives", "who_never_receives", "cooldown"]),
    ("TAX-06", "playbook-section-trigger-taxonomy.md", "Family E",
     ["earn", "who_receives", "who_never_receives", "cooldown", "CAT-PRO"]),
    ("TAX-07", "playbook-section-trigger-taxonomy.md", "Family F",
     ["LTV", "who_receives", "who_never_receives", "cooldown"]),
]
for req_id, filename, family, required in families:
    check_file(filename, required, req_id,
               f"{family} triggers with eligibility criteria")

# TAX-08: Asset universe mapping
check_file("playbook-section-asset-universe.md",
    ["wallet", "brokerage", "pro", "earn", "card", "loan", "launchpad",
     "space center", "asset scope", "eligibility"],
    "TAX-08", "Asset universe with product-asset mapping")

# BENCH-01, BENCH-02, BENCH-03: Competitor benchmark
check_file("playbook-section-competitor-benchmark.md",
    ["Coinbase", "Binance", "Kraken", "Bitpanda", "Revolut", "Nexo"],
    "BENCH-01", "Competitor matrix with 6 competitors")
check_file("playbook-section-competitor-benchmark.md",
    ["preference center", "channels", "asset scope", "gaps"],
    "BENCH-02", "Per-competitor analysis dimensions")
check_file("playbook-section-competitor-benchmark.md",
    ["copy", "avoid", "innovate"],
    "BENCH-03", "Copy/avoid/innovate recommendations")

# COMP-01: Compliance checklist
check_file("playbook-section-compliance-per-trigger.md",
    ["MiCA", "GDPR", "ePrivacy", "CNMV", "checklist"],
    "COMP-01", "Compliance checklist per trigger")

# COMP-02: Diego review workflow
check_file("playbook-section-compliance-per-trigger.md",
    ["Tier 1", "Tier 2", "Diego", "approval", "four-eyes"],
    "COMP-02", "Diego review workflow")

# COMP-03: Investment advice vs informational
check_file("playbook-section-compliance-per-trigger.md",
    ["informational", "advisory", "bright line", "safe", "dangerous"],
    "COMP-03", "Investment advice vs informational boundary")

# COMP-04: Market abuse protocol
check_file("playbook-section-compliance-per-trigger.md",
    ["market abuse", "public data", "simultaneous", "audit log", "Article 87"],
    "COMP-04", "Market abuse prevention protocol")

# Print results
print("=" * 60)
print("Phase 2 Validation Results")
print("=" * 60)
passed = sum(1 for r in RESULTS if r.startswith("PASS"))
failed = sum(1 for r in RESULTS if r.startswith("FAIL"))
for r in RESULTS:
    print(r)
print(f"\n{passed} passed, {failed} failed out of {len(RESULTS)} checks")
sys.exit(0 if failed == 0 else 1)
