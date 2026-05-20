# Validation OS Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Validation OS that converts top-scored opportunities into 8-section validation packages, triggered automatically in the daily pipeline (score ≥ 7.0, stage == "scout") and manually via `opp-os validate <opp-id>`.

**Architecture:** `validation_engine.py` is a pure-computation module (no I/O, no side effects) that follows the exact pattern of `pain_intelligence.py`. It returns a dict with `_validation_markdown` and schema fields. Step 14 in `daily_run.py` owns all file writes. Output goes to `reports/validation/` (file) and Deep Dives Notion DB (via appended JSON sync payload).

**Tech Stack:** Python 3.11+, uv, Click CLI, existing Pydantic schema, Notion MCP (Claude Code in-session only). No new dependencies.

---

## Task 1: Config + report directory scaffolding

**Files:**
- Modify: `config/scoring_weights.yaml`
- Modify: `src/opportunity_os/reports.py`

**Step 1: Add validation threshold to config**

In `config/scoring_weights.yaml`, append a new top-level section at the bottom:
```yaml
thresholds:
  auto_validation: 7.0   # opps scoring >= this are auto-promoted in daily Step 14
```

**Step 2: Add `reports/validation/` to ensure_report_dirs()**

In `src/opportunity_os/reports.py`, find the `ensure_report_dirs()` function. It creates `reports/daily/`, `reports/weekly/`, `reports/deep-dives/`. Add validation alongside them:
```python
os.makedirs(os.path.join(root, "reports", "validation"), exist_ok=True)
```

Also find the `report_path()` function and add a `"validation"` case:
```python
elif report_type == "validation":
    return os.path.join(root, "reports", "validation", f"{date}-{suffix}.md")
```

**Step 3: Verify directories are created**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -c "from opportunity_os.reports import ensure_report_dirs; ensure_report_dirs(); import os; print(os.path.exists('reports/validation'))"
```
Expected: `True`

**Step 4: Commit**
```bash
git add config/scoring_weights.yaml src/opportunity_os/reports.py
git commit -m "feat(validation-os): add config threshold + reports/validation/ directory"
```

---

## Task 2: Write failing tests for validation_engine.py

**Files:**
- Create: `tests/test_validation_engine.py`

**Step 1: Write the tests**

```python
"""Tests for validation_engine.py"""
import pytest
from opportunity_os.validation_engine import (
    run_validation,
    build_validation_queries,
    is_validation_complete,
    validation_status_label,
    AUTO_SECTION_COUNT,
    FULL_SECTION_COUNT,
)


# ─── Minimal valid opp fixture ───────────────────────────────────────────────

@pytest.fixture
def scout_opp():
    return {
        "id": "opp_test_001",
        "name": "USDT Accounting Tool",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.82,
        "geography": "venezuela",
        "vertical": "smb_software",
        "target_customer": "Venezuelan informal SMB operators",
        "problem_statement": "Manual USDT accounting in spreadsheets causes reconciliation errors",
        "trigger_signal": "Reddit: merchants complaining about manual tracking",
        "pain_severity": 8,
        "competition_intensity": 3,
        "executability_score": 7.5,
        "why_now": "USDT volume in VE up 340% YoY",
        "path_to_first_revenue": "Charge $29/mo for automated USDT reconciliation",
        "willingness_to_pay": 6,
        "speed_to_mvp": 7,
        "venezuela_wedge_category": "smb_software_informal_operators",
        "portfolio_lane": "now",
    }


@pytest.fixture
def scout_opp_minimal():
    """Opp with only required fields — tests graceful fallback."""
    return {
        "id": "opp_test_002",
        "name": "Minimal Test Opp",
        "stage": "scout",
        "kill_decision": False,
        "final_score": 7.1,
        "geography": "global",
        "vertical": "fintech",
        "target_customer": "SMB owners",
        "problem_statement": "Manual processes waste time",
    }


# ─── run_validation — auto mode (sections 1-7) ───────────────────────────────

class TestRunValidationAuto:
    def test_returns_dict(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert isinstance(result, dict)

    def test_has_validation_markdown_key(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert "_validation_markdown" in result
        assert isinstance(result["_validation_markdown"], str)
        assert len(result["_validation_markdown"]) > 100

    def test_auto_has_correct_section_count(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        section_count = md.count("\n## ")
        assert section_count == AUTO_SECTION_COUNT  # 7

    def test_full_has_correct_section_count(self, scout_opp):
        result = run_validation(scout_opp, mode="full")
        md = result["_validation_markdown"]
        section_count = md.count("\n## ")
        assert section_count == FULL_SECTION_COUNT  # 8

    def test_opp_name_in_markdown(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        assert "USDT Accounting Tool" in result["_validation_markdown"]

    def test_interview_questions_exactly_five(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        # Each question starts with "Q1." "Q2." ... "Q5."
        for i in range(1, 6):
            assert f"Q{i}." in md
        assert "Q6." not in md

    def test_pricing_has_three_options(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        assert "Option A" in md
        assert "Option B" in md
        assert "Option C" in md

    def test_landing_page_has_headline(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        md = result["_validation_markdown"]
        assert "Headline:" in md

    def test_minimal_opp_does_not_crash(self, scout_opp_minimal):
        result = run_validation(scout_opp_minimal, mode="auto")
        assert "_validation_markdown" in result
        assert len(result["_validation_markdown"]) > 50

    def test_schema_fields_returned(self, scout_opp):
        result = run_validation(scout_opp, mode="auto")
        # These schema fields should be set by the engine
        assert result.get("validation_status") == "in_progress"
        assert result.get("stage") == "validation"
        assert "_opp_id" in result
        assert "_opp_name" in result


# ─── build_validation_queries ────────────────────────────────────────────────

class TestBuildValidationQueries:
    def test_returns_list_of_strings(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        assert isinstance(queries, list)
        assert all(isinstance(q, str) for q in queries)

    def test_returns_5_to_8_queries(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        assert 5 <= len(queries) <= 8

    def test_geography_influences_queries(self, scout_opp):
        queries = build_validation_queries(scout_opp)
        # Venezuela opp should have Spanish-language queries
        combined = " ".join(queries).lower()
        assert any(term in combined for term in ["venezuela", "venezolano", "usdt", "smb"])


# ─── convenience helpers ─────────────────────────────────────────────────────

class TestHelpers:
    def test_is_validation_complete_false_when_in_progress(self):
        opp = {"validation_status": "in_progress"}
        assert is_validation_complete(opp) is False

    def test_is_validation_complete_true_when_passed(self):
        opp = {"validation_status": "passed"}
        assert is_validation_complete(opp) is True

    def test_validation_status_label_returns_string(self):
        assert isinstance(validation_status_label("in_progress"), str)
        assert isinstance(validation_status_label(None), str)
```

**Step 2: Run tests to verify they fail correctly**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run pytest tests/test_validation_engine.py -v 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'opportunity_os.validation_engine'`

**Step 3: Commit the failing tests**
```bash
git add tests/test_validation_engine.py
git commit -m "test(validation-os): add failing tests for validation_engine"
```

---

## Task 3: Implement validation_engine.py

**Files:**
- Create: `src/opportunity_os/validation_engine.py`

**Step 1: Write the module**

```python
"""
Validation Engine — template-driven validation package builder.

Follows the exact pattern of pain_intelligence.py and distribution_intelligence.py:
- Pure computation, no I/O, no side effects
- Input: opp: dict (not Pydantic model — always a dict from the pipeline)
- Output: dict with schema fields + _-prefixed helper keys
- daily_run.py Step 14 and validation_run.py own all file writes

Public API:
  run_validation(opp, mode="auto") -> dict
  build_validation_queries(opp) -> list[str]
  is_validation_complete(opp) -> bool
  validation_status_label(status) -> str

Constants:
  AUTO_SECTION_COUNT = 7   (sections 1-7)
  FULL_SECTION_COUNT = 8   (sections 1-8, manual mode only)
  AUTO_VALIDATION_THRESHOLD = 7.0
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────

AUTO_SECTION_COUNT = 7
FULL_SECTION_COUNT = 8
AUTO_VALIDATION_THRESHOLD = 7.0

# Interview question templates keyed by geography + vertical
# Q format: past-focused, open-ended (SKILL.md quality gate)
INTERVIEW_QUESTION_BANK = {
    "venezuela": [
        "Cuéntame la última vez que tuviste un problema con [PROBLEM] — ¿qué pasó exactamente?",
        "¿Cómo estás manejando [PROBLEM] hoy? ¿Qué herramientas o procesos usas?",
        "¿Cuánto tiempo o dinero perdiste la última vez que [PROBLEM] te causó un error?",
        "¿Cuándo fue la última vez que buscaste una solución para [PROBLEM]? ¿Qué encontraste?",
        "Si [SOLUTION] existiera hoy, ¿cómo cambiaría tu semana típica?",
        "¿Quién más en tu negocio sufre este problema? ¿Cómo lo resuelven ellos?",
        "¿Has pagado por algo para resolver [PROBLEM] antes? ¿Qué fue? ¿Funcionó?",
    ],
    "latam": [
        "Tell me about the last time [PROBLEM] caused you a real headache — what happened?",
        "Walk me through how you currently handle [PROBLEM] day to day.",
        "How much time or money did you lose the last time [PROBLEM] went wrong?",
        "When did you last look for a solution to [PROBLEM]? What did you find?",
        "If [SOLUTION] existed today, what would your typical week look like?",
        "Who else in your business faces this? How do they deal with it?",
        "Have you paid for anything to solve [PROBLEM] before? What? Did it work?",
    ],
    "global": [
        "Tell me about the last time [PROBLEM] caused you a real problem — what happened?",
        "Walk me through how you currently handle [PROBLEM] day to day.",
        "How much time or money did you lose the last time [PROBLEM] went wrong?",
        "When did you last actively look for a solution to [PROBLEM]? What did you find?",
        "If [SOLUTION] existed today, how would your typical week change?",
        "Who else in your organization faces this? How do they deal with it?",
        "Have you ever paid for something to solve [PROBLEM]? What was it? Did it work?",
    ],
}

# Kill criteria templates from DecisionFilterResults
KILL_CRITERIA_TEMPLATES = {
    "can_sell_fast": (
        "Kill if: Cannot identify and contact 10 potential buyers within 7 days via "
        "direct outreach, WhatsApp, or existing network."
    ),
    "can_build_lean": (
        "Kill if: MVP requires more than 2 weeks of solo development OR costs more than "
        "$500 to test the core value proposition."
    ),
    "can_compound": (
        "Kill if: After 3 paying customers, there is no evidence of word-of-mouth, "
        "referral, data accumulation, or switching cost forming."
    ),
}

# Trust mechanisms by geography — imported logic from distribution_intelligence
TRUST_SNIPPETS = {
    "venezuela": "Reference a mutual contact or local community. Use WhatsApp voice message, not email. Mention specific VE context (USDT, P2P, Binance P2P).",
    "latam": "Mention a specific local reference or case. Lead with outcome in first message. WhatsApp preferred over email.",
    "colombia": "Use LinkedIn for B2B. Reference local industry context. Formal tone for first contact.",
    "mexico": "WhatsApp or LinkedIn. Reference shared network if possible. Short, direct first message.",
    "spain": "LinkedIn or email. Formal first contact. Reference relevant EU/fintech context.",
    "global": "LinkedIn or email. Lead with specific pain point observation. Keep first message under 100 words.",
}


# ─── Query builder ────────────────────────────────────────────────────────────

def build_validation_queries(opp: dict) -> list[str]:
    """
    Build 5-8 customer discovery search queries from opp fields.
    Used by in-session agent to research customer pain evidence.
    """
    geo = opp.get("geography", "global").lower()
    vertical = opp.get("vertical", "").replace("_", " ")
    problem = opp.get("problem_statement", opp.get("name", ""))[:80]
    target = opp.get("target_customer", "")[:60]
    wedge = opp.get("venezuela_wedge_category", "")

    queries = []

    if geo == "venezuela":
        queries += [
            f"Venezuela {vertical} problemas {problem[:40]} Reddit OR Twitter",
            f"venezolanos {target} herramientas alternativas site:reddit.com OR site:twitter.com",
            f"USDT Venezuela {vertical} queja OR frustración 2024 OR 2025",
        ]
        if wedge:
            queries.append(f"Venezuela {wedge.replace('_', ' ')} pain complaints workaround")
    elif geo == "latam":
        queries += [
            f"LATAM {vertical} {problem[:40]} Reddit complaints",
            f"{target} {vertical} herramienta frustración OR workaround site:reddit.com",
        ]
    else:
        queries += [
            f"{vertical} {problem[:40]} reddit complaints workaround",
            f'"{target}" "{problem[:30]}" frustration OR "pain point" site:reddit.com',
        ]

    # Universal queries
    queries += [
        f"{opp.get('name', vertical)} alternatives competitors review site:g2.com OR site:capterra.com",
        f"{target} {problem[:40]} \"I wish\" OR \"why isn't there\" OR \"does anyone know\"",
        f"{vertical} {problem[:40]} \"paying for\" OR \"hired someone\" OR \"built internally\"",
    ]

    # Deduplicate and limit
    seen = set()
    result = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            result.append(q)
        if len(result) >= 8:
            break

    return result[:8] if len(result) > 5 else result


# ─── Section renderers ────────────────────────────────────────────────────────

def _safe(val, default: str = "TBD", max_len: int = 500) -> str:
    if val is None:
        return default
    return str(val)[:max_len]


def _render_section_1_thesis(opp: dict) -> str:
    """Section 1: Thesis brief + kill criteria."""
    name = _safe(opp.get("name"), "Unknown Opportunity")
    score = opp.get("final_score", 0)
    lane = opp.get("portfolio_lane", "strategic")
    problem = _safe(opp.get("problem_statement"), "Problem not defined")
    why_now = _safe(opp.get("why_now") or opp.get("why_now_venezuela", {}).get("recent_change") if isinstance(opp.get("why_now_venezuela"), dict) else None, "Timing not specified")
    pain_reason = _safe(opp.get("pain_severity_reason"), "")
    filters = opp.get("decision_filter_results") or {}
    sell_fast = filters.get("can_sell_fast")
    build_lean = filters.get("can_build_lean")
    compound = filters.get("can_compound")

    filter_lines = []
    for label, val, key in [
        ("Can sell fast", sell_fast, "can_sell_fast"),
        ("Can build lean", build_lean, "can_build_lean"),
        ("Can compound", compound, "can_compound"),
    ]:
        if val is True:
            filter_lines.append(f"  - ✅ {label}")
        elif val is False:
            filter_lines.append(f"  - ❌ {label} — {KILL_CRITERIA_TEMPLATES[key]}")
        else:
            filter_lines.append(f"  - ⬜ {label} — not yet scored")

    filter_block = "\n".join(filter_lines) if filter_lines else "  - Not yet scored"

    return f"""## 1. Thesis

**{name}** | Score: {score:.2f} | Lane: {lane.upper()}

**Problem:** {problem}

**Why now:** {why_now}

**Pain evidence:** {pain_reason if pain_reason else "Run pain intelligence agent to populate."}

**Decision filters:**
{filter_block}
"""


def _render_section_2_customer(opp: dict) -> str:
    """Section 2: Customer + pain snapshot."""
    target = _safe(opp.get("target_customer"), "Not specified")
    pain_level = opp.get("customer_pain_level") or opp.get("pain_severity", "?")
    urgency = opp.get("urgency_of_need", "?")
    frequency = opp.get("frequency_of_need", "?")
    wtp = opp.get("willingness_to_pay", "?")
    phrases = opp.get("exact_customer_phrases") or []
    workarounds = opp.get("workarounds_found") or []

    phrases_block = "\n".join(f'  - "{p}"' for p in phrases[:4]) if phrases else "  - Run pain intelligence agent to collect real customer language."
    workarounds_block = "\n".join(f"  - {w}" for w in workarounds[:3]) if workarounds else "  - Not yet documented — ask in interviews."

    return f"""## 2. Customer + Pain

**Target:** {target}

**Pain dimensions (1-10):**
  - Severity: {pain_level} | Urgency: {urgency} | Frequency: {frequency} | WTP: {wtp}

**Exact customer language:**
{phrases_block}

**Current workarounds:**
{workarounds_block}
"""


def _render_section_3_interviews(opp: dict) -> str:
    """Section 3: 5 interview questions (SKILL.md quality gate: open-ended, past-focused)."""
    geo = opp.get("geography", "global").lower()
    problem = _safe(opp.get("problem_statement", opp.get("name", "this problem")), max_len=60)
    solution = opp.get("name", "this solution")[:60]
    target = _safe(opp.get("target_customer", "the customer"), max_len=40)

    bank = INTERVIEW_QUESTION_BANK.get(geo, INTERVIEW_QUESTION_BANK["global"])
    questions = []
    for q in bank[:5]:
        q = q.replace("[PROBLEM]", problem)
        q = q.replace("[SOLUTION]", solution)
        q = q.replace("[TARGET]", target)
        questions.append(q)

    q_block = "\n\n".join(f"Q{i+1}. {q}" for i, q in enumerate(questions))

    return f"""## 3. Interview Script

**Target:** {target} — aim for 5 interviews in 7 days.

**Logistics:** 20-minute call or WhatsApp voice. Record with permission. Focus on past behavior, not hypothetical intent.

{q_block}

**After each interview:** Note exact words they use. Flag any kill signal immediately.
"""


def _render_section_4_assumptions(opp: dict) -> str:
    """Section 4: 3 falsifiable assumptions from DecisionFilterResults."""
    filters = opp.get("decision_filter_results") or {}
    risks = opp.get("risks") or []
    assumptions_raw = opp.get("assumptions") or []

    # Derive 3 assumptions from the decision filter logic
    assumptions = [
        f"**A1 — Reachability:** We can identify and contact 10 {_safe(opp.get('target_customer', 'potential buyers'), max_len=40)} within 7 days via existing channels.",
        f"**A2 — Pain is real:** At least 4 of 5 interviewees confirm the pain is severe enough that they have already tried to solve it.",
        f"**A3 — WTP exists:** At least 2 of 5 interviewees express willingness to pay €{_estimate_price(opp)}/mo or more.",
    ]

    kill_criteria = [
        KILL_CRITERIA_TEMPLATES["can_sell_fast"],
        KILL_CRITERIA_TEMPLATES["can_build_lean"],
        KILL_CRITERIA_TEMPLATES["can_compound"],
    ]

    # Add any extra risks from the schema
    extra_risks = [f"- {r}" for r in risks[:2]] if risks else []
    extra_block = "\n".join(extra_risks) if extra_risks else ""

    assumptions_block = "\n\n".join(assumptions)
    kill_block = "\n".join(f"{i+1}. {k}" for i, k in enumerate(kill_criteria))

    return f"""## 4. Falsifiable Assumptions

{assumptions_block}

**Kill criteria (stop if any of these trigger):**
{kill_block}
{extra_block}
"""


def _render_section_5_pricing(opp: dict) -> str:
    """Section 5: 3 pricing options with EUR amounts."""
    base = _estimate_price(opp)
    low = max(9, int(base * 0.5))
    mid = base
    high = int(base * 2.5)

    geo = opp.get("geography", "global")
    frp = opp.get("first_revenue_path") or {}
    first_offer = _safe(frp.get("first_offer") if isinstance(frp, dict) else None,
                        opp.get("path_to_first_revenue", "Core product access"), max_len=80)
    model = opp.get("monetization_model", "monthly subscription")

    return f"""## 5. Pricing Test

**Model:** {model}
**First offer:** {first_offer}
**Geography:** {geo} (adjust EUR/USD if needed)

| Option | Price | Framing | Test signal |
|--------|-------|---------|-------------|
| **A — Anchor** | €{high}/mo | Premium tier, full feature set | Baseline willingness to pay |
| **B — Target** | €{mid}/mo | Standard access, core value | Primary conversion target |
| **C — Entry** | €{low}/mo | Starter / first 10 customers discount | Remove price as objection |

**Test method:** Present all three options in interviews. Ask: "If this existed tomorrow, which would you choose?" Note hesitation, not just answer.

**Kill signal:** If Option C triggers "that's too expensive" → rethink unit economics.
"""


def _render_section_6_landing_page(opp: dict) -> str:
    """Section 6: Landing page hypothesis."""
    name = _safe(opp.get("name"), "Product Name")
    target = _safe(opp.get("target_customer"), "Your customer")
    problem = _safe(opp.get("problem_statement"), "the problem")[:120]
    phrases = opp.get("exact_customer_phrases") or []
    why_now = _safe(opp.get("why_now"), "")[:100]

    # Generate headline from customer language or problem statement
    if phrases:
        headline = f'Stop doing "{phrases[0][:60]}" manually'
    else:
        headline = f"The fastest way to solve {problem[:60]}"

    subheadline = f"Built for {target}. {why_now}" if why_now else f"Built for {target}."
    cta = "Get early access" if opp.get("stage") == "scout" else "Start free trial"

    return f"""## 6. Landing Page Hypothesis

**URL:** [create a simple Carrd or Notion page to test]

**Headline:** {headline}

**Subheadline:** {subheadline}

**CTA:** {cta}

**Conversion target:** 15% of visitors click CTA (cold traffic), 40%+ from outreach.

**Traffic source:** Direct outreach to 50 targeted contacts. Do NOT run paid ads yet.

**Pass condition:** 15+ people click CTA and leave their email within 7 days.

**Kill signal:** Less than 5 clicks from 50 targeted outreach contacts → headline/framing is wrong, or the pain is not strong enough.
"""


def _render_section_7_outreach(opp: dict) -> str:
    """Section 7: Outreach script (uses TRUST_SNIPPETS)."""
    geo = opp.get("geography", "global").lower()
    target = _safe(opp.get("target_customer"), "operators")
    problem = _safe(opp.get("problem_statement"), "manual processes")[:80]
    name = _safe(opp.get("name"), "this solution")

    # Get distribution channel
    dist = opp.get("distribution_profile") or {}
    channels = dist.get("top_channels") if isinstance(dist, dict) else []
    channel = channels[0] if channels else ("WhatsApp" if geo == "venezuela" else "LinkedIn")

    trust_note = TRUST_SNIPPETS.get(geo, TRUST_SNIPPETS["global"])

    # Template first message
    if geo == "venezuela":
        first_msg = (
            f"Hola [Nombre], soy Daniel. Vi que trabajas en [CONTEXT]. "
            f"Estoy investigando cómo los {target} manejan {problem[:50]}. "
            f"¿Tendrías 15 minutos esta semana para contarme tu experiencia? "
            f"No es una venta — solo quiero entender el problema."
        )
    else:
        first_msg = (
            f"Hi [Name], I'm Daniel. I noticed you work in [CONTEXT]. "
            f"I'm researching how {target} handle {problem[:50]}. "
            f"Would you have 15 minutes this week to share your experience? "
            f"Not a sales call — I'm trying to understand the problem."
        )

    return f"""## 7. Outreach Script

**Primary channel:** {channel}
**Trust note:** {trust_note}

**First message template:**
> {first_msg}

**List source:** LinkedIn Sales Navigator (filter: {target}, {geo.upper()}) OR local community groups OR existing network.

**Target:** 50 outreach messages → 10 replies → 5 interviews.

**Expected response rate:** 10-20% (higher if warm intro, lower if cold).

**Follow-up (48h no reply):**
> "Quick follow-up — are you the right person to talk to about this, or should I reach out to someone else on your team?"

**Kill signal:** Less than 5% reply rate from 30+ outreach messages → channel or target customer is wrong.
"""


def _render_section_8_mvp(opp: dict) -> str:
    """Section 8: MVP scope + 7-day sprint (full mode only)."""
    speed = opp.get("speed_to_mvp", 5)
    capital = opp.get("capital_intensity", 5)
    ai_leverage = opp.get("ai_leverage", opp.get("ai_leverage_potential", 5))
    first_proof = ""
    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict):
        first_proof = _safe(frp.get("first_proof_point_needed"), max_len=120)
    if not first_proof:
        first_proof = _safe(opp.get("path_to_first_revenue"), max_len=120)

    # Estimate build time
    if speed >= 8:
        build_estimate = "3-5 days"
        mvp_type = "No-code / spreadsheet + Zapier automation"
    elif speed >= 6:
        build_estimate = "5-10 days"
        mvp_type = "Lightweight webapp or Notion template + manual fulfillment"
    else:
        build_estimate = "2-4 weeks"
        mvp_type = "Minimal coded tool — defer to post-validation"

    ai_note = f"AI leverage score: {ai_leverage}/10 — " + (
        "High AI automation potential. Use Claude/GPT for core logic before writing custom code." if ai_leverage >= 7
        else "Moderate AI potential. Use for reporting/summary layer." if ai_leverage >= 5
        else "Low AI leverage. Build manually."
    )

    return f"""## 8. MVP Scope + 7-Day Sprint

**MVP type:** {mvp_type}
**Build estimate:** {build_estimate}
**Capital intensity:** {capital}/10 (lower = cheaper)

**{ai_note}**

**First proof point needed:** {first_proof if first_proof else "Confirm with 3 paying customers."}

**7-day sprint:**
- Day 1-2: 5 customer interviews (section 3 script)
- Day 3: Synthesize interviews. Kill or continue decision.
- Day 4-5: Build MVP (if continue): {mvp_type}
- Day 6: Launch landing page (section 6). Send 50 outreach messages (section 7).
- Day 7: Tally results against kill criteria (section 4). Decide: build / pivot / kill.

**Kill criteria check (Day 7):**
- [ ] 5 interviews completed with real pain confirmation
- [ ] 15+ landing page CTA clicks
- [ ] At least 2 verbal WTP signals at target price
- [ ] At least 1 "when can I use this?" response
"""


# ─── Price estimator helper ───────────────────────────────────────────────────

def _estimate_price(opp: dict) -> int:
    """Estimate mid-tier price point in EUR from schema signals."""
    frp = opp.get("first_revenue_path") or {}
    if isinstance(frp, dict) and frp.get("first_price_point"):
        try:
            raw = str(frp["first_price_point"]).replace("€", "").replace("$", "").replace("/mo", "").strip()
            return int(float(raw.split()[0]))
        except (ValueError, IndexError):
            pass

    # Fallback: derive from WTP score and geography
    wtp = opp.get("willingness_to_pay", 5)
    geo = opp.get("geography", "global")
    geo_multiplier = {"venezuela": 0.3, "latam": 0.6, "colombia": 0.7, "mexico": 0.7, "spain": 1.2, "global": 1.0}
    base = max(9, int(wtp * 8 * geo_multiplier.get(geo, 1.0)))
    # Round to nearest "clean" price
    for clean in [9, 19, 29, 49, 79, 99, 149, 199]:
        if base <= clean:
            return clean
    return 199


# ─── Main runner ─────────────────────────────────────────────────────────────

def run_validation(opp: dict, mode: str = "auto") -> dict:
    """
    Build a validation package for an opportunity.

    Args:
        opp: opportunity dict from pipeline or storage
        mode: "auto" (sections 1-7) or "full" (sections 1-8)

    Returns:
        dict with:
          Schema fields: stage, validation_status, validation_start_date, validation_deadline
          Helper fields (_-prefixed): _validation_markdown, _validation_queries,
                                      _opp_id, _opp_name, _mode
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")

    sections = [
        _render_section_1_thesis(opp),
        _render_section_2_customer(opp),
        _render_section_3_interviews(opp),
        _render_section_4_assumptions(opp),
        _render_section_5_pricing(opp),
        _render_section_6_landing_page(opp),
        _render_section_7_outreach(opp),
    ]
    if mode == "full":
        sections.append(_render_section_8_mvp(opp))

    header = (
        f"# Validation Package: {opp.get('name', 'Unknown')}\n\n"
        f"**Generated:** {today} | **Mode:** {mode.upper()} | "
        f"**Score:** {opp.get('final_score', 0):.2f} | "
        f"**Deadline:** {deadline}\n\n---\n"
    )
    markdown = header + "\n".join(sections)

    return {
        # Schema fields (merged back by daily_run.py, filtering out _ keys)
        "stage": "validation",
        "validation_status": "in_progress",
        "validation_start_date": today,
        "validation_deadline": deadline,
        # Helper fields (stripped by _ filter in daily_run.py)
        "_validation_markdown": markdown,
        "_validation_queries": build_validation_queries(opp),
        "_opp_id": str(opp.get("id", "")),
        "_opp_name": str(opp.get("name", "")),
        "_mode": mode,
    }


# ─── Convenience helpers ──────────────────────────────────────────────────────

def is_validation_complete(opp: dict) -> bool:
    """Return True if validation has passed or failed (not in_progress or None)."""
    return opp.get("validation_status") in ("passed", "failed")


def validation_status_label(status: Optional[str]) -> str:
    """Human-readable validation status label."""
    return {
        "in_progress": "🔄 In Progress",
        "passed": "✅ Passed",
        "failed": "❌ Failed",
        None: "⬜ Not Started",
    }.get(status, "⬜ Not Started")
```

**Step 2: Run tests to verify they pass**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run pytest tests/test_validation_engine.py -v
```
Expected: All tests PASS

**Step 3: Commit**
```bash
git add src/opportunity_os/validation_engine.py
git commit -m "feat(validation-os): implement validation_engine — 8-section template-driven package builder"
```

---

## Task 4: Add Deep Dives support to notion_sync.py

**Files:**
- Modify: `src/opportunity_os/notion_sync.py`

**Step 1: Add Deep Dives constants and property builder**

After the existing `DAILY_FEED_COLLECTION_ID` constant, add:

```python
DEEP_DIVES_PAGE_ID = "0bcd4caa79aa43a9b39f2d2dc059d8ff"       # Deep Dives database page
DEEP_DIVES_COLLECTION_ID = "e8079401-811e-4e9b-a43a-234bc03cce7b"  # Deep Dives collection
```

Then add a new function after `build_scout_row_properties()`:

```python
def build_validation_properties(opp: dict, package: dict) -> dict:
    """
    Build Notion page properties for one Deep Dives validation entry.

    opp: the opportunity dict
    package: the dict returned by validation_engine.run_validation()
    """
    return {
        "Name": {"title": [{"text": {"content": _safe_str(opp.get("name") or "", 100)}}]},
        "Opportunity ID": {"rich_text": [{"text": {"content": _safe_str(opp.get("id") or "")}}]},
        "Score At Validation": {"number": round(float(opp.get("final_score") or 0), 4)},
        "Validation Date": {"date": {"start": package.get("validation_start_date", "")}},
        "Auto Triggered": {"checkbox": package.get("_mode", "auto") == "auto"},
        "Decision": {"select": {"name": "Validate"}},
        "Geography": {"select": {"name": opp.get("geography") or "global"}},
        "Vertical": {"rich_text": [{"text": {"content": _safe_str(opp.get("vertical") or "")}}]},
        "Deadline": {"date": {"start": package.get("validation_deadline", "")}},
    }
```

**Step 2: Extend build_sync_payload() to include validation_packages**

In `build_sync_payload()`, add an optional `validation_packages` parameter and include it in the returned dict:

```python
def build_sync_payload(
    opportunities: list,
    run_stats: dict,
    date: str,
    validation_packages: list = None,  # NEW: list of (opp, package) tuples
) -> dict:
    ...
    # After building upsert_opps and scout_row, add:
    validated_opps = []
    if validation_packages:
        for opp, package in validation_packages:
            validated_opps.append({
                "parent": {"database_id": DEEP_DIVES_PAGE_ID},
                "properties": build_validation_properties(opp, package),
                "_opp_id": str(opp.get("id") or ""),
                "_opp_name": str(opp.get("name") or ""),
            })

    return {
        ...existing keys...,
        "validation_packages": validated_opps,  # NEW key
    }
```

**Step 3: Verify**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -c "
from opportunity_os.notion_sync import DEEP_DIVES_PAGE_ID, build_validation_properties
from opportunity_os.validation_engine import run_validation
opp = {'id': 't01', 'name': 'Test', 'final_score': 7.5, 'geography': 'venezuela', 'vertical': 'fintech'}
pkg = run_validation(opp)
props = build_validation_properties(opp, pkg)
print('OK — keys:', list(props.keys()))
"
```
Expected: `OK — keys: ['Name', 'Opportunity ID', 'Score At Validation', ...]`

**Step 4: Commit**
```bash
git add src/opportunity_os/notion_sync.py
git commit -m "feat(validation-os): add Deep Dives constants + build_validation_properties to notion_sync"
```

---

## Task 5: Create validation_run.py (manual pipeline)

**Files:**
- Create: `src/opportunity_os/pipelines/validation_run.py`

**Step 1: Write the module**

```python
"""
Validation Run — manual pipeline for `opp-os validate <opp-id>`.

Loads an opportunity by ID, runs the full 8-section validation package,
writes the markdown file, and builds a Notion sync payload.
"""
import json
import os
from datetime import datetime, timezone


def run_validation_pipeline(opp_id: str, dry_run: bool = False) -> dict:
    """
    Run full validation package for one opportunity.

    Returns dict with:
      path: str (path to written markdown file)
      notion_sync_path: str (path to written JSON sync file)
      opp_name: str
      error: str (only if failed)
    """
    from opportunity_os.storage import get_opportunity_by_id
    from opportunity_os.validation_engine import run_validation
    from opportunity_os.notion_sync import build_sync_payload
    from opportunity_os.reports import ensure_report_dirs, _get_project_root

    # Load opportunity
    opp = get_opportunity_by_id(opp_id)
    if opp is None:
        return {"error": f"Opportunity '{opp_id}' not found in opportunities.jsonl"}

    if opp.get("kill_decision"):
        return {"error": f"Opportunity '{opp_id}' is killed — cannot run validation."}

    # Run validation (full mode = all 8 sections)
    package = run_validation(opp, mode="full")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    root = _get_project_root()

    if dry_run:
        print(f"[DRY RUN] Would write validation for: {opp.get('name')}")
        print(f"[DRY RUN] Markdown preview (first 400 chars):")
        print(package["_validation_markdown"][:400])
        return {
            "path": "(dry-run)",
            "notion_sync_path": "(dry-run)",
            "opp_name": opp.get("name", ""),
        }

    # Ensure output directory exists
    ensure_report_dirs()
    val_dir = os.path.join(root, "reports", "validation")

    # Write markdown file
    safe_id = str(opp_id).replace("/", "-").replace("\\", "-")[:40]
    md_path = os.path.join(val_dir, f"{date}-{safe_id}-validation.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(package["_validation_markdown"])

    # Build Notion sync payload
    sync_payload = build_sync_payload(
        opportunities=[],
        run_stats={"signals_total": 0, "new_opps": 0, "killed": 0, "top_score": 0,
                   "score_range": "N/A", "by_geo": {}, "top_opportunity": opp.get("name", ""), "notes": "Manual validation run"},
        date=date,
        validation_packages=[(opp, package)],
    )
    sync_path = os.path.join(root, "reports", "daily", f"{date}-validation-sync.json")
    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(sync_payload, f, indent=2, default=str)

    # Update opp stage in storage
    from opportunity_os.storage import update_opportunity
    update_opportunity(opp_id, {
        "stage": "validation",
        "validation_status": "in_progress",
        "validation_start_date": package["validation_start_date"],
        "validation_deadline": package["validation_deadline"],
    })

    return {
        "path": md_path,
        "notion_sync_path": sync_path,
        "opp_name": opp.get("name", ""),
    }
```

**Step 2: Check storage.py for update_opportunity function**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
grep -n "def update_opportunity" src/opportunity_os/storage.py
```

If `update_opportunity` does not exist, add it to `storage.py`:
```python
def update_opportunity(opp_id: str, updates: dict, path: str = None) -> bool:
    """Update fields on a single opportunity by ID. Returns True if found and updated."""
    all_opps = list(read_all_opportunities(path))
    found = False
    for opp in all_opps:
        if opp.get("id") == opp_id:
            opp.update(updates)
            found = True
            break
    if found:
        _write_all_opportunities(all_opps, path)
    return found
```

(Check if `_write_all_opportunities` exists too — if not, look for the pattern used in daily_run.py Step 12 and replicate.)

**Step 3: Commit**
```bash
git add src/opportunity_os/pipelines/validation_run.py src/opportunity_os/storage.py
git commit -m "feat(validation-os): add validation_run pipeline + update_opportunity to storage"
```

---

## Task 6: Wire Step 14 into daily_run.py

**Files:**
- Modify: `src/opportunity_os/pipelines/daily_run.py`

**Step 1: Add Step 14 after line 224 (end of Step 13 block)**

Find the Step 13 closing `except` and insert immediately after:

```python
    # ─── Step 14: Auto-validation for high-scoring scout opps ───
    print("Step 14: Auto-validating high-scoring scouts...")
    try:
        from opportunity_os.validation_engine import run_validation, AUTO_VALIDATION_THRESHOLD
        import yaml

        # Read threshold from config (fallback to module default)
        config_path = os.path.join(_get_project_root(), "config", "scoring_weights.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            threshold = cfg.get("thresholds", {}).get("auto_validation", AUTO_VALIDATION_THRESHOLD)
        except Exception:
            threshold = AUTO_VALIDATION_THRESHOLD

        validation_candidates = [
            o for o in all_opps_sorted
            if float(o.get("final_score", 0)) >= threshold
            and not o.get("kill_decision")
            and o.get("stage") == "scout"
        ]

        validation_packages_for_sync = []
        for opp in validation_candidates:
            package = run_validation(opp, mode="auto")
            # Merge schema fields back (strips _ keys)
            opp.update({k: v for k, v in package.items() if not k.startswith("_")})

            if not dry_run:
                ensure_report_dirs()
                safe_id = str(opp.get("id", "unknown"))[:40]
                md_path = os.path.join(
                    _get_project_root(), "reports", "validation",
                    f"{date}-{safe_id}-validation.md"
                )
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(package["_validation_markdown"])

            validation_packages_for_sync.append((opp, package))
            print(f"  Validated: {opp.get('name', 'unknown')} (score {opp.get('final_score', 0):.2f})")

        if validation_candidates:
            print(f"  {len(validation_candidates)} opp(s) promoted to validation stage")
        else:
            print(f"  No scouts above threshold {threshold} — no auto-validation triggered")

        # Pass to Step 13 payload if it wasn't already written
        # Store on context for summary
        context["validation_count"] = len(validation_candidates)

    except ImportError as e:
        print(f"WARNING  validation_engine not available: {e}")
    except Exception as e:
        print(f"WARNING  Step 14 error (non-blocking): {e}")
```

**Step 2: Update the Step 13 build_sync_payload call to include validation_packages**

In Step 13, find the `build_sync_payload(...)` call and update it:
```python
sync_payload = build_sync_payload(
    all_opps_sorted[:20],
    run_stats,
    date,
    validation_packages=validation_packages_for_sync if 'validation_packages_for_sync' in dir() else [],
)
```
Note: Step 14 runs after Step 13, so this requires moving validation collection to before Step 13, or writing a second sync file. Simplest fix: move the Step 14 validation candidate collection to a pre-Step 13 block, and pass `validation_packages_for_sync` into Step 13's `build_sync_payload` call. See implementation details — the executor should use judgment here based on actual variable scope in the file.

**Step 3: Test the full pipeline**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -m opportunity_os.main daily 2>&1 | grep -E "Step 14|Validated|validation"
```
Expected output (with current data — 3 VE opps already at validation stage, not scout):
```
Step 14: Auto-validating high-scoring scouts...
  No scouts above threshold 7.0 — no auto-validation triggered
```
(The 3 VE opps are already `stage: "validation"` so the guard correctly skips them.)

**Step 4: Test with a forced scout opp (optional dry-run check)**

```bash
PYTHONPATH=src uv run python -c "
from opportunity_os.validation_engine import run_validation
opp = {'id': 'test', 'name': 'Test', 'final_score': 7.5, 'stage': 'scout',
       'kill_decision': False, 'geography': 'venezuela', 'vertical': 'fintech',
       'target_customer': 'VE merchants', 'problem_statement': 'Manual USDT tracking'}
pkg = run_validation(opp, mode='auto')
print('Sections:', pkg['_validation_markdown'].count('\n## '))
print('First 200 chars:', pkg['_validation_markdown'][:200])
"
```
Expected: `Sections: 7`

**Step 5: Commit**
```bash
git add src/opportunity_os/pipelines/daily_run.py
git commit -m "feat(validation-os): add Step 14 auto-validation to daily pipeline"
```

---

## Task 7: Add `validate` CLI command to main.py

**Files:**
- Modify: `src/opportunity_os/main.py`

**Step 1: Add the command following the deep-dive pattern**

Find the `deep_dive` command in `main.py` and add `validate` immediately after it:

```python
@cli.command()
@click.argument("opp_id")
@click.option("--dry-run", is_flag=True, help="Preview output without writing files")
def validate(opp_id, dry_run):
    """Run full 8-section validation package on a specific opportunity ID."""
    from opportunity_os.pipelines.validation_run import run_validation_pipeline

    result = run_validation_pipeline(opp_id=opp_id, dry_run=dry_run)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        import sys
        sys.exit(1)
    click.echo(f"Validation complete: {result['opp_name']}")
    click.echo(f"  Report: {result['path']}")
    click.echo(f"  Notion sync: {result['notion_sync_path']}")
```

**Step 2: Verify the command is registered**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -m opportunity_os.main --help
```
Expected: `validate` appears in the command list.

**Step 3: Test with an existing opp ID**

Get a real opp ID from the JSONL:
```bash
PYTHONPATH=src uv run python -c "
import json
with open('data/opportunities/opportunities.jsonl') as f:
    opps = [json.loads(l) for l in f if l.strip()]
print(opps[0]['id'], opps[0]['name'], opps[0]['stage'])
"
```
Then run:
```bash
PYTHONPATH=src uv run python -m opportunity_os.main validate <OPP_ID> --dry-run
```
Expected: Preview output without file writes.

**Step 4: Commit**
```bash
git add src/opportunity_os/main.py
git commit -m "feat(validation-os): add opp-os validate CLI command"
```

---

## Task 8: Update validation-runner SKILL.md

**Files:**
- Modify: `.claude/skills/validation-runner/SKILL.md`

**Step 1: Add reference to validation_engine.py at the top**

Add a note at the start of the skill:

```markdown
> **Engineering note:** The template scaffolding for all 8 sections is implemented in
> `src/opportunity_os/validation_engine.py`. Run `opp-os validate <opp-id>` to generate
> a package automatically. This skill is for agent-driven enrichment on top of that output.
```

**Step 2: Add Section 8 (MVP Scope) as Step 7**

Add the new step to the skill's workflow list matching the pattern of the other 6 steps.

**Step 3: Commit**
```bash
git add .claude/skills/validation-runner/SKILL.md
git commit -m "docs(validation-os): update validation-runner skill to reference validation_engine.py"
```

---

## Task 9: End-to-end integration test

**Step 1: Run full daily pipeline**

```bash
cd "C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"
PYTHONPATH=src uv run python -m opportunity_os.main daily 2>&1
```
Expected: All 14 steps complete. Steps 13 + 14 print without errors.

**Step 2: Run validate on a scout-stage opp**

Pick an opp with `stage: "scout"` and `final_score >= 7.0` (rows 13-14 in opportunities.jsonl should qualify):
```bash
PYTHONPATH=src uv run python -m opportunity_os.main validate opp_20260402_XXX
```
Expected: Markdown file written to `reports/validation/`, Notion sync JSON written.

**Step 3: Check reports/validation/ contains the markdown**

```bash
ls reports/validation/
```
Expected: One or more `*.md` files.

**Step 4: Run all tests**

```bash
PYTHONPATH=src uv run pytest tests/ -v
```
Expected: All tests pass.

**Step 5: Final commit**
```bash
git add .
git commit -m "feat(validation-os): complete integration — auto + manual validation pipeline live"
```
