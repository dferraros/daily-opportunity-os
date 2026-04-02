"""
Validation Run — manual pipeline for `opp-os validate <opp-id>`.

Loads an opportunity by ID, runs the full 8-section validation package,
writes the markdown file, and builds a Notion sync payload.
"""
import json
import os
from datetime import datetime, timezone


def run_validation_pipeline(opp_id: str, dry_run: bool = False) -> dict:
    """
    Run full validation package for one opportunity.

    Returns dict with:
      path: str (path to written markdown file)
      notion_sync_path: str (path to written JSON sync file)
      opp_name: str
      error: str (only if failed)
    """
    from opportunity_os.storage import get_opportunity_by_id, update_opportunity
    from opportunity_os.validation_engine import run_validation
    from opportunity_os.notion_sync import build_sync_payload
    from opportunity_os.reports import ensure_report_dirs, get_project_root

    # Load opportunity
    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        return {"error": f"Opportunity '{opp_id}' not found in opportunities.jsonl"}

    if opp.get("kill_decision"):
        return {"error": f"Opportunity '{opp_id}' is killed — cannot run validation."}

    # Run validation (full mode = all 8 sections)
    package = run_validation(opp, mode="full")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    root = get_project_root()

    if dry_run:
        print(f"[DRY RUN] Would write validation for: {opp.get('name')}")
        print(f"[DRY RUN] Markdown preview (first 400 chars):")
        print(package["_validation_markdown"][:400])
        return {
            "path": "(dry-run)",
            "notion_sync_path": "(dry-run)",
            "opp_name": opp.get("name", ""),
        }

    # Ensure output directory exists
    ensure_report_dirs()
    val_dir = os.path.join(root, "reports", "validation")

    # Write markdown file
    safe_id = str(opp_id).replace("/", "-").replace("\\", "-")[:40]
    md_path = os.path.join(val_dir, f"{date}-{safe_id}-validation.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(package["_validation_markdown"])

    # Build Notion sync payload
    sync_payload = build_sync_payload(
        opportunities=[],
        run_stats={
            "signals_total": 0,
            "new_opps": 0,
            "killed": 0,
            "top_score": 0,
            "score_range": "N/A",
            "by_geo": {},
            "top_opportunity": opp.get("name", ""),
            "notes": "Manual validation run",
        },
        date=date,
        validation_packages=[(opp, package)],
    )
    sync_path = os.path.join(root, "reports", "daily", f"{date}-validation-sync.json")
    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(sync_payload, f, indent=2, default=str)

    # Update opp stage in storage
    update_opportunity(opp_id, {
        "stage": "validation",
        "validation_status": "in_progress",
        "validation_start_date": package["validation_start_date"],
        "validation_deadline": package["validation_deadline"],
    })

    return {
        "path": md_path,
        "notion_sync_path": sync_path,
        "opp_name": opp.get("name", ""),
    }
