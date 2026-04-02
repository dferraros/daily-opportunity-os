"""
AI Backfill — rescores all opportunities that lack ai_scored_at
(heuristically-scored or never scored) using Claude Haiku.

Usage:
    cd .worktrees/daily-opportunity-os
    PYTHONPATH=src python scripts/run_ai_backfill.py

Flags:
    --dry-run   Print what would be rescored without writing anything
    --force     Rescore ALL records, even those already AI-scored
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
# Resolve .env relative to repo root (two levels up from scripts/)
_repo_root = Path(__file__).parent.parent
load_dotenv(dotenv_path=_repo_root / ".env", override=True)

from opportunity_os.storage import read_all_opportunities, update_opportunity
from opportunity_os.ai_scorer import score_dimensions_with_ai
from opportunity_os.engines.scoring_engine import score_opportunity


def main():
    parser = argparse.ArgumentParser(description="AI backfill for opportunity scoring")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be rescored without writing")
    parser.add_argument("--force", action="store_true", help="Rescore ALL records including already AI-scored ones")
    args = parser.parse_args()

    opps = read_all_opportunities()
    total = len(opps)

    if args.force:
        targets = opps
        print(f"FORCE mode: rescoring all {total} opportunities")
    else:
        targets = [o for o in opps if not o.get("ai_scored_at")]
        print(f"Found {len(targets)} unscored opportunities (of {total} total)")

    if not targets:
        print("Nothing to backfill. All opportunities already AI-scored.")
        print("Use --force to rescore everything.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Would rescore:")
        for o in targets:
            print(f"  - {o.get('name', '?')[:60]} [{o.get('geography', '?')}] score={o.get('final_score', '?')}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check your .env file.")
        sys.exit(1)

    print(f"\nStarting AI backfill for {len(targets)} opportunities...\n")
    succeeded = 0
    failed = 0
    score_deltas = []

    for i, opp in enumerate(targets, 1):
        name = opp.get("name", "?")[:55]
        old_score = opp.get("final_score")

        # Mark for rescore if already has ai_scored_at (force mode)
        if args.force and opp.get("ai_scored_at"):
            opp["rescore_requested"] = True

        print(f"[{i}/{len(targets)}] {name}...")
        scored = score_dimensions_with_ai(opp)

        if scored.get("ai_scored_at"):
            # Re-run weighted scoring to update final_score
            scored = score_opportunity(scored)
            new_score = scored.get("final_score")

            if old_score is not None and new_score is not None:
                delta = round(new_score - old_score, 2)
                score_deltas.append((name, old_score, new_score, delta))

            update_opportunity(scored["id"], scored)
            succeeded += 1
            print(f"  → {old_score} → {new_score} (Δ{delta:+.2f})" if old_score else f"  → {new_score}")
        else:
            failed += 1
            print(f"  [FAIL] Heuristic fallback used (check API key or rate limit)")

        # Rate limit: 0.5s between calls (Haiku allows ~60 RPM)
        if i < len(targets):
            time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"Backfill complete: {succeeded} succeeded, {failed} failed")

    if score_deltas:
        print(f"\nScore changes (AI vs heuristic):")
        score_deltas.sort(key=lambda x: abs(x[3]), reverse=True)
        for name, old, new, delta in score_deltas[:15]:
            bar = "▲" if delta > 0 else "▼"
            print(f"  {bar} {delta:+.2f}  {name[:50]}  ({old} → {new})")

        upgrades = [d for _, _, _, d in score_deltas if d >= 0.5]
        downgrades = [d for _, _, _, d in score_deltas if d <= -0.5]
        print(f"\n  Significant upgrades (≥+0.5): {len(upgrades)}")
        print(f"  Significant downgrades (≤-0.5): {len(downgrades)}")


if __name__ == "__main__":
    main()
