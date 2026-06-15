"""
Deep dive pipeline -- full analysis for a single shortlisted opportunity.

Generates a comprehensive markdown deep dive that incorporates ALL enriched fields:
- Pain validation (score, phrases, evidence, workarounds)
- Distribution (channels, CAC logic, first-10-customer path, trust mechanism)
- Market sizing (TAM/SAM/SOM)
- Benchmark archetypes and analog comparables
- Venezuela wedge analysis (when geography == venezuela)
- Decision filters and founder-fit signals
- First revenue path
- Kill gate summary and scoring breakdown

Auto-runs research_executor if the opp has not been researched yet.
"""

import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

RICH_REASONS_TTL_DAYS = 30


def _needs_rich_reasons(opp: dict) -> bool:
    """True if the opp lacks fresh full-dimension reasoning.

    The daily batch scorer stores only 4 sample reasons; a deep dive wants all
    16 evidence-backed ones. Skip the refresh only if it ran within the TTL, so
    repeat dives of the same opp don't re-pay for the Haiku call.
    """
    stamp = opp.get("dimension_reasons_at")
    if not stamp:
        return True
    try:
        return datetime.fromisoformat(stamp) <= datetime.now() - timedelta(days=RICH_REASONS_TTL_DAYS)
    except ValueError:
        return True


def run_deep_dive(opp_id: str, dry_run: bool = False, synthesize: bool = False) -> dict:
    """
    Run a full deep dive for a single opportunity by ID.

    synthesize=True adds a Sonnet-powered judgment section (~$0.10/dive, Wave 2.2).
    Returns summary dict: {opp_id, path, archetype, synthesized} or {error}.
    """
    from opportunity_os.storage import get_opportunity_by_id, update_opportunity
    from opportunity_os.engines.tam_engine import estimate_tam
    from opportunity_os.engines.benchmark_engine import (
        classify_archetype,
        get_analog_benchmarks,
        detect_whitespace,
    )
    from opportunity_os.reports import write_report, ensure_report_dirs

    ensure_report_dirs()

    opp = get_opportunity_by_id(opp_id)
    if not opp:
        logger.warning("Opportunity %s not found.", opp_id)
        return {"error": f"Not found: {opp_id}"}

    # Auto-research if this opp hasn't been through the research executor yet
    if not opp.get("research_executed_at"):
        try:
            from opportunity_os.research_executor import run_research_executor
            opp = run_research_executor(opp)
            if not dry_run:
                update_opportunity(opp_id, {
                    k: opp[k] for k in (
                        "pain_validation_score", "exact_customer_phrases",
                        "pain_evidence_sources", "workarounds_found",
                        "distribution_validated", "top_distribution_channels",
                        "estimated_cac_logic", "first_10_customer_path",
                        "trust_mechanism_latam", "direct_competitors",
                        "research_executed_at",
                    ) if k in opp
                })
        except Exception as exc:
            logger.warning("[deep_dive] Research executor failed (%s: %s) — continuing without research", type(exc).__name__, exc)

    # Refresh full per-dimension reasoning for THIS opp (the daily batch scorer
    # only stores 4 sample reasons to save tokens; the deep dive is where the
    # full 16 evidence-backed reasons earn their cost). Guarded so repeat dives
    # of the same opp don't re-pay.
    if _needs_rich_reasons(opp):
        try:
            from opportunity_os.ai_scorer import score_dimensions_with_ai
            scored = score_dimensions_with_ai({**opp, "rescore_requested": True})
            # Take ONLY the _reason text, never the re-scored numbers: the numeric
            # dimensions feed final_score + portfolio normalization (computed by the
            # batch scorer across all opps), so re-scoring one opp here would desync
            # its report from its stored/normalized score.
            reason_updates = {k: v for k, v in scored.items() if k.endswith("_reason")}
            reason_updates["dimension_reasons_at"] = datetime.now().isoformat()
            opp = {**opp, **reason_updates}
            if not dry_run:
                update_opportunity(opp_id, reason_updates)
        except Exception as exc:
            logger.warning("[deep_dive] Dimension reasoning refresh failed (%s: %s)", type(exc).__name__, exc)

    # Run benchmark analysis
    archetype = classify_archetype(opp)
    analogs = get_analog_benchmarks(opp.get("vertical", ""), opp.get("geography", ""))
    whitespace = detect_whitespace(opp)

    # Run TAM estimate if missing — derive inputs from opp instead of hardcoding
    if not opp.get("tam_usd_estimate"):
        target_customers, annual_price_usd = _derive_tam_inputs(opp)
        tam_result = estimate_tam(
            method="bottom_up",
            geography="global",  # geo already baked into inputs by _derive_tam_inputs
            target_customers=target_customers,
            annual_price_usd=annual_price_usd,
        )
        opp = {**opp, "tam_usd_estimate": tam_result.get("tam_usd")}

    # Optional Sonnet synthesis (Wave 2.2) -- opt-in, costs ~$0.10/dive
    synthesis = None
    if synthesize:
        from opportunity_os.deep_dive_synthesis import synthesize_opportunity
        synthesis = synthesize_opportunity(opp)
        if synthesis is None:
            logger.warning("[deep_dive] Synthesis requested but unavailable for %s -- writing without it", opp_id)

    date = datetime.now().strftime("%Y-%m-%d")
    lines = _build_deep_dive_content(opp, opp_id, date, archetype, analogs, whitespace, synthesis)
    content = "\n".join(lines) + "\n"

    path = os.path.join(
        _get_project_root(),
        "reports",
        "deep-dives",
        f"{date}-{opp_id}-deep-dive.md",
    )
    if not dry_run:
        write_report(content, path)
        dd_updates = {"deep_dive_status": "complete", "benchmark_archetype": archetype}
        if synthesis:
            dd_updates.update(synthesis)
        update_opportunity(opp_id, dd_updates)

    logger.info("Deep dive written: %s", os.path.basename(path))
    return {"opp_id": opp_id, "path": path, "archetype": archetype,
            "synthesized": synthesis is not None}


def _build_deep_dive_content(opp: dict, opp_id: str, date: str, archetype: str,
                             analogs: list, whitespace: dict, synthesis: dict = None) -> list:
    """Build full deep dive markdown lines from all enriched opp fields."""
    lines = []

    # --- Header ---
    lines += [
        f"# Deep Dive: {opp.get('name', 'Unknown')}",
        f"**Date:** {date} | **ID:** {opp_id}",
        "",
    ]

    # --- Analyst synthesis (Sonnet) -- judgment up top, before the raw layout ---
    if synthesis:
        from opportunity_os.deep_dive_synthesis import build_synthesis_section
        lines += build_synthesis_section(synthesis)

    # --- Thesis snapshot ---
    lines += _section_thesis(opp)

    # --- Market sizing ---
    lines += _section_market_size(opp)

    # --- Pain validation ---
    lines += _section_pain_validation(opp)

    # --- Distribution & GTM ---
    lines += _section_distribution(opp)

    # --- Venezuela wedge (only when relevant) ---
    if opp.get("geography") == "venezuela" or opp.get("venezuela_wedge_category"):
        lines += _section_venezuela(opp)

    # --- Benchmark archetypes & analogs ---
    lines += _section_benchmarks(opp, archetype, analogs, whitespace)

    # --- Founder fit & Daniel's wedges ---
    lines += _section_founder_fit(opp).split("\n")

    # --- Full per-variable scoring breakdown (every dimension + reason) ---
    lines += _section_scoring_breakdown(opp)

    # --- Decision filters ---
    lines += _section_decision_filters(opp).split("\n")

    # --- First revenue path ---
    lines += _section_first_revenue(opp)

    # --- Kill gate summary ---
    lines += _section_kill_gate(opp).split("\n")

    # --- Next actions ---
    lines += _section_next_actions(opp)

    return lines


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _section_thesis(opp: dict) -> list:
    score = opp.get("final_score", "N/A")
    raw_score = opp.get("raw_final_score")
    score_str = f"{score}/10"
    if raw_score is not None and raw_score != score:
        score_str += f" (raw: {raw_score})"

    lines = [
        "## Opportunity Summary",
        opp.get("problem_statement") or opp.get("description") or "No problem statement.",
        "",
        f"**Geography:** {opp.get('geography', 'N/A')} | "
        f"**Vertical:** {opp.get('vertical', 'N/A')} | "
        f"**Bucket:** {opp.get('bucket', 'N/A')}",
        f"**Score:** {score_str} | **Lane:** {opp.get('portfolio_lane', 'N/A')} | "
        f"**Stage:** {opp.get('stage', 'scout')}",
        f"**Business model:** {opp.get('business_model_type', 'N/A')}",
        "",
    ]
    target = opp.get("target_customer")
    if target:
        lines += [f"**Target customer:** {target}", ""]

    thesis_score = opp.get("thesis_fit_score")
    if thesis_score is not None:
        lines += [f"**Thesis fit:** {thesis_score}/10", ""]

    return lines


def _section_market_size(opp: dict) -> list:
    lines = ["## Market Size", ""]

    tam = opp.get("tam_usd_estimate") or opp.get("tam") or 0
    sam = opp.get("sam_usd_estimate") or 0
    som = opp.get("som_usd_estimate") or 0

    def _fmt(v) -> str:
        try:
            fv = float(v)
            if fv >= 1_000_000_000:
                return f"${fv / 1_000_000_000:.1f}B"
            if fv >= 1_000_000:
                return f"${fv / 1_000_000:.1f}M"
            if fv >= 1_000:
                return f"${fv / 1_000:.0f}K"
            return f"${fv:,.0f}"
        except (TypeError, ValueError):
            return str(v) if v else "N/A"

    lines += [
        f"| Level | Estimate | Notes |",
        f"|-------|----------|-------|",
        f"| TAM | {_fmt(tam)} | Total addressable market |",
        f"| SAM | {_fmt(sam) if sam else '—'} | Serviceable addressable |",
        f"| SOM | {_fmt(som) if som else '—'} | Serviceable obtainable (Y1-3) |",
        "",
    ]

    notes = opp.get("tam_estimation_notes") or opp.get("tam_notes")
    if notes:
        lines += [f"**TAM methodology:** {notes}", ""]

    return lines


def _section_pain_validation(opp: dict) -> list:
    lines = ["## Pain Validation", ""]

    pvs = opp.get("pain_validation_score")
    pain_bar = _score_bar(pvs) if pvs is not None else "Not researched"
    lines.append(f"**Pain validation score:** {pain_bar}")
    lines.append("")

    phrases = opp.get("exact_customer_phrases") or []
    if phrases:
        lines.append("**Real customer phrases:**")
        for p in phrases:
            lines.append(f'> "{p}"')
        lines.append("")

    workarounds = opp.get("workarounds_found") or []
    if workarounds:
        lines.append("**Current workarounds (what people do today):**")
        for w in workarounds:
            lines.append(f"- {w}")
        lines.append("")

    sources = opp.get("pain_evidence_sources") or []
    if sources:
        lines.append("**Evidence sources:**")
        for s in sources:
            lines.append(f"- {s}")
        lines.append("")

    if not phrases and not sources and pvs is None:
        lines += ["_No pain research available. Run `/validation-runner` to validate._", ""]

    return lines


def _section_distribution(opp: dict) -> list:
    lines = ["## Distribution & Go-To-Market", ""]

    channels = opp.get("top_distribution_channels") or []
    is_validated = opp.get("distribution_validated")
    validated_label = "Validated" if is_validated else ("Not validated" if is_validated is False else "Unknown")
    lines.append(f"**Distribution status:** {validated_label}")
    lines.append("")

    if channels:
        lines.append("**Top channels:**")
        for c in channels:
            lines.append(f"- {c}")
        lines.append("")

    cac = opp.get("estimated_cac_logic")
    if cac:
        lines += [f"**CAC logic:** {cac}", ""]

    path_10 = opp.get("first_10_customer_path")
    if path_10:
        lines += [f"**Path to first 10 customers:** {path_10}", ""]

    trust = opp.get("trust_mechanism_latam")
    if trust:
        lines += [f"**Trust mechanism (LATAM/VE):** {trust}", ""]

    if not channels and not cac and not path_10:
        lines += ["_No distribution research available. Run distribution-mapper skill._", ""]

    return lines


def _section_venezuela(opp: dict) -> list:
    lines = ["## Venezuela Wedge Analysis", ""]

    wedge_cat = opp.get("venezuela_wedge_category")
    if wedge_cat:
        lines += [f"**Wedge category:** `{wedge_cat}`", ""]

    why_now = opp.get("why_now_venezuela") or {}
    if isinstance(why_now, dict) and why_now:
        lines.append("**Why now in Venezuela:**")
        field_labels = {
            "local_friction": "Local friction",
            "friction_persistence": "Why it persists",
            "who_suffers_most": "Who suffers most",
            "recent_change": "Recent change",
            "regional_export_potential": "Export potential",
        }
        for key, label in field_labels.items():
            val = why_now.get(key)
            if val:
                lines.append(f"- **{label}:** {val}")
        lines.append("")

    ve_adjustments = [
        ("WTP multiplier", "0.25x vs US baseline"),
        ("SaaS pricing", "$3–15/month"),
        ("Payment rails", "Zelle, USDT, Binance P2P"),
        ("Distribution", "WhatsApp-first, TikTok organic"),
        ("Trust signal", "referral > brand"),
    ]
    lines.append("**Venezuela adjustments applied:**")
    for label, val in ve_adjustments:
        lines.append(f"- {label}: {val}")
    lines.append("")

    return lines


def _section_benchmarks(opp: dict, archetype: str, analogs: list, whitespace: dict) -> list:
    lines = [
        "## Archetype & Benchmarks",
        "",
        f"**Archetype:** `{archetype}` | `{opp.get('benchmark_archetype', 'unclassified')}`",
        "",
    ]

    if analogs:
        lines.append("**Analog comparables:**")
        lines.append("| Company | Model | Lesson |")
        lines.append("|---------|-------|--------|")
        for a in analogs[:3]:
            lines.append(f"| {a.get('name', '?')} | {a.get('model', '?')} | {a.get('lesson', '—')} |")
        lines.append("")

    weak_signals = whitespace.get("weak_competitor_signals") or []
    if weak_signals:
        lines.append("**Competitive whitespace signals:**")
        for s in weak_signals:
            lines.append(f"- {s}")
        lines.append("")

    non_obviousness = opp.get("non_obviousness_score")
    if non_obviousness is not None:
        lines += [f"**Non-obviousness score:** {non_obviousness}/8", ""]

    return lines


def _section_founder_fit(opp: dict) -> str:
    lines = ["## Founder Fit", ""]

    daniels_wedge = opp.get("daniels_wedge_score")
    founder_fit = opp.get("founder_fit_score")

    if daniels_wedge is not None:
        risk_flag = " ⚠ founder-fit risk" if float(daniels_wedge) < 2 else ""
        lines += [f"**Daniel's wedge score:** {daniels_wedge}/6{risk_flag}", ""]

    if founder_fit is not None:
        lines += [f"**Founder-fit score:** {founder_fit}/10", ""]

    wedge_labels = [
        "Growth & GTM edge (lifecycle, CRM, paid, organic, A/B)",
        "Narrative & positioning edge (frame and sell a story fast)",
        "LATAM + Spanish-speaking intuition (Venezuela, Spain, Colombia)",
        "Fintech & crypto adjacency (exchange ops, payment rails)",
        "Speed to prototype (Claude Code, MVP systems)",
        "Distribution instincts (WhatsApp funnels, performance, community)",
    ]

    wedge_matches = _infer_wedge_matches(opp)
    matched = sum(wedge_matches)
    risk_flag = " ⚠ founder-fit risk" if matched < 2 else ""
    lines.append(f"**Daniel's 6 wedges — match assessment ({matched}/6{risk_flag}):**")
    for label, is_match in zip(wedge_labels, wedge_matches):
        icon = "[+]" if is_match else "[ ]"
        lines.append(f"- {icon} {label}")
    lines.append("")

    return "\n".join(lines)


_DATA_BACKED_DIMS = {
    "pain_validation_score", "market_momentum_score",
    "competitor_weakness_score", "distribution_quality",
}
_DIM_LABELS = {
    "market_size": "Market size", "timing_tailwind": "Timing tailwind",
    "pain_severity": "Pain severity", "willingness_to_pay": "Willingness to pay",
    "monetization_clarity": "Monetization clarity", "pain_validation_score": "Pain validation (researched)",
    "speed_to_mvp": "Speed to MVP", "capital_efficiency": "Capital efficiency",
    "distribution_accessibility": "Distribution accessibility",
    "distribution_quality": "Distribution quality (validated)",
    "competition_intensity": "Competition intensity (inverted)", "defensibility": "Defensibility",
    "regional_fit": "Regional fit", "founder_fit": "Founder fit", "ai_leverage": "AI leverage",
    "operational_simplicity": "Operational simplicity", "regulatory_simplicity": "Regulatory simplicity",
    "revenue_speed_score": "Revenue speed", "gross_margin_potential": "Gross margin potential",
    "network_effect_strength": "Network effect strength", "switching_cost_score": "Switching cost",
    "market_momentum_score": "Market momentum (job postings)",
    "competitor_weakness_score": "Competitor weakness (reviews)",
}


def _scoring_layer_table(opp: dict, fields: list, weight_map: dict) -> list:
    """One markdown table: every dimension in a layer with score, weight, contribution, why.

    Surfaces the per-dimension `<dim>_reason` the AI scorer already computes (and
    that the report previously discarded), plus the data-backed basis. Weight-0
    dimensions are shown but marked 'not scored' so the breakdown is honest about
    what actually moved the number.
    """
    rows = []
    for field in fields:
        value = opp.get(field)
        weight = weight_map.get(field, 0.0)
        label = _DIM_LABELS.get(field, field)
        score_str = f"{value}/10" if value is not None else "—"

        if weight == 0.0:
            weight_str, contrib_str = "0 (consolidated)", "—"
        else:
            weight_str = f"{weight:.2f}"
            if value is not None:
                eff = (10.0 - float(value)) if field == "competition_intensity" else float(value)
                contrib_str = f"{eff * weight:.2f}"
            else:
                contrib_str = "—"

        why = opp.get(f"{field}_reason") or ""
        if not why and field in _DATA_BACKED_DIMS:
            why = "_data-backed signal (no narrative)_"
        why = str(why).replace("\n", " ").replace("|", "/")[:160] or "—"

        rows.append(f"| {label} | {score_str} | {weight_str} | {contrib_str} | {why} |")
    return rows


def _section_scoring_breakdown(opp: dict) -> list:
    """Complete dimension-by-dimension scoring breakdown -- the deep research the
    layer-aggregate summary hides. Every one of the ~23 dimensions with its score,
    weight, weighted contribution, and the reasoning behind it."""
    from opportunity_os.engines.scoring_engine import (
        ATTRACTIVENESS_FIELDS, EXECUTABILITY_FIELDS, STRATEGIC_VALUE_FIELDS, load_weights,
    )

    weight_map = load_weights().get("weights", {})
    lines = [
        "## Scoring Breakdown — Every Variable",
        "",
        "Each dimension the score is built from: its 1-10 value, its weight, its weighted "
        "contribution, and the reasoning behind the value. Weight-0 rows were consolidated "
        "out (redundant signal) and do not move the score.",
        "",
    ]

    for layer_name, layer_pct, fields, layer_score_field in [
        ("Attractiveness", "50%", ATTRACTIVENESS_FIELDS, "attractiveness_score"),
        ("Executability", "30%", EXECUTABILITY_FIELDS, "executability_score"),
        ("Strategic Value", "20%", STRATEGIC_VALUE_FIELDS, "strategic_value_score"),
    ]:
        layer_score = opp.get(layer_score_field)
        score_label = f" — layer score {layer_score}/10" if layer_score is not None else ""
        lines += [
            f"### {layer_name} ({layer_pct} of composite){score_label}",
            "",
            "| Dimension | Score | Weight | Contribution | Why |",
            "|-----------|-------|--------|--------------|-----|",
        ]
        lines += _scoring_layer_table(opp, fields, weight_map)
        lines.append("")

    # Adversarial counterweight: the kill thesis caps the score regardless of the above.
    kt = opp.get("kill_thesis")
    if kt:
        strength = opp.get("kill_thesis_strength")
        lines += [
            "### Adversarial check (kill thesis)",
            "",
            f"**Strength {strength}/10** — {str(kt).replace(chr(10), ' ')}",
            ("_Strength >= 7 caps the final score at 5.0._" if (strength or 0) >= 7
             else "_Below the cap threshold; recorded as a watch-item._"),
            "",
        ]

    return lines


def _section_decision_filters(opp: dict) -> str:
    lines = ["## Decision Filters", ""]

    filter_results = opp.get("decision_filter_results") or {}

    filter_labels = {
        "can_sell_fast": "Can Daniel reach the buyer and get real interest in < 2 weeks?",
        "can_build_lean": "MVP < $2K, < 2 people, < 6 weeks?",
        "can_compound": "Can this compound? (software, data, network, repeatable distribution)",
    }
    _FILTER_KEYS = ("can_sell_fast", "can_build_lean", "can_compound")

    if isinstance(filter_results, dict):
        # Scope count to known filter keys only — avoids Pydantic computed fields
        # (e.g. should_cap_score=True) being counted as passing filters.
        passed = sum(1 for k in _FILTER_KEYS if filter_results.get(k) is True)
        failed = sum(1 for k in _FILTER_KEYS if filter_results.get(k) is False)

        should_cap = filter_results.get("should_cap_score") or failed >= 2
        cap_warning = " — **SCORE CAPPED AT 5.0**" if should_cap else ""

        lines.append(f"**Passed {passed}/3{cap_warning}**")
        lines.append("")

        for key, label in filter_labels.items():
            val = filter_results.get(key)
            if val is True:
                icon = "PASS"
            elif val is False:
                icon = "FAIL"
            else:
                icon = "?"
            lines.append(f"- [{icon}] {label}")
        lines.append("")
    else:
        lines += ["_Decision filters not yet evaluated._", ""]

    filters_failed = opp.get("decision_filters_failed", 0)
    if filters_failed:
        lines += [f"**Filters failed count:** {filters_failed}", ""]

    return "\n".join(lines)


def _section_first_revenue(opp: dict) -> list:
    lines = ["## First Revenue Path", ""]

    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict) and frp:
        field_labels = {
            "first_customer_type": "Customer type",
            "first_offer": "First offer",
            "first_sales_channel": "Sales channel",
            "first_price_point": "Price point",
            "first_proof_point_needed": "Proof needed",
        }
        for key, label in field_labels.items():
            val = frp.get(key)
            if val:
                lines.append(f"**{label}:** {val}")
        lines.append("")

    path_desc = opp.get("path_to_first_revenue_description") or opp.get("path_to_first_revenue")
    if path_desc and not frp:
        lines += [f"**Revenue path:** {path_desc}", ""]

    if not frp and not path_desc:
        lines += ["_First revenue path not specified. Define offer + sales channel + price point._", ""]

    return lines


def _section_kill_gate(opp: dict) -> str:
    lines = ["## Kill Gate Summary", ""]

    kill_decision = opp.get("kill_decision")
    kill_criteria_passed = opp.get("kill_criteria_passed")
    kill_reasons = opp.get("kill_reasons") or opp.get("kill_reason")

    if kill_decision:
        lines.append("**STATUS: KILLED** — this opportunity failed the kill gate.")
        if kill_reasons:
            reasons = kill_reasons if isinstance(kill_reasons, list) else [kill_reasons]
            for r in reasons:
                # Sanitize embedded newlines from LLM-sourced fields — a bare \n
                # inside a list item corrupts the section when joined then split.
                sanitized = str(r).replace("\n", " ").replace("\r", " ")
                lines.append(f"- {sanitized}")
    else:
        gate_str = f"{kill_criteria_passed}/7" if kill_criteria_passed is not None else "N/A"
        lines.append(f"**Kill gate:** PASSED | Criteria met: {gate_str}")

    lines.append("")

    # Scoring breakdown
    a = opp.get("attractiveness_score")
    e = opp.get("executability_score")
    s = opp.get("strategic_value_score")
    f = opp.get("final_score")

    if any(v is not None for v in [a, e, s, f]):
        lines.append("**Scoring breakdown:**")
        lines.append("| Layer | Score |")
        lines.append("|-------|-------|")
        if a is not None:
            lines.append(f"| Attractiveness (50%) | {a}/10 |")
        if e is not None:
            lines.append(f"| Executability (30%) | {e}/10 |")
        if s is not None:
            lines.append(f"| Strategic value (20%) | {s}/10 |")
        if f is not None:
            lines.append(f"| **Final score** | **{f}/10** |")
        lines.append("")

    # VC moat fields — only shown when present (optional fields, absent = neutral)
    gm = opp.get("gross_margin_potential")
    ne = opp.get("network_effect_strength")
    sw = opp.get("switching_cost_score")
    if any(v is not None for v in [gm, ne, sw]):
        lines.append("**VC moat signals:**")
        if gm is not None:
            lines.append(f"- Gross margin potential: {gm}/10")
        if ne is not None:
            lines.append(f"- Network effect strength: {ne}/10")
        if sw is not None:
            lines.append(f"- Switching cost score: {sw}/10")
        lines.append("")

    return "\n".join(lines)


def _section_next_actions(opp: dict) -> list:
    lane = opp.get("portfolio_lane", "soon")
    score = float(opp.get("final_score", 0) or 0)
    geography = opp.get("geography", "")

    lines = ["## Recommended Next Actions", ""]

    if lane == "now":
        lines += [
            "**Lane: NOW** — Start validation immediately.",
            "",
            "1. Run `validation-runner` skill to build landing page test + interview script",
            "2. Find first 5 target customers (see First Revenue Path above)",
            "3. Send first 3 cold messages this week",
            "4. Set a 14-day go/no-go decision date",
        ]
    elif lane == "soon":
        lines += [
            "**Lane: SOON** — Queue for next validation cycle (60-90 days).",
            "",
            "1. Run `customer-pain-miner` to deepen evidence",
            "2. Monitor for timing catalysts",
            "3. Revisit in the next weekly review",
        ]
    elif lane == "strategic":
        lines += [
            "**Lane: STRATEGIC** — High-upside, slower build. Track the signal.",
            "",
            "1. Identify the key thesis risk (regulatory? technology? distribution?)",
            "2. Set a check-in milestone in 60 days",
            "3. Watch for a fast-cash entry point within this vertical",
        ]
    else:
        lines += [
            "**Lane: NO** — Rejected. Reason logged.",
            "",
            f"Kill reason: {opp.get('kill_reason', 'See kill gate above')}",
        ]

    if geography in ("venezuela", "latam"):
        lines += [
            "",
            f"**LATAM/VE note:** WhatsApp is the primary channel here. "
            f"First contact via personal referral > cold outreach.",
        ]

    lines.append("")
    lines += [
        "---",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"Research: {'complete' if opp.get('research_executed_at') else 'pending'}*",
    ]

    return lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_bar(score: float, width: int = 10) -> str:
    """Convert a 0-10 score into a simple text bar + label."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "N/A"

    filled = round(s)
    bar = "█" * filled + "░" * (width - filled)
    label = (
        "STRONG" if s >= 8 else
        "MODERATE" if s >= 6 else
        "WEAK" if s >= 4 else
        "VERY WEAK"
    )
    return f"{bar} {s:.1f}/10 ({label})"


def _get_project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])


def _derive_tam_inputs(opp: dict) -> tuple:
    """Derive TAM estimation inputs from opp fields instead of using hardcoded values.

    Returns (target_customers: int, annual_price_usd: int).
    """
    geo = (opp.get("geography") or "global").lower()
    wtp = float(opp.get("willingness_to_pay") or 5)

    geo_market_size = {
        "venezuela": 50_000,
        "latam": 500_000,
        "colombia": 100_000,
        "mexico": 200_000,
        "spain": 150_000,
        "global": 1_000_000,
    }
    geo_price_mult = {
        "venezuela": 0.25,
        "latam": 0.5,
        "colombia": 0.6,
        "mexico": 0.6,
        "spain": 1.1,
        "global": 1.0,
    }
    base_customers = geo_market_size.get(geo, 500_000)
    mult = geo_price_mult.get(geo, 1.0)
    annual_price_usd = max(36, int(wtp * 10 * mult * 12))
    return base_customers, annual_price_usd


def _infer_wedge_matches(opp: dict) -> list:
    """Infer per-wedge match for Daniel's 6 wedges. Returns 6-element list of bools."""
    geo = (opp.get("geography") or "").lower()
    vertical = (opp.get("vertical") or "").lower()
    tags = " ".join([
        str(opp.get("vertical", "")),
        str(opp.get("business_model_type", "")),
        str(opp.get("problem_statement", "")),
        str(opp.get("path_to_first_revenue", "")),
    ]).lower()

    wedge_1 = any(t in tags for t in ["saas", "crm", "lifecycle", "marketing", "growth", "acquisition"])
    # wedge_2: narrative + positioning — requires a concrete revenue hypothesis AND timing signal.
    # The previous proxy (len > 40) matched almost every opp and was meaningless.
    wedge_2 = bool(
        opp.get("path_to_first_revenue") and
        (opp.get("why_now") or opp.get("trigger_signal"))
    )
    wedge_3 = geo in ("venezuela", "latam", "colombia", "mexico", "spain")
    wedge_4 = vertical == "fintech" or any(
        t in tags for t in ["payment", "crypto", "usdt", "remittance", "banking", "wallet"]
    )
    wedge_5 = float(opp.get("speed_to_mvp") or 0) >= 7
    channels = opp.get("top_distribution_channels") or []
    channel_str = " ".join(str(c).lower() for c in channels)
    wedge_6 = (
        any(t in channel_str for t in ["whatsapp", "community", "telegram", "reddit"])
        or geo == "venezuela"
    )
    return [wedge_1, wedge_2, wedge_3, wedge_4, wedge_5, wedge_6]
