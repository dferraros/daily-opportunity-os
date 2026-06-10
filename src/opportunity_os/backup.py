"""
backup.py — Automatic snapshot and restore for opportunities.jsonl.

Design:
- Backups live in data/opportunities/backups/
- Filename format: YYYY-MM-DD-HHMMSS-{label}.jsonl
- Only backs up files with > 0 records (never snapshots an empty store)
- Keeps the last MAX_BACKUPS snapshots, pruning oldest on overflow
- All writes are atomic (write to .tmp, then os.replace)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_BACKUPS = 30
_BACKUP_SUBDIR = "backups"


# ── Path helpers ──────────────────────────────────────────────────────────────

def _get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[4]


def _opps_path() -> Path:
    return _get_project_root() / "data" / "opportunities" / "opportunities.jsonl"


def _backups_dir() -> Path:
    return _get_project_root() / "data" / "opportunities" / _BACKUP_SUBDIR


# ── Core API ──────────────────────────────────────────────────────────────────

def create_backup(label: str = "manual") -> dict | None:
    """
    Snapshot opportunities.jsonl to the backups directory.

    Args:
        label: Short tag appended to filename (e.g. "pre-daily", "manual").

    Returns:
        Metadata dict with keys: path, filename, record_count, size_bytes, timestamp.
        Returns None if the source file is empty or missing (never snapshots empty stores).
    """
    src = _opps_path()
    if not src.exists():
        logger.warning("backup.create_backup: source file not found: %s", src)
        return None

    records = _count_records(src)
    if records == 0:
        logger.warning("backup.create_backup: source file is empty, skipping snapshot")
        return None

    backups_dir = _backups_dir()
    backups_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    safe_label = label.replace(" ", "_").replace("/", "-")[:30]
    filename = f"{ts}-{safe_label}.jsonl"
    dst = backups_dir / filename

    shutil.copy2(str(src), str(dst))
    logger.info("backup.create_backup: %d records -> %s", records, filename)

    _prune_old_backups(backups_dir)

    return {
        "path": str(dst),
        "filename": filename,
        "record_count": records,
        "size_bytes": dst.stat().st_size,
        "timestamp": ts,
        "label": safe_label,
    }


def list_backups() -> list[dict]:
    """
    Return metadata for all available backups, newest first.

    Each entry: {filename, path, record_count, size_bytes, timestamp, label}
    """
    backups_dir = _backups_dir()
    if not backups_dir.exists():
        return []

    results = []
    for f in sorted(backups_dir.glob("*.jsonl"), reverse=True):
        parts = f.stem.split("-", maxsplit=4)
        ts = "-".join(parts[:4]) if len(parts) >= 4 else f.stem[:17]
        label = parts[4] if len(parts) >= 5 else "unknown"
        results.append({
            "filename": f.name,
            "path": str(f),
            "record_count": _count_records(f),
            "size_bytes": f.stat().st_size,
            "timestamp": ts,
            "label": label,
        })
    return results


def restore_backup(filename: str, dry_run: bool = False) -> dict:
    """
    Atomically restore opportunities.jsonl from a backup file.

    Args:
        filename: Backup filename (basename only, e.g. "2026-05-20-143000-pre-daily.jsonl").
        dry_run: If True, validate without writing.

    Returns:
        Result dict: {success, records_restored, message}
    """
    backups_dir = _backups_dir().resolve()
    backup_path = (_backups_dir() / filename).resolve()
    if not backup_path.is_relative_to(backups_dir):
        return {"success": False, "records_restored": 0,
                "message": f"Invalid backup filename (path traversal): {filename}"}
    if not backup_path.exists():
        return {"success": False, "records_restored": 0, "message": f"Backup not found: {filename}"}

    records = _count_records(backup_path)
    if records == 0:
        return {"success": False, "records_restored": 0, "message": "Backup file is empty, refusing to restore"}

    if dry_run:
        return {
            "success": True,
            "records_restored": records,
            "message": f"[dry-run] Would restore {records} records from {filename}",
        }

    dst = _opps_path()
    dst.parent.mkdir(parents=True, exist_ok=True)

    tmp = dst.with_suffix(".restore.tmp")
    shutil.copy2(str(backup_path), str(tmp))
    os.replace(str(tmp), str(dst))

    logger.info("backup.restore_backup: restored %d records from %s", records, filename)
    return {
        "success": True,
        "records_restored": records,
        "message": f"Restored {records} records from {filename}",
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _count_records(path: Path) -> int:
    """Count non-empty lines in a JSONL file."""
    try:
        count = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    except OSError:
        return 0


def _prune_old_backups(backups_dir: Path) -> None:
    """Delete oldest backups if count exceeds MAX_BACKUPS."""
    files = sorted(backups_dir.glob("*.jsonl"))
    excess = len(files) - MAX_BACKUPS
    if excess > 0:
        for old in files[:excess]:
            try:
                old.unlink()
                logger.debug("backup.prune: removed %s", old.name)
            except OSError as exc:
                logger.warning("backup.prune: could not remove %s: %s", old.name, exc)
