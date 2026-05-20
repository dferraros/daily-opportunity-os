"""
Geo Lens -- applies regional adjustments to opportunity scoring and analysis.

Venezuela and LATAM have structural differences that affect:
- Willingness to pay (WTP multipliers)
- SaaS pricing ranges
- Payment rail availability
- Distribution channel effectiveness
- Trust barrier to adoption

These are NOT restrictions on what to scout. They are lenses applied AFTER global scouting
to adjust scores and provide context-aware analysis.
"""

from typing import Optional

VENEZUELA_ADJUSTMENTS = {
    "wtp_multiplier": 0.25,
    "saas_price_range": "$3-15/mo",
    "dominant_payment_rails": ["Zelle", "USDT", "Binance P2P"],
    "distribution_primary": "WhatsApp",
    "distribution_secondary": "TikTok organic",
    "informal_commerce_pct": 0.55,
    "internet_penetration": 0.72,
    "smartphone_first": True,
    "trust_signal": "referral > brand",
    "regional_fit_bonus": 1.5,  # score bonus if opportunity maps to structural wedge
}

LATAM_ADJUSTMENTS = {
    "wtp_multiplier_vs_us": 0.40,
    "preferred_payment": {
        "colombia": "PSE",
        "brazil": "PIX",
        "mexico": "OXXO",
        "argentina": "Mercado Pago",
        "venezuela": "Zelle/USDT",
        "spain": "card",
        "default": "card",
    },
    "informal_commerce_pct": 0.45,
    "whatsapp_penetration": 0.90,
    "cash_economy_note": "significant in tier-2/3 cities",
}

LATAM_GEOGRAPHIES = [
    "latam",
    "venezuela",
    "colombia",
    "brazil",
    "mexico",
    "argentina",
    "peru",
    "chile",
    "ecuador",
    "bolivia",
    "paraguay",
    "uruguay",
    "panama",
    "costa_rica",
    "guatemala",
    "honduras",
    "el_salvador",
    "nicaragua",
    "dominican_republic",
    "cuba",
    "spain",
]

VENEZUELA_WEDGE_CATEGORIES = [
    "payments_and_collections",
    "remittances_and_diaspora_finance",
    "smb_software_informal_operators",
    "retail_inventory_working_capital",
    "logistics_coordination",
    "commerce_trust_layers",
    "creator_monetization",
    "cross_border_service_businesses",
    "diaspora_finance_and_commerce",
    "ai_labor_replacement_tools",
]

# Map vertical values to the most fitting Venezuela wedge category.
# Used as fallback when venezuela_wedge_category is not set by AI scoring.
VERTICAL_TO_WEDGE_CATEGORY: dict[str, str] = {
    "fintech": "payments_and_collections",
    "payments": "payments_and_collections",
    "remittances": "remittances_and_diaspora_finance",
    "diaspora": "diaspora_finance_and_commerce",
    "smb_software": "smb_software_informal_operators",
    "b2b_saas": "smb_software_informal_operators",
    "saas": "smb_software_informal_operators",
    "ecommerce": "commerce_trust_layers",
    "marketplace": "commerce_trust_layers",
    "retail": "retail_inventory_working_capital",
    "inventory": "retail_inventory_working_capital",
    "logistics": "logistics_coordination",
    "delivery": "logistics_coordination",
    "creator": "creator_monetization",
    "media": "creator_monetization",
    "content": "creator_monetization",
    "cross_border": "cross_border_service_businesses",
    "services": "cross_border_service_businesses",
    "ai": "ai_labor_replacement_tools",
    "automation": "ai_labor_replacement_tools",
}


def apply_geo_adjustments(opp_dict: dict) -> dict:
    """Apply regional adjustments to a raw opportunity dict.

    If geography is "venezuela": applies Venezuela WTP multiplier,
    adds payment rail context, boosts regional_fit if venezuela_wedge_category is set.
    If geography is in LATAM list: applies LATAM WTP multiplier.
    Returns updated dict (does not mutate original).
    """
    opp = dict(opp_dict)  # shallow copy
    geo = (opp.get("geography") or "").lower().strip()

    if geo == "venezuela":
        # Pricing context: store geo-adjusted WTP estimate for TAM/pricing calculations.
        # willingness_to_pay (1-10 scoring dimension) is intentionally NOT overwritten —
        # it reflects customer willingness relative to their own market, not vs. US prices.
        wtp = opp.get("willingness_to_pay")
        if wtp is not None:
            opp["wtp_pricing_estimate"] = round(wtp * VENEZUELA_ADJUSTMENTS["wtp_multiplier"], 4)

        # Add payment rail context
        opp["payment_rail_context"] = get_payment_rail_context(geo)

        # Infer venezuela_wedge_category from vertical if not already set
        if not opp.get("venezuela_wedge_category"):
            vertical = (opp.get("vertical") or "").lower().strip()
            inferred = VERTICAL_TO_WEDGE_CATEGORY.get(vertical)
            if inferred:
                opp["venezuela_wedge_category"] = inferred

        # Bucket fallback: Venezuela records default to latam_asymmetry
        if not opp.get("bucket"):
            opp["bucket"] = "latam_asymmetry"

        # Apply regional_fit bonus if wedge category is set
        category = opp.get("venezuela_wedge_category") or opp.get("category")
        if category and is_venezuela_wedge(str(category)):
            existing_rf = opp.get("regional_fit", 5.0) or 5.0
            opp["regional_fit"] = min(10.0, existing_rf + VENEZUELA_ADJUSTMENTS["regional_fit_bonus"])
            opp["venezuela_wedge_match"] = True
        else:
            opp["venezuela_wedge_match"] = False

    elif geo in LATAM_GEOGRAPHIES:
        wtp = opp.get("willingness_to_pay")
        if wtp is not None:
            opp["wtp_pricing_estimate"] = round(wtp * LATAM_ADJUSTMENTS["wtp_multiplier_vs_us"], 4)

        # Add payment rail context
        opp["payment_rail_context"] = get_payment_rail_context(geo)

    return opp


def get_payment_rail_context(geography: str) -> dict:
    """Return payment rail info for a geography.

    Returns dict with primary_rail, secondary_rail, cash_economy_risk (bool), wtp_multiplier.
    """
    geo = (geography or "").lower().strip()

    preferred = LATAM_ADJUSTMENTS["preferred_payment"]
    primary_rail = preferred.get(geo, preferred["default"])

    # Derive secondary rail
    secondary_map = {
        "venezuela": "Binance P2P",
        "colombia": "Nequi",
        "brazil": "card",
        "mexico": "card",
        "argentina": "card",
        "spain": "PayPal",
    }
    secondary_rail = secondary_map.get(geo, "bank_transfer")

    # Cash economy risk: high for most LATAM tier-2/3, lower for VE (USD-ised)
    cash_economy_risk = geo not in ["venezuela", "brazil", "spain", "argentina"]

    wtp_multiplier = VENEZUELA_ADJUSTMENTS["wtp_multiplier"] if geo == "venezuela" else LATAM_ADJUSTMENTS["wtp_multiplier_vs_us"]

    return {
        "primary_rail": primary_rail,
        "secondary_rail": secondary_rail,
        "cash_economy_risk": cash_economy_risk,
        "wtp_multiplier": wtp_multiplier,
    }


def is_venezuela_wedge(category: str) -> bool:
    """Return True if category is in VENEZUELA_WEDGE_CATEGORIES."""
    return (category or "").lower().strip() in VENEZUELA_WEDGE_CATEGORIES


def get_geo_context_note(geography: str) -> str:
    """Return a human-readable context note for a geography.

    Example: "Venezuela: WTP 0.25x vs US. Primary rails: Zelle, USDT. WhatsApp-first distribution."
    """
    geo = (geography or "").lower().strip()

    if geo == "venezuela":
        rails = ", ".join(VENEZUELA_ADJUSTMENTS["dominant_payment_rails"])
        return (
            f"Venezuela: WTP {VENEZUELA_ADJUSTMENTS['wtp_multiplier']}x vs US. "
            f"Primary rails: {rails}. "
            f"WhatsApp-first distribution. "
            f"Informal commerce: {int(VENEZUELA_ADJUSTMENTS['informal_commerce_pct'] * 100)}% of economy. "
            f"Trust signal: {VENEZUELA_ADJUSTMENTS['trust_signal']}. "
            f"SaaS price range: {VENEZUELA_ADJUSTMENTS['saas_price_range']}. "
            f"Wedge categories: {len(VENEZUELA_WEDGE_CATEGORIES)} structural vectors."
        )

    if geo in LATAM_GEOGRAPHIES:
        preferred = LATAM_ADJUSTMENTS["preferred_payment"]
        rail = preferred.get(geo, preferred["default"])
        return (
            f"{geography.title()}: WTP {LATAM_ADJUSTMENTS['wtp_multiplier_vs_us']}x vs US. "
            f"Primary payment rail: {rail}. "
            f"WhatsApp penetration: {int(LATAM_ADJUSTMENTS['whatsapp_penetration'] * 100)}%. "
            f"Informal commerce: {int(LATAM_ADJUSTMENTS['informal_commerce_pct'] * 100)}%."
        )

    return f"{geography}: No specific geo adjustment configured. Using global defaults."
