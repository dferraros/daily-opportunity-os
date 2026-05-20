"""
run_free_research_backfill.py — Populate free_research_at + pain_signal_count
on all live opps that are missing it.

Previously, free research was skipped for opps with research_executed_at (a bug).
This script backfills those 78+ opps that were incorrectly excluded.

Run from project root:
    uv run python scripts/run_free_research_backfill.py

Dry-run (no writes):
    uv run python scripts/run_free_research_backfill.py --dry-run

Rate limiting: 0.5s sleep between opps. ~95 opps = ~60-90s total.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT / "src"))

_OPPS_PATH = _ROOT / "data" / "opportunities" / "opportunities.jsonl"


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
    tmp = path.with_suffix(".backfill.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")
    os.replace(str(tmp), str(path))


def main(dry_run: bool = False) -> None:
    if not _OPPS_PATH.exists():
        logger.error("opportunities.jsonl not found at %s", _OPPS_PATH)
        sys.exit(1)

    from opportunity_os.free_research import research_opportunity_free

    records = _read_all(_OPPS_PATH)
    live = [r for r in records if not r.get("kill_decision")]
    needs_free = [r for r in live if not r.get("free_research_at")]

    logger.info("Total records: %d | Live: %d | Missing free_research_at: %d",
                len(records), len(live), len(needs_free))

    if not needs_free:
        logger.info("All live opps already have free_research_at — nothing to do.")
        return

    updated_map: dict[str, dict] = {}
    success_count = 0
    error_count = 0

    for i, opp in enumerate(needs_free, 1):
        name = opp.get("name", opp.get("id", "?"))[:50]
        logger.info("[%d/%d] %s", i, len(needs_free), name)
        try:
            updates = research_opportunity_free(opp)
            pain_count = updates.get("pain_signal_count", 0)
            logger.info("  pain_signal_count=%d  new_fields=%d",
                        pain_count, len([k for k in updates if k not in opp]))
            updated_map[opp["id"]] = {**opp, **updates}
            success_count += 1
        except Exception as exc:
            logger.warning("  ERROR: %s", exc)
            error_count += 1
        time.sleep(0.5)

    logger.info("")
    logger.info("Backfill complete: %d succeeded, %d errors", success_count, error_count)

    if dry_run:
        logger.info("[dry-run] No files written.")
        return

    if not updated_map:
        logger.info("No updates to write.")
        return

    # Merge updates back into full record list (preserves killed opps unchanged)
    result = []
    for r in records:
        if r.get("id") in updated_map:
            result.append(updated_map[r["id"]])
        else:
            result.append(r)

    _write_atomic(result, _OPPS_PATH)
    logger.info("Wrote %d records to %s", len(result), _OPPS_PATH.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill free research on all live opps.")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
