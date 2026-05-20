"""Data loaders and shared path constants for Opportunity OS dashboard."""

import json
import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

from opportunity_os.storage import get_project_root as _get_project_root_str

PROJECT_ROOT = Path(_get_project_root_str())


def _parse_tam(val) -> float | None:
    """Return TAM as float, handling both numeric and legacy string formats like '$80.0M'."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().upper().lstrip("$").replace(",", "")
    multipliers = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
    for suffix, mult in multipliers.items():
        if s.endswith(suffix):
            try:
                return float(s[:-1]) * mult
            except ValueError:
                return None
    try:
        return float(s)
    except ValueError:
        return None


@st.cache_data(ttl=60)
def load_opportunities():
    path = PROJECT_ROOT / "data" / "opportunities" / "opportunities.jsonl"
    opps = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        opps.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.debug("Skipping malformed opportunities line: %s", exc)
    return opps


@st.cache_data(ttl=60)
def load_automation_runs():
    path = PROJECT_ROOT / "data" / "automation_runs.jsonl"
    runs = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        runs.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.debug("Skipping malformed automation_runs line: %s", exc)
    return runs


@st.cache_data(ttl=60)
def load_machine_metrics():
    path = PROJECT_ROOT / "data" / "machine_metrics.jsonl"
    metrics = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        metrics.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.debug("Skipping malformed machine_metrics line: %s", exc)
    return metrics


@st.cache_data(ttl=60)
def load_pipeline_failures():
    path = PROJECT_ROOT / "data" / "pipeline_failures.jsonl"
    failures = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        failures.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.debug("Skipping malformed pipeline_failures line: %s", exc)
    return failures


@st.cache_data(ttl=60)
def load_weekly_quotas():
    import yaml
    path = PROJECT_ROOT / "config" / "weekly_quotas.yaml"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
