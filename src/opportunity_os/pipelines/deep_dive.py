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

from datetime import datetime
import os


def run_deep_dive(opp_id: str, dry_run: bool = False) -> dict:
    """
    Run a full deep dive for a single opportunity by ID.
    Returns summary dict: {opp_id, path, archetype} or {error}.
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
        print(f"Opportunity {opp_id} not found.")
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
                        "trust_mechanism_latam", "research_executed_at",
                    ) if k in opp
                })
        except Exception as exc:
            print(f"  [deep_dive] Research executor failed ({type(exc).__name__}: {exc}) — continuing without research")

    # Run benchmark analysis
    archetype = classify_archetype(opp)
    analogs = get_analog_benchmarks(opp.get("vertical", ""), opp.get("geography", ""))
    whitespace = detect_whitespace(opp)

    # Run TAM estimate if missing
    if not opp.get("tam_usd_estimate"):
        tam_result = estimate_tam(
            method="bottom_up",
            geography=opp.get("geography", "global"),
            target_customers=1000,
            annual_price_usd=60,
        )
        opp["tam_usd_estimate"] = tam_result.get("tam_usd")

    date = datetime.now().strftime("%Y-%m-%d")
    lines = _build_deep_dive_content(opp, opp_id, date, archetype, analogs, whitespace)
    content = "\n".join(lines) + "\n"

    path = os.path.join(
        _get_project_root(),
        "reports",
        "deep-dives",
        f"{date}-{opp_id}-deep-dive.md",
    )
    if not dry_run:
        write_report(content, path)
        update_opportunity(
            opp_id,
            {"deep_dive_status": "complete", "benchmark_archetype": archetype},
        )

    print(f"Deep dive written: {os.path.basename(path)}")
    return {"opp_id": opp_id, "path": path, "archetype": archetype}


def _build_deep_dive_content(opp: dict, opp_id: str, date: str, archetype: str, analogs: list, whitespace: dict) -> list:
    """Build full deep dive markdown lines from all enriched opp fields."""
    lines = []

    # --- Header ---
    lines += [
        f"# Deep Dive: {opp.get('name', 'Unknown')}",
        f"**Date:** {date} | **ID:** {opp_id}",
        "",
    ]

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
    lines += _section_founder_fit(opp)

    # --- Decision filters ---
    lines += _section_decision_filters(opp)

    # --- First revenue path ---
    lines += _section_first_revenue(opp)

    # --- Kill gate summary ---
    lines += _section_kill_gate(opp)

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


def _section_founder_fit(opp: dict) -> list:
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
        "Fintech & crypto adjacency (Bit2Me, payment rails)",
        "Speed to prototype (Claude Code, MVP systems)",
        "Distribution instincts (WhatsApp funnels, performance, community)",
    ]

    if daniels_wedge is not None:
        lines.append("**Daniel's 6 wedges — match assessment:**")
        for i, label in enumerate(wedge_labels, 1):
            lines.append(f"- {label}")
        lines.append(f"  → **{daniels_wedge}/6 matching**")
        lines.append("")

    return lines


def _section_decision_filters(opp: dict) -> list:
    lines = ["## Decision Filters", ""]

    filter_results = (
        opp.get("DecisionFilterResults")
        or opp.get("decision_filter_results")
        or {}
    )

    filter_labels = {
        "can_sell_fast": "Can Daniel reach the buyer and get real interest in < 2 weeks?",
        "can_build_lean": "MVP < $2K, < 2 people, < 6 weeks?",
        "can_compound": "Can this compound? (software, data, network, repeatable distribution)",
    }

    if isinstance(filter_results, dict):
        passed = sum(1 for v in filter_results.values() if v is True)
        failed = sum(1 for v in filter_results.values() if v is False)

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

    return lines


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


def _section_kill_gate(opp: dict) -> list:
    lines = ["## Kill Gate Summary", ""]

    kill_decision = opp.get("kill_decision")
    kill_criteria_passed = opp.get("kill_criteria_passed")
    kill_reasons = opp.get("kill_reasons") or opp.get("kill_reason")

    if kill_decision:
        lines.append("**STATUS: KILLED** — this opportunity failed the kill gate.")
        if kill_reasons:
            reasons = kill_reasons if isinstance(kill_reasons, list) else [kill_reasons]
            for r in reasons:
                lines.append(f"- {r}")
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

    return lines


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
