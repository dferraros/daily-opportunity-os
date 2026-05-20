"""
Normalize final_score distribution across ALL stored opportunities.

Problem: 64 opps scored 6.8-9.8 with mean 7.97 — no discrimination.
Fix: Remap to 2.0-10.0 range preserving relative rankings. Zero API cost.

Usage:
    cd .worktrees/daily-opportunity-os
    PYTHONPATH=src uv run python scripts/normalize_existing_scores.py
    PYTHONPATH=src uv run python scripts/normalize_existing_scores.py --dry-run
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PROJECT_ROOT = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Normalize opportunity scores")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without writing")
    parser.add_argument("--output-min", type=float, default=2.0)
    parser.add_argument("--output-max", type=float, default=10.0)
    args = parser.parse_args()

    from opportunity_os.engines.scoring_engine import normalize_portfolio_scores

    opps_path = PROJECT_ROOT / "data" / "opportunities" / "opportunities.jsonl"
    if not opps_path.exists():
        print(f"ERROR: {opps_path} not found")
        sys.exit(1)

    opps = []
    with open(opps_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    opps.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    print(f"Loaded {len(opps)} opportunities")

    # Pre-normalization stats
    live = [o for o in opps if o.get("final_score") and not o.get("kill_decision")]
    if not live:
        print("No scored, non-killed opportunities found. Nothing to normalize.")
        return

    raw_scores = sorted([float(o["final_score"]) for o in live])
    mean_raw = sum(raw_scores) / len(raw_scores)
    print(f"\nBefore normalization ({len(live)} live opps):")
    print(f"  Range: {raw_scores[0]:.4f} - {raw_scores[-1]:.4f}")
    print(f"  Mean:  {mean_raw:.4f}")
    print(f"  Distribution:")
    for lo, hi in [(9, 10), (8, 9), (7, 8), (6, 7), (5, 6), (0, 5)]:
        count = sum(1 for s in raw_scores if lo <= s < hi or (hi == 10 and s == 10))
        bar = "#" * count
        print(f"    {lo}-{hi}: {bar} ({count})")

    if args.dry_run:
        print("\n[DRY RUN] Would normalize. Run without --dry-run to apply.")
        # Show what the scores would become
        import copy
        opps_copy = copy.deepcopy(opps)
        normalize_portfolio_scores(opps_copy, output_min=args.output_min, output_max=args.output_max)
        new_live = [o for o in opps_copy if o.get("final_score") and not o.get("kill_decision")]
        new_scores = sorted([float(o["final_score"]) for o in new_live])
        new_mean = sum(new_scores) / len(new_scores)
        print(f"\nAfter normalization (projected):")
        print(f"  Range: {new_scores[0]:.4f} - {new_scores[-1]:.4f}")
        print(f"  Mean:  {new_mean:.4f}")
        print(f"\nTop 10 scores (before -> after):")
        combined = sorted(zip(raw_scores, new_scores), reverse=True)[:10]
        for raw, norm in combined:
            print(f"  {raw:.4f} -> {norm:.4f}")
        return

    # Backup before writing
    backup_path = opps_path.with_suffix(".jsonl.pre-normalize")
    with open(backup_path, "w", encoding="utf-8") as f:
        for opp in opps:
            f.write(json.dumps(opp, default=str) + "\n")
    print(f"\nBacked up to: {backup_path.name}")

    # Apply normalization
    opps = normalize_portfolio_scores(
        opps, output_min=args.output_min, output_max=args.output_max
    )

    # Write back
    with open(opps_path, "w", encoding="utf-8") as f:
        for opp in opps:
            f.write(json.dumps(opp, default=str) + "\n")

    # Post-normalization stats
    new_live = [o for o in opps if o.get("final_score") and not o.get("kill_decision")]
    new_scores = sorted([float(o["final_score"]) for o in new_live])
    new_mean = sum(new_scores) / len(new_scores)
    print(f"\nAfter normalization ({len(new_live)} live opps):")
    print(f"  Range: {new_scores[0]:.4f} - {new_scores[-1]:.4f}")
    print(f"  Mean:  {new_mean:.4f}")
    print(f"  Distribution:")
    for lo, hi in [(9, 10), (8, 9), (7, 8), (6, 7), (5, 6), (2, 5)]:
        count = sum(1 for s in new_scores if lo <= s < hi or (hi == 10 and s == 10))
        bar = "#" * count
        print(f"    {lo}-{hi}: {bar} ({count})")

    # Show top + bottom
    print(f"\nTop 5 opportunities:")
    top5 = sorted(new_live, key=lambda x: float(x["final_score"]), reverse=True)[:5]
    for o in top5:
        raw = o.get("raw_final_score", "?")
        print(f"  {float(o['final_score']):.2f} (was {raw:.4f if isinstance(raw, float) else raw})"
              f" — {o.get('name', '?')[:55]} [{o.get('geography', '?')}]")

    print(f"\nBottom 5 opportunities:")
    bot5 = sorted(new_live, key=lambda x: float(x["final_score"]))[:5]
    for o in bot5:
        raw = o.get("raw_final_score", "?")
        print(f"  {float(o['final_score']):.2f} (was {raw:.4f if isinstance(raw, float) else raw})"
              f" — {o.get('name', '?')[:55]} [{o.get('geography', '?')}]")

    print(f"\nDone. {len(new_live)} scores normalized. "
          f"Original scores in 'raw_final_score' field.")


if __name__ == "__main__":
    main()
