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

logger = logging.getLogger(__name__)

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

    # Apply geo adjustments after normalisation
    final = []
    for opp in rescored:
        if opp.get("id") in target_ids and not opp.get("kill_decision"):
            final.append(apply_geo_adjustments(opp))
        else:
            final.append(opp)

    # Report deltas
    changed = 0
    id_to_old = {o.get("id"): o for o in all_opps}
    for new_opp in final:
        old_opp = id_to_old.get(new_opp.get("id"), {})
        old_s = old_opp.get("final_score")
        new_s = new_opp.get("final_score")
        if old_s != new_s:
            if old_s is not None and new_s is not None:
                delta = f"{float(new_s) - float(old_s):+.2f}"
            else:
                delta = "new"
            name = (new_opp.get("name") or "?")[:50]
            old_str = f"{float(old_s):.2f}" if old_s is not None else "—"
            new_str = f"{float(new_s):.2f}" if new_s is not None else "—"
            click.echo(f"  {name:<50}  {old_str:>5} -> {new_str:>5}  ({delta})")
            changed += 1

    click.echo(f"\n{changed}/{len(all_opps)} scores changed.")

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
    from opportunity_os.free_research import research_opportunity_free
    from opportunity_os.engines.scoring_engine import score_opportunity, normalize_portfolio_scores
    from opportunity_os.geo_lens import apply_geo_adjustments
    from opportunity_os.backup import create_backup

    all_opps = read_all_opportunities()
    if not all_opps:
        click.echo("No opportunities found.", err=True)
        return

    # Sort by score, take top-N alive opps as candidates
    alive = [o for o in all_opps if not o.get("kill_decision")]
    sorted_alive = sorted(alive, key=lambda o: float(o.get("final_score") or 0), reverse=True)
    candidates = sorted_alive[:top_n]

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


if __name__ == "__main__":
    cli()
