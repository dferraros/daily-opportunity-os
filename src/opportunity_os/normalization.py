"""
Normalization -- converts raw signal dicts into validated Opportunity objects.

Raw signals come from agents and web research in various shapes.
This module enforces the schema and fills in defaults before scoring.

The normalization pipeline:
1. Clean and standardize field names (snake_case, strip whitespace)
2. Apply geo context (infer currency, WTP adjustments)
3. Auto-fill computable defaults (id, timestamps, stage)
4. Validate against Opportunity schema via Pydantic
5. Return validated Opportunity or list of validation errors
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

# -- Alias maps ---------------------------------------------------------------

FIELD_ALIASES: dict[str, str] = {
    "title": "name",
    "opportunity_name": "name",
    "market": "vertical",
    "geo": "geography",
    "country": "geography",
    "region": "geography",
    "tam_usd": "tam",
    "tam_usd_estimate": "tam",
    "score": "attractiveness_score",
    "pain": "pain_severity",
    "pain_level": "pain_severity",
    "competition": "competition_intensity",
    "mvp_time": "speed_to_mvp",
    "revenue_path": "path_to_first_revenue",
}

GEO_NORMALIZER: dict[str, str] = {
    "ve": "venezuela",
    "vzla": "venezuela",
    "ven": "venezuela",
    "co": "colombia",
    "col": "colombia",
    "mx": "mexico",
    "mex": "mexico",
    "ar": "argentina",
    "arg": "argentina",
    "br": "brazil",
    "bra": "brazil",
    "es": "spain",
    "esp": "spain",
    "latam": "latam",
    "latin america": "latam",
    "global": "global",
}

# Geography values accepted by the Opportunity Literal field
_VALID_GEOS = {"global", "latam", "venezuela", "spain", "us", "other"}


# -- Normalization steps ------------------------------------------------------

def normalize_field_names(raw: dict) -> dict:
    """
    Apply FIELD_ALIASES mapping and convert all keys to snake_case.
    Strips leading/trailing whitespace from string values.
    """
    result = {}
    for key, value in raw.items():
        # Normalise key: lowercase, spaces -> underscores
        norm_key = key.lower().replace(" ", "_").strip("_")
        # Apply alias if present
        canonical_key = FIELD_ALIASES.get(norm_key, norm_key)
        # Strip string values
        if isinstance(value, str):
            value = value.strip()
        result[canonical_key] = value
    return result


def normalize_geography(raw: dict) -> dict:
    """
    Normalize geography field using GEO_NORMALIZER.
    Falls back to 'global' if not recognized.
    """
    raw = dict(raw)
    geo_raw = (raw.get("geography") or "").lower().strip()
    normalized = GEO_NORMALIZER.get(geo_raw, None)

    if normalized is None:
        # Try partial match against valid geo names
        for valid_geo in _VALID_GEOS:
            if geo_raw == valid_geo or geo_raw.startswith(valid_geo):
                normalized = valid_geo
                break

    if normalized not in _VALID_GEOS:
        normalized = "global"

    raw["geography"] = normalized
    return raw


def infer_missing_fields(raw: dict) -> dict:
    """
    Infer required narrative fields from available signal fields.
    Allows harvested signals to omit problem_statement/target_customer/trigger_signal
    while still passing validation.
    """
    raw = dict(raw)

    # problem_statement <- raw_text / description / raw_notes if missing
    if not raw.get("problem_statement"):
        for src in ("raw_text", "description", "raw_notes"):
            if raw.get(src):
                raw["problem_statement"] = raw[src]
                break

    # trigger_signal <- raw_text / raw_notes / description if missing
    if not raw.get("trigger_signal"):
        for src in ("raw_text", "raw_notes", "description"):
            if raw.get(src):
                raw["trigger_signal"] = str(raw[src])[:300]
                break

    # target_customer <- infer from vertical + geography if missing
    if not raw.get("target_customer"):
        vertical = raw.get("vertical", "")
        geo = raw.get("geography", "global")
        geo_label = {"venezuela": "Venezuelan", "latam": "LATAM", "spain": "Spanish",
                     "colombia": "Colombian", "mexico": "Mexican", "global": "global"}.get(geo, geo.capitalize())
        vertical_label = vertical.replace("_", " ").title() if vertical else "business"
        raw["target_customer"] = f"{geo_label} {vertical_label} operators and founders"

    return raw


def fill_defaults(raw: dict) -> dict:
    """
    Fill in computable defaults before validation:
    - id: auto-generate if missing
    - first_seen: prefer harvested_at from raw signal, fallback to now
    - last_updated: always set to now
    - stage: 'scout' if missing
    - kill_decision: False if missing
    - source: 'manual' if missing
    """
    raw = dict(raw)
    now_iso = datetime.now().isoformat()

    if not raw.get("id"):
        date_str = datetime.now().strftime("%Y%m%d")
        geo = (raw.get("geography") or "xx")[:3].lower()
        raw["id"] = f"opp_{date_str}_{geo}_{str(uuid.uuid4())[:8]}"

    if not raw.get("first_seen"):
        # Preserve the harvested_at timestamp from raw signals as the discovery date
        raw["first_seen"] = raw.get("harvested_at") or now_iso

    raw["last_updated"] = now_iso

    if not raw.get("stage"):
        raw["stage"] = "scout"

    if "kill_decision" not in raw:
        raw["kill_decision"] = False

    if not raw.get("source"):
        raw["source"] = "manual"

    return raw


def validate_opportunity(raw: dict) -> tuple:
    """
    Validate raw dict against the Opportunity Pydantic model.

    Returns:
        (Opportunity, [])          on success
        (None, [error_msg, ...])   on ValidationError
    """
    from opportunity_os.models import Opportunity
    from pydantic import ValidationError

    try:
        opp = Opportunity.model_validate(raw)
        return opp, []
    except ValidationError as exc:
        errors = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            errors.append(f"{loc}: {err['msg']} (got {err.get('input')!r})")
        return None, errors


def normalize_signal(raw: dict) -> tuple:
    """
    Main entry point: chain normalize_field_names -> normalize_geography
    -> fill_defaults -> validate_opportunity.

    Returns:
        (Opportunity, [])          on success
        (None, [error_msg, ...])   on failure
    """
    step1 = normalize_field_names(raw)
    step2 = normalize_geography(step1)
    step3 = infer_missing_fields(step2)
    step4 = fill_defaults(step3)
    return validate_opportunity(step4)


def normalize_signals_batch(raws: list) -> tuple:
    """
    Process a list of raw signal dicts.

    Returns:
        (valid_opportunities: list[Opportunity], failed_records: list[dict])
        Failed records include the original raw dict plus an 'errors' key.
    """
    valid = []
    failed = []
    for raw in raws:
        opp, errs = normalize_signal(raw)
        if opp is not None:
            valid.append(opp)
        else:
            failed_record = dict(raw)
            failed_record["errors"] = errs
            failed.append(failed_record)
    return valid, failed
