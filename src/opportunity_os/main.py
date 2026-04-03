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

    if not all_opps:
        click.echo(" No opportunities yet. Run 'opp-os daily' to start.")



@cli.command()
def audit():
    """Show pipeline failure audit -- failure rates by step and error type."""
    from opportunity_os.pipeline_monitor import audit_report
    click.echo(audit_report())


if __name__ == "__main__":
    cli()
