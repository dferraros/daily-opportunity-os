"""
Deep-dive synthesis -- Sonnet-powered analyst judgment (Wave 2.2).

The mechanical deep dive lays out every enriched field but reasons about none of
them. This adds one Sonnet pass that does what the templates can't: weigh the
evidence into the single strongest bull case, the 2-3 risks most likely to kill
it, and a go / validate / pass recommendation with a one-line rationale.

Opt-in only (the deep-dive --synthesize flag) because it costs ~$0.10/dive on
Sonnet. Never fabricates: no key or API failure returns None and the deep dive
is written without the synthesis section.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

SYNTHESIS_MODEL = os.environ.get("ANTHROPIC_SYNTHESIS_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 1200

SYNTHESIS_SYSTEM_PROMPT = (
    "You are a senior venture analyst writing the judgment section of a deep dive "
    "for a solo founder. You have the full enriched dossier below. Do NOT restate "
    "it -- reason over it. Weigh the evidence into: the single strongest bull case, "
    "the 2-3 risks most likely to actually kill this, and a recommendation of "
    "exactly 'go', 'validate', or 'pass' with a one-sentence rationale. Be concrete "
    "and skeptical; a solo founder with limited time is acting on this. Where the "
    "evidence is thin or AI-guessed rather than researched, say so. Return ONLY valid JSON."
)

# Fields worth feeding the model -- the researched/scored signal, not raw notes.
_DOSSIER_FIELDS = [
    "name", "geography", "vertical", "bucket", "problem_statement", "target_customer",
    "business_model_type", "final_score", "raw_final_score", "attractiveness_score",
    "executability_score", "strategic_value_score", "portfolio_lane",
    "pain_validation_score", "exact_customer_phrases", "workarounds_found",
    "top_distribution_channels", "estimated_cac_logic", "first_10_customer_path",
    "tam_usd_estimate", "sam_usd_estimate", "som_usd_estimate",
    "competitor_negative_review_rate", "competitor_complaint_themes",
    "competitor_signal_basis", "kill_thesis", "kill_thesis_strength",
    "evidence_coverage", "low_evidence_flag", "daniels_wedge_score", "founder_fit_score",
]


def _build_dossier(opp: dict) -> str:
    """Compact JSON of the researched signal, omitting empty fields."""
    dossier = {k: opp[k] for k in _DOSSIER_FIELDS if opp.get(k) not in (None, "", [], {})}
    return json.dumps(dossier, ensure_ascii=False, indent=2, default=str)


def _parse_synthesis(raw: str) -> Optional[dict]:
    """Parse the Sonnet JSON. None on malformation; normalizes recommendation."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    bull = data.get("bull_case")
    rec = data.get("recommendation")
    if not bull or not rec:
        return None
    rec_norm = str(rec).strip().lower()
    if rec_norm not in {"go", "validate", "pass"}:
        return None

    risks = data.get("key_risks")
    if not isinstance(risks, list):
        risks = [risks] if risks else []
    return {
        "synthesis_bull_case": str(bull).strip(),
        "synthesis_key_risks": [str(r).strip() for r in risks if str(r).strip()][:3],
        "synthesis_recommendation": rec_norm,
        "synthesis_rationale": str(data.get("rationale", "")).strip(),
    }


def synthesize_opportunity(opp: dict) -> Optional[dict]:
    """One Sonnet pass over the dossier. Returns synthesis dict or None on failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from opportunity_os.ai_scorer import _load_env_key
        api_key = _load_env_key()
    if not api_key:
        logger.error("[synthesis] No ANTHROPIC_API_KEY -- skipping %s", opp.get("name", "?")[:50])
        return None

    prompt = (
        f"DOSSIER:\n{_build_dossier(opp)}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "bull_case": "<strongest reason this wins, max 70 words>",\n'
        '  "key_risks": ["<risk most likely to kill it>", "<second>", "<third optional>"],\n'
        '  "recommendation": "go" | "validate" | "pass",\n'
        '  "rationale": "<one sentence justifying the recommendation>"\n'
        "}"
    )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=SYNTHESIS_MODEL,
            max_tokens=MAX_TOKENS,
            system=SYNTHESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = _parse_synthesis(response.content[0].text)
        if parsed is None:
            logger.error("[synthesis] Unparseable response for %s", opp.get("name", "?")[:50])
        return parsed
    except Exception as exc:  # noqa: BLE001 -- any API failure means no synthesis, never a fake one
        logger.error("[synthesis] Sonnet call failed for %s: %s", opp.get("name", "?")[:50], exc)
        return None


def build_synthesis_section(synthesis: dict) -> list:
    """Markdown lines for the synthesis section. Empty list if no synthesis."""
    if not synthesis:
        return []
    rec = synthesis.get("synthesis_recommendation", "").upper()
    lines = [
        "## Analyst Synthesis (Sonnet)",
        "",
        f"**Recommendation: {rec}** — {synthesis.get('synthesis_rationale', '')}",
        "",
        f"**Bull case:** {synthesis.get('synthesis_bull_case', '')}",
        "",
    ]
    risks = synthesis.get("synthesis_key_risks") or []
    if risks:
        lines.append("**Key risks:**")
        lines += [f"- {r}" for r in risks]
        lines.append("")
    lines += ["_Synthesized by Sonnet from the researched dossier — judgment, not new data._", ""]
    return lines
