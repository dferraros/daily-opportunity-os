"""
Enrichment pipeline step — extracted from daily_run.py to keep it under 800 lines.

Contains: step 9.7 (benchmark mapping), step 10 (pain OS), step 11 (distribution OS),
step 11.5 (research executor), step 11.6 (free research), step 11.8 (pain library).
"""

import logging
import time
from opportunity_os.pipeline_monitor import log_failure

logger = logging.getLogger(__name__)


def run_enrichment_steps(all_opps_sorted: list, dry_run: bool) -> tuple:
    """Steps 9.7–11.8: benchmark mapping, pain/distribution OS, research, pain library.

    Returns (all_opps_sorted, top_20) — both may be enriched in place.
    """
    # Step 9.7: Benchmark Mapping
    logger.info("Step 9.7: Running Benchmark Mapper on top 30 opportunities...")
    top_30 = all_opps_sorted[:30]
    try:
        from opportunity_os.engines.benchmark_engine import run_benchmark
        for i, opp in enumerate(top_30):
            if not opp.get("benchmark_archetype"):
                result = run_benchmark(opp)
                top_30[i] = {**opp, **{k: v for k, v in result.items() if not k.startswith("_")}}
        bench_populated = sum(1 for o in top_30 if o.get("benchmark_archetype"))
        logger.info("  Benchmark archetypes populated for %d/%d opportunities", bench_populated, len(top_30))
    except ImportError as e:
        logger.warning("Benchmark engine not available: %s", e)
    except Exception as e:
        log_failure("benchmark_mapping", e)

    # Step 10: Customer Pain OS
    logger.info("Step 10: Running Customer Pain OS on top 20 opportunities...")
    top_20 = all_opps_sorted[:20]
    try:
        from opportunity_os.pain_intelligence import run_pain_intelligence, execute_pain_research
        for i, opp in enumerate(top_20):
            pain_result = run_pain_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in pain_result.items() if not k.startswith("_")}}
        logger.info("  Pain templates built for %d opportunities", len(top_20))

        # Execute real research on top 5 only (API cost ~$0.15/opp)
        if not dry_run:
            top_5 = top_20[:5]
            researched_count = 0
            for i, opp in enumerate(top_5):
                research_result = execute_pain_research(opp)
                if research_result:
                    top_20[i] = {**top_20[i], **research_result}
                    researched_count += 1
                    logger.info("  Pain researched: %s (score: %s)",
                                opp.get("name", "unknown")[:40],
                                research_result.get("pain_validation_score"))
            logger.info("  Pain research executed for %d/5 opportunities", researched_count)
    except ImportError as e:
        logger.warning("Pain intelligence module not available: %s", e)
    except Exception as e:
        log_failure("pain_os", e)

    # Step 11: Distribution OS
    logger.info("Step 11: Running Distribution OS on top 20 opportunities...")
    try:
        from opportunity_os.distribution_intelligence import (
            run_distribution_intelligence,
            execute_distribution_research,
        )
        for i, opp in enumerate(top_20):
            dist_result = run_distribution_intelligence(opp)
            top_20[i] = {**opp, **{k: v for k, v in dist_result.items() if not k.startswith("_")}}
        logger.info("  Distribution templates built for %d opportunities", len(top_20))

        if not dry_run:
            researched_count = 0
            for i, opp in enumerate(top_20[:5]):
                research_result = execute_distribution_research(opp)
                if research_result:
                    top_20[i] = {**top_20[i], **research_result}
                    researched_count += 1
                    logger.info("  Distribution researched: %s (validated: %s)",
                                opp.get("name", "unknown")[:40],
                                research_result.get("distribution_validated"))
            logger.info("  Distribution research executed for %d/5 opportunities", researched_count)
    except ImportError as e:
        logger.warning("Distribution intelligence module not available: %s", e)
    except Exception as e:
        log_failure("distribution_os", e)

    # Step 11.5: Research Executor — top 3 ONLY (API cost ~$0.08-0.15/opp)
    # Never increase this limit without checking Anthropic billing first.
    top_3_research = [o for o in all_opps_sorted[:3] if not o.get("research_executed_at")]
    logger.info("Step 11.5: Running Research Executor on top 3 new opportunities (%d unresearched)...", len(top_3_research))
    if dry_run:
        logger.info("  [dry-run] Skipping research executor (API cost ~$0.08-0.15/opp)")
    else:
        try:
            from opportunity_os.research_executor import run_research_executor
            for i, opp in enumerate(top_3_research, 1):
                logger.info("  Researching %d/%d: %s", i, len(top_3_research), opp.get("name", "unknown")[:50])
                run_research_executor(opp)
        except ImportError as e:
            logger.warning("Research executor not available: %s", e)
        except Exception as e:
            log_failure("research_executor", e)

    # Step 11.6: Free Research — Jina + HN + Reddit for opps 4-20 (zero cost)
    logger.info("Step 11.6: Running free research (Jina + HN + Reddit) on top 20...")
    try:
        from opportunity_os.free_research import research_opportunity_free
        from opportunity_os.engines.scoring_engine import score_opportunity
        from opportunity_os.geo_lens import apply_geo_adjustments
        free_researched = 0
        for i, opp in enumerate(all_opps_sorted[:20]):
            if not opp.get("free_research_at"):  # independent of paid research
                updates = research_opportunity_free(opp)
                if updates:
                    enriched = {**opp, **updates}
                    if not enriched.get("kill_decision"):
                        enriched = score_opportunity(enriched)
                        enriched = apply_geo_adjustments(enriched)
                    all_opps_sorted[i] = enriched
                    free_researched += 1
                time.sleep(0.5)
        logger.info("  Free research complete: %d opps enriched", free_researched)
    except Exception as e:
        log_failure("free_research", e)

    # Step 11.8: Pain Library — persist pain clusters from researched opps
    logger.info("Step 11.8: Updating pain library with researched opportunities...")
    try:
        from opportunity_os.pain_library import upsert_pain_cluster
        written = 0
        for opp in top_20:
            if opp.get("research_executed_at") and opp.get("pain_validation_score") is not None:
                if upsert_pain_cluster(opp):
                    written += 1
        logger.info("  Pain library updated: %d clusters upserted", written)
    except ImportError as e:
        logger.warning("Pain library not available: %s", e)
    except Exception as e:
        log_failure("pain_library", e)

    return all_opps_sorted, top_20
