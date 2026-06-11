"""Venture validation and business planning support for the conviction bridge.

`opp-os build` command writes:
  - validation-kit.md  (pure template: 2-week interview script, decision rules)
  - REQUIREMENTS.md    (acceptance criteria skeleton for Phase 0 + Phase 1)
  - business-plan.md   (Claude API call: lean business plan with unit economics)

Used by the build command flow: like → build validate mode → outcome validated
→ build build mode (full pack + claude launch) → outcome shipped/revenue.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# GEO WTP anchors — mirrors kickoff.py for consistency
GEO_WTP_ANCHORS = {
    "venezuela": {"label": "Venezuela", "multiplier": 0.25, "range": "$3-15/mo SaaS"},
    "latam": {"label": "LATAM", "multiplier": 0.40, "range": "$20-50/mo SaaS"},
    "colombia": {"label": "Colombia", "multiplier": 0.40, "range": "$20-50/mo SaaS"},
    "mexico": {"label": "Mexico", "multiplier": 0.40, "range": "$20-50/mo SaaS"},
    "spain": {"label": "Spain", "multiplier": 1.0, "range": "$30-80/mo SaaS"},
    "global": {"label": "Global", "multiplier": 1.0, "range": "$50-200/mo SaaS"},
}


def _text_or(opp: dict, field: str, fallback: str) -> str:
    """Return field only if it is a non-empty string (mirrors kickoff._text_or)."""
    val = opp.get(field)
    return val.strip() if isinstance(val, str) and val.strip() else fallback


def _fmt_list(items, limit: int = 5) -> str:
    """Format list items for display, with fallback."""
    vals = [str(i).strip() for i in (items or [])[:limit] if str(i).strip()]
    return ", ".join(vals) if vals else "not yet recorded"


def build_validation_kit(opp: dict) -> str:
    """Generate a 2-week customer validation kit (pure template, no API calls).

    Includes: interview script with verbatim customer phrases, where to find
    interviewees, disqualifying evidence section, and decision rule for proceeding.
    """
    name = opp.get("name", "this opportunity")
    problem = _text_or(opp, "problem_statement", "the pain described in PROJECT.md")
    target = _text_or(opp, "target_customer", "the target customer in PROJECT.md")
    phrases = opp.get("exact_customer_phrases") or []
    risks = opp.get("risks") or []
    channels = opp.get("top_distribution_channels") or []

    # Build interview script questions incorporating exact phrases
    script_questions = [
        '1. "Can you walk me through your current workflow for ' + _text_or(opp, "vertical", "this task") + '?"',
    ]
    if phrases:
        for phrase in phrases[:2]:
            script_questions.append(
                f'   → Have you ever said something like: "{phrase}"? What triggered that?'
            )
    script_questions.extend([
        '2. "How often does this problem affect you? What\'s your current workaround?"',
        '3. "How much time/money does this cost you per week/month?"',
        '4. "What would an ideal solution look like? How much would it be worth?"',
        '5. "If I built this, would you be my first customer? When could you start using it?"',
        '6. "Who else in your network faces this same problem?"',
    ])
    script_text = "\n   ".join(script_questions)

    # Where to find interviewees
    channel_text = _fmt_list(channels, 4)

    # Disqualifying evidence
    disqualifying = []
    if risks:
        disqualifying.append(f"- Interviewee mentions: {risks[0] if risks else 'competitor X already solves this'}")
    disqualifying.extend([
        "- Interviewee says: 'I don't have time for this problem' or 'It's not really an issue'",
        "- Interviewee cannot articulate a specific dollar cost of the problem",
        "- Interviewee says: 'I'm happy with my current solution' (unprompted)",
    ])
    disqualifying_text = "\n".join(disqualifying)

    return f"""# Validation Kit — {name}

> Generated {datetime.now().strftime('%Y-%m-%d')} | 2-week window to confirm pain with 5+ customer conversations

## Goal

Confirm that the pain is real and worth solving by having structured conversations
with **5 target customers** over the next 14 days. This is not a demo; this is discovery.

## Interview Script

Conduct 30–45 min conversations with people matching: {target}.

   {script_text}

**Scoring:** After each conversation, note:
- Does the interviewee clearly articulate the pain? (y/n)
- Does the interviewee have a specific workaround? (y/n)
- Would they pay for a solution? If so, rough price point?
- Do they know others with the same problem? (y/n)

## Where to Find Interviewees

Start with these channels to recruit 5 conversations:
- {channel_text}
- Twitter/Reddit communities where your target customer hangs out
- Personal network warm intros (highest signal)

**Target:** 5 conversations, 80+ hours combined pain exposure, by day 14.

## Disqualifying Evidence

If ANY of these appear in 3+ of your 5 conversations, the pain may not be real:

{disqualifying_text}

## Decision Rule

**Proceed to BUILD mode if:**
- ✓ At least 4 of 5 interviewees clearly confirm the pain (workaround + daily occurrence + money cost)
- ✓ At least 2 interviewees state willingness to pay a specific amount (even rough estimate)
- ✓ No disqualifying evidence appears in >1 conversation

**Kill and return to inbox if:**
- ✗ Fewer than 4 of 5 confirm pain when asked directly
- ✗ Interviewees consistently say this is nice-to-have, not urgent
- ✗ No one willing to state a price point
→ Run `opp-os outcome {opp.get('id', 'OPP_ID')} killed --note 'Pain not validated in interviews'`

## Next Steps After Validation

1. Document each conversation: who, date, key quotes, pain severity (1-10), WTP quote
2. Synthesize findings in an outcome comment
3. If decision rule ✓: run `opp-os outcome {opp.get('id', 'OPP_ID')} validated`
4. Then run `opp-os build {opp.get('id', 'OPP_ID')}` in build mode for full business plan + MVP spec

---

**Deadline:** {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')} (14 days from today)
"""


def build_requirements_seed(opp: dict) -> str:
    """Generate REQUIREMENTS.md skeleton with Phase 0 + Phase 1 acceptance criteria.

    Phase 0: Validation (2 weeks). Phase 1: MVP build (4-6 weeks).
    """
    name = opp.get("name", "this opportunity")
    path = _text_or(opp, "path_to_first_revenue", "the path defined in PROJECT.md")

    return f"""# REQUIREMENTS.md — {name}

> Acceptance criteria for Phases 0-1. Updated per /spec and /plan.

## Phase 0: Validation (2 weeks)

**Goal:** Confirm that the pain is real with 5+ customer conversations.

### Acceptance Criteria (MVP)
- [ ] 5 target customer interviews logged (name, date, raw notes)
- [ ] Pain severity confirmed for ≥4 interviews (daily occurrence + workaround + $cost)
- [ ] ≥2 interviewees state willingness-to-pay price point (even rough: "$X/month")
- [ ] 0 disqualifying evidence in >1 conversation (see validation-kit.md decision rule)
- [ ] Outcome recorded: `opp-os outcome ... validated`

**Kill Criteria:**
- [ ] <4 interviews confirm pain (re-read decision rule)
- [ ] Consistent "nice-to-have" feedback vs "urgent daily pain"
- [ ] No one willing to articulate a price

If killed: `opp-os outcome ... killed --note '...'`

---

## Phase 1: MVP Build (4-6 weeks)

**Goal:** Ship a minimal product that reaches first paying customer via: {path}

### Product Acceptance
- [ ] Product delivers core value in <6 weeks, solo + AI tooling
- [ ] Reaches first paying customer via documented path (not via discount)
- [ ] First customer pays at least: [TBD — use WTP from validation]
- [ ] Technical scope: [TBD — define in /spec]

### Go-to-Market Acceptance
- [ ] First 10 customers sourced via: [TBD — top_distribution_channels]
- [ ] Customer acquisition cost ≤ [TBD — estimated_cac_logic]
- [ ] Repeatable channel validated with ≥2 paying customers

### Financial Acceptance
- [ ] Cumulative spend ≤ $2K before first revenue
- [ ] Unit economics: [TBD]
  - Customer acquisition cost (CAC)
  - Monthly/annual revenue per customer
  - LTV:CAC ratio
  - Break-even customers

### Success Criteria (Phase 1 end)
- [ ] ≥1 paying customer
- [ ] ≥$X revenue run-rate (TBD)
- [ ] Path to next 10 customers clear (repeatable channel)

---

## Phase 2+: Scale (future)

TBD in post-Phase-1 review. Placeholder for future planning.
"""


def build_business_plan(opp: dict) -> str | None:
    """Generate a lean business plan via Claude API (claude-sonnet-4-6).

    Returns markdown string or None if API unavailable/fails. Never raises.
    Uses the opportunity record (without score_history) to avoid token waste.
    Marks every number not present in the input as [ESTIMATE].
    """
    from opportunity_os.env import load_env_file

    # Ensure env is loaded
    load_env_file()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("build_business_plan: ANTHROPIC_API_KEY not set, returning None")
        return None

    try:
        import anthropic
    except ImportError:
        logger.warning("build_business_plan: anthropic not installed")
        return None

    # Strip score_history and pipeline timestamps to save tokens
    opp_for_api = {
        k: v for k, v in opp.items()
        if k not in (
            "score_history",
            "liked_at",
            "kickoff_at",
            "build_mode",
            "validation_start_date",
            "validation_deadline",
            "outcome",
            "outcome_at",
            "outcome_note",
        )
    }

    client = anthropic.Anthropic(api_key=api_key)
    geo = (opp.get("geography") or "global").lower()
    wtp_anchor = GEO_WTP_ANCHORS.get(geo, GEO_WTP_ANCHORS["global"])

    prompt = f"""Generate a lean business plan for this opportunity. Use ONLY facts from the
opportunity record below. For any number/metric not present in the record, mark it [ESTIMATE].

OPPORTUNITY RECORD:
{json.dumps(opp_for_api, indent=2, default=str)}

INSTRUCTIONS:
1. Executive Summary (100 words): one-liner value prop, target customer, path to first revenue
2. Problem & Evidence: use ONLY evidence present in the record (exact_customer_phrases,
   pain_evidence_sources). Do not invent statistics.
3. Market (TAM/SAM/SOM): use record fields. If missing, mark [ESTIMATE].
4. Unit Economics:
   - Price point: use willingness_to_pay OR [ESTIMATE]
   - CAC: use estimated_cac_logic OR [ESTIMATE]
   - WTP geo multiplier: {wtp_anchor['label']} = {wtp_anchor['multiplier']}x US baseline
   - LTV (assume 24-month lifetime)
   - Break-even: # customers at 6 months
5. Go-to-Market:
   - First 10 customers: use first_10_customer_path
   - Primary channels: use top_distribution_channels
6. 12-Month Milestones (month 1-3-6-12):
   - Revenue, customer count, key product milestones
7. Kill Criteria: use risks + problems that would make the business unviable

Format as markdown with clear sections. Keep it 1-2 pages. Every number should have a source or [ESTIMATE].
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return message.content[0].text
    except Exception as exc:
        logger.error("build_business_plan API call failed: %s", exc)
        return None


def write_venture_pack(opp: dict, target_dir: Path, include_business_plan: bool = True) -> dict:
    """Write validation-kit.md, REQUIREMENTS.md, and optionally business-plan.md.

    Atomic writes (tmp + os.replace). Returns {files: [...], skipped: [...]}.
    """
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    files = []
    skipped = []

    # validation-kit.md
    path = target_dir / "validation-kit.md"
    content = build_validation_kit(opp)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    files.append(str(path))

    # REQUIREMENTS.md
    path = target_dir / "REQUIREMENTS.md"
    content = build_requirements_seed(opp)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    files.append(str(path))

    # business-plan.md (conditional)
    if include_business_plan:
        content = build_business_plan(opp)
        if content:
            path = target_dir / "business-plan.md"
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(content, encoding="utf-8")
            os.replace(tmp, path)
            files.append(str(path))
        else:
            skipped.append("business-plan.md (API unavailable or failed)")
    else:
        skipped.append("business-plan.md (excluded in validate mode)")

    return {"files": files, "skipped": skipped}
