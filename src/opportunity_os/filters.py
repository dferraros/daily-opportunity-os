"""
Filters — pre-scoring and post-scoring gates for the opportunity pipeline.

Three filter types:
1. KillCriteriaFilter  — wraps kill_gate, marks opportunities with kill_decision
2. ConfidenceThresholdFilter — drops opportunities below minimum confidence
3. PortfolioLaneAssigner — assigns now/soon/strategic/no based on schema fields
"""

from __future__ import annotations
from typing import List, Optional

from opportunity_os.models import Opportunity
from opportunity_os.engines.kill_gate import evaluate_kill_gate, KILL_CRITERIA


# ─── 1. Kill Criteria Filter ──────────────────────────────────────────────────

class KillCriteriaFilter:
    """
    Wraps the kill gate engine and stamps kill_decision onto an Opportunity.

    In production, kill criteria answers come from the scouting agent which
    evaluates each of the 7 KG questions and stores them as metadata. This
    filter checks whether kill_decision is already set (from prior evaluation)
    or needs to be inferred from available fields on the opportunity.

    Inference logic (when no explicit answers are available):
    - KG-01 passes if problem_statement is non-empty
    - KG-02 passes if target_customer is non-empty and not generic ("TBD")
    - KG-06 passes if tam is not None and tam >= 10_000_000
    All other criteria default to True (benefit of the doubt) at inference time.
    Full evaluation requires explicit answers from the scouting agent.
    """

    def apply(self, opp: Opportunity) -> Opportunity:
        """
        Run kill gate logic on an opportunity and update its kill_decision field.

        If kill_decision is already True, the opportunity is returned as-is — it
        has already been killed and should not be scored.

        If kill_criteria_passed is already set (0-7 integer from scouting agent),
        kill_decision is derived directly: kill if kill_criteria_passed <= 5
        (meaning 2+ failures out of 7).

        Otherwise, infers answers from available model fields and runs evaluate_kill_gate.

        Args:
            opp: The Opportunity to evaluate.

        Returns:
            The same Opportunity with kill_decision and stage updated in place.
        """
        # Already killed — do not re-evaluate
        if opp.kill_decision:
            return opp

        # Scouting agent set kill_criteria_passed — derive kill_decision from it
        if opp.kill_criteria_passed is not None:
            failures = 7 - opp.kill_criteria_passed
            if failures >= 2:
                opp.kill_decision = True
                opp.stage = "killed"
            return opp

        # Infer from available fields
        answers = _infer_kill_answers(opp)
        result = evaluate_kill_gate(answers)

        opp.kill_decision = result.kill_decision
        if result.kill_decision:
            opp.stage = "killed"
            # Append kill reason to kill_reasons list
            if result.kill_reason not in opp.kill_reasons:
                opp.kill_reasons.append(result.kill_reason)

        return opp


def _infer_kill_answers(opp: Opportunity) -> dict:
    """
    Build a partial kill-gate answers dict from available Opportunity fields.

    Only the criteria that can be reliably inferred are included. This is
    a best-effort inference — the scouting agent should supply explicit answers.

    Args:
        opp: The Opportunity to inspect.

    Returns:
        Dict mapping criterion IDs to bool answers (partial, not all 7).
    """
    answers: dict = {}

    # KG-01: Can I explain the pain in 1 sentence?
    # Pass if problem_statement is non-empty and not the placeholder
    kg01 = bool(
        opp.problem_statement
        and opp.problem_statement.strip()
        and opp.problem_statement.strip().upper() != "TBD"
    )
    answers["KG-01"] = kg01

    # KG-02: Can I name a specific, reachable buyer?
    # Pass if target_customer is set and not generic
    kg02 = bool(
        opp.target_customer
        and opp.target_customer.strip()
        and opp.target_customer.strip().upper() not in ("TBD", "UNKNOWN", "SMBS", "USERS")
    )
    answers["KG-02"] = kg02

    # KG-06: Is the market big enough (TAM > $10M)?
    # Only infer if tam is explicitly set
    if opp.tam is not None:
        answers["KG-06"] = opp.tam >= 10_000_000

    return answers


# ─── 2. Confidence Threshold Filter ──────────────────────────────────────────

class ConfidenceThresholdFilter:
    """
    Drops opportunities below a minimum confidence threshold.

    Operates on attractiveness_score (0-10 scale). The min_confidence parameter
    is a 0-1 fraction: an opportunity passes if its attractiveness_score is at
    least min_confidence * 10.

    Default threshold is 0.4 (score >= 4.0 out of 10).
    """

    def apply(self, opp: Opportunity, min_confidence: float = 0.4) -> bool:
        """
        Return True if the opportunity meets the minimum confidence threshold.

        Args:
            opp:            The Opportunity to evaluate.
            min_confidence: Minimum required score as a 0-1 fraction.
                            Default 0.4 means attractiveness_score must be >= 4.0.

        Returns:
            True if the opportunity passes the threshold (should be kept).
            False if it falls below the threshold (should be dropped).

        Note:
            Opportunities without an attractiveness_score (None) are allowed
            through by default — they have not been scored yet and should not
            be dropped at this stage.
        """
        if opp.attractiveness_score is None:
            return True  # Unscored — do not pre-emptively drop

        threshold = min_confidence * 10.0
        return opp.attractiveness_score >= threshold


# ─── 3. Portfolio Lane Assigner ───────────────────────────────────────────────

class PortfolioLaneAssigner:
    """
    Assigns a portfolio lane to each opportunity based on schema fields.

    Lanes:
    - "no"         : kill_decision is True
    - "now"        : fast_cash bucket with strong speed + revenue signals
    - "strategic"  : venture_scale bucket with large TAM signal
    - "soon"       : everything else that survives the kill gate
    """

    # TAM threshold for strategic lane (in USD)
    STRATEGIC_TAM_THRESHOLD: float = 100_000_000  # $100M

    def assign(self, opp: Opportunity) -> str:
        """
        Compute and return the portfolio lane for the given opportunity.

        Also stamps the result onto opp.portfolio_lane before returning.

        Rules applied in priority order:
        1. "no"         — kill_decision is True
        2. "now"        — bucket is fast_cash AND path_to_first_revenue is set
                          AND time_to_mvp is set (both non-None, non-empty)
        3. "strategic"  — bucket is venture_scale AND tam >= STRATEGIC_TAM_THRESHOLD
        4. "soon"       — all surviving opportunities not matched above

        Args:
            opp: The Opportunity to classify.

        Returns:
            One of: "no", "now", "soon", "strategic"
        """
        # Rule 1 — Killed
        if opp.kill_decision:
            opp.portfolio_lane = "no"
            return "no"

        # Rule 2 — Now (fast cash with clear execution path)
        if (
            opp.bucket == "fast_cash"
            and opp.path_to_first_revenue is not None
            and str(opp.path_to_first_revenue).strip()
            and str(opp.path_to_first_revenue).strip().upper() != "TBD"
            and opp.time_to_mvp is not None
            and str(opp.time_to_mvp).strip()
        ):
            opp.portfolio_lane = "now"
            return "now"

        # Rule 3 — Strategic (venture scale with large market)
        if (
            opp.bucket == "venture_scale"
            and opp.tam is not None
            and opp.tam >= self.STRATEGIC_TAM_THRESHOLD
        ):
            opp.portfolio_lane = "strategic"
            return "strategic"

        # Rule 4 — Soon (default for anything that survives)
        opp.portfolio_lane = "soon"
        return "soon"


# ─── Pipeline Orchestrator ────────────────────────────────────────────────────

def apply_pipeline_filters(opps: List[Opportunity]) -> List[Opportunity]:
    """
    Run all pipeline filters in sequence across a list of opportunities.

    Filter sequence:
    1. KillCriteriaFilter   — sets kill_decision and stage on each opportunity
    2. ConfidenceThresholdFilter — removes opportunities below confidence floor
    3. PortfolioLaneAssigner — assigns portfolio_lane to surviving opportunities

    Opportunities killed in step 1 are retained in the output (for audit trail)
    but have portfolio_lane="no" and stage="killed". Only the confidence filter
    actually removes records from the output list.

    Args:
        opps: List of Opportunity objects to process.

    Returns:
        Filtered and annotated list of Opportunity objects. Killed opportunities
        are kept (for audit) but low-confidence non-killed opportunities are removed.
    """
    kill_filter = KillCriteriaFilter()
    confidence_filter = ConfidenceThresholdFilter()
    lane_assigner = PortfolioLaneAssigner()

    surviving: List[Opportunity] = []

    for opp in opps:
        # Step 1 — Kill gate
        opp = kill_filter.apply(opp)

        # Step 2 — Confidence threshold (only drop non-killed opportunities)
        if not opp.kill_decision:
            if not confidence_filter.apply(opp):
                # Below confidence floor — skip (do not include in output)
                continue

        # Step 3 — Portfolio lane assignment
        lane_assigner.assign(opp)

        surviving.append(opp)

    return surviving
