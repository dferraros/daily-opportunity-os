"""
Kill-Thesis Engine -- adversarial pass on top opportunities (Wave 2.1).

Normal research accumulates reasons to believe. This module does the opposite:
inverted searches hunting for evidence the opportunity FAILS, synthesized by a
hard-nosed skeptic prompt into one strongest kill thesis with a 1-10 strength.
Strength >= KILL_THESIS_CAP_THRESHOLD caps final_score like decision filters
(scoring_engine.apply_caps). The pass never invents a kill: no API or no
search signal -> the opp is returned unchanged, loudly logged.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from opportunity_os import tavily_client
from opportunity_os.engines.scoring_engine import KILL_THESIS_CAP_THRESHOLD

logger = logging.getLogger(__name__)

KILL_THESIS_TTL_DAYS = 30
MAX_RESULTS_PER_QUERY = 3

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

SKEPTIC_SYSTEM_PROMPT = (
    "You are a professional venture skeptic. Your only job is to find the single "
    "STRONGEST reason this business opportunity fails -- the kill thesis. You are "
    "not balanced; another analyst already made the bull case. "
    "STRENGTH RUBRIC: 1-3 = generic risk any startup has; 4-6 = plausible "
    "obstacle but mitigable; 7-8 = strong structural reason supported by the "
    "search evidence; 9-10 = fatal flaw with direct evidence. Reserve 7+ for "
    "theses the evidence actually supports -- an unsupported hunch is a 5, not "
    "an 8. Return ONLY valid JSON."
)


def build_inverted_queries(opp: dict) -> list[str]:
    """Inverted search queries: hunt for failure evidence, not confirmation."""
    vertical = (opp.get("vertical") or "").strip()
    geo = (opp.get("geography") or "").strip()
    bucket = (opp.get("bucket") or opp.get("bucket_hypothesis") or vertical).strip()

    raw_queries = [
        f"why {vertical} startups fail" if vertical else None,
        f"{vertical} startup shutdown postmortem" if vertical else None,
        f"{bucket} market too small evidence" if bucket else None,
        f"{vertical} {geo} customers refuse to pay" if vertical and geo else None,
    ]
    queries, seen = [], set()
    for q in raw_queries:
        if q and q not in seen:
            queries.append(q)
            seen.add(q)
    return queries


def _parse_thesis_response(raw: str) -> Optional[dict]:
    """Parse the skeptic JSON; clamp strength to 1-10. None on any malformation."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    thesis = data.get("kill_thesis")
    strength = data.get("kill_thesis_strength")
    if not thesis or strength is None:
        return None
    try:
        strength_int = max(1, min(10, int(strength)))
    except (TypeError, ValueError):
        return None

    evidence = data.get("kill_thesis_evidence") or []
    if not isinstance(evidence, list):
        evidence = [str(evidence)]
    return {
        "kill_thesis": str(thesis).strip(),
        "kill_thesis_strength": strength_int,
        "kill_thesis_evidence": [str(e) for e in evidence[:3]],
    }


def generate_kill_thesis(opp: dict, search_digest: str) -> Optional[dict]:
    """Synthesize the strongest kill thesis from inverted-search evidence.

    Returns None (logged) on missing key or API failure -- adversarial verdicts
    are never fabricated from a fallback heuristic.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from opportunity_os.ai_scorer import _load_env_key
        api_key = _load_env_key()
    if not api_key:
        logger.error("[kill_thesis] No ANTHROPIC_API_KEY -- skipping %s", opp.get("name", "?")[:50])
        return None

    prompt = (
        f"Opportunity: {opp.get('name', '')}\n"
        f"Vertical: {opp.get('vertical', '')} | Geography: {opp.get('geography', '')}\n"
        f"Problem it claims to solve: {opp.get('problem_statement', '') or opp.get('description', '')}\n"
        f"Current score: {opp.get('final_score')}\n\n"
        f"INVERTED SEARCH EVIDENCE (failure signals found on the web):\n{search_digest[:6000]}\n\n"
        'Return ONLY this JSON:\n'
        '{\n'
        '  "kill_thesis": "<the single strongest failure argument, max 60 words>",\n'
        '  "kill_thesis_strength": <int 1-10 per the rubric>,\n'
        '  "kill_thesis_evidence": ["<short evidence cite>", "<short evidence cite>"]\n'
        '}'
    )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SKEPTIC_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = _parse_thesis_response(response.content[0].text)
        if parsed is None:
            logger.error("[kill_thesis] Unparseable response for %s", opp.get("name", "?")[:50])
        return parsed
    except Exception as exc:  # noqa: BLE001 -- any API failure means no verdict, never a fake one
        logger.error("[kill_thesis] API call failed for %s: %s", opp.get("name", "?")[:50], exc)
        return None


def _is_fresh(opp: dict) -> bool:
    stamp = opp.get("kill_thesis_at")
    if not stamp:
        return False
    try:
        return datetime.fromisoformat(stamp) > datetime.now() - timedelta(days=KILL_THESIS_TTL_DAYS)
    except ValueError:
        return False


def run_kill_thesis_pass(opp: dict, force: bool = False) -> dict:
    """Run the adversarial pass on one opportunity. Returns a NEW dict.

    Unchanged (and logged) when: fresh within TTL and not forced, Tavily is
    unavailable, searches return nothing, or synthesis fails.
    """
    name = opp.get("name", "?")[:50]

    if _is_fresh(opp) and not force:
        logger.info("[kill_thesis] %s fresh within %dd TTL -- skipping", name, KILL_THESIS_TTL_DAYS)
        return opp

    if not tavily_client.is_available():
        logger.error("[kill_thesis] Tavily unavailable -- cannot run inverted searches for %s", name)
        return opp

    queries = build_inverted_queries(opp)
    if not queries:
        logger.warning("[kill_thesis] No queries buildable for %s (missing vertical/bucket)", name)
        return opp

    digest = tavily_client.search_multi(queries, max_results_per_query=MAX_RESULTS_PER_QUERY)
    if not digest or not digest.strip():
        logger.warning("[kill_thesis] Inverted searches returned nothing for %s", name)
        return opp

    thesis = generate_kill_thesis(opp, digest)
    if thesis is None:
        return opp

    will_cap = thesis["kill_thesis_strength"] >= KILL_THESIS_CAP_THRESHOLD
    logger.info(
        "[kill_thesis] %s -> strength %d/10%s",
        name, thesis["kill_thesis_strength"], " (CAPS SCORE)" if will_cap else "",
    )
    return {
        **opp,
        **thesis,
        "kill_thesis_at": datetime.now().isoformat(),
    }
