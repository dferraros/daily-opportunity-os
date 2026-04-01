"""Deep dive pipeline -- full analysis for a single shortlisted opportunity."""

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

    # Build deep dive content
    date = datetime.now().strftime("%Y-%m-%d")
    tam_val = opp.get("tam_usd_estimate") or 0
    try:
        tam_formatted = f"${float(tam_val):,.0f}"
    except (TypeError, ValueError):
        tam_formatted = str(tam_val)

    lines = [
        f"# Deep Dive: {opp.get('name', 'Unknown')}",
        f"**Date:** {date} | **ID:** {opp_id}",
        "",
        "## Opportunity Summary",
        opp.get("problem_statement", "No problem statement."),
        "",
        f"**Geography:** {opp.get('geography')} | **Vertical:** {opp.get('vertical')} | **Bucket:** {opp.get('bucket')}",
        f"**Score:** {opp.get('final_score', 'N/A')} | **Lane:** {opp.get('portfolio_lane', 'N/A')}",
        "",
        "## Market Size",
        f"TAM: {tam_formatted} | Method: bottom_up",
        "",
        "## Archetype",
        f"**{archetype}** -- {opp.get('benchmark_archetype', 'unclassified')}",
        "",
        "## Analog Benchmarks",
    ]
    for analog in analogs[:3]:
        lines.append(
            f"- **{analog['name']}** ({analog['model']}): {analog.get('lesson', '')}"
        )

    lines += ["", "## Competitive Whitespace"]
    for signal in whitespace.get("weak_competitor_signals", []):
        lines.append(f"- {signal}")

    content = "\n".join(lines) + "\n"

    # Write report
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


def _get_project_root() -> str:
    from pathlib import Path

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])
