"""
Benchmark Engine — maps opportunities to archetypes and identifies competitive whitespace.

Two jobs:
1. Archetype classification: HOW does this business win? (8 archetypes)
2. Whitespace detection: WHERE is competition weakest? (gap analysis)
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Archetype taxonomy
# ---------------------------------------------------------------------------

BENCHMARK_ARCHETYPES: dict[str, str] = {
    "local_clone": "Proven US/EU model adapted for LATAM/emerging market",
    "regional_wedge": "Exploits broken local infrastructure as competitive moat",
    "workflow_unbundling": "Takes one painful workflow from large software product",
    "trust_compliance_layer": "Adds trust/compliance layer where market lacks it",
    "ai_operator_replacement": "AI reduces labor cost for a specific, repeatable job",
    "fragmented_supply_marketplace": "Connects fragmented supply that cannot find demand",
    "smb_operating_system": "Becomes the core OS for a specific SMB vertical",
    "diaspora_bridge": "Connects two sides of a diaspora market (VE/CO/MX diaspora)",
}

# ---------------------------------------------------------------------------
# Analog benchmark lookup table
# ---------------------------------------------------------------------------

ANALOG_BENCHMARKS: dict[tuple[str, str], list[dict]] = {
    ("fintech", "venezuela"): [
        {
            "name": "Pagatodo",
            "model": "payment_aggregator",
            "status": "active",
            "lesson": "trust via telco partnership",
        },
        {
            "name": "Binance P2P VE",
            "model": "p2p_exchange",
            "status": "active",
            "lesson": "informal trust via reputation scores",
        },
        {
            "name": "Reserve Protocol",
            "model": "stablecoin_wallet",
            "status": "active",
            "lesson": "USD-pegged store of value beats local currency fear",
        },
    ],
    ("logistics", "latam"): [
        {
            "name": "Rappi",
            "model": "on_demand_logistics",
            "status": "active",
            "lesson": "super-app expansion from food delivery",
        },
        {
            "name": "iVoy",
            "model": "last_mile_b2b",
            "status": "active",
            "lesson": "SMB focus beats consumer-first in LATAM",
        },
        {
            "name": "Melonn",
            "model": "fulfillment_as_a_service",
            "status": "active",
            "lesson": "ecommerce logistics as SaaS wins over 3PL incumbents",
        },
    ],
    ("lending", "latam"): [
        {
            "name": "Konfio",
            "model": "sme_lending",
            "status": "active",
            "lesson": "SAT tax data as underwriting proxy beats credit bureaus",
        },
        {
            "name": "Creditas",
            "model": "secured_consumer_lending",
            "status": "active",
            "lesson": "collateral-backed loans survive macro downturns",
        },
        {
            "name": "Addi",
            "model": "bnpl_latam",
            "status": "active",
            "lesson": "BNPL at POS captures first-time credit users",
        },
    ],
    ("lending", "venezuela"): [
        {
            "name": "M-Kopa",
            "model": "asset_finance_gps_kill_switch",
            "status": "active",
            "lesson": "GPS kill-switch drives 90%+ repayment without courts",
        },
        {
            "name": "Watu Credit",
            "model": "motorcycle_asset_finance",
            "status": "active",
            "lesson": "productive asset loans outperform consumer loans in risk",
        },
    ],
    ("saas", "latam"): [
        {
            "name": "Alegra",
            "model": "accounting_smb_saas",
            "status": "active",
            "lesson": "local tax compliance = must-have, beats global tools",
        },
        {
            "name": "Siigo",
            "model": "erp_smb",
            "status": "acquired",
            "lesson": "verticalized ERP captures accountant channel network effects",
        },
        {
            "name": "Contabilizei",
            "model": "accounting_automation",
            "status": "active",
            "lesson": "Brazilian tax complexity = moat for local players",
        },
    ],
    ("marketplace", "latam"): [
        {
            "name": "Mercado Libre",
            "model": "horizontal_marketplace",
            "status": "active",
            "lesson": "fintech (ML Pay) monetization exceeds GMV take-rate",
        },
        {
            "name": "Kavak",
            "model": "used_car_marketplace",
            "status": "active",
            "lesson": "trust layer on opaque market commands premium pricing",
        },
    ],
    ("remittances", "venezuela"): [
        {
            "name": "Zelle informal VE",
            "model": "p2p_us_to_ve",
            "status": "active",
            "lesson": "diaspora demand creates informal rails before formal ones",
        },
        {
            "name": "Senders",
            "model": "fx_remittance_latam",
            "status": "active",
            "lesson": "compliance-light corridors attract volume before regulation catches up",
        },
    ],
    ("healthtech", "latam"): [
        {
            "name": "Nuvemshop Health",
            "model": "vertical_ecommerce",
            "status": "active",
            "lesson": "vertical-specific checkout increases conversion 2-3x vs generic",
        },
        {
            "name": "Mia Salud",
            "model": "telemedicine_b2b2c",
            "status": "active",
            "lesson": "employer channel reduces CAC 10x vs direct-to-consumer",
        },
    ],
    ("proptech", "latam"): [
        {
            "name": "La Haus",
            "model": "residential_marketplace",
            "status": "active",
            "lesson": "agent network beats portal-only in relationship-driven markets",
        },
        {
            "name": "Houm",
            "model": "rental_management",
            "status": "active",
            "lesson": "full-stack property mgmt commands 3-5x fees of listing-only",
        },
    ],
}

# ---------------------------------------------------------------------------
# Classification heuristics
# ---------------------------------------------------------------------------

_LATAM_GEOS = {"venezuela", "colombia", "mexico", "argentina", "peru", "chile", "latam"}

_ARCHETYPE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("diaspora_bridge", ["diaspora", "remittance", "send money", "cross-border", "migrant"]),
    ("regional_wedge", ["infrastructure", "broken", "cash", "informal", "unbanked", "corrupt", "power cut"]),
    ("trust_compliance_layer", ["trust", "compliance", "kyc", "aml", "regulated", "fraud", "legal"]),
    ("ai_operator_replacement", ["ai", "automate", "replace", "labor", "bot", "llm", "gpt"]),
    ("fragmented_supply_marketplace", ["marketplace", "fragmented", "connect", "supply", "demand", "aggregat"]),
    ("smb_operating_system", ["smb", "small business", "operating system", "erp", "accounting", "payroll"]),
    ("workflow_unbundling", ["workflow", "unbundle", "extract", "specific", "one feature", "pain"]),
    ("local_clone", ["clone", "latam version", "emerging market", "like uber", "like airbnb", "proven model"]),
]


def classify_archetype(opp_dict: dict) -> str:
    """
    Heuristic archetype classification based on available opportunity fields.

    Checks geography, vertical, and problem_statement keywords.
    Returns archetype key or 'unknown'.
    """
    problem = (opp_dict.get("problem_statement") or "").lower()
    vertical = (opp_dict.get("vertical") or "").lower()
    geography = (opp_dict.get("geography") or "").lower()

    combined_text = f"{problem} {vertical} {geography}"

    # Diaspora bridge: strong signal = remittance + latam geo
    if geography in _LATAM_GEOS or any(g in geography for g in _LATAM_GEOS):
        if any(kw in problem for kw in ["remittance", "diaspora", "send money", "migrant"]):
            return "diaspora_bridge"

    # Score each archetype by keyword hits
    scores: dict[str, int] = {}
    for archetype, keywords in _ARCHETYPE_KEYWORDS:
        hits = sum(1 for kw in keywords if kw in combined_text)
        if hits > 0:
            scores[archetype] = hits

    if not scores:
        # Fallback: if LATAM geo with known US/EU vertical, assume local_clone
        if geography in _LATAM_GEOS and vertical in ("fintech", "saas", "logistics", "marketplace"):
            return "local_clone"
        return "unknown"

    return max(scores, key=lambda k: scores[k])


# ---------------------------------------------------------------------------
# Whitespace detection
# ---------------------------------------------------------------------------

def detect_whitespace(opp_dict: dict) -> dict:
    """
    Identifies competitive whitespace signals for the opportunity.

    Returns:
        weak_competitor_signals: list of strings describing where competition is weak
        underserved_segments: list of segments lacking solutions
        pricing_gap: bool — is incumbent pricing out of reach for target?
        geographic_gap: bool — does solution exist in target geo?
    """
    problem = (opp_dict.get("problem_statement") or "").lower()
    vertical = (opp_dict.get("vertical") or "").lower()
    geography = (opp_dict.get("geography") or "").lower()

    weak_signals: list[str] = []
    underserved: list[str] = []

    # Geographic gap: LATAM/VE with low penetration verticals
    geo_gap = geography in _LATAM_GEOS
    if geo_gap:
        weak_signals.append(f"Most global competitors lack presence in {geography}")

    # Pricing gap: enterprise incumbents dominate
    incumbent_terms = ["enterprise", "expensive", "complex", "sap", "oracle", "salesforce", "legacy"]
    pricing_gap = any(term in problem for term in incumbent_terms)
    if pricing_gap:
        weak_signals.append("Incumbent pricing targets enterprises — SMB/micro-SMB underserved")
        underserved.append("SMB / micro-SMB segment")

    # Informal market signal
    if any(term in problem for term in ["informal", "cash", "unbanked", "no credit"]):
        weak_signals.append("Informal economy actors excluded from formal solutions")
        underserved.append("Informal / unbanked population")

    # Trust gap
    if any(term in problem for term in ["fraud", "scam", "trust", "verification"]):
        weak_signals.append("No trusted intermediary operating in this space")
        underserved.append("Users requiring verified/trusted counterparty")

    # Vertical-specific signals
    if vertical == "logistics" and geography in _LATAM_GEOS:
        weak_signals.append("Last-mile infrastructure gaps create 30-40% delivery failure rates")
        underserved.append("Rural and peri-urban delivery recipients")

    if vertical in ("fintech", "lending") and geography == "venezuela":
        weak_signals.append("USD-denominated products non-existent in formal banking")
        underserved.append("Bolivar-averse savers and borrowers seeking USD stability")

    if not weak_signals:
        weak_signals.append("No obvious whitespace signals detected — manual research required")

    return {
        "weak_competitor_signals": weak_signals,
        "underserved_segments": underserved,
        "pricing_gap": pricing_gap,
        "geographic_gap": geo_gap,
    }


# ---------------------------------------------------------------------------
# Analog lookup
# ---------------------------------------------------------------------------

def get_analog_benchmarks(vertical: str, geography: str) -> list[dict]:
    """
    Returns known analog businesses for a vertical + geography combo.

    Tries exact match first, then geography="latam" fallback, then empty list.
    """
    v = vertical.lower()
    g = geography.lower()

    # Exact match
    exact = ANALOG_BENCHMARKS.get((v, g))
    if exact:
        return exact

    # LATAM fallback
    latam_fallback = ANALOG_BENCHMARKS.get((v, "latam"))
    if latam_fallback:
        return latam_fallback

    return []


# ---------------------------------------------------------------------------
# Benchmark fit scorer
# ---------------------------------------------------------------------------

def score_benchmark_fit(opp_dict: dict) -> float:
    """
    Returns 0-10 score for how well the archetype + analog fit for this opportunity.

    Scoring:
    - Archetype identified (not 'unknown'): +4 pts
    - Analogs found: +3 pts (capped at 3 even with many analogs)
    - Whitespace signals detected: +2 pts
    - Geography in lookup table: +1 pt
    """
    score = 0.0

    archetype = classify_archetype(opp_dict)
    if archetype != "unknown":
        score += 4.0

    vertical = opp_dict.get("vertical", "")
    geography = opp_dict.get("geography", "")
    analogs = get_analog_benchmarks(vertical, geography)
    if analogs:
        score += min(3.0, len(analogs) * 1.0)

    whitespace = detect_whitespace(opp_dict)
    if len(whitespace["weak_competitor_signals"]) > 1:
        score += 2.0

    if geography.lower() in GEO_KNOWN:
        score += 1.0

    return round(min(score, 10.0), 2)


# Known geos set (mirrors GEO_TAM_MULTIPLIERS from tam_engine)
GEO_KNOWN = {"venezuela", "colombia", "mexico", "argentina", "spain", "latam", "global"}


# ---------------------------------------------------------------------------
# Pipeline adapter — single-dict interface used by daily_run.py
# ---------------------------------------------------------------------------

def run_benchmark(opp: dict) -> dict:
    """
    Pipeline adapter: accepts an opportunity dict and returns benchmark enrichment.

    Returns a flat dict suitable for opp.update():
      benchmark_archetype, benchmark_archetype_description,
      analog_benchmarks, whitespace, benchmark_fit_score
    """
    archetype = classify_archetype(opp)
    archetype_desc = BENCHMARK_ARCHETYPES.get(archetype, "")
    vertical = opp.get("vertical", "")
    geography = opp.get("geography", "global")
    analogs = get_analog_benchmarks(vertical, geography)
    whitespace = detect_whitespace(opp)
    fit_score = score_benchmark_fit(opp)

    return {
        "benchmark_archetype": archetype,
        "benchmark_archetype_description": archetype_desc,
        "analog_benchmarks": analogs,
        "whitespace": whitespace,
        "benchmark_fit_score": fit_score,
    }
