"""
Customer Pain Intelligence OS — query builder + schema for pain validation.

This module does NOT scrape at runtime. It provides:
  1. PAIN_CATEGORY_QUERIES  — search terms by Venezuela structural wedge category
  2. PAIN_SOURCES           — source types + search patterns for each platform
  3. build_pain_queries()   — generates 5-8 targeted queries from an opportunity dict
  4. run_pain_intelligence() — returns a structured template for the pain-intelligence-agent to fill in

Real scraping is performed by the pain-intelligence-agent at runtime using WebSearch/WebFetch.
"""

from __future__ import annotations

from datetime import date
from typing import Optional


# ─── Pain Category Queries ────────────────────────────────────────────────────
# Keyed by Venezuela structural wedge category (matches CLAUDE.md + models.py)

PAIN_CATEGORY_QUERIES: dict[str, list[str]] = {
    "payments_and_collections": [
        "cobrar dolares Venezuela 2024",
        "USDT comercio Venezuela problemas",
        "pago digital sin banco Venezuela",
        "como cobrar por transferencia Venezuela",
        "punto de venta Venezuela falla",
    ],
    "remittances_and_diaspora_finance": [
        "enviar dinero Venezuela dificultad",
        "remesas Venezuela costo alto 2024",
        "recibir dinero desde exterior Venezuela",
        "zelle Venezuela problema familiar",
        "envio dinero colombianos Venezuela",
    ],
    "smb_software_informal_operators": [
        "software negocio informal Venezuela",
        "control inventario pequeño negocio Venezuela",
        "factura WhatsApp Venezuela problemas",
        "sistema para bodega Venezuela gratis",
        "llevar cuentas negocio Venezuela sin internet",
    ],
    "retail_inventory_working_capital": [
        "capital trabajo Venezuela comercio",
        "credito para negocio Venezuela 2024",
        "financiamiento comerciante Venezuela informal",
        "prestamo para negocio venezolano",
        "reposicion inventario comercio Venezuela",
    ],
    "logistics_coordination": [
        "envios Venezuela problemas 2024",
        "mensajeria Venezuela informal confiable",
        "courier Venezuela sin tracking",
        "delivery Venezuela falla mototaxi",
        "envio paquete interior Venezuela precio",
    ],
    "commerce_trust_layers": [
        "estafa compra venta Venezuela Instagram",
        "como saber si vendedor Venezuela es confiable",
        "fraude marketplace Venezuela 2024",
        "comprar en linea Venezuela miedo",
        "reputacion vendedor Venezuela whatsapp",
    ],
    "creator_monetization": [
        "cobrar contenido digital Venezuela",
        "monetizar seguidores Venezuela sin paypal",
        "plataforma pago creadores venezolanos",
        "vender curso online Venezuela cobro",
        "suscripcion fans Venezuela dolares",
    ],
    "cross_border_service_businesses": [
        "trabajar remoto Venezuela cobrar dolares",
        "freelancer venezolano cobro exterior",
        "servicio digital Venezuela cliente extranjero",
        "facturar cliente EEUU desde Venezuela",
        "payoneer Venezuela alternativa",
    ],
    "diaspora_finance_and_commerce": [
        "venezolano en el exterior enviar dinero casa",
        "diaspora venezolana remesas baratas",
        "comprar en Venezuela desde Colombia Peru Chile",
        "venezolanos Colombia enviar articulos familia",
        "ayudar familia Venezuela desde afuera",
    ],
    "ai_labor_replacement_tools": [
        "automatizar tarea repetitiva negocio Venezuela",
        "herramienta IA pequeña empresa LATAM",
        "reemplazar empleado con software Venezuela",
        "chatbot atencion cliente venezolano bajo costo",
        "IA para emprendedor venezolano",
    ],
}


# ─── Pain Sources ─────────────────────────────────────────────────────────────
# Platform descriptions and search patterns. URLs/scraping handled by the agent.

PAIN_SOURCES: list[dict] = [
    {
        "source_type": "reddit",
        "description": "Spanish-language Reddit communities for VE/LATAM",
        "subreddits": [
            "r/vzla",
            "r/Venezuela",
            "r/Colombia",
            "r/mexico",
            "r/argentina",
            "r/espanol",
            "r/finanzas",
            "r/Emprendedores",
        ],
        "search_pattern": "site:reddit.com {query} Venezuela OR LATAM",
        "geo_priority": "venezuela",
    },
    {
        "source_type": "app_store_reviews",
        "description": "Google Play store reviews from LATAM users in Spanish",
        "search_pattern": 'site:play.google.com/store "{vertical}" reseñas Venezuela Colombia',
        "geo_priority": "latam",
    },
    {
        "source_type": "youtube_comments",
        "description": "YouTube comment sections on LATAM fintech / commerce creator channels",
        "search_pattern": "site:youtube.com {query} comentarios",
        "channels": [
            "finanzas personales Venezuela",
            "emprendimiento Venezuela",
            "negocios Colombia",
            "tips fintech LATAM",
        ],
        "geo_priority": "latam",
    },
    {
        "source_type": "twitter_x",
        "description": "X/Twitter Spanish-language complaints and workarounds",
        "search_pattern": 'site:x.com OR site:twitter.com "{query}" lang:es',
        "geo_priority": "latam",
    },
    {
        "source_type": "google_search_intent",
        "description": "Google autocomplete and related searches — intent signals",
        "search_pattern": "{query} site:google.com",
        "use_as": "query validation — high volume = real pain",
        "geo_priority": "global",
    },
    {
        "source_type": "trustpilot_g2_capterra",
        "description": "Competitor reviews revealing pain with existing solutions",
        "search_pattern": '(site:trustpilot.com OR site:g2.com OR site:capterra.com) "{competitor}" Venezuela OR LATAM',
        "geo_priority": "latam",
    },
    {
        "source_type": "forums_and_communities",
        "description": "Venezuelan/LATAM WhatsApp-visible forums, Telegram channels, Facebook groups",
        "search_pattern": '"{query}" Venezuela foro OR grupo OR comunidad',
        "geo_priority": "venezuela",
    },
]


# ─── Vertical-Level Query Overrides ──────────────────────────────────────────
# Additional query sets keyed by vertical field (not just wedge category)

VERTICAL_QUERIES: dict[str, list[str]] = {
    "fintech": [
        "cobrar dinero Venezuela problema 2024",
        "banco Venezuela falla pagos",
        "USDT Venezuela comercio diario",
        "dolares Venezuela cobro digital alternativa",
    ],
    "payments": [
        "metodo pago Venezuela comercio problema",
        "como cobrar en dolares Venezuela legalmente",
        "POS Venezuela falla constantemente",
        "transferencia bancaria Venezuela demora",
    ],
    "logistics": [
        "envio paquete Venezuela interior problema",
        "courier Venezuela no llega",
        "tracking envio Venezuela imposible",
        "mensajero Venezuela sin app",
    ],
    "saas_smb": [
        "software venezolano pequeña empresa barato",
        "sistema inventario Venezuela gratis",
        "facturacion digital Venezuela problema",
        "herramienta negocio Venezuela sin internet",
    ],
    "ecommerce": [
        "vender en linea Venezuela sin PayPal",
        "tienda online Venezuela cobro problema",
        "marketplace Venezuela confianza",
        "dropshipping Venezuela imposible",
    ],
    "remittances": [
        "enviar dinero Venezuela rapido barato",
        "remesas Venezuela 2024 mejor opcion",
        "costo envio dinero Venezuela desde EEUU",
        "binance P2P Venezuela familia",
    ],
    "hr_and_payroll": [
        "pagar empleados Venezuela dolares",
        "nomina empresa Venezuela bolivares dolares",
        "contrato laboral Venezuela informal",
    ],
    "lending_and_credit": [
        "prestamo negocio Venezuela requisitos",
        "credito informal Venezuela tasa",
        "financiamiento Venezuela emprendedor problema",
    ],
}


# ─── Query Builder ────────────────────────────────────────────────────────────

def build_pain_queries(opp: dict) -> list[str]:
    """
    Generate 5-8 targeted Spanish-language search queries for the given opportunity.

    Priority order:
      1. venezuela_wedge_category -> PAIN_CATEGORY_QUERIES
      2. vertical -> VERTICAL_QUERIES
      3. problem_statement keywords -> generic complaint pattern
      4. target_customer + geography -> persona-level query

    Returns a deduplicated list of 5-8 queries.
    """
    queries: list[str] = []

    # 1. Wedge category queries
    wedge = opp.get("venezuela_wedge_category") or ""
    if wedge and wedge in PAIN_CATEGORY_QUERIES:
        queries.extend(PAIN_CATEGORY_QUERIES[wedge][:3])

    # 2. Vertical queries
    vertical = (opp.get("vertical") or "").lower().replace(" ", "_")
    if vertical in VERTICAL_QUERIES:
        queries.extend(VERTICAL_QUERIES[vertical][:3])

    # 3. Derive queries from problem_statement keywords
    problem = opp.get("problem_statement") or ""
    geography = opp.get("geography") or "Venezuela"
    geo_label = "Venezuela" if geography == "venezuela" else geography.upper()
    if problem:
        # Extract the core pain noun phrase (first 6 words)
        core_words = " ".join(problem.split()[:6])
        queries.append(f"{core_words} problema {geo_label}")

    # 4. Target customer persona query
    customer = opp.get("target_customer") or ""
    if customer:
        short_customer = " ".join(customer.split()[:4])
        queries.append(f"{short_customer} queja {geo_label} 2024")

    # 5. Fallback generic pain signal
    name = opp.get("name") or ""
    if name:
        queries.append(f'"{name}" problemas {geo_label}')

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            deduped.append(q)

    # Return 5-8 queries
    return deduped[:8] if len(deduped) >= 5 else deduped


# ─── Pain Intelligence Runner ─────────────────────────────────────────────────

def run_pain_intelligence(opp: dict) -> dict:
    """
    Build the pain intelligence template for the given opportunity.

    This function does NOT scrape. It returns a structured template dict
    that the pain-intelligence-agent fills in with real evidence at runtime.

    Returns a dict with all pain validation fields (all Optional).
    Fields are None until populated by the agent:
      - pain_validation_score: float 0-10
      - pain_evidence_sources: list[str]   (source descriptions, not raw URLs)
      - exact_customer_phrases: list[str]  (max 3, Spanish complaint phrases)
      - workarounds_found: list[str]       (what people use today)
      - pain_validated_date: str           (ISO date string, today)

    Also includes helper fields for the agent:
      - _pain_queries: list[str]           (queries to execute)
      - _pain_sources: list[dict]          (source types to check)
    """
    queries = build_pain_queries(opp)

    template: dict = {
        # Schema fields — populated by pain-intelligence-agent
        "pain_validation_score": None,
        "pain_evidence_sources": [],
        "exact_customer_phrases": [],
        "workarounds_found": [],
        "pain_validated_date": date.today().isoformat(),

        # Agent helper fields (prefixed with _ to distinguish from schema fields)
        "_pain_queries": queries,
        "_pain_sources": PAIN_SOURCES,
        "_opportunity_id": opp.get("id"),
        "_opportunity_name": opp.get("name"),
        "_vertical": opp.get("vertical"),
        "_geography": opp.get("geography"),
        "_wedge_category": opp.get("venezuela_wedge_category"),
    }

    return template


# ─── Convenience helpers ──────────────────────────────────────────────────────

def is_pain_validated(opp: dict) -> bool:
    """Return True if this opportunity has a populated pain_validation_score >= 7."""
    score = opp.get("pain_validation_score")
    if score is None:
        return False
    return float(score) >= 7.0


def pain_score_label(score: Optional[float]) -> str:
    """Human-readable label for a pain_validation_score."""
    if score is None:
        return "unscored"
    if score >= 9:
        return "critical — daily urgent pain, failed workarounds"
    if score >= 7:
        return "high — frequent pain, imperfect workarounds"
    if score >= 5:
        return "moderate — occasional pain"
    return "low — inconvenience, not pain"
