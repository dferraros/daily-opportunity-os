#!/usr/bin/env python3
"""
Phase 4 Validation Script
Checks both Phase 4 output files for requirement coverage (MEAS-01 to MEAS-05, REC-01 to REC-05).
Usage: python3 validate_phase4.py [--verbose]
Exit code 0 if all pass, 1 if any fail.
"""

import sys
from pathlib import Path

VERBOSE = "--verbose" in sys.argv

SCRIPT_DIR = Path(__file__).parent

REQUIREMENTS = {
    "MEAS-01": {
        "file": "playbook-section-measurement-framework.md",
        "keywords": ["CTR", "session rate", "trade rate", "deposit rate"],
        "description": "KPIs per trigger and family",
    },
    "MEAS-02": {
        "file": "playbook-section-measurement-framework.md",
        "keywords": ["push disable", "negative action", "fatigue"],
        "description": "Pressure and fatigue metrics",
    },
    "MEAS-03": {
        "file": "playbook-section-measurement-framework.md",
        "keywords": ["token health", "email reputation", "opt-in"],
        "description": "Deliverability metrics",
    },
    "MEAS-04": {
        "file": "playbook-section-measurement-framework.md",
        "keywords": ["holdout", "10%", "Welch", "4 week"],
        "description": "Incremental lift framework with holdout design",
    },
    "MEAS-05": {
        "file": "playbook-section-measurement-framework.md",
        "keywords": ["NNV", "incremental revenue", "opt-out cost", "complaint cost"],
        "description": "Net Notification Value formula",
    },
    "REC-01": {
        "file": "playbook-section-final-recommendations.md",
        "keywords": ["executive", "0.12%", "19.5M", "reactivation"],
        "description": "Executive summary with business impact",
    },
    "REC-02": {
        "file": "playbook-section-final-recommendations.md",
        "keywords": ["MVP", "30 day", "Katy", "Alvaro"],
        "description": "MVP 30-day plan with resources",
    },
    "REC-03": {
        "file": "playbook-section-final-recommendations.md",
        "keywords": ["V2", "90 day"],
        "description": "V2 90-day roadmap",
    },
    "REC-04": {
        "file": "playbook-section-final-recommendations.md",
        "keywords": ["V3", "180 day", "ML"],
        "description": "V3 180-day roadmap with ML scoring",
    },
    "REC-05": {
        "file": "playbook-section-final-recommendations.md",
        "keywords": ["Diego", "Engineering", "dependency", "bottleneck"],
        "description": "Team dependencies and bottlenecks",
    },
}


def check_requirement(req_id: str, spec: dict) -> tuple[bool, list[str]]:
    """Check a single requirement. Returns (passed, details)."""
    file_path = SCRIPT_DIR / spec["file"]
    details = []

    if not file_path.exists():
        details.append(f"  FILE NOT FOUND: {spec['file']}")
        return False, details

    content = file_path.read_text(encoding="utf-8").lower()
    all_found = True

    for keyword in spec["keywords"]:
        found = keyword.lower() in content
        if VERBOSE:
            status = "FOUND" if found else "MISSING"
            details.append(f"  [{status}] '{keyword}'")
        if not found:
            all_found = False
            if not VERBOSE:
                details.append(f"  MISSING keyword: '{keyword}'")

    return all_found, details


def main():
    print("=" * 60)
    print("Phase 4 Requirement Validation")
    print("=" * 60)
    print()

    passed = 0
    failed = 0
    results = []

    for req_id in sorted(REQUIREMENTS.keys()):
        spec = REQUIREMENTS[req_id]
        ok, details = check_requirement(req_id, spec)

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        results.append((req_id, status, spec["description"], details))

    # Print results grouped by file
    current_file = None
    for req_id, status, description, details in results:
        file_name = REQUIREMENTS[req_id]["file"]
        if file_name != current_file:
            current_file = file_name
            print(f"--- {file_name} ---")
            print()

        icon = "+" if status == "PASS" else "X"
        print(f"  [{icon}] {req_id}: {description} ... {status}")
        if VERBOSE or status == "FAIL":
            for d in details:
                print(f"    {d}")
        print()

    # Summary
    total = passed + failed
    print("=" * 60)
    print(f"RESULT: {passed}/{total} requirements validated")
    print("=" * 60)

    if failed > 0:
        print(f"\n{failed} requirement(s) FAILED.")
        print("Note: REC-01 to REC-05 require playbook-section-final-recommendations.md")
        print("      (created by Plan 04-02). MEAS-01 to MEAS-05 should all pass now.")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
