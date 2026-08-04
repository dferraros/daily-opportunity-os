"""
Hypothesis-mode support: neighborhood generation + feasibility interrogation.

Standing requirements 2026-07-22 (d) and (e): a hypothesis run must return a
verdict PLUS a neighborhood map (6 axes, including absorb-into-existing-asset),
and legal viability is first-class — any answer resting on an unverified legal
assumption sets legal_opinion_required, which blocks a "build" verdict in
hypothesis_mode. Never fabricates: no key / no parse -> empty results, loudly
logged.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

from opportunity_os import tavily_client

logger = logging.getLogger(__name__)

HAIKU_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
MAX_NEIGHBORS = 6

# Verticals that trigger the 12-question component interrogation.
REGULATED_VERTICAL_MARKERS = (
    "fintech", "payment", "remittance", "crypto", "banking", "lending",
    "insurance", "infrastructure", "treasury", "payroll",
)

# Daniel's existing assets for the absorb axis (standing requirement f.2).
EXISTING_ASSETS = {
    "Konecto": "SMB invoicing/collections/payment-evidence platform for Venezuela "
               "(owner/admin users, WhatsApp-centric, multi-rail payment claims)",
    "Arranca": "early-stage venture project (personal portfolio)",
    "Bit2Me network": "Spanish crypto exchange employer network: fintech distribution, "
                      "compliance know-how, crypto rails",
}

NEIGHBORHOOD_SYSTEM_PROMPT = (
    "You are a venture strategist mapping the opportunity NEIGHBORHOOD around a "
    "founder's hypothesis. Generate adjacent plays that could BEAT the original. "
    "Be concrete and skeptical — a neighbor is only worth listing if there is a "
    "plausible reason it wins. Return ONLY a valid JSON array."
)

FEASIBILITY_SYSTEM_PROMPT = (
    "You are a fintech feasibility and regulatory analyst for Venezuela/LATAM. "
    "Answer strictly from the evidence provided. When evidence is missing for a "
    "legal or licensing question, say 'unverified' — never guess a legal "
    "conclusion. Return ONLY valid JSON."
)


def _get_api_key() -> Optional[str]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    from opportunity_os.ai_scorer import _load_env_key
    return _load_env_key()


def _parse_json_block(raw: str):
    """Strip markdown fences and parse the first JSON object/array. None on failure."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", (raw or "").strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"[\[{][\s\S]*[\]}]", cleaned)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def call_model_json(system: str, user: str, model: str = None, max_tokens: int = 1500):
    """One Anthropic call returning parsed JSON, or None (logged) on any failure."""
    api_key = _get_api_key()
    if not api_key:
        logger.error("[hypothesis] No ANTHROPIC_API_KEY — model call skipped")
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model or HAIKU_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parsed = _parse_json_block(response.content[0].text)
        if parsed is None:
            logger.error("[hypothesis] Unparseable model response (%s)", (model or HAIKU_MODEL))
        return parsed
    except Exception as exc:  # noqa: BLE001
        logger.error("[hypothesis] Model call failed: %s", exc)
        return None


def generate_neighborhood(opp: dict) -> list[dict]:
    """Generate 5-6 adjacent plays along the 6 standing axes.

    Axes: customer, problem, entry_rung (aggregator -> orchestration -> ops
    platform -> regulated infra), geography, business_model (incl. productized
    service), absorb_into_asset (module of an existing asset, with a two-sided
    check). Returns [] (logged) on any model failure — a missing neighborhood
    is visible, never invented.
    """
    assets = "\n".join(f"- {k}: {v}" for k, v in EXISTING_ASSETS.items())
    user = (
        f"HYPOTHESIS:\n"
        f"Name: {opp.get('name', '')}\n"
        f"Problem: {opp.get('problem_statement', '')}\n"
        f"Customer: {opp.get('target_customer', '')}\n"
        f"Geography: {opp.get('geography', '')} | Vertical: {opp.get('vertical', '')}\n"
        f"Model: {opp.get('monetization_model', '')}\n\n"
        f"FOUNDER'S EXISTING ASSETS (for the absorb axis):\n{assets}\n\n"
        f"Generate exactly {MAX_NEIGHBORS} adjacent plays, one per axis:\n"
        "1. same problem, different customer\n"
        "2. same customer, different problem\n"
        "3. different entry rung (aggregator -> orchestration -> ops platform -> regulated infra)\n"
        "4. different geography (VE-first vs Colombia/Mexico-first vs diaspora-side)\n"
        "5. different business model (SaaS vs productized service vs done-for-you)\n"
        "6. absorb into an existing asset (which asset, as what module)\n\n"
        "Return ONLY a JSON array where each item is:\n"
        "{\n"
        '  "name": "<short name>",\n'
        '  "axis": "customer|problem|entry_rung|geography|business_model|absorb_into_asset",\n'
        '  "thesis": "<1 sentence>",\n'
        '  "entry_rung": "aggregator|orchestration|ops_platform|regulated_infra",\n'
        '  "geography": "<geo>",\n'
        '  "why_it_might_beat_original": "<1 sentence>",\n'
        '  "two_sided_check": {"icp_match": "...", "roadmap_conflict": "...", '
        '"cannibalization_risk": "..."}  // absorb axis ONLY, else null\n'
        "}"
    )
    parsed = call_model_json(NEIGHBORHOOD_SYSTEM_PROMPT, user, max_tokens=2000)
    if not isinstance(parsed, list):
        logger.error("[hypothesis] Neighborhood generation failed for %s", opp.get("name", "?")[:50])
        return []

    neighbors = []
    for item in parsed[:MAX_NEIGHBORS]:
        if not isinstance(item, dict) or not item.get("name") or not item.get("axis"):
            continue
        neighbors.append({
            "name": str(item["name"])[:120],
            "axis": str(item["axis"]),
            "thesis": str(item.get("thesis") or "")[:300],
            "entry_rung": str(item.get("entry_rung") or "")[:40],
            "geography": str(item.get("geography") or "")[:40],
            "why_it_might_beat_original": str(item.get("why_it_might_beat_original") or "")[:300],
            "two_sided_check": item.get("two_sided_check")
            if isinstance(item.get("two_sided_check"), dict) else None,
        })
    logger.info("[hypothesis] Generated %d neighbors for %s", len(neighbors), opp.get("name", "?")[:50])
    return neighbors


def _is_regulated_vertical(opp: dict) -> bool:
    text = " ".join([
        str(opp.get("vertical") or ""),
        str(opp.get("subvertical") or ""),
        str(opp.get("bucket") or ""),
    ]).lower()
    return any(marker in text for marker in REGULATED_VERTICAL_MARKERS)


FEASIBILITY_QUESTIONS = [
    "q1_real_api_or_provider_exists",
    "q2_integration_legal",
    "q3_license_needed",
    "q4_who_custodies_funds",
    "q5_sanctions_fraud_liability_risk",
    "q6_revenue_model",
    "q7_launchable_without_bank_agreements",
    "q8_buildable_in_90_days",
    "q9_hard_to_get_dependencies",
    "q10_regulatory_moat_or_arbitrage",
    "q11_data_access_legality",
    "q12_hard_to_reverse_decisions",
]


def run_feasibility_interrogation(opp: dict) -> dict:
    """12-question component feasibility interrogation for regulated verticals.

    ONE Tavily round (max 3 queries) + ONE Haiku synthesis. Any legal/licensing
    answer without direct evidence must be 'unverified' -> legal_opinion_required
    True, which blocks a build verdict downstream (standing requirement e).
    """
    name = opp.get("name", "?")[:50]
    if not _is_regulated_vertical(opp):
        return {"feasibility_skipped": "non-regulated vertical"}

    geo = opp.get("geography") or "venezuela"
    vertical = opp.get("vertical") or "fintech"
    queries = [
        f"{vertical} {geo} regulation license requirements",
        f"{geo} SUDEBAN fintech license sanctions compliance" if geo == "venezuela"
        else f"{geo} fintech regulatory framework license",
        f"{opp.get('name', vertical)} bank API availability {geo}",
    ]

    snippets: list[str] = []
    evidence_urls: list[str] = []
    if tavily_client.is_available():
        for q in queries[:3]:
            for r in (tavily_client.search_with_content(q, max_results=2) or []):
                text = (r.get("raw_content") or r.get("content") or "").strip()
                if text:
                    snippets.append(text[:1800])
                    if r.get("url"):
                        evidence_urls.append(r["url"])
    else:
        logger.warning("[hypothesis] Tavily unavailable — feasibility runs without search evidence for %s", name)

    digest = "\n---\n".join(snippets) if snippets else "(no search evidence available)"
    questions_block = "\n".join(f"- {q}" for q in FEASIBILITY_QUESTIONS)
    user = (
        f"OPPORTUNITY: {opp.get('name', '')}\n"
        f"Problem: {opp.get('problem_statement', '')}\n"
        f"Geography: {geo} | Vertical: {vertical}\n\n"
        f"EVIDENCE:\n{digest[:6000]}\n\n"
        f"Answer each question in 1-2 sentences (say 'unverified' when the evidence "
        f"does not support a legal/licensing conclusion):\n{questions_block}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "answers": {"q1_real_api_or_provider_exists": "...", ... all 12 keys ...},\n'
        '  "legal_flags": ["<specific legal/sanctions/licensing risks>"],\n'
        '  "any_unverified_legal_assumption": true|false\n'
        "}"
    )
    parsed = call_model_json(FEASIBILITY_SYSTEM_PROMPT, user, max_tokens=2000)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("answers"), dict):
        logger.error("[hypothesis] Feasibility synthesis failed for %s — marking legal opinion required", name)
        return {
            "feasibility_answers": {},
            "legal_flags": ["feasibility synthesis failed — treat all legal questions as unverified"],
            "legal_opinion_required": True,
        }

    answers = {k: str(v)[:400] for k, v in parsed["answers"].items()}
    answer_text = " ".join(answers.values()).lower()
    # Code-enforced, not prompt-trusted: no search evidence, a model admission,
    # or the word 'unverified' in any answer all force the flag.
    legal_opinion_required = bool(
        parsed.get("any_unverified_legal_assumption")
        or "unverified" in answer_text
        or not snippets
    )
    legal_flags = [str(f)[:300] for f in (parsed.get("legal_flags") or []) if f]
    if evidence_urls:
        legal_flags.append("evidence: " + "; ".join(evidence_urls[:3]))

    logger.info(
        "[hypothesis] Feasibility for %s: %d answers, legal_opinion_required=%s",
        name, len(answers), legal_opinion_required,
    )
    return {
        "feasibility_answers": answers,
        "legal_flags": legal_flags,
        "legal_opinion_required": legal_opinion_required,
    }
