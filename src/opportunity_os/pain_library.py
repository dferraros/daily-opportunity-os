"""
Pain Library — persistent store of pain clusters extracted from researched opportunities.

Each entry in data/pain_library.jsonl represents one pain cluster observed across
one or more opportunities. Clusters are keyed by (geography, wedge_category, pain_theme).

Purpose: As more opportunities are researched, recurring pain patterns compound.
The weekly-review skill reads this library to find conviction areas.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def _project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[4]


def _library_path() -> Path:
    return _project_root() / "data" / "pain_library.jsonl"


def upsert_pain_cluster(opp: dict) -> bool:
    """
    Upsert pain cluster data from a researched opportunity into pain_library.jsonl.

    Only writes if the opp has research_executed_at and pain_validation_score.
    Returns True if written, False if skipped.
    """
    if not opp.get("research_executed_at"):
        return False
    if opp.get("pain_validation_score") is None:
        return False

    geo = opp.get("geography", "global")
    wedge = opp.get("venezuela_wedge_category") or opp.get("vertical") or "general"
    name = opp.get("name", "unknown")
    pain_score = opp.get("pain_validation_score", 0)
    phrases = opp.get("exact_customer_phrases") or []
    workarounds = opp.get("workarounds_found") or []
    sources = opp.get("pain_evidence_sources") or []

    # Cluster key: geographic + wedge + opportunity name
    cluster_key = f"{geo}:{wedge}:{name[:40]}"

    entry = {
        "cluster_key": cluster_key,
        "opportunity_id": opp.get("id", ""),
        "opportunity_name": name,
        "geography": geo,
        "wedge_category": wedge,
        "pain_validation_score": pain_score,
        "exact_customer_phrases": phrases,
        "workarounds_found": workarounds,
        "pain_evidence_sources": sources,
        "first_seen": opp.get("first_seen") or datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().isoformat(),
    }

    lib_path = _library_path()
    lib_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing, update or append
    existing = {}
    if lib_path.exists():
        with open(lib_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        existing[rec.get("cluster_key", "")] = rec
                    except json.JSONDecodeError:
                        pass

    existing[cluster_key] = entry

    with open(lib_path, "w", encoding="utf-8") as f:
        for rec in existing.values():
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")

    return True


def get_top_pain_clusters(geo: Optional[str] = None, top_n: int = 10) -> list[dict]:
    """Return top pain clusters by pain_validation_score, optionally filtered by geo."""
    lib_path = _library_path()
    if not lib_path.exists():
        return []

    clusters = []
    with open(lib_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                    if geo and rec.get("geography") != geo:
                        continue
                    clusters.append(rec)
                except json.JSONDecodeError:
                    continue

    return sorted(clusters, key=lambda x: float(x.get("pain_validation_score") or 0), reverse=True)[:top_n]


def get_library_stats() -> dict:
    """Return summary stats about the pain library."""
    lib_path = _library_path()
    if not lib_path.exists():
        return {"total_clusters": 0, "geos": {}, "avg_pain_score": 0.0}

    clusters = []
    with open(lib_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    clusters.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if not clusters:
        return {"total_clusters": 0, "geos": {}, "avg_pain_score": 0.0}

    geos: dict = {}
    scores = []
    for c in clusters:
        g = c.get("geography", "global")
        geos[g] = geos.get(g, 0) + 1
        s = c.get("pain_validation_score")
        if s is not None:
            scores.append(float(s))

    return {
        "total_clusters": len(clusters),
        "geos": geos,
        "avg_pain_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
    }
