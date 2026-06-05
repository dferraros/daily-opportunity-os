"""
Storage -- JSONL-based persistence for opportunities and machine metrics.

Design choices:
- JSONL (JSON Lines): one JSON object per line, appendable, git-friendly, no infrastructure
- All reads are full scans (small dataset, simplicity wins over indexing)
- Deduplication on write: same name+geography within 7 days = update, not insert
- Immutable history: score changes go to opportunity_history.jsonl, not mutation

File paths (relative to project root):
  data/opportunities/opportunities.jsonl
  data/opportunities/opportunity_history.jsonl
  data/machine_metrics.jsonl
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


# -- Path helpers -------------------------------------------------------------

def get_project_root() -> str:
    """Find project root by walking up from __file__ until pyproject.toml is found."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return str(parent)
    # Fallback: two levels up from this file (src/opportunity_os/ -> project root)
    return str(Path(__file__).resolve().parent.parent.parent)


def _default_opps_path() -> str:
    return os.path.join(get_project_root(), "data", "opportunities", "opportunities.jsonl")


def _default_history_path() -> str:
    return os.path.join(get_project_root(), "data", "opportunities", "opportunity_history.jsonl")


def _default_metrics_path() -> str:
    return os.path.join(get_project_root(), "data", "machine_metrics.jsonl")


def _ensure_dir(file_path: str) -> None:
    """Create parent directories for file_path if they do not exist."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


# -- ID generation ------------------------------------------------------------

def _make_id(opp: dict) -> str:
    """Generate opp_{date}_{geo}_{hash4} id from opportunity dict.

    Uses hashlib.md5 instead of hash() for deterministic output regardless
    of PYTHONHASHSEED (Python randomizes hash() per process since 3.3).
    """
    date_str = datetime.now().strftime("%Y%m%d")
    geo = (opp.get("geography") or "xx")[:3].lower().replace(" ", "")
    name = opp.get("name", "")
    name_hash = int(
        hashlib.md5(name.encode("utf-8"), usedforsecurity=False).hexdigest(), 16
    ) % 10000
    return f"opp_{date_str}_{geo}_{name_hash:04d}"


# -- Core JSONL I/O -----------------------------------------------------------

def append_opportunity(opp: dict, path: str = None) -> str:
    """
    Append one opportunity to the JSONL store.

    - Auto-generates id if missing.
    - Sets first_seen and last_updated if not already present.
    - Returns the opportunity ID.
    - Does NOT mutate the caller's dict.
    """
    if path is None:
        path = _default_opps_path()
    _ensure_dir(path)

    now_iso = datetime.now().isoformat()
    opp_id = opp.get("id") or _make_id(opp)

    record = {
        **opp,
        "id": opp_id,
        "first_seen": opp.get("first_seen") or now_iso,
        "last_updated": now_iso,
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")

    return opp_id


def read_all_opportunities(path: str = None) -> list[dict]:
    """Read all opportunities from JSONL. Returns list of dicts (empty list if file missing)."""
    if path is None:
        path = _default_opps_path()
    if not os.path.exists(path):
        return []
    opps = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    opps.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    logger.warning("Skipping malformed JSON line in %s: %s", path, exc)
    return opps


# -- Query helpers ------------------------------------------------------------

def query_by_geo(geography: str, path: str = None) -> list[dict]:
    """Return opportunities filtered by geography (case-insensitive)."""
    all_opps = read_all_opportunities(path)
    geo_lower = geography.lower().strip()
    return [o for o in all_opps if (o.get("geography") or "").lower().strip() == geo_lower]


def query_by_score(min_score: float = 6.0, path: str = None) -> list[dict]:
    """Return opportunities with final_score (or attractiveness_score fallback) >= min_score, sorted desc."""
    all_opps = read_all_opportunities(path)
    results = []
    for o in all_opps:
        score = o.get("final_score") or o.get("attractiveness_score")
        if score is not None and float(score) >= min_score:
            results.append(o)
    results.sort(
        key=lambda o: float(o.get("final_score") or o.get("attractiveness_score") or 0),
        reverse=True,
    )
    return results


def query_by_stage(stage: str, path: str = None) -> list[dict]:
    """Return opportunities filtered by stage field (case-insensitive)."""
    all_opps = read_all_opportunities(path)
    stage_lower = stage.lower().strip()
    return [o for o in all_opps if (o.get("stage") or "").lower().strip() == stage_lower]


def query_by_lane(lane: str, path: str = None) -> list[dict]:
    """Return opportunities filtered by portfolio_lane (case-insensitive)."""
    all_opps = read_all_opportunities(path)
    lane_lower = lane.lower().strip()
    return [o for o in all_opps if (o.get("portfolio_lane") or "").lower().strip() == lane_lower]


def get_opportunity_by_id(opp_id: str, path: str = None) -> dict | None:
    """Return single opportunity dict by ID, or None if not found."""
    for opp in read_all_opportunities(path):
        if opp.get("id") == opp_id:
            return opp
    return None


def update_opportunity(opp_id: str, updates: dict, path: str = None) -> bool:
    """
    Update fields of an existing opportunity by ID.
    Rewrites the full JSONL file via write-to-temp + atomic rename to
    prevent corruption on crash mid-write.
    Returns True if found and updated, False otherwise.
    """
    if path is None:
        path = _default_opps_path()
    all_opps = read_all_opportunities(path)
    found = False
    updated_opps = []
    for opp in all_opps:
        if opp.get("id") == opp_id:
            opp = {**opp, **updates, "last_updated": datetime.now().isoformat()}
            found = True
        updated_opps.append(opp)
    if not found:
        return False
    all_opps = updated_opps
    _ensure_dir(path)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for opp in all_opps:
            f.write(json.dumps(opp, default=str) + "\n")
    os.replace(tmp_path, path)
    return True


def replace_all_opportunities(opps: list[dict], path: str = None) -> int:
    """Atomically replace the entire opportunities store.

    Writes all records to a .tmp file, then os.replace() for crash safety.
    Returns number of records written.
    Does NOT mutate the input list or any dicts inside it.
    """
    if path is None:
        path = _default_opps_path()
    _ensure_dir(path)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for opp in opps:
            f.write(json.dumps(opp, default=str) + "\n")
    os.replace(tmp_path, path)
    return len(opps)


# -- History / audit trail ----------------------------------------------------

def append_score_history(
    opp_id: str,
    old_score: float,
    new_score: float,
    reason: str = "",
    path: str = None,
) -> None:
    """Append a score change event to opportunity_history.jsonl."""
    if path is None:
        path = _default_history_path()
    _ensure_dir(path)
    record = {
        "opp_id": opp_id,
        "timestamp": datetime.now().isoformat(),
        "old_score": old_score,
        "new_score": new_score,
        "delta": round(new_score - old_score, 4),
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def append_opp_score_history(opp_id: str, new_score: float, path: str = None) -> bool:
    """
    Append a score entry to the opportunity's own score_history list field.

    Format: {"date": "YYYY-MM-DD", "score": float, "delta": float}
    Delta = new_score - previous score. First entry delta = 0.

    Single file scan: reads all opps once, mutates the matching record in-place,
    then writes back atomically — avoiding the double-scan of get_opportunity_by_id
    followed by update_opportunity.

    Returns True if updated, False if opp not found.
    """
    if path is None:
        path = _default_opps_path()
    all_opps = read_all_opportunities(path)

    found = False
    updated_opps = []
    for opp in all_opps:
        if opp.get("id") == opp_id and not found:
            found = True
            today = datetime.now().strftime("%Y-%m-%d")
            history = list(opp.get("score_history") or [])

            if history and history[-1].get("date") == today:
                return True

            prev_score = history[-1]["score"] if history else new_score
            delta = round(new_score - prev_score, 4)
            history = [*history, {"date": today, "score": round(new_score, 4), "delta": delta}]
            opp = {**opp, "score_history": history, "last_updated": datetime.now().isoformat()}
        updated_opps.append(opp)
    all_opps = updated_opps

    if not found:
        return False

    _ensure_dir(path)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for opp in all_opps:
            f.write(json.dumps(opp, default=str) + "\n")
    os.replace(tmp_path, path)
    return True


# -- Deduplication ------------------------------------------------------------

def dedupe_check(
    name: str,
    geography: str,
    path: str = None,
    days: int = 7,
) -> str | None:
    """
    Return existing opportunity ID if name+geography exact match found within `days` days.
    Returns None if no duplicate found.

    V1: exact match (lowercase + strip) only.
    """
    all_opps = read_all_opportunities(path)
    cutoff = datetime.now() - timedelta(days=days)
    name_norm = name.lower().strip()
    geo_norm = geography.lower().strip()

    for opp in all_opps:
        # Check name + geography match
        if (
            opp.get("name", "").lower().strip() != name_norm
            or (opp.get("geography") or "").lower().strip() != geo_norm
        ):
            continue
        # Check recency
        first_seen_raw = opp.get("first_seen")
        if first_seen_raw:
            try:
                # Handle ISO strings with or without timezone
                ts_str = str(first_seen_raw).split("+")[0].replace("Z", "")
                first_seen_dt = datetime.fromisoformat(ts_str)
                if first_seen_dt >= cutoff:
                    return opp.get("id")
            except (ValueError, AttributeError):
                # Cannot parse date -- treat as match to be safe
                return opp.get("id")
        else:
            return opp.get("id")
    return None


# -- Machine metrics ----------------------------------------------------------

def append_machine_metrics(metrics: dict, path: str = None) -> None:
    """Append a machine run metrics record to data/machine_metrics.jsonl."""
    if path is None:
        path = _default_metrics_path()
    _ensure_dir(path)
    record = {"timestamp": datetime.now().isoformat(), **metrics}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
