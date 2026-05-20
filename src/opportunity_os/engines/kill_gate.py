"""
Kill Gate — 7 binary questions that filter opportunities before scoring.
2 or more failures = kill_decision = True. Do not score killed opportunities.

Philosophy: Reject fast. The value is in what survives, not in scoring everything.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


# ─── Constants ────────────────────────────────────────────────────────────────

KILL_THRESHOLD: int = 2
"""Number of failed criteria required to trigger a kill decision."""


KILL_CRITERIA: List[Dict[str, str]] = [
    {
        "id": "KG-01",
        "question": "Can I explain the pain in 1 sentence?",
        "rationale": "If you cannot articulate it, you do not understand it.",
    },
    {
        "id": "KG-02",
        "question": "Can I name a specific, reachable buyer?",
        "rationale": "SMBs is not a buyer. Venezuelan retail shop owner in Caracas is.",
    },
    {
        "id": "KG-03",
        "question": "Can I reach that buyer cheaply (CAC < 3x monthly revenue)?",
        "rationale": "Distribution must be proven before building.",
    },
    {
        "id": "KG-04",
        "question": "Is there a realistic first revenue path in < 90 days?",
        "rationale": "Ideas that need 6 months before money are ventures, not opportunities.",
    },
    {
        "id": "KG-05",
        "question": "Can an MVP be built in 2-6 weeks with < 2 people?",
        "rationale": "If it needs a team, it is not an opportunity, it is a startup.",
    },
    {
        "id": "KG-06",
        "question": "Is the market big enough if this works (TAM > $10M)?",
        "rationale": "Do not build for a 200-customer ceiling.",
    },
    {
        "id": "KG-07",
        "question": "Do I have a wedge (edge, timing, or distribution advantage)?",
        "rationale": "No wedge = competing on execution alone = expensive.",
    },
]
"""Ordered list of kill-gate criteria. Each entry has id, question, and rationale."""


# ─── Result Dataclass ─────────────────────────────────────────────────────────

@dataclass
class KillGateResult:
    """
    The output of evaluating all 7 kill-gate criteria against an opportunity.

    Attributes:
        passed_count:    Number of criteria answered True (pass).
        failed_count:    Number of criteria answered False (fail).
        failed_criteria: List of criterion IDs that failed (e.g. ["KG-02", "KG-05"]).
        kill_decision:   True when failed_count >= KILL_THRESHOLD. Do not score if True.
        kill_reason:     Human-readable summary of why the opportunity was killed (or cleared).
    """

    passed_count: int
    failed_count: int
    failed_criteria: List[str] = field(default_factory=list)
    kill_decision: bool = False
    kill_reason: str = ""


# ─── Core Evaluation ──────────────────────────────────────────────────────────

def evaluate_kill_gate(answers: Dict[str, bool]) -> KillGateResult:
    """
    Evaluate the 7 binary kill-gate criteria and return a KillGateResult.

    Each criterion is answered with True (passes) or False (fails). Criteria not
    present in the answers dict are treated as unanswered and skipped. Only the
    7 canonical IDs (KG-01 through KG-07) are evaluated.

    Args:
        answers: Mapping of criterion ID to boolean answer.
                 Example: {"KG-01": True, "KG-02": False, "KG-03": True, ...}

    Returns:
        KillGateResult with kill_decision=True if failed_count >= KILL_THRESHOLD.

    Example:
        >>> result = evaluate_kill_gate({
        ...     "KG-01": True,
        ...     "KG-02": False,
        ...     "KG-03": True,
        ...     "KG-04": False,
        ...     "KG-05": True,
        ...     "KG-06": True,
        ...     "KG-07": True,
        ... })
        >>> result.kill_decision
        True
        >>> result.failed_criteria
        ["KG-02", "KG-04"]
    """
    valid_ids = {c["id"] for c in KILL_CRITERIA}
    failed_criteria: List[str] = []
    passed_count = 0

    for criterion_id, passed in answers.items():
        if criterion_id not in valid_ids:
            continue
        if passed:
            passed_count += 1
        else:
            failed_criteria.append(criterion_id)

    failed_count = len(failed_criteria)
    kill_decision = failed_count >= KILL_THRESHOLD

    if kill_decision:
        criteria_labels = ", ".join(sorted(failed_criteria))
        kill_reason = (
            f"Kill gate triggered: {failed_count} of 7 criteria failed "
            f"(threshold: {KILL_THRESHOLD}). Failed: {criteria_labels}."
        )
    elif failed_count == 1:
        kill_reason = (
            f"Kill gate cleared with 1 warning: {failed_criteria[0]} failed. "
            f"Proceed to scoring but flag this criterion."
        )
    else:
        kill_reason = f"Kill gate cleared: all {passed_count} answered criteria passed."

    return KillGateResult(
        passed_count=passed_count,
        failed_count=failed_count,
        failed_criteria=sorted(failed_criteria),
        kill_decision=kill_decision,
        kill_reason=kill_reason,
    )


# ─── Report Formatter ─────────────────────────────────────────────────────────

def format_kill_report(result: KillGateResult) -> str:
    """
    Format a KillGateResult as a human-readable text report.

    Args:
        result: A KillGateResult produced by evaluate_kill_gate().

    Returns:
        Multi-line string suitable for logging, CLI output, or Notion embedding.

    Example output (2 failures):
        KILL GATE REPORT
        ================
        Decision   : KILLED
        Passed     : 5 / 7 answered
        Failed     : 2 / 7 answered
        Failed IDs : KG-02, KG-04
        Reason     : Kill gate triggered: 2 of 7 criteria failed (threshold: 2). Failed: KG-02, KG-04.

        Failed criteria detail:
          KG-02 | Can I name a specific, reachable buyer?
                | Rationale: SMBs is not a buyer. Venezuelan retail shop owner in Caracas is.
          KG-04 | Is there a realistic first revenue path in < 90 days?
                | Rationale: Ideas that need 6 months before money are ventures, not opportunities.
    """
    criteria_by_id = {c["id"]: c for c in KILL_CRITERIA}
    total_answered = result.passed_count + result.failed_count
    decision_label = "KILLED" if result.kill_decision else "CLEARED"

    lines = [
        "KILL GATE REPORT",
        "================",
        f"Decision   : {decision_label}",
        f"Passed     : {result.passed_count} / {total_answered} answered",
        f"Failed     : {result.failed_count} / {total_answered} answered",
        f"Failed IDs : {', '.join(result.failed_criteria) if result.failed_criteria else 'none'}",
        f"Reason     : {result.kill_reason}",
    ]

    if result.failed_criteria:
        lines.append("")
        lines.append("Failed criteria detail:")
        for cid in result.failed_criteria:
            c = criteria_by_id.get(cid)
            if c:
                lines.append(f"  {cid} | {c['question']}")
                lines.append(f"       | Rationale: {c['rationale']}")

    return "\n".join(lines)
