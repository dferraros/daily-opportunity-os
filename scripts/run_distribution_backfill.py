"""
Distribution Backfill — runs dedicated Tavily distribution research on
opportunities missing distribution_validated or with False distribution.

Usage:
    cd .worktrees/daily-opportunity-os
    PYTHONPATH=src uv run python scripts/run_distribution_backfill.py

Flags:
    --dry-run   Print what would be researched without writing
    --force     Re-run even opps that already have distribution_validated=True
    --batch N   Max opportunities to process (default: 10)
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

_repo_root = Path(__file__).parent.parent


def _load_env_file():
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
                    if key and key not in __import__("os").environ:
                        __import__("os").environ[key] = val


_load_env_file()


def main():
    parser = argparse.ArgumentParser(description="Distribution backfill for opportunities")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-run even if distribution_validated=True")
    parser.add_argument("--batch", type=int, default=10, help="Max opportunities to process (default: 10)")
    args = parser.parse_args()

    from opportunity_os.storage import read_all_opportunities, update_opportunity
    from opportunity_os.distribution_intelligence import run_distribution_executor
    import os

    opps = read_all_opportunities()
    total = len(opps)

    if args.force:
        targets = opps[:args.batch]
        print(f"FORCE mode: re-running distribution on up to {args.batch} opps ({total} total)")
    else:
        unvalidated = [o for o in opps if not o.get("distribution_validated")]
        already_done = total - len(unvalidated)
        targets = unvalidated[:args.batch]
        print(f"Found {len(unvalidated)} unvalidated opps ({already_done} distribution-validated, {total} total)")
        if len(unvalidated) > args.batch:
            print(f"Batch limit: processing first {args.batch} (use --batch N to change)")

    if not targets:
        print("Nothing to do. All opportunities have distribution_validated.")
        print("Use --force to re-run everything.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Would run distribution research on:")
        for o in targets:
            dv = o.get("distribution_validated")
            path = "path_ok" if o.get("first_10_customer_path") else "no_path"
            print(f"  - {o.get('name', '?')[:55]:55} [{o.get('geography','?'):10}] dist={dv} {path}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    print(f"\nRunning distribution research on {len(targets)} opportunities...\n")
    succeeded = 0
    failed = 0

    for i, opp in enumerate(targets, 1):
        name = opp.get("name", "?")[:55]
        geo = opp.get("geography", "?")
        print(f"{i}/{len(targets)}: {name} [{geo}]")

        result = run_distribution_executor(opp)

        if result:
            opp.update(result)
            save_opp = {k: v for k, v in opp.items() if not k.startswith("_")}
            update_opportunity(save_opp["id"], save_opp)
            succeeded += 1
            dv = result.get("distribution_validated", "?")
            cac = (result.get("estimated_cac_logic") or "")[:60]
            print(f"  OK dist_validated={dv} | {cac}")
        else:
            failed += 1
            print(f"  [FAIL] No result returned (Tavily/API unavailable?)")

        if i < len(targets):
            time.sleep(1.0)

    print(f"\n{'='*60}")
    print(f"Distribution backfill: {succeeded} succeeded, {failed} failed")

    # Final coverage
    all_opps = read_all_opportunities()
    n_validated = sum(1 for o in all_opps if o.get("distribution_validated"))
    n_path = sum(1 for o in all_opps if o.get("first_10_customer_path"))
    n_cac = sum(1 for o in all_opps if o.get("estimated_cac_logic"))
    print(f"\nFinal distribution coverage ({total} total):")
    print(f"  distribution_validated:  {n_validated}/{total}")
    print(f"  first_10_customer_path:  {n_path}/{total}")
    print(f"  estimated_cac_logic:     {n_cac}/{total}")


if __name__ == "__main__":
    main()
