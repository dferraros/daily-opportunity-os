"""
Filters — portfolio lane assignment for the opportunity pipeline.

PortfolioLaneAssigner assigns now/soon/strategic/no based on schema fields.
"""

from __future__ import annotations


# ─── Portfolio Lane Assigner ──────────────────────────────────────────────────

class PortfolioLaneAssigner:
    """
    Assigns a portfolio lane to each opportunity based on schema fields.

    Lanes:
    - "no"         : kill_decision is True
    - "now"        : fast_cash bucket with strong speed + revenue signals
    - "strategic"  : venture_scale bucket with large TAM signal
    - "soon"       : everything else that survives the kill gate
    """

    STRATEGIC_TAM_THRESHOLD: float = 100_000_000  # $100M

    def assign_from_dict(self, opp_dict: dict) -> str:
        """
        Compute portfolio lane for a raw dict.

        Rules (priority order):
        1. "no"         — kill_decision is True
        2. "now"        — bucket is fast_cash AND path_to_first_revenue is non-empty
                          AND time_to_mvp is non-empty
        3. "strategic"  — bucket is venture_scale AND tam >= STRATEGIC_TAM_THRESHOLD
        4. "soon"       — all surviving opportunities not matched above
        """
        if opp_dict.get("kill_decision"):
            return "no"

        bucket = opp_dict.get("bucket", "")
        path_to_rev = opp_dict.get("path_to_first_revenue")
        time_to_mvp = opp_dict.get("time_to_mvp")

        if (
            bucket == "fast_cash"
            and path_to_rev is not None
            and str(path_to_rev).strip()
            and str(path_to_rev).strip().upper() != "TBD"
            and time_to_mvp is not None
            and str(time_to_mvp).strip()
        ):
            return "now"

        tam = opp_dict.get("tam") or opp_dict.get("tam_usd_estimate")
        if bucket == "venture_scale" and tam is not None:
            try:
                if float(tam) >= self.STRATEGIC_TAM_THRESHOLD:
                    return "strategic"
            except (TypeError, ValueError):
                pass

        return "soon"
