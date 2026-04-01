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

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


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
    """Generate opp_{date}_{geo}_{hash4} id from opportunity dict."""
    date_str = datetime.now().strftime("%Y%m%d")
    geo = (opp.get("geography") or "xx")[:3].lower().replace(" ", "")
    name_hash = abs(hash(opp.get("name", ""))) % 10000
    return f"opp_{date_str}_{geo}_{name_hash:04d}"


# -- Core JSONL I/O -----------------------------------------------------------

def append_opportunity(opp: dict, path: str = None) -> str:
    """
    Append one opportunity to the JSONL store.

    - Auto-generates id if missing.
    - Sets first_seen and last_updated if not already present.
    - Returns the opportunity ID.
    """
    if path is None:
        path = _default_opps_path()
    _ensure_dir(path)

    now_iso = datetime.now().isoformat()

    # Assign id
    if not opp.get("id"):
        opp["id"] = _make_id(opp)

    # Timestamps
    if not opp.get("first_seen"):
        opp["first_seen"] = now_iso
    opp["last_updated"] = now_iso

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(opp, default=str) + "\n")

    return opp["id"]


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
                except json.JSONDecodeError:
                    continue
    return opps


# -- Query helpers ------------------------------------------------------------

def query_by_geo(geography: str, path: str = None) -> list[dict]:
    """Return opportunities filtered by geography (case-insensitive)."""
    all_opps = read_all_opportunities(path)
    geo_lower = geography.lower().strip()
    return [o for o in all_opps if (o.get("geography") or "").lower().strip() == geo_lower]


def query_by_score(min_score: float = 6.0, path: str = None) -> list[dict]:
    """Return opportunities with attractiveness_score (or final_score) >= min_score, sorted desc."""
    all_opps = read_all_opportunities(path)
    results = []
    for o in all_opps:
        score = o.get("attractiveness_score") or o.get("final_score")
        if score is not None and float(score) >= min_score:
            results.append(o)
    results.sort(
        key=lambda o: float(o.get("attractiveness_score") or o.get("final_score") or 0),
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
    Rewrites the full JSONL file (dataset is small).
    Returns True if found and updated, False otherwise.
    """
    if path is None:
        path = _default_opps_path()
    all_opps = read_all_opportunities(path)
    found = False
    for opp in all_opps:
        if opp.get("id") == opp_id:
            opp.update(updates)
            opp["last_updated"] = datetime.now().isoformat()
            found = True
            break
    if not found:
        return False
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        for opp in all_opps:
            f.write(json.dumps(opp, default=str) + "\n")
    return True


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
                    return opp["id"]
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
    metrics.setdefault("timestamp", datetime.now().isoformat())
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics, default=str) + "\n")
