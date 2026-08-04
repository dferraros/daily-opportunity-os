"""
Hypothesis Mode -- validate Daniel's OWN ideas, adversarial-first.

Standing requirements 2026-07-22 (a, d, e, f): intake a free-text idea, map its
neighborhood BEFORE judging it, attack it (kill thesis + feasibility
interrogation) BEFORE scoring it, then return a verdict PLUS the neighborhood:
build | validate | pivot_to_neighbor | drop_but_run_neighbor | absorb_into_asset.

Code-enforced (never prompt-trusted):
- legal_opinion_required True  -> "build" downgrades to "validate"
- kill_thesis_strength >= 7    -> "build" downgrades to "validate"

Flow: intake -> neighborhood -> kill thesis -> feasibility -> revenue evidence
-> score x confidence -> neighbor mini-scores -> Sonnet verdict -> report
(+ MVP build package when verdict is build/validate).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from opportunity_os import hypothesis_neighbors
from opportunity_os.hypothesis_neighbors import (
    call_model_json,
    generate_neighborhood,
    run_feasibility_interrogation,
)

logger = logging.getLogger(__name__)

SYNTHESIS_MODEL = os.environ.get("OPP_OS_SYNTHESIS_MODEL", "claude-sonnet-5")

ALLOWED_VERDICTS = frozenset([
    "build", "validate", "pivot_to_neighbor", "drop_but_run_neighbor", "absorb_into_asset",
])

INTAKE_SYSTEM_PROMPT = (
    "You structure a founder's raw business idea into a normalized opportunity "
    "record. Extract only what the text supports; leave unknown fields null. "
    "The problem_statement MUST follow: '[customer] loses [money/time/capacity] "
    "because [specific failing process], currently solved via [workaround]' — "
    "reconstruct it from the idea if implied, null if you cannot. "
    "Return ONLY valid JSON."
)

VERDICT_SYSTEM_PROMPT = (
    "You are the final investment-committee synthesizer. You have the bull case "
    "(scores), the bear case (kill thesis), feasibility answers, and a map of "
    "adjacent plays. Pick ONE verdict: build (evidence supports starting now), "
    "validate (promising, needs the validation sprint), pivot_to_neighbor (a "
    "neighbor beats the original — name it), drop_but_run_neighbor (original "
    "dies but a neighbor deserves its own run — name it), absorb_into_asset "
    "(best as a module of an existing asset — name it). Be decisive and "
    "evidence-bound. Return ONLY valid JSON."
)


def intake_hypothesis(idea_text: str) -> dict:
    """Structure a free-text idea into an Opportunity-shaped dict.

    Fails FAST (RuntimeError) without an Anthropic key — hypothesis mode is
    meaningless on heuristics — and raises ValueError when the structured
    record does not validate against the Opportunity model.
    """
    if not (idea_text or "").strip():
        raise ValueError("intake_hypothesis: idea_text is empty")
    if not hypothesis_neighbors._get_api_key():
        raise RuntimeError(
            "hypothesis mode requires ANTHROPIC_API_KEY — refusing to run on heuristics"
        )

    user = (
        f"IDEA (verbatim from the founder):\n{idea_text.strip()[:4000]}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "name": "<short opportunity name>",\n'
        '  "geography": "venezuela|latam|spain|global|us|other",\n'
        '  "vertical": "<e.g. fintech, logistics, smb_software>",\n'
        '  "problem_statement": "<loses/because/workaround schema or null>",\n'
        '  "target_customer": "<specific buyer or null>",\n'
        '  "monetization_model": "<or null>",\n'
        '  "direct_competitors": ["<only if named or clearly implied>"]\n'
        "}"
    )
    parsed = call_model_json(INTAKE_SYSTEM_PROMPT, user, max_tokens=800)
    if not isinstance(parsed, dict) or not parsed.get("name"):
        raise ValueError("intake_hypothesis: model returned no usable structure")

    raw = {
        **{k: v for k, v in parsed.items() if v not in (None, "", [])},
        "source": "hypothesis",
        "stage": "hypothesis",
        "hypothesis_at": datetime.now().isoformat(),
        "raw_notes": idea_text.strip()[:2000],
        # The trigger for a hypothesis IS the founder's idea (field is required).
        "trigger_signal": f"founder hypothesis: {idea_text.strip()[:180]}",
    }
    if raw.get("geography") not in ("global", "latam", "venezuela", "spain", "us", "other"):
        raw["geography"] = "other"

    from opportunity_os.normalization import validate_opportunity
    model, errors = validate_opportunity(raw)
    if model is None:
        raise ValueError(f"intake_hypothesis: record failed validation: {errors}")
    result = model.model_dump(mode="json")
    logger.info("[hypothesis] Intake: %s (%s/%s)", result["name"][:50],
                result.get("geography"), result.get("vertical"))
    return result


def _score_neighbors(opp: dict, neighbors: list[dict]) -> list[dict]:
    """One batched Haiku call mini-scoring every neighbor from run context.

    No extra searches — recycles evidence already on the record (standing
    requirement d: research spent killing an idea maps its neighborhood).
    """
    if not neighbors:
        return neighbors
    context = (
        f"ORIGINAL: {opp.get('name')} | kill thesis (strength "
        f"{opp.get('kill_thesis_strength', '?')}): {opp.get('kill_thesis', 'n/a')} | "
        f"legal flags: {'; '.join(opp.get('legal_flags') or []) or 'none'} | "
        f"pricing evidence: {opp.get('competitor_pricing_model') or 'none'} | "
        f"funding evidence: {opp.get('competitor_funding_raised') or 'none'}"
    )
    listing = "\n".join(
        f"{i + 1}. {n['name']} [{n['axis']}]: {n['thesis']}" for i, n in enumerate(neighbors)
    )
    user = (
        f"EVIDENCE GATHERED THIS RUN:\n{context}\n\n"
        f"NEIGHBORS:\n{listing}\n\n"
        "Mini-score each neighbor 1-10 (pain reality, feasibility, founder fit "
        "combined) USING ONLY the evidence above. Return ONLY a JSON array of "
        '{"name": "...", "mini_score": <1-10>, "reason": "<1 line>"}'
    )
    parsed = call_model_json(
        "You mini-score adjacent plays from recycled evidence. Return ONLY valid JSON.",
        user, max_tokens=1200,
    )
    if not isinstance(parsed, list):
        logger.warning("[hypothesis] Neighbor mini-scoring failed — neighbors kept unscored")
        return neighbors

    scores = {str(p.get("name", "")): p for p in parsed if isinstance(p, dict)}
    out = []
    for n in neighbors:
        s = scores.get(n["name"], {})
        try:
            mini = max(1.0, min(10.0, float(s.get("mini_score"))))
        except (TypeError, ValueError):
            mini = None
        out.append({**n, "mini_score": mini, "mini_score_reason": str(s.get("reason") or "")[:200]})
    return out


def _synthesize_verdict(opp: dict, neighbors: list[dict]) -> dict:
    """Sonnet verdict over the full run context; sanitized + code-enforced caps."""
    nb = "\n".join(
        f"- {n['name']} [{n['axis']}] mini_score={n.get('mini_score')}: {n['thesis']}"
        for n in neighbors
    ) or "(no neighborhood generated)"
    feas = opp.get("feasibility_answers") or {}
    feas_txt = "\n".join(f"  {k}: {v}" for k, v in list(feas.items())[:12]) or "  (skipped)"
    user = (
        f"HYPOTHESIS: {opp.get('name')}\n"
        f"Problem: {opp.get('problem_statement')}\n"
        f"Customer: {opp.get('target_customer')} | Geo: {opp.get('geography')} | "
        f"Vertical: {opp.get('vertical')}\n"
        f"Score: {opp.get('final_score')} (evidence_coverage {opp.get('evidence_coverage')})\n"
        f"KILL THESIS (strength {opp.get('kill_thesis_strength', 'n/a')}): {opp.get('kill_thesis', 'none')}\n"
        f"LEGAL: opinion_required={opp.get('legal_opinion_required')} "
        f"flags={'; '.join(opp.get('legal_flags') or []) or 'none'}\n"
        f"FEASIBILITY:\n{feas_txt}\n"
        f"REVENUE EVIDENCE: funding={opp.get('competitor_funding_raised') or 'none'} "
        f"pricing={opp.get('competitor_pricing_model') or 'none'}\n"
        f"NEIGHBORHOOD:\n{nb}\n\n"
        "Return ONLY this JSON:\n"
        "{\n"
        '  "verdict": "build|validate|pivot_to_neighbor|drop_but_run_neighbor|absorb_into_asset",\n'
        '  "rationale": "<2-3 sentences, evidence-bound>",\n'
        '  "best_neighbor": "<neighbor name or null>",\n'
        '  "key_unknowns": ["<missing evidence that would change the verdict>"]\n'
        "}"
    )
    parsed = call_model_json(VERDICT_SYSTEM_PROMPT, user, model=SYNTHESIS_MODEL, max_tokens=800)
    if not isinstance(parsed, dict):
        return {
            "verdict": "validate",
            "rationale": "Verdict synthesis failed — defaulting to validate (never build on a failed synthesis).",
            "best_neighbor": None,
            "key_unknowns": ["verdict synthesis failed"],
        }

    verdict = str(parsed.get("verdict") or "").strip()
    if verdict not in ALLOWED_VERDICTS:
        verdict = "validate"
    rationale = str(parsed.get("rationale") or "")[:800]

    # Hard gates — enforced in code, not left to the model.
    if verdict == "build" and opp.get("legal_opinion_required"):
        verdict = "validate"
        rationale += " [DOWNGRADED from build: LEGAL OPINION REQUIRED blocks build promotion.]"
    strength = opp.get("kill_thesis_strength")
    if verdict == "build" and strength is not None and int(strength) >= 7:
        verdict = "validate"
        rationale += f" [DOWNGRADED from build: kill thesis strength {strength}/10.]"

    return {
        "verdict": verdict,
        "rationale": rationale,
        "best_neighbor": parsed.get("best_neighbor") or None,
        "key_unknowns": [str(u)[:200] for u in (parsed.get("key_unknowns") or [])][:6],
    }


def _write_report(opp: dict, neighbors: list[dict], out_dir: Optional[str] = None) -> str:
    """Write the hypothesis report markdown; returns the path."""
    from opportunity_os.storage import get_project_root
    base = Path(out_dir) if out_dir else Path(get_project_root()) / "reports" / "hypotheses"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{datetime.now().strftime('%Y-%m-%d')}-{opp.get('id')}-hypothesis.md"

    nb_rows = "\n".join(
        f"| {n['name']} | {n['axis']} | {n.get('mini_score', '—')} | {n['thesis']} "
        f"| {n.get('mini_score_reason') or n.get('why_it_might_beat_original', '')} |"
        for n in neighbors
    ) or "| (none generated) | | | | |"
    feas = opp.get("feasibility_answers") or {}
    feas_block = "\n".join(f"- **{k}**: {v}" for k, v in feas.items()) or "_Skipped (non-regulated vertical)._"
    sources = opp.get("revenue_evidence_sources") or []
    src_block = "\n".join(f"- {s.get('url')} ({s.get('claim')})" for s in sources if isinstance(s, dict)) or "_None collected._"
    unknowns = "\n".join(f"- {u}" for u in (opp.get("hypothesis_key_unknowns") or [])) or "- (none listed)"
    legal_line = (
        "**[LEGAL OPINION REQUIRED]** — build promotion blocked until verified.\n"
        if opp.get("legal_opinion_required") else ""
    )

    content = f"""# Hypothesis Run: {opp.get('name')}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **ID:** {opp.get('id')} | **Geography:** {opp.get('geography')} | **Vertical:** {opp.get('vertical')}

## Idea (verbatim)
{opp.get('raw_notes', '')}

## Verdict: {str(opp.get('hypothesis_verdict', '')).upper()}
{opp.get('hypothesis_rationale', '')}

Best neighbor: **{opp.get('best_neighbor') or '—'}**
Score: **{opp.get('final_score', '—')}** (evidence coverage {opp.get('evidence_coverage', '—')})

## Kill Thesis (adversarial pass)
Strength: **{opp.get('kill_thesis_strength', 'n/a')}/10**

{opp.get('kill_thesis', '_No kill thesis produced (no search signal or API unavailable)._')}

## Feasibility Interrogation
{legal_line}{feas_block}

**Legal flags:** {'; '.join(opp.get('legal_flags') or []) or 'none'}

## Neighborhood Map
| Neighbor | Axis | Mini-score | Thesis | Note |
|---|---|---|---|---|
{nb_rows}

## Revenue Evidence
- Funding: {opp.get('competitor_funding_raised') or 'none found'}
- Pricing: {opp.get('competitor_pricing_model') or 'none found'}
- TAM note: {opp.get('tam_validation_note') or '—'}

### Citations
{src_block}

## Questions That Cannot Yet Be Answered
{unknowns}
"""
    path.write_text(content, encoding="utf-8")
    return str(path)


def run_hypothesis(
    idea_text: str,
    skip_research: bool = False,
    out_dir: Optional[str] = None,
) -> dict:
    """Full hypothesis-mode run. Returns a summary dict; persists the record."""
    opp = intake_hypothesis(idea_text)

    # 1. Neighborhood BEFORE judgment (evidence gets tagged against it).
    neighbors = generate_neighborhood(opp)

    # 2. Adversarial-first: kill thesis, then feasibility interrogation.
    from opportunity_os.kill_thesis import run_kill_thesis_pass
    opp = run_kill_thesis_pass(opp, force=True)
    opp = {**opp, **run_feasibility_interrogation(opp)}

    # 3. Evidence: revenue search (skippable for cost control).
    if not skip_research:
        from opportunity_os.revenue_evidence import run_revenue_evidence
        opp = run_revenue_evidence(opp, force=True)

    # 4. Score with confidence (AI dims + engine caps; kill-thesis cap applies).
    from opportunity_os.ai_scorer import score_dimensions_with_ai
    from opportunity_os.engines.scoring_engine import score_opportunity
    opp = score_dimensions_with_ai(opp)
    opp = score_opportunity(opp)

    # 5. Neighbor mini-scores from recycled evidence.
    neighbors = _score_neighbors(opp, neighbors)

    # 6. Verdict (Sonnet), with code-enforced downgrades.
    verdict = _synthesize_verdict(opp, neighbors)
    opp = {
        **opp,
        "neighborhood": neighbors,
        "hypothesis_verdict": verdict["verdict"],
        "hypothesis_rationale": verdict["rationale"],
        "best_neighbor": verdict["best_neighbor"],
        "hypothesis_key_unknowns": verdict["key_unknowns"],
    }

    # 7. Persist + report (+ build package when the verdict warrants it).
    from opportunity_os.storage import append_opportunity
    opp_id = append_opportunity(opp)
    opp = {**opp, "id": opp.get("id") or opp_id}
    report_path = _write_report(opp, neighbors, out_dir=out_dir)

    build_paths: dict = {}
    if verdict["verdict"] in ("build", "validate"):
        from opportunity_os.mvp_build_spec import write_build_package
        build_paths = write_build_package(opp, out_dir=out_dir)

    logger.info(
        "[hypothesis] %s -> %s (best neighbor: %s)",
        opp.get("name", "?")[:50], verdict["verdict"], verdict["best_neighbor"] or "—",
    )
    return {
        "opp": opp,
        "verdict": verdict["verdict"],
        "rationale": verdict["rationale"],
        "best_neighbor": verdict["best_neighbor"],
        "key_unknowns": verdict["key_unknowns"],
        "report_path": report_path,
        "build_paths": build_paths,
    }
