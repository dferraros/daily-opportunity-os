"""
main.py -- CLI entry point for daily-opportunity-os.

Commands:
  opp-os daily       Run full daily pipeline
  opp-os weekly      Run weekly review
  opp-os deep-dive   Run deep dive on specific opportunity
  opp-os search      Search opportunities by keyword
  opp-os stats       Show machine metrics summary
"""

import logging
import sys
import os
from datetime import timedelta

logger = logging.getLogger(__name__)

import click


@click.group()
def cli():
    """Daily Opportunity OS -- scout, score, rank business opportunities."""
    from opportunity_os.env import load_env_file
    load_env_file()


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

    # Force re-run: create a clean copy without the research timestamp
    # Never mutate the dict returned from storage
    opp = {k: v for k, v in opp.items() if k != "research_executed_at"}
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


@cli.command("apify-research")
@click.option("--top-n", default=10, show_default=True, type=int,
              help="Enrich the top N standing opportunities (max 10 per pass).")
@click.option("--force", is_flag=True, help="Ignore the 14-day apify_researched_at skip guard.")
@click.option("--dry-run", is_flag=True, help="Show candidates without calling Apify.")
def apify_research(top_n, force, dry_run):
    """Run Apify enrichment (LinkedIn jobs + G2 reviews) on standing opportunities.

    The daily pipeline only enriches each day's NEW batch -- this command applies
    step 11.7 to the existing portfolio. Populates job_posting_count (market
    momentum) and competitor data, then rescores and renormalizes.
    Cost: ~\\$0.02-0.10 per opp, hard-capped at \\$0.25/actor-run.
    """
    from opportunity_os import apify_client
    from opportunity_os.backup import create_backup
    from opportunity_os.engines.scoring_engine import normalize_portfolio_scores
    from opportunity_os.pipelines.enrichment import _enrich_apify
    from opportunity_os.storage import read_all_opportunities, replace_all_opportunities

    if not apify_client.is_available():
        click.echo("APIFY_API_TOKEN not set -- nothing to do.", err=True)
        return

    all_opps = read_all_opportunities()
    if not all_opps:
        click.echo("No opportunities found.", err=True)
        return

    alive = [o for o in all_opps if not o.get("kill_decision")]
    from opportunity_os.free_research import sort_research_candidates
    candidates = sort_research_candidates(alive)[: min(top_n, 10)]

    if force:
        # Strip the skip-guard timestamp on copies -- never mutate storage dicts
        candidates = [
            {k: v for k, v in o.items() if k != "apify_researched_at"} for o in candidates
        ]

    if dry_run:
        click.echo(f"Would run Apify enrichment on {len(candidates)} opportunities:")
        for i, o in enumerate(candidates, 1):
            guard = " (skip guard active)" if o.get("apify_researched_at") else ""
            click.echo(f"  {i:2}. {(o.get('name') or '?')[:60]}{guard}")
        click.echo("[dry-run] No API calls made.")
        return

    bak = create_backup("pre-apify-research")
    if bak:
        click.echo(f"Backup: {bak['filename']}")

    click.echo(f"Running Apify enrichment on top {len(candidates)} opportunities...")
    enriched = _enrich_apify(candidates, dry_run=False)

    # Merge back, renormalize the whole portfolio, persist
    enriched_map = {o.get("id"): o for o in enriched if o.get("id")}
    merged = [enriched_map.get(o.get("id"), o) for o in all_opps]
    final = normalize_portfolio_scores(merged)

    jobs_populated = sum(1 for o in enriched if o.get("job_posting_count") is not None)
    g2_populated = sum(1 for o in enriched if o.get("competitor_negative_review_rate") is not None)
    n = replace_all_opportunities(final)
    click.echo(
        f"\nDone: job_posting_count on {jobs_populated}, competitor data on {g2_populated} "
        f"of {len(candidates)} candidates. Wrote {n} records."
    )
    for o in enriched:
        if o.get("job_posting_count") is not None:
            click.echo(f"  {(o.get('name') or '?')[:55]:<55} jobs={o['job_posting_count']}")


@cli.command("like")
@click.argument("opp_id")
@click.option("--undo", is_flag=True, help="Remove the liked mark.")
def like(opp_id, undo):
    """Mark an opportunity as liked -- the conviction flag.

    Sets liked_at + recommendation=build. Follow with 'opp-os export' for the
    full report bundle and 'opp-os kickoff' for a Claude Code starter pack.
    """
    from datetime import datetime
    from opportunity_os.storage import get_opportunity_by_id, update_opportunity

    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        click.echo(f"Error: Opportunity '{opp_id}' not found.", err=True)
        sys.exit(1)

    name = (opp.get("name") or opp_id)[:60]
    if undo:
        update_opportunity(opp_id, {"liked_at": None})
        click.echo(f"Unliked: {name}")
        return

    update_opportunity(
        opp_id,
        {"liked_at": datetime.now().isoformat(), "recommendation": "build"},
    )
    click.echo(f"Liked: {name}")
    click.echo(f"Next steps:  opp-os export {opp_id}   |   opp-os kickoff {opp_id}")


@cli.command("liked")
def liked_list():
    """List liked opportunities, newest first."""
    from opportunity_os.storage import read_all_opportunities

    opps = [o for o in read_all_opportunities() if o.get("liked_at")]
    if not opps:
        click.echo("No liked opportunities yet. Use 'opp-os like <opp_id>'.")
        return
    opps.sort(key=lambda o: str(o.get("liked_at")), reverse=True)
    click.echo(f"\n{len(opps)} liked opportunit{'y' if len(opps) == 1 else 'ies'}:\n")
    for i, o in enumerate(opps, 1):
        score = o.get("final_score")
        score_str = f"{float(score):.1f}" if score is not None else "--"
        click.echo(
            f"{i:2}. [{score_str}] {(o.get('name') or '?')[:55]:<55} "
            f"liked {str(o.get('liked_at'))[:10]}  {o.get('id')}"
        )


@cli.command("export")
@click.argument("opp_id")
@click.option("--to", "out_dir", default=None, help="Output directory. Default: exports/<opp_id>/")
def export(opp_id, out_dir):
    """Write a self-contained report bundle for one opportunity.

    Produces exports/<opp_id>/report.md with scoring breakdown, evidence,
    market data, risks, and any existing validation/deep-dive reports attached.
    """
    from opportunity_os.export_report import write_report_bundle

    result = write_report_bundle(opp_id, out_dir=out_dir)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        sys.exit(1)
    click.echo(f"Report written: {result['path']}")
    for attached in result.get("attached", []):
        click.echo(f"  attached: {attached}")


@cli.command("kickoff")
@click.argument("opp_id")
@click.option("--to", "out_dir", default=None, help="Output directory. Default: exports/<opp_id>/")
def kickoff(opp_id, out_dir):
    """Generate a Claude Code starter pack for a liked opportunity.

    Writes PROJECT.md (seed brief from everything the pipeline learned) and
    kickoff-prompt.md (paste into a fresh Claude Code session: /spec -> /plan).
    """
    from opportunity_os.kickoff import write_kickoff_pack

    result = write_kickoff_pack(opp_id, out_dir=out_dir)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        sys.exit(1)
    click.echo("Kickoff pack written:")
    for f in result["files"]:
        click.echo(f"  {f}")
    click.echo("\nStart building: open a new Claude Code session in your project folder")
    click.echo(f"and paste the contents of {result['files'][-1]}.")


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

    today_opps = [o for o in all_opps if str(o.get("first_seen") or "").startswith(today)]
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
    except Exception as exc:
        logger.warning("quota display failed: %s", exc)

    if not all_opps:
        click.echo(" No opportunities yet. Run 'opp-os daily' to start.")



@cli.command()
@click.option("--date", default=None, help="Date string YYYY-MM-DD. Default: today.")
@click.option("--dry-run", is_flag=True, help="Print signals without writing to disk.")
@click.option("--min-quality", default=0.30, type=float, help="Heuristic quality threshold 0-1.")
@click.option("--max-signals", default=25, type=int, help="Cap on signals returned.")
def harvest(date, dry_run, min_quality, max_signals):
    """Auto-harvest opportunity signals from HN, Reddit, and Serper (free sources)."""
    from datetime import date as date_cls
    from pathlib import Path
    import json as _json

    from opportunity_os.pipelines.signal_harvester import harvest_signals
    from opportunity_os.storage import read_all_opportunities

    if date is None:
        date = date_cls.today().isoformat()

    existing_names = [o.get("name", "") for o in read_all_opportunities()]
    click.echo(f"Harvesting signals for {date} (existing={len(existing_names)} opps)...")

    signals = harvest_signals(
        today=date,
        existing_names=existing_names,
        min_quality=min_quality,
        max_signals=max_signals,
    )

    if not signals:
        click.echo("No new signals found.")
        return

    click.echo(f"Found {len(signals)} signals:")
    for i, s in enumerate(signals, 1):
        geo = s.get("geography", "?")
        vertical = s.get("vertical", "?")
        name = s.get("name", "")[:80].encode("ascii", errors="replace").decode("ascii")
        click.echo(f"  {i:2}. [{geo}/{vertical}] {name}")

    if dry_run:
        click.echo("\n[dry-run] No files written.")
        return

    root = Path(__file__).resolve().parent.parent.parent
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_file = raw_dir / f"{date}-signals.jsonl"

    if out_file.exists():
        click.echo(f"\nFile already exists: {out_file.name} -- appending.")
        mode = "a"
    else:
        mode = "w"

    with open(out_file, mode, encoding="utf-8") as f:
        for s in signals:
            f.write(_json.dumps(s, ensure_ascii=False) + "\n")

    click.echo(f"\nWrote {len(signals)} signals to {out_file.name}")
    click.echo("Run 'opp-os daily' to score them.")


@cli.command()
def audit():
    """Show pipeline failure audit -- failure rates by step and error type."""
    from opportunity_os.pipeline_monitor import audit_report
    click.echo(audit_report())


@cli.command("backup")
@click.option("--label", default="manual", help="Short tag for the backup filename.")
def backup(label):
    """Snapshot opportunities.jsonl to data/opportunities/backups/."""
    from opportunity_os.backup import create_backup

    result = create_backup(label)
    if result is None:
        click.echo("Snapshot skipped: opportunities store is empty or missing.", err=True)
        return
    click.echo(
        f"Snapshot created: {result['filename']} "
        f"({result['record_count']} records, {result['size_bytes'] // 1024} KB)"
    )


@cli.command("backups")
def list_backups():
    """List all available opportunity snapshots."""
    from opportunity_os.backup import list_backups as _list

    items = _list()
    if not items:
        click.echo("No backups found. Run 'opp-os backup' to create one.")
        return
    click.echo(f"\n{'='*60}")
    click.echo(f" {'#':>3}  {'Timestamp':<20}  {'Label':<18}  {'Records':>7}  {'Size':>6}")
    click.echo(f"{'='*60}")
    for i, b in enumerate(items, 1):
        size_kb = b["size_bytes"] // 1024
        click.echo(
            f" {i:>3}  {b['timestamp']:<20}  {b['label']:<18}  {b['record_count']:>7}  {size_kb:>5}K"
        )
    click.echo(f"{'='*60}")
    click.echo(f" {len(items)} backup(s). Use 'opp-os restore <filename>' to recover.\n")


@cli.command("restore")
@click.argument("filename")
@click.option("--dry-run", is_flag=True, help="Validate without writing.")
def restore(filename, dry_run):
    """Restore opportunities.jsonl from a backup snapshot.

    FILENAME is the backup basename, e.g. 2026-05-20-143000-pre-daily.jsonl.
    Run 'opp-os backups' to list available snapshots.
    """
    from opportunity_os.backup import restore_backup

    if not dry_run:
        click.echo(f"WARNING: This will overwrite opportunities.jsonl with {filename}.")
        click.confirm("Continue?", abort=True)

    result = restore_backup(filename, dry_run=dry_run)
    if result["success"]:
        click.echo(result["message"])
    else:
        click.echo(f"Restore failed: {result['message']}", err=True)
        raise SystemExit(1)


@cli.command("rescore-all")
@click.option("--dry-run", is_flag=True, help="Show score deltas without writing.")
@click.option(
    "--top-n",
    default=None,
    type=int,
    help="Only rescore the top N opportunities by current score.",
)
def rescore_all(dry_run, top_n):
    """Rescore all opportunities with the current scoring formula.

    Applies data-backed sub-scores (market_momentum, competitor_weakness),
    pain signal fallback, and portfolio normalisation in a single batch pass.
    Creates a backup before writing unless --dry-run.
    """
    from opportunity_os.storage import read_all_opportunities, replace_all_opportunities
    from opportunity_os.engines.scoring_engine import score_opportunity, normalize_portfolio_scores
    from opportunity_os.geo_lens import apply_geo_adjustments
    from opportunity_os.filters import PortfolioLaneAssigner
    from opportunity_os.backup import create_backup

    all_opps = read_all_opportunities()
    if not all_opps:
        click.echo("No opportunities found.")
        return

    if not dry_run:
        bak = create_backup("pre-rescore")
        if bak:
            click.echo(f"Backup created: {bak['filename']}")

    # Determine which opps to rescore
    if top_n is not None:
        sorted_opps = sorted(
            all_opps,
            key=lambda o: float(o.get("final_score") or 0),
            reverse=True,
        )
        target_ids = {o.get("id") for o in sorted_opps[:top_n]}
    else:
        target_ids = {o.get("id") for o in all_opps}

    # Pass 1: score each opp independently
    rescored = []
    for opp in all_opps:
        if opp.get("id") in target_ids and not opp.get("kill_decision"):
            rescored.append(score_opportunity(opp))
        else:
            rescored.append(opp)

    # Pass 2: portfolio normalisation (requires all opps together)
    rescored = normalize_portfolio_scores(rescored)

    # Pass 3: geo adjustments + lane reassignment
    lane_assigner = PortfolioLaneAssigner()
    final = []
    for opp in rescored:
        if opp.get("id") in target_ids and not opp.get("kill_decision"):
            opp = apply_geo_adjustments(opp)
            new_lane = lane_assigner.assign_from_dict(opp)
            opp = {**opp, "portfolio_lane": new_lane}
        elif opp.get("kill_decision") and opp.get("portfolio_lane") != "no":
            opp = {**opp, "portfolio_lane": "no"}
        final.append(opp)

    # Report deltas (scores + lane changes)
    changed = 0
    lane_changed = 0
    id_to_old = {o.get("id"): o for o in all_opps}
    for new_opp in final:
        old_opp = id_to_old.get(new_opp.get("id"), {})
        old_s = old_opp.get("final_score")
        new_s = new_opp.get("final_score")
        old_lane = old_opp.get("portfolio_lane", "?")
        new_lane = new_opp.get("portfolio_lane", "?")
        name = (new_opp.get("name") or "?")[:45]
        if old_s != new_s:
            delta = (
                f"{float(new_s) - float(old_s):+.2f}"
                if old_s is not None and new_s is not None else "new"
            )
            old_str = f"{float(old_s):.2f}" if old_s is not None else "—"
            new_str = f"{float(new_s):.2f}" if new_s is not None else "—"
            click.echo(f"  {name:<45}  score {old_str} -> {new_str} ({delta})")
            changed += 1
        if old_lane != new_lane:
            click.echo(f"  {name:<45}  lane  {old_lane} -> {new_lane}")
            lane_changed += 1

    click.echo(f"\n{changed}/{len(all_opps)} scores changed, {lane_changed} lanes reassigned.")

    if dry_run:
        click.echo("[dry-run] No files written.")
        return

    n = replace_all_opportunities(final)
    click.echo(f"Wrote {n} records.")


@cli.command("free-research")
@click.option(
    "--top-n",
    default=20,
    type=int,
    show_default=True,
    help="Run on the top N opportunities by current score.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Re-run even if free_research_at is already set.",
)
@click.option("--dry-run", is_flag=True, help="Show what would run without writing.")
def free_research(top_n, force, dry_run):
    """Run Tavily + free-source research on unresearched top opportunities.

    Populates news_signal_count, pain_signal_count, and pain_evidence_sources
    using Tavily news search, HN, Reddit, Serper, and Exa — then rescores
    the portfolio so the new signals feed into final_score immediately.

    Skip guard: opps that already have free_research_at set are skipped unless
    --force is passed (prevents re-running the full stack every daily cycle).
    """
    from opportunity_os.storage import read_all_opportunities, replace_all_opportunities
    from opportunity_os.free_research import research_opportunity_free, get_unavailable_sources
    from opportunity_os.engines.scoring_engine import score_opportunity, normalize_portfolio_scores
    from opportunity_os.geo_lens import apply_geo_adjustments
    from opportunity_os.backup import create_backup

    all_opps = read_all_opportunities()
    if not all_opps:
        click.echo("No opportunities found.", err=True)
        return

    # Surface missing keys upfront: "news=0 pain=0" must read as "source not
    # configured", never be mistaken for "no demand signal".
    missing_sources = get_unavailable_sources()
    if missing_sources:
        click.echo(
            f"WARNING: {len(missing_sources)} research source(s) not configured: "
            f"{', '.join(missing_sources)}",
            err=True,
        )
        click.echo("  Zero news/pain counts may reflect missing keys, not absent demand.", err=True)

    # Take top-N alive opps; low-evidence high scorers jump the queue
    alive = [o for o in all_opps if not o.get("kill_decision")]
    from opportunity_os.free_research import sort_research_candidates
    candidates = sort_research_candidates(alive)[:top_n]

    # Apply skip guard unless --force
    if not force:
        candidates = [o for o in candidates if not o.get("free_research_at")]

    if not candidates:
        verb = "re-researched" if force else "researched"
        click.echo(
            f"All top-{top_n} opportunities already {verb}. "
            "Pass --force to re-run, or --top-n N to expand the window."
        )
        return

    click.echo(f"Running free research on {len(candidates)} opportunities...")
    if dry_run:
        for i, opp in enumerate(candidates, 1):
            score_str = f"{float(opp.get('final_score') or 0):.2f}"
            click.echo(f"  {i:2}. [{score_str}] {(opp.get('name') or '')[:60]}")
        click.echo(f"\n[dry-run] Would research {len(candidates)} opps. No files written.")
        return

    # Backup before any writes
    bak = create_backup("pre-free-research")
    if bak:
        click.echo(f"Backup: {bak['filename']}")

    # Build a lookup: id -> enriched opp (start with all opps unchanged)
    opp_by_id: dict = {o.get("id"): o for o in all_opps}

    research_count = 0
    for i, opp in enumerate(candidates, 1):
        name = (opp.get("name") or "?")[:55]
        click.echo(f"  [{i}/{len(candidates)}] {name}...", nl=False)
        try:
            delta = research_opportunity_free(opp)
            enriched = {**opp, **delta}
            # Rescore immediately so news_signal_count feeds into the score
            rescored = score_opportunity(enriched)
            opp_by_id[opp.get("id")] = rescored
            news_n = delta.get("news_signal_count")
            pain_n = delta.get("pain_signal_count", 0)
            click.echo(f" news={news_n} pain={pain_n}")
            research_count += 1
        except Exception as exc:
            click.echo(f" ERROR: {exc}", err=True)

    # Rebuild full list preserving order of original file
    rescored_all = [opp_by_id.get(o.get("id"), o) for o in all_opps]

    # Portfolio normalisation (needs all opps together)
    normalised = normalize_portfolio_scores(rescored_all)

    # Apply geo adjustments only to opps we just touched
    researched_ids = {o.get("id") for o in candidates}
    final = []
    for opp in normalised:
        if opp.get("id") in researched_ids and not opp.get("kill_decision"):
            final.append(apply_geo_adjustments(opp))
        else:
            final.append(opp)

    # Report score deltas
    changed = 0
    id_to_old = {o.get("id"): o for o in all_opps}
    for new_opp in final:
        if new_opp.get("id") not in researched_ids:
            continue
        old_opp = id_to_old.get(new_opp.get("id"), {})
        old_s = old_opp.get("final_score")
        new_s = new_opp.get("final_score")
        if old_s != new_s:
            delta_str = (
                f"{float(new_s) - float(old_s):+.2f}"
                if old_s is not None and new_s is not None
                else "new"
            )
            name = (new_opp.get("name") or "?")[:50]
            old_str = f"{float(old_s):.2f}" if old_s is not None else "—"
            new_str = f"{float(new_s):.2f}" if new_s is not None else "—"
            click.echo(f"  {name:<50}  {old_str:>5} -> {new_str:>5}  ({delta_str})")
            changed += 1

    n = replace_all_opportunities(final)
    click.echo(
        f"\nResearched {research_count}/{len(candidates)} opps. "
        f"{changed} scores changed. Wrote {n} records."
    )


@cli.command()
@click.argument("opp_id")
@click.option("--dir", "out_dir", default=None, help="Output directory. Default: Projects/<slug>/")
@click.option(
    "--mode",
    type=click.Choice(["validate", "build", "auto"]),
    default="auto",
    help="Mode: validate (2-week kit only) or build (full pack). Default: auto (detect via pain_validated_date).",
)
@click.option("--launch/--no-launch", default=False, help="Launch claude in target dir (requires --mode build).")
@click.option("--force", is_flag=True, help="Skip conviction gate (like required); overwrite non-empty dir.")
@click.option("--dry-run", is_flag=True, help="Show what would be created without writing.")
def build(opp_id, out_dir, mode, launch, force, dry_run):
    """Build a conviction bridge: validation kit or full business plan + MVP spec.

    Writes PROJECT.md, kickoff-prompt.md, report.md, validation-kit.md, REQUIREMENTS.md,
    and optionally business-plan.md. Stamps the opportunity record with build metadata.

    Flow: like -> build validate -> outcome validated -> build build -> outcome shipped.
    """
    from datetime import datetime
    from pathlib import Path
    import subprocess
    import re

    from opportunity_os.kickoff import build_project_md, build_kickoff_prompt, _slugify
    from opportunity_os.export_report import build_opportunity_report_md
    from opportunity_os.storage import get_opportunity_by_id, update_opportunity, get_project_root
    from opportunity_os.venture_pack import write_venture_pack

    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        click.echo(f"Error: Opportunity '{opp_id}' not found.", err=True)
        sys.exit(1)

    name = (opp.get("name") or opp_id)[:60]

    # CONVICTION GATE
    if not opp.get("liked_at") and not force:
        click.echo(
            f"Not liked yet: {name}\n"
            f"  Run:  opp-os like {opp_id}\n"
            f"  Or:   opp-os build {opp_id} --force",
            err=True,
        )
        sys.exit(1)

    # MODE RESOLUTION
    if mode == "auto":
        if opp.get("pain_validated_date"):
            resolved_mode = "build"
        else:
            resolved_mode = "validate"
    else:
        resolved_mode = mode

    # TARGET DIR
    if out_dir:
        target = Path(out_dir)
    else:
        slug = _slugify(name)
        target = Path(get_project_root()) / "Projects" / slug

    # CHECK FOR EXISTING DIR
    if target.exists() and any(target.iterdir()):
        if not force:
            click.echo(
                f"Directory exists and is not empty: {target}\n"
                f"  Run with --force to proceed (will not delete, only add/overwrite our files)",
                err=True,
            )
            sys.exit(1)
        click.echo(f"[force] Will add/overwrite files in: {target}")
    else:
        target.mkdir(parents=True, exist_ok=True)

    # DRY-RUN PREVIEW
    if dry_run:
        click.echo(f"[dry-run] Would build in {resolved_mode} mode:")
        click.echo(f"  Directory: {target}")
        click.echo(f"  Files:")
        click.echo(f"    - PROJECT.md")
        click.echo(f"    - kickoff-prompt.md")
        click.echo(f"    - report.md")
        click.echo(f"    - validation-kit.md")
        click.echo(f"    - REQUIREMENTS.md")
        if resolved_mode == "build":
            click.echo(f"    - business-plan.md (if API available)")
        click.echo(f"  Record stamps:")
        click.echo(f"    - kickoff_at={datetime.now().isoformat()}")
        click.echo(f"    - build_mode={resolved_mode}")
        if resolved_mode == "validate" and not opp.get("validation_start_date"):
            click.echo(f"    - validation_start_date=today")
            click.echo(f"    - validation_deadline=today+14d")
        click.echo("[dry-run] No files written, no records stamped.")
        return

    # WRITE FILES
    target.mkdir(parents=True, exist_ok=True)

    files_written = []

    # PROJECT.md + kickoff-prompt.md
    for filename, content in [
        ("PROJECT.md", build_project_md(opp)),
        ("kickoff-prompt.md", build_kickoff_prompt(opp)),
        ("report.md", build_opportunity_report_md(opp)),
    ]:
        path = target / filename
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
        files_written.append(filename)

    # venture pack
    result = write_venture_pack(opp, target, include_business_plan=(resolved_mode == "build"))
    files_written.extend([Path(f).name for f in result["files"]])
    if result["skipped"]:
        click.echo(f"  Skipped: {', '.join(result['skipped'])}")

    # GIT INIT (non-fatal)
    try:
        git_dir = target / ".git"
        if not git_dir.exists():
            subprocess.run(
                ["git", "init"],
                cwd=str(target),
                capture_output=True,
                check=False,
                timeout=5,
            )
            # Create .gitignore if absent
            gitignore = target / ".gitignore"
            if not gitignore.exists():
                gitignore.write_text(".env\n", encoding="utf-8")
    except Exception as exc:
        logger.warning("build: git init failed: %s", exc)

    # STAMP OPPORTUNITY RECORD
    stamps = {
        "kickoff_at": datetime.now().isoformat(),
        "build_mode": resolved_mode,
    }

    if resolved_mode == "validate":
        if not opp.get("validation_start_date"):
            stamps["validation_start_date"] = datetime.now().strftime("%Y-%m-%d")
            stamps["validation_deadline"] = (
                datetime.now() + timedelta(days=14)
            ).strftime("%Y-%m-%d")

    update_opportunity(opp_id, stamps)

    # ECHO SUMMARY
    click.echo(f"\nBuild complete: {name}")
    click.echo(f"  Mode: {resolved_mode}")
    click.echo(f"  Directory: {target}")
    click.echo(f"  Files: {', '.join(files_written)}")

    if resolved_mode == "validate":
        click.echo(f"\nNext: Run the validation-kit.md interviews (deadline {stamps.get('validation_deadline', 'TBD')})")
        click.echo(f"  Then: opp-os outcome {opp_id} validated")
    else:
        click.echo(f"\nNext: Review PROJECT.md and kickoff-prompt.md, then:")
        if launch:
            click.echo(f"  Claude is launching in the directory...")
        else:
            click.echo(
                f"  Run: claude 'Read PROJECT.md and kickoff-prompt.md, then follow the kickoff instructions.'"
            )

    # LAUNCH (optional, Windows-safe)
    if launch:
        try:
            # Windows: start cmd in target dir with claude bootstrap prompt
            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    f"cd /d {target} && claude 'Read PROJECT.md and kickoff-prompt.md, then follow the kickoff instructions.'",
                ],
                shell=False,
            )
            click.echo(f"  Claude launching in: {target}")
        except OSError as exc:
            logger.warning("build: could not launch claude: %s", exc)
            click.echo(f"  Manual: cd {target} && claude ...", err=True)


@cli.command()
@click.argument("opp_id")
@click.argument("status", type=click.Choice(["validated", "killed", "shipped", "revenue"]))
@click.option("--note", default=None, help="Outcome note/reason (optional).")
def outcome(opp_id, status, note):
    """Record the outcome of a conviction bridge phase.

    Stamps opportunity with outcome metadata. Used to close validation window or
    record product outcomes (shipped, generating revenue).

    Statuses:
      validated  -- pain confirmed, ready for build mode
      killed     -- validation failed or founder decided to stop
      shipped    -- MVP launched, seeking first customers
      revenue    -- first paying customer live
    """
    from datetime import datetime

    from opportunity_os.storage import get_opportunity_by_id, update_opportunity

    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        click.echo(f"Error: Opportunity '{opp_id}' not found.", err=True)
        sys.exit(1)

    name = (opp.get("name") or opp_id)[:60]

    stamps = {
        "outcome": status,
        "outcome_note": note or f"outcome: {status}",
        "outcome_at": datetime.now().isoformat(),
    }

    # Snapshot into the calibration log BEFORE stamping: for 'killed' the kill
    # cap will zero final_score on the next rescore, destroying the record of
    # what the model predicted. This snapshot is what `opp-os calibrate` reads.
    from opportunity_os.engines.calibration_engine import BRIDGE_OUTCOME_MAP
    from opportunity_os.outcome_tracking import record_outcome

    try:
        record_outcome(opp_id, BRIDGE_OUTCOME_MAP[status], notes=note or f"bridge: {status}")
    except OSError as exc:
        logger.error("outcome: calibration snapshot failed for %s: %s", opp_id, exc)
        click.echo("  Warning: calibration snapshot failed (stamp still applied).", err=True)

    # Status-specific stamps
    if status == "killed":
        stamps["kill_decision"] = True
        stamps["kill_reason"] = f"manual outcome: {note or 'killed after validation'}"
        stamps["kill_date"] = datetime.now().strftime("%Y-%m-%d")
        stamps["stage"] = "killed"
        stamps["portfolio_lane"] = "no"
    elif status == "validated":
        if not opp.get("pain_validated_date"):
            stamps["pain_validated_date"] = datetime.now().strftime("%Y-%m-%d")
        stamps["recommendation"] = "build"

    update_opportunity(opp_id, stamps)

    click.echo(f"Outcome recorded: {name}")
    click.echo(f"  Status: {status}")
    if note:
        click.echo(f"  Note: {note}")

    if status == "validated":
        click.echo(f"\nNext: opp-os build {opp_id} --mode build")
    elif status == "killed":
        click.echo(f"\nMarked for kill-list review.")


@cli.command()
@click.option(
    "--include-stamps/--no-include-stamps",
    default=True,
    show_default=True,
    help="Also derive outcomes from conviction-bridge stamps on opportunity records.",
)
def calibrate(include_stamps):
    """Quantitative calibration: does final_score actually predict outcomes?

    Reads outcome_tracking.jsonl (plus bridge stamps), then reports score-bucket
    discrimination, Brier skill vs base rate, per-dimension effect sizes, and a
    damped weight proposal. Proposals are NEVER auto-applied -- edit
    config/scoring_weights.yaml manually with an audit comment.
    """
    from opportunity_os.engines.calibration_engine import (
        calibration_summary,
        dimension_redundancy,
        outcomes_from_opportunity_stamps,
    )
    from opportunity_os.engines.scoring_engine import load_weights
    from opportunity_os.outcome_tracking import SCORING_DIMENSIONS, _read_outcomes
    from opportunity_os.storage import read_all_opportunities

    outcomes = _read_outcomes()
    all_opps = read_all_opportunities()
    if include_stamps:
        tracked_ids = {o.get("opp_id") for o in outcomes}
        derived = [
            d for d in outcomes_from_opportunity_stamps(all_opps, SCORING_DIMENSIONS)
            if d["opp_id"] not in tracked_ids
        ]
        outcomes = outcomes + derived
        click.echo(f"Outcomes: {len(outcomes)} ({len(derived)} derived from bridge stamps)")
    else:
        click.echo(f"Outcomes: {len(outcomes)} (tracking log only)")

    weights = load_weights().get("weights", {})
    summary = calibration_summary(outcomes, weights, SCORING_DIMENSIONS)

    disc = summary["discrimination"]
    click.echo(f"\n-- Discrimination: {disc['verdict']} "
               f"({disc['resolved_count']} resolved outcomes)")
    for b in disc.get("buckets", []):
        rate = f"{b['success_rate']:.0%}" if b["success_rate"] is not None else "--"
        click.echo(f"   bucket {b['bucket']} (n={b['n']}): success rate {rate}")

    brier = summary["brier"]
    if "skill" in brier:
        click.echo(f"\n-- Brier: {brier['brier']} vs base-rate {brier['brier_reference']} "
                   f"-> skill {brier['skill']:+.2f} (positive = score beats guessing the average)")

    if summary["dimension_effects"]:
        click.echo("\n-- Dimension effects (success avg - failure avg, top 8):")
        for e in summary["dimension_effects"][:8]:
            click.echo(f"   {e['dimension']:<28} {e['effect']:+.3f} "
                       f"(succ {e['avg_success']} vs fail {e['avg_failure']}, "
                       f"n={e['n_success']}+{e['n_failure']})")

    proposal = summary["weight_proposal"]
    click.echo(f"\n-- Weight proposal: {proposal.get('recommendation', proposal.get('note', ''))}")
    for dim, adj in proposal.get("adjusted_dimensions", {}).items():
        click.echo(f"   {dim:<28} {adj['current']:.4f} -> {adj['proposed']:.4f} "
                   f"(effect {adj['effect']:+.3f}, n={adj['n']})")
    if proposal.get("adjusted_dimensions"):
        click.echo("   Apply manually in config/scoring_weights.yaml with an audit comment.")

    redundant = dimension_redundancy(all_opps, SCORING_DIMENSIONS)
    if redundant:
        click.echo("\n-- Redundant dimension pairs (|spearman| >= 0.6 -- double-counted signal):")
        for r in redundant[:5]:
            # A pair is already harmless if either side carries no weight
            neutralized = weights.get(r["dim_a"], 0) == 0 or weights.get(r["dim_b"], 0) == 0
            marker = "  [resolved: weight 0]" if neutralized else ""
            click.echo(f"   {r['dim_a']} ~ {r['dim_b']}: rho {r['spearman']} (n={r['n']}){marker}")


if __name__ == "__main__":
    cli()
