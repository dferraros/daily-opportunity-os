"""Export a self-contained markdown report bundle for one opportunity.

Used by `opp-os export` and the dashboard download button. Pure assembly from
the stored record plus any validation / deep-dive markdown already on disk --
no API calls, no key requirements.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from opportunity_os.storage import get_opportunity_by_id, get_project_root

logger = logging.getLogger(__name__)

# Dimension list mirrors ai_scorer.DIMENSIONS; each pairs with a *_reason field.
SCORED_DIMENSIONS = [
    "pain_severity", "market_size", "timing_tailwind", "willingness_to_pay",
    "monetization_clarity", "speed_to_mvp", "capital_efficiency",
    "distribution_accessibility", "competition_intensity", "defensibility",
    "regional_fit", "founder_fit", "ai_leverage", "operational_simplicity",
    "regulatory_simplicity", "revenue_speed_score",
]


def _fmt_money(val) -> str:
    try:
        v = float(val)
    except (TypeError, ValueError):
        return str(val) if val else "--"
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"${v / 1e6:.1f}M"
    if v >= 1e3:
        return f"${v / 1e3:.0f}K"
    return f"${v:.0f}"


def _section(title: str, lines: list[str]) -> str:
    body = "\n".join(lines).strip()
    return f"## {title}\n\n{body}\n" if body else ""


def _bullets(items, limit: int = 10) -> list[str]:
    return [f"- {str(i).strip()}" for i in (items or [])[:limit] if str(i).strip()]


def find_attached_reports(opp_id: str) -> dict:
    """Return {'validation': text|None, 'deep_dive': text|None} from reports/ on disk."""
    root = Path(get_project_root())
    attached: dict = {"validation": None, "deep_dive": None}
    safe_id = str(opp_id)[:40]
    for key, subdir, suffix in [
        ("validation", "validation", "-validation.md"),
        ("deep_dive", "deep-dives", "-deep-dive.md"),
    ]:
        report_dir = root / "reports" / subdir
        if not report_dir.exists():
            continue
        matches = sorted(
            (f for f in report_dir.glob(f"*{suffix}") if safe_id in f.name),
            reverse=True,
        )
        if matches:
            try:
                attached[key] = matches[0].read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("export: could not read %s: %s", matches[0], exc)
    return attached


def build_opportunity_report_md(opp: dict, attached: Optional[dict] = None) -> str:
    """Assemble the full report markdown for one opportunity record."""
    attached = attached or {}
    name = opp.get("name", "Unknown")
    score = opp.get("final_score")
    score_str = f"{float(score):.2f}/10" if score is not None else "unscored"
    raw = opp.get("raw_final_score")
    raw_str = f" (raw {float(raw):.2f})" if raw is not None else ""

    parts: list[str] = [
        f"# {name}",
        "",
        f"**Score:** {score_str}{raw_str} | **Lane:** {opp.get('portfolio_lane', '--')} | "
        f"**Geography:** {opp.get('geography', '--')} | **Vertical:** {opp.get('vertical', '--')} | "
        f"**Bucket:** {opp.get('bucket', '--')}",
        "",
        f"_ID: `{opp.get('id', '')}` | Stage: {opp.get('stage', '--')} | "
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
    ]

    # --- Problem ---
    problem_lines = [
        f"**Problem:** {opp.get('problem_statement', '--')}",
        "",
        f"**Target customer:** {opp.get('target_customer', '--')}",
        "",
        f"**Trigger signal:** {opp.get('trigger_signal', '--')}",
    ]
    if opp.get("why_now"):
        problem_lines += ["", f"**Why now:** {opp['why_now']}"]
    parts.append(_section("Problem", problem_lines))

    # --- Scoring breakdown ---
    layer_lines = []
    for label, field in [
        ("Attractiveness (50%)", "attractiveness_score"),
        ("Executability (30%)", "executability_score"),
        ("Strategic value (20%)", "strategic_value_score"),
    ]:
        v = opp.get(field)
        layer_lines.append(f"- **{label}:** {f'{float(v):.2f}' if v is not None else '--'}")
    dim_rows = ["", "| Dimension | Score | Reasoning |", "|---|---|---|"]
    for dim in SCORED_DIMENSIONS:
        v = opp.get(dim)
        if v is None:
            continue
        reason = (opp.get(f"{dim}_reason") or "").replace("|", "/")[:160]
        dim_rows.append(f"| {dim} | {v} | {reason} |")
    parts.append(_section("Scoring", layer_lines + (dim_rows if len(dim_rows) > 3 else [])))

    # --- Data-backed signals ---
    signal_lines = []
    for label, field in [
        ("News signals (30d)", "news_signal_count"),
        ("Pain signals found", "pain_signal_count"),
        ("LinkedIn job postings", "job_posting_count"),
        ("Competitor negative review rate", "competitor_negative_review_rate"),
        ("Pain validation score", "pain_validation_score"),
    ]:
        v = opp.get(field)
        if v is not None:
            signal_lines.append(f"- **{label}:** {v}")
    parts.append(_section("Data-Backed Signals", signal_lines))

    # --- Evidence ---
    evidence_lines = []
    if opp.get("evidence_summary"):
        evidence_lines += [opp["evidence_summary"], ""]
    if opp.get("exact_customer_phrases"):
        evidence_lines += ["**Customer phrases:**"] + _bullets(opp["exact_customer_phrases"], 5) + [""]
    if opp.get("workarounds_found"):
        evidence_lines += ["**Current workarounds:**"] + _bullets(opp["workarounds_found"], 5) + [""]
    sources = (opp.get("pain_evidence_sources") or []) + (opp.get("source_links") or [])
    if sources:
        evidence_lines += ["**Sources:**"] + _bullets(sources, 8)
    parts.append(_section("Evidence", evidence_lines))

    # --- Market ---
    market_lines = []
    tam_disp = opp.get("tam_display") or _fmt_money(opp.get("tam") or opp.get("tam_usd_estimate"))
    if tam_disp and tam_disp != "--":
        sam = _fmt_money(opp.get("sam") or opp.get("sam_usd"))
        som = _fmt_money(opp.get("som") or opp.get("som_usd"))
        market_lines.append(
            f"- **TAM:** {tam_disp} | **SAM:** {sam} | **SOM:** {som} "
            f"(method: {opp.get('tam_method', '--')}, confidence: {opp.get('tam_confidence', '--')})"
        )
    if opp.get("tam_formula"):
        market_lines.append(f"- **TAM formula:** {opp['tam_formula']}")
    if opp.get("monetization_model"):
        market_lines.append(f"- **Monetization:** {opp['monetization_model']}")
    if opp.get("pricing_benchmark"):
        market_lines.append(f"- **Pricing benchmark:** {opp['pricing_benchmark']}")
    if opp.get("direct_competitors"):
        market_lines.append(f"- **Direct competitors:** {', '.join(opp['direct_competitors'][:6])}")
    if opp.get("benchmark_archetype"):
        market_lines.append(f"- **Benchmark archetype:** {opp['benchmark_archetype']}")
    pricing_data = opp.get("competitor_pricing_data") or []
    if pricing_data:
        market_lines.append("- **Competitor pricing (scraped):**")
        for p in pricing_data[:4]:
            market_lines.append(
                f"  - {p.get('url', '?')}: ${p.get('price_usd', '?')} "
                f"({p.get('pricing_model', '?')})"
            )
    parts.append(_section("Market", market_lines))

    # --- Distribution ---
    dist_lines = []
    if opp.get("top_distribution_channels"):
        dist_lines.append(f"- **Channels:** {', '.join(opp['top_distribution_channels'][:4])}")
    if opp.get("estimated_cac_logic"):
        dist_lines.append(f"- **CAC logic:** {opp['estimated_cac_logic']}")
    if opp.get("first_10_customer_path"):
        dist_lines.append(f"- **First 10 customers:** {opp['first_10_customer_path']}")
    if opp.get("trust_mechanism_latam"):
        dist_lines.append(f"- **Trust mechanism:** {opp['trust_mechanism_latam']}")
    if opp.get("distribution_validated") is not None:
        dist_lines.append(f"- **Validated:** {opp['distribution_validated']}")
    parts.append(_section("Distribution", dist_lines))

    # --- Revenue path ---
    rev_lines = []
    for label, field in [
        ("First revenue", "path_to_first_revenue"),
        ("Path to $1M ARR", "path_to_1m_arr"),
        ("Path to $10M ARR", "path_to_10m_arr"),
    ]:
        if opp.get(field):
            rev_lines.append(f"- **{label}:** {opp[field]}")
    parts.append(_section("Revenue Path", rev_lines))

    # --- Risks ---
    risk_lines = []
    kp = opp.get("kill_criteria_passed")
    if kp is not None:
        risk_lines.append(f"- **Kill gate:** {kp}/7 criteria passed")
    risk_lines += _bullets(opp.get("risks"), 6)
    risk_lines += [f"- (kill reason) {r}" for r in (opp.get("kill_reasons") or [])[:3]]
    if opp.get("assumptions"):
        risk_lines += ["", "**Assumptions:**"] + _bullets(opp["assumptions"], 5)
    parts.append(_section("Risks & Assumptions", risk_lines))

    # --- Attached reports ---
    if attached.get("validation"):
        parts.append("\n---\n\n# Attached: Validation Package\n\n" + attached["validation"])
    if attached.get("deep_dive"):
        parts.append("\n---\n\n# Attached: Deep Dive\n\n" + attached["deep_dive"])

    return "\n".join(p for p in parts if p)


def write_report_bundle(opp_id: str, out_dir: Optional[str] = None) -> dict:
    """Write exports/<opp_id>/report.md. Returns {path, attached} or {error}."""
    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        return {"error": f"Opportunity '{opp_id}' not found."}

    attached = find_attached_reports(opp_id)
    content = build_opportunity_report_md(opp, attached)

    target = Path(out_dir) if out_dir else Path(get_project_root()) / "exports" / str(opp_id)[:60]
    target.mkdir(parents=True, exist_ok=True)
    path = target / "report.md"
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)

    attached_names = [k for k, v in attached.items() if v]
    return {"path": str(path), "attached": attached_names}
