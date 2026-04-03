"""
Research Backfill — runs pain_intelligence + distribution_intelligence template builders
then fires real web searches via research_executor for all 64 opportunities.

Usage:
    cd .worktrees/daily-opportunity-os
    PYTHONPATH=src uv run python scripts/run_research_backfill.py

Flags:
    --dry-run   Print what would be researched without writing anything
    --force     Re-research ALL opps, even those with research_executed_at
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

_repo_root = Path(__file__).parent.parent


def _load_env_file():
    """Load .env file into os.environ without requiring python-dotenv."""
    import os
    env_path = _repo_root / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val


_load_env_file()


def main():
    parser = argparse.ArgumentParser(description="Research backfill for all opportunities")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-run even if research_executed_at exists")
    parser.add_argument("--batch", type=int, default=20, help="Max number of opportunities to research (default: 20)")
    args = parser.parse_args()

    from opportunity_os.storage import read_all_opportunities, update_opportunity
    from opportunity_os.pain_intelligence import run_pain_intelligence
    from opportunity_os.distribution_intelligence import run_distribution_intelligence
    from opportunity_os.research_executor import run_research_executor
    import os

    opps = read_all_opportunities()
    total = len(opps)

    if args.force:
        targets = opps[:args.batch]
        print(f"FORCE mode: researching up to {args.batch} opportunities ({total} total)")
    else:
        unresearched = [o for o in opps if not o.get("research_executed_at")]
        already_done = total - len(unresearched)
        targets = unresearched[:args.batch]
        print(f"Found {len(unresearched)} unresearched opportunities ({already_done} already done, {total} total)")
        if len(unresearched) > args.batch:
            print(f"Batch limit: processing first {args.batch} of {len(unresearched)} (use --batch N to change)")

    if not targets:
        print("Nothing to backfill. All opportunities already have research_executed_at.")
        print("Use --force to re-research everything.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Would research:")
        for o in targets:
            pain_status = "pain_ok" if o.get("pain_validation_score") else "pain_null"
            dist_status = "dist_ok" if o.get("distribution_validated") else "dist_null"
            print(f"  - {o.get('name', '?')[:55]:55} [{o.get('geography','?'):10}] {pain_status} {dist_status}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check your .env file.")
        sys.exit(1)

    print(f"\nStarting research backfill for {len(targets)} opportunities...\n")
    succeeded = 0
    failed = 0
    fields_populated = {
        "pain_validation_score": 0,
        "exact_customer_phrases": 0,
        "distribution_validated": 0,
        "first_10_customer_path": 0,
    }

    for i, opp in enumerate(targets, 1):
        name = opp.get("name", "?")[:55]
        geo = opp.get("geography", "?")
        print(f"Backfill {i}/{len(targets)}: {name} [{geo}]")

        # Build query templates (fast, no API calls)
        try:
            pain_template = run_pain_intelligence(opp)
            opp["_pain_queries"] = pain_template.get("_pain_queries", [])
        except Exception as e:
            opp["_pain_queries"] = []

        try:
            dist_template = run_distribution_intelligence(opp)
            opp["_recommended_channels"] = dist_template.get("_recommended_channels", [])
            opp["_distribution_queries"] = dist_template.get("_distribution_queries", [])
        except Exception as e:
            opp["_recommended_channels"] = []
            opp["_distribution_queries"] = []

        # Force re-research if flag set
        if args.force:
            opp.pop("research_executed_at", None)

        # Fire real web searches
        researched = run_research_executor(opp)

        if researched.get("research_executed_at"):
            for field in fields_populated:
                val = researched.get(field)
                if val is not None and val != [] and val is not False:
                    fields_populated[field] += 1

            # Strip internal _ fields before saving
            save_opp = {k: v for k, v in researched.items() if not k.startswith("_")}
            update_opportunity(save_opp["id"], save_opp)
            succeeded += 1
            print(f"  OK (pain_score={researched.get('pain_validation_score', 'null')}, dist_validated={researched.get('distribution_validated', 'null')})")
        else:
            failed += 1
            print(f"  [FAIL] No research_executed_at set")

        # Rate limit: 1.5s between opps (web_search heavier than text-only)
        if i < len(targets):
            time.sleep(1.5)

    print(f"\n{'='*60}")
    print(f"Research backfill complete: {succeeded} succeeded, {failed} failed")
    print(f"\nFields populated across {succeeded} researched opportunities:")
    for field, count in fields_populated.items():
        pct = round(count / max(succeeded, 1) * 100)
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"  {field:30} [{bar}] {count}/{succeeded} ({pct}%)")


if __name__ == "__main__":
    main()
