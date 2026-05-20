"""
rescore_all.py — Re-evaluate kill gate and re-score all stored opportunities.

Run from the project root:
    uv run python scripts/rescore_all.py

What it does:
1. Creates an automatic backup before touching anything.
2. Reads every record in data/opportunities/opportunities.jsonl.
3. Re-runs _infer_kill_answers() + evaluate_kill_gate() with the current (fixed) logic.
4. Re-runs score_opportunity() + apply_geo_adjustments() on survivors.
5. Re-applies portfolio normalisation.
6. Writes the result back atomically (tmp + os.replace).
7. Prints a before/after summary.

Dry-run mode (no writes):
    uv run python scripts/rescore_all.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ── Project root ──────────────────────────────────────────────────────────────

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT / "src"))

_OPPS_PATH = _ROOT / "data" / "opportunities" / "opportunities.jsonl"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_all(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    logger.warning("Skipping malformed line: %s", exc)
    return records


def _write_atomic(records: list[dict], path: Path) -> None:
    tmp = path.with_suffix(".rescore.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")
    os.replace(str(tmp), str(path))


def _bucket_score(score: float) -> str:
    if score >= 8.0:
        return "8+"
    if score >= 6.0:
        return "6-8"
    if score >= 4.0:
        return "4-6"
    return "<4"


# ── Main ──────────────────────────────────────────────────────────────────────

def main(dry_run: bool = False) -> None:
    # ── 0. Validate file exists ───────────────────────────────────────────────
    if not _OPPS_PATH.exists():
        logger.error("opportunities.jsonl not found at %s", _OPPS_PATH)
        sys.exit(1)

    # ── 1. Backup ─────────────────────────────────────────────────────────────
    if not dry_run:
        from opportunity_os.backup import create_backup
        result = create_backup("pre-rescore")
        if result:
            logger.info("Backup created: %s (%d records)", result["filename"], result["record_count"])
        else:
            logger.warning("Backup skipped (empty store).")

    # ── 2. Load ───────────────────────────────────────────────────────────────
    records = _read_all(_OPPS_PATH)
    logger.info("Loaded %d records", len(records))

    # ── 3. Imports ────────────────────────────────────────────────────────────
    from opportunity_os.pipelines.daily_run import _infer_kill_answers, _enrich_fields
    from opportunity_os.engines.kill_gate import evaluate_kill_gate
    from opportunity_os.engines.scoring_engine import score_opportunity, normalize_portfolio_scores
    from opportunity_os.geo_lens import apply_geo_adjustments

    # ── 4. Re-score ───────────────────────────────────────────────────────────
    before_killed = sum(1 for r in records if r.get("kill_decision"))
    before_scores = [r.get("final_score") for r in records if r.get("final_score") is not None]

    newly_killed: list[str] = []
    newly_survived: list[str] = []
    results: list[dict] = []

    for opp in records:
        was_killed = bool(opp.get("kill_decision"))

        # Preserve manual kills — humans reviewed these and overrode the kill gate.
        # Do not re-evaluate; do not score; carry forward as-is.
        if opp.get("manual_kill"):
            results.append(opp)
            continue

        # Enrich first (same order as daily_run)
        opp = _enrich_fields(opp)

        # Re-evaluate kill gate
        answers = _infer_kill_answers(opp)
        kg_result = evaluate_kill_gate(answers)

        opp = {
            **opp,
            "kill_decision": kg_result.kill_decision,
            "kill_criteria_passed": kg_result.passed_count,
        }
        if kg_result.kill_decision:
            opp["kill_reason"] = kg_result.kill_reason

        if kg_result.kill_decision and not was_killed:
            newly_killed.append(opp.get("name", opp.get("id", "?")))
            opp["stage"] = "killed"
            opp["portfolio_lane"] = "no"

        if not kg_result.kill_decision and was_killed:
            newly_survived.append(opp.get("name", opp.get("id", "?")))
            opp.pop("kill_reason", None)

        if not kg_result.kill_decision:
            opp = score_opportunity(opp)
            opp = apply_geo_adjustments(opp)

        results.append(opp)

    # Portfolio normalisation (live opps only)
    results = normalize_portfolio_scores(results)

    # ── 5. Summary ────────────────────────────────────────────────────────────
    after_killed = sum(1 for r in results if r.get("kill_decision"))
    after_scores = [r.get("final_score") for r in results if r.get("final_score") is not None and not r.get("kill_decision")]

    logger.info("")
    logger.info("══ Re-score summary ══════════════════════════════")
    logger.info("  Records:       %d", len(results))
    logger.info("  Killed before: %d  →  after: %d  (Δ %+d)",
                before_killed, after_killed, after_killed - before_killed)
    logger.info("  Live before:   %d  →  after: %d",
                len(records) - before_killed, len(results) - after_killed)

    if before_scores:
        logger.info("  Score (before): min=%.2f  max=%.2f  avg=%.2f",
                    min(before_scores), max(before_scores),
                    sum(before_scores) / len(before_scores))
    if after_scores:
        logger.info("  Score (after):  min=%.2f  max=%.2f  avg=%.2f",
                    min(after_scores), max(after_scores),
                    sum(after_scores) / len(after_scores))

    if newly_killed:
        logger.info("")
        logger.info("  Newly KILLED (%d):", len(newly_killed))
        for name in newly_killed[:20]:
            logger.info("    - %s", name[:80])

    if newly_survived:
        logger.info("")
        logger.info("  Newly SURVIVED (%d) — previously wrongly killed:", len(newly_survived))
        for name in newly_survived[:20]:
            logger.info("    - %s", name[:80])

    # Score distribution (live only)
    if after_scores:
        dist: dict[str, int] = {"8+": 0, "6-8": 0, "4-6": 0, "<4": 0}
        for s in after_scores:
            dist[_bucket_score(s)] += 1
        logger.info("")
        logger.info("  Score distribution (live): %s", dist)

    logger.info("══════════════════════════════════════════════════")
    logger.info("")

    # ── 6. Write ──────────────────────────────────────────────────────────────
    if dry_run:
        logger.info("[dry-run] No files written.")
        return

    _write_atomic(results, _OPPS_PATH)
    logger.info("Wrote %d records to %s", len(results), _OPPS_PATH.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-score all stored opportunities.")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
