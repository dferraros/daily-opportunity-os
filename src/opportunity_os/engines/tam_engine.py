"""
TAM Engine — 4 methods for market size estimation with geo adjustments.

Method selection guide:
- bottom_up: preferred when you can count real customers × price
- top_down: quick sizing when market reports exist
- proxy: when you have an analog market with different scale
- competitor_revenue: cross-check when competitor revenue is known

Always run 2 methods and take the lower estimate. Overconfidence kills.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Geography multipliers relative to US market
# ---------------------------------------------------------------------------

GEO_TAM_MULTIPLIERS: dict[str, float] = {
    "venezuela": 0.008,   # ~0.8% of US market
    "colombia": 0.04,     # ~4% of US market
    "mexico": 0.12,       # ~12% of US market
    "argentina": 0.025,
    "spain": 0.06,
    "latam": 0.20,        # total LATAM addressable
    "global": 1.0,
}


def _apply_geo(value: float, geography: str) -> float:
    """Multiply value by the geo multiplier (default 1.0 for unknown geos)."""
    mult = GEO_TAM_MULTIPLIERS.get(geography.lower(), 1.0)
    return value * mult


# ---------------------------------------------------------------------------
# Method 1 — Bottom-up (preferred)
# ---------------------------------------------------------------------------

def tam_bottom_up(
    target_customers: int,
    annual_price_usd: float,
    conversion_rate: float = 0.02,
    geography_multiplier: float = 1.0,
) -> dict:
    """
    Preferred method. Count real buyers × real price.

    Returns: {method, tam_usd, sam_usd, som_usd, assumptions}
    SAM = TAM × 0.30 (addressable segment)
    SOM = SAM × conversion_rate (realistically capturable)
    """
    tam = target_customers * annual_price_usd * geography_multiplier
    sam = tam * 0.30
    som = sam * conversion_rate
    return {
        "method": "bottom_up",
        "tam_usd": tam,
        "sam_usd": sam,
        "som_usd": som,
        "assumptions": {
            "target_customers": target_customers,
            "annual_price_usd": annual_price_usd,
            "conversion_rate": conversion_rate,
            "geography_multiplier": geography_multiplier,
            "sam_pct_of_tam": 0.30,
        },
    }


# ---------------------------------------------------------------------------
# Method 2 — Top-down (sanity check only)
# ---------------------------------------------------------------------------

def tam_top_down(
    total_market_usd: float,
    addressable_pct: float,
    som_pct: float = 0.01,
    geography_multiplier: float = 1.0,
) -> dict:
    """
    Quick sizing from market reports. Often overestimates.
    Use only as sanity check, not primary method.

    addressable_pct: 0.0-1.0, e.g. 0.15 for 15%
    som_pct: share of SAM that is realistically capturable
    """
    if not 0.0 <= addressable_pct <= 1.0:
        raise ValueError("addressable_pct must be between 0 and 1")
    if not 0.0 <= som_pct <= 1.0:
        raise ValueError("som_pct must be between 0 and 1")

    tam = total_market_usd * geography_multiplier
    sam = tam * addressable_pct
    som = sam * som_pct
    return {
        "method": "top_down",
        "tam_usd": tam,
        "sam_usd": sam,
        "som_usd": som,
        "assumptions": {
            "total_market_usd": total_market_usd,
            "addressable_pct": addressable_pct,
            "som_pct": som_pct,
            "geography_multiplier": geography_multiplier,
        },
    }


# ---------------------------------------------------------------------------
# Method 3 — Proxy (analog scaling)
# ---------------------------------------------------------------------------

def tam_proxy(
    analog_tam_usd: float,
    analog_market: str,
    target_market: str,
    size_ratio: float,
) -> dict:
    """
    When target market = smaller version of known analog.
    E.g. Venezuela payments = 0.15 × Colombia payments

    size_ratio: e.g. 0.15 if target is 15% the size of analog
    """
    if size_ratio <= 0:
        raise ValueError("size_ratio must be positive")

    tam = analog_tam_usd * size_ratio
    sam = tam * 0.30
    som = sam * 0.02
    return {
        "method": "proxy",
        "tam_usd": tam,
        "sam_usd": sam,
        "som_usd": som,
        "assumptions": {
            "analog_tam_usd": analog_tam_usd,
            "analog_market": analog_market,
            "target_market": target_market,
            "size_ratio": size_ratio,
        },
    }


# ---------------------------------------------------------------------------
# Method 4 — Competitor revenue back-calculation
# ---------------------------------------------------------------------------

def tam_competitor_revenue(
    competitor_arr_usd: float,
    competitor_market_share_estimate: float,
    geography_multiplier: float = 1.0,
) -> dict:
    """
    Back-calculate market from competitor revenue.
    Requires honest market share estimate.

    competitor_market_share_estimate: 0.0-1.0
    """
    if not 0.0 < competitor_market_share_estimate <= 1.0:
        raise ValueError("competitor_market_share_estimate must be between 0 (exclusive) and 1")

    tam = (competitor_arr_usd / competitor_market_share_estimate) * geography_multiplier
    sam = tam * 0.30
    som = sam * 0.02
    return {
        "method": "competitor_revenue",
        "tam_usd": tam,
        "sam_usd": sam,
        "som_usd": som,
        "assumptions": {
            "competitor_arr_usd": competitor_arr_usd,
            "competitor_market_share_estimate": competitor_market_share_estimate,
            "geography_multiplier": geography_multiplier,
        },
    }


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

_METHOD_MAP = {
    "bottom_up": tam_bottom_up,
    "top_down": tam_top_down,
    "proxy": tam_proxy,
    "competitor_revenue": tam_competitor_revenue,
}

_CONFIDENCE_MAP = {
    "bottom_up": "high",
    "proxy": "medium",
    "competitor_revenue": "medium",
    "top_down": "low",
}


def estimate_tam(
    method: str,
    geography: str = "global",
    **kwargs,
) -> dict:
    """
    Routes to the correct TAM method and applies geo multiplier.

    Returns dict with:
      method, geography, tam_usd, sam_usd, som_usd,
      confidence, assumptions, notes
    """
    method_key = method.lower()
    if method_key not in _METHOD_MAP:
        raise ValueError(
            f"Unknown method '{method}'. Choose from: {list(_METHOD_MAP.keys())}"
        )

    geo_key = geography.lower()
    geo_mult = GEO_TAM_MULTIPLIERS.get(geo_key, 1.0)

    # Inject geography_multiplier for methods that accept it
    fn = _METHOD_MAP[method_key]
    import inspect
    sig = inspect.signature(fn)
    if "geography_multiplier" in sig.parameters and "geography_multiplier" not in kwargs:
        kwargs["geography_multiplier"] = geo_mult

    result = fn(**kwargs)

    # Augment with routing metadata
    result["geography"] = geography
    result["confidence"] = _CONFIDENCE_MAP.get(method_key, "medium")

    notes = []
    if method_key == "top_down":
        notes.append("Top-down often overestimates. Use as upper bound only.")
    if geo_key not in GEO_TAM_MULTIPLIERS:
        notes.append(f"Geography '{geography}' not in lookup table — using 1.0x multiplier.")
    if method_key in ("bottom_up",) and "target_customers" in kwargs:
        notes.append("Validate customer count with primary research before Series A.")

    result["notes"] = notes
    return result


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def format_tam_usd(value: float | None) -> str:
    """Returns human-readable USD string: $10M, $1.2B, $450K."""
    if value is None:
        return "Unknown"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:.0f}"


def format_tam_summary(result: dict) -> str:
    """Returns a clean, human-readable TAM summary."""
    method = result.get("method", "unknown")
    geography = result.get("geography", "global")
    confidence = result.get("confidence", "?")
    tam = format_tam_usd(result.get("tam_usd"))
    sam = format_tam_usd(result.get("sam_usd"))
    som = format_tam_usd(result.get("som_usd"))
    notes = result.get("notes", [])

    lines = [
        f"TAM Estimate ({method.replace('_', '-')} method | {geography} | confidence: {confidence})",
        f"  TAM: {tam}",
        f"  SAM: {sam}",
        f"  SOM: {som}",
    ]
    if notes:
        lines.append("  Notes:")
        for n in notes:
            lines.append(f"    - {n}")
    return "\n".join(lines)
