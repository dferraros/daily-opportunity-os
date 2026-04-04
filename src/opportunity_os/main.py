"""
main.py -- CLI entry point for daily-opportunity-os.

Commands:
  opp-os daily       Run full daily pipeline
  opp-os weekly      Run weekly review
  opp-os deep-dive   Run deep dive on specific opportunity
  opp-os search      Search opportunities by keyword
  opp-os stats       Show machine metrics summary
"""

import sys
import os

import click


@click.group()
def cli():
    """Daily Opportunity OS -- scout, score, rank business opportunities."""
    pass


@cli.command()
@click.option("--date", default=None, help="Date to run (YYYY-MM-DD). Default: today.")
@click.option("--geo", default="global", help="Geography filter. Default: global.")
@click.option("--dry-run", is_flag=True, help="Run without writing to disk.")
def daily(date, geo, dry_run):
    """Run full daily scout + score + report pipeline."""
    from opportunity_os.pipelines.daily_run import run_daily

    summary = run_daily(date=date, geo=geo, dry_run=dry_run)
    if dry_run:
        click.echo("\n[dry-run] No files written.")
    click.echo(
        f"\nDone: {summary['scored']} scored, {summary['killed']} killed, "
        f"{len(summary['reports_written'])} reports."
    )


@cli.command()
@click.option("--dry-run", is_flag=True)
def weekly(dry_run):
    """Run weekly review -- 4 mandatory outputs."""
    from opportunity_os.pipelines.weekly_run import run_weekly

    result = run_weekly(dry_run=dry_run)
    click.echo(
        f"Weekly review complete: {result['promote_count']} to promote, "
        f"{result['kill_count']} to kill."
    )


@cli.command("deep-dive")
@click.argument("opp_id")
@click.option("--dry-run", is_flag=True)
def deep_dive(opp_id, dry_run):
    """Run full deep dive on a specific opportunity ID."""
    from opportunity_os.pipelines.deep_dive import run_deep_dive

    result = run_deep_dive(opp_id=opp_id, dry_run=dry_run)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        sys.exit(1)
    click.echo(f"Deep dive complete: {result.get('path', 'unknown path')}")


@cli.command()
@click.argument("opp_id")
@click.option("--dry-run", is_flag=True, help="Preview output without writing files")
def validate(opp_id, dry_run):
    """Run full 8-section validation package on a specific opportunity ID."""
    from opportunity_os.pipelines.validation_run import run_validation_pipeline

    result = run_validation_pipeline(opp_id=opp_id, dry_run=dry_run)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        sys.exit(1)
    click.echo(f"Validation complete: {result['opp_name']}")
    click.echo(f"  Report: {result['path']}")
    click.echo(f"  Notion sync: {result['notion_sync_path']}")


@cli.command()
@click.argument("opp_id")
def research(opp_id):
    """Run combined pain + distribution research on a specific opportunity ID."""
    from opportunity_os.storage import get_opportunity_by_id, update_opportunity
    from opportunity_os.research_executor import run_research_executor

    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        click.echo(f"Error: Opportunity '{opp_id}' not found.", err=True)
        sys.exit(1)

    # Force re-run by clearing the research timestamp
    opp.pop("research_executed_at", None)
    click.echo(f"Running research for: {opp.get('name', opp_id)[:60]}")
    enriched = run_research_executor(opp)
    # Extract only the research fields to update (don't overwrite id/name/etc.)
    research_fields = {
        k: v for k, v in enriched.items()
        if k in (
            "pain_validation_score", "exact_customer_phrases", "pain_evidence_sources",
            "workarounds_found", "distribution_validated", "top_distribution_channels",
            "estimated_cac_logic", "first_10_customer_path", "trust_mechanism_latam",
            "research_executed_at",
        )
    }
    update_opportunity(opp_id, research_fields)
    click.echo(f"  Pain score: {enriched.get('pain_validation_score', '—')}")
    click.echo(f"  Distribution validated: {enriched.get('distribution_validated', '—')}")
    click.echo(f"  First 10 path: {str(enriched.get('first_10_customer_path', '—'))[:80]}")
    click.echo("Research complete.")


@cli.command()
@click.argument("query")
@click.option("--min-score", default=0.0, help="Minimum score filter.")
@click.option("--geo", default=None, help="Filter by geography.")
def search(query, min_score, geo):
    """Search opportunities by keyword."""
    from opportunity_os.storage import read_all_opportunities

    all_opps = read_all_opportunities()
    query_lower = query.lower()
    results = [
        o
        for o in all_opps
        if (
            query_lower in (o.get("name") or "").lower()
            or query_lower in (o.get("problem_statement") or "").lower()
            or query_lower in (o.get("vertical") or "").lower()
        )
        and o.get("final_score", 0) >= min_score
        and (geo is None or o.get("geography") == geo)
    ]
    results = sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
    if not results:
        click.echo(f"No results for '{query}'")
        return
    click.echo(f"\nFound {len(results)} opportunities matching '{query}':\n")
    for i, r in enumerate(results[:20], 1):
        score = r.get("final_score", 0)
        score_str = f"{score:.1f}" if score else "unscored"
        click.echo(
            f"{i:2}. [{score_str}] {r.get('name', 'Unknown')} "
            f"({r.get('geography', '?')}) -- {r.get('bucket', '')}"
        )


@cli.command()
def stats():
    """Show machine metrics and system summary."""
    from opportunity_os.storage import read_all_opportunities
    from datetime import datetime

    all_opps = read_all_opportunities()
    today = datetime.now().strftime("%Y-%m-%d")

    today_opps = [o for o in all_opps if o.get("first_seen", "").startswith(today)]
    scored = [o for o in all_opps if o.get("final_score") is not None]
    killed = [o for o in all_opps if o.get("kill_decision")]

    top = (
        max(scored, key=lambda x: x.get("final_score", 0), default=None)
        if scored
        else None
    )

    ve_count = len([o for o in all_opps if o.get("geography") == "venezuela"])
    latam_count = len(
        [
            o
            for o in all_opps
            if o.get("geography")
            in ["colombia", "mexico", "argentina", "brazil", "chile", "peru", "latam"]
        ]
    )

    lanes: dict = {}
    for o in all_opps:
        lane = o.get("portfolio_lane", "unassigned")
        lanes[lane] = lanes.get(lane, 0) + 1

    click.echo(f"\n{'='*50}")
    click.echo(" OPPORTUNITY OS -- STATS")
    click.echo(f"{'='*50}")
    click.echo(f" Total opportunities: {len(all_opps)}")
    click.echo(f" Scored:             {len(scored)}")
    click.echo(f" Killed:             {len(killed)}")
    click.echo(f" Today:              {len(today_opps)}")
    click.echo(f" Venezuela:          {ve_count}")
    click.echo(f" LATAM:              {latam_count}")
    if top:
        click.echo(
            f"\n Top opportunity:    {top.get('name')} ({top.get('final_score', 0):.1f}/10)"
        )
    click.echo("\n Portfolio lanes:")
    for lane, count in sorted(lanes.items()):
        click.echo(f"   {lane:12} {count}")
    click.echo(f"{'='*50}\n")

    # Weekly quota progress
    try:
        import yaml
        import json
        from pathlib import Path
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / "config" / "weekly_quotas.yaml"
        metrics_path = project_root / "data" / "machine_metrics.jsonl"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                quotas = yaml.safe_load(f).get("weekly_quotas", {})

            from datetime import timedelta
            week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
            week_signals = 0
            week_opps = 0
            week_deep_dives = 0
            week_validations = 0

            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            m = json.loads(line)
                            if m.get("date", "") >= week_start:
                                week_signals += m.get("signals_ingested", 0)
                                week_opps += m.get("opportunities_scored", 0)
                                week_deep_dives += m.get("deep_dives_produced", 0)
                                week_validations += m.get("validations_run", 0)
                        except json.JSONDecodeError:
                            continue

            sig_target = quotas.get("signals_ingested", {}).get("target", 40)
            opp_target = quotas.get("structured_opportunities", {}).get("target", 10)
            dd_target = quotas.get("deep_dives_produced", {}).get("target", 3)
            val_target = quotas.get("validations_run", {}).get("target", 2)

            click.echo(f" Weekly quotas (since {week_start}):")
            click.echo(f"   Signals:     {week_signals}/{sig_target}")
            click.echo(f"   Opps scored: {week_opps}/{opp_target}")
            click.echo(f"   Deep dives:  {week_deep_dives}/{dd_target}")
            click.echo(f"   Validations: {week_validations}/{val_target}")
            click.echo("")
    except Exception:
        pass  # quota display is non-critical

    if not all_opps:
        click.echo(" No opportunities yet. Run 'opp-os daily' to start.")



@cli.command()
def audit():
    """Show pipeline failure audit -- failure rates by step and error type."""
    from opportunity_os.pipeline_monitor import audit_report
    click.echo(audit_report())


if __name__ == "__main__":
    cli()
