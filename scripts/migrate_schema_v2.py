"""
migrate_schema_v2.py — Strip 15 deprecated fields from opportunities.jsonl.

Reads data/opportunities/opportunities.jsonl, removes all deprecated fields
from each record, adds missing fields with defaults, and writes back.
Creates a backup at data/opportunities/opportunities_pre_v2.jsonl first.

Usage:
    cd project_root && PYTHONPATH=src uv run python scripts/migrate_schema_v2.py
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

DEPRECATED_FIELDS = [
    "pain_cluster_id",
    "trust_profile",
    "why_now_venezuela",
    "first_revenue_path",
    "daniels_wedge_score",
    "non_obviousness_score",
    "business_model_type",
    "thesis_fit_score",
    "decision_filter_results",
    "distribution_profile",
    "benchmark_archetype",
    "founder_fit_score",
    "pain_validation_score",
    "pain_evidence_sources",
    "workarounds_found",
]

NEW_FIELD_DEFAULTS = {
    "score_history": None,
    "venezuela_lens_applied": False,
}

JSONL_PATH = Path("data/opportunities/opportunities.jsonl")
BACKUP_PATH = Path("data/opportunities/opportunities_pre_v2.jsonl")


def main() -> None:
    if not JSONL_PATH.exists():
        print(f"ERROR: {JSONL_PATH} not found. Run from project root.")
        raise SystemExit(1)

    # Create backup
    shutil.copy2(JSONL_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

    # Read all records
    raw_lines = [l for l in JSONL_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Records read: {len(raw_lines)}")

    records = [json.loads(l) for l in raw_lines]

    # Count field occurrences before stripping
    field_removal_counts: dict[str, int] = defaultdict(int)
    for rec in records:
        for f in DEPRECATED_FIELDS:
            if f in rec and rec[f] is not None:
                field_removal_counts[f] += 1

    # Migrate each record
    migrated = []
    for rec in records:
        # Strip deprecated fields
        for f in DEPRECATED_FIELDS:
            rec.pop(f, None)

        # Add missing new fields (only if not already present)
        for field, default in NEW_FIELD_DEFAULTS.items():
            if field not in rec:
                rec[field] = default

        migrated.append(rec)

    # Write back
    output = "\n".join(json.dumps(r, ensure_ascii=False) for r in migrated)
    JSONL_PATH.write_text(output + "\n", encoding="utf-8")

    print(f"Migrated {len(migrated)} records.")
    print("Fields removed (non-null values stripped):")
    if field_removal_counts:
        for f, count in sorted(field_removal_counts.items(), key=lambda x: -x[1]):
            print(f"  {f}: {count} non-null values removed")
    else:
        print("  All deprecated fields were already null (clean removal).")
    print(f"Backup at: {BACKUP_PATH}")
    print("Done — schema v2 migration complete.")


if __name__ == "__main__":
    main()
