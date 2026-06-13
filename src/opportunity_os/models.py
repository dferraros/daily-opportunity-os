"""Opportunity data models — v2 Phase 6 cleanup.
Removed 15 deprecated fields, added score_history + tam_formula + tam_confidence + venezuela_lens_applied."""

from __future__ import annotations
from typing import Dict, List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, computed_field
import uuid


# ─── Sub-models ──────────────────────────────────────────────────────────────

class DistributionProfile(BaseModel):
    """How the business reaches its customers — especially important for LATAM/VE."""
    top_channels: List[str] = Field(default_factory=list, max_length=3)
    estimated_cac_logic: Optional[str] = None  # e.g. "WhatsApp cold ~$2 CPL"
    organic_viable: Optional[bool] = None
    paid_viable: Optional[bool] = None
    partnership_angle: Optional[str] = None
    founder_led_growth_angle: Optional[str] = None
    content_angle: Optional[str] = None
    referral_angle: Optional[str] = None
    local_trust_mechanism: Optional[str] = None  # critical for LATAM/VE


class TrustProfile(BaseModel):
    """Trust friction score — higher = more friction. Critical for LATAM/VE markets."""
    trust_barrier_to_adoption: Optional[int] = Field(None, ge=1, le=10)
    brand_credibility_needed: Optional[int] = Field(None, ge=1, le=10)
    local_presence_required: Optional[bool] = None
    payment_friction: Optional[int] = Field(None, ge=1, le=10)
    fraud_risk: Optional[int] = Field(None, ge=1, le=10)
    onboarding_friction: Optional[int] = Field(None, ge=1, le=10)

    @computed_field
    @property
    def trust_score(self) -> Optional[float]:
        """Average of available dimensions. Lower = better (less friction)."""
        vals = [v for v in [
            self.trust_barrier_to_adoption, self.brand_credibility_needed,
            self.payment_friction, self.fraud_risk, self.onboarding_friction
        ] if v is not None]
        return round(sum(vals) / len(vals), 1) if vals else None


class FirstRevenuePath(BaseModel):
    """The bridge from intelligence to first cash. The most underweighted field."""
    first_customer_type: Optional[str] = None   # e.g. "Venezuelan SMB owner, retail"
    first_offer: Optional[str] = None            # e.g. "Done-for-you WhatsApp catalog, $50/mo"
    first_sales_channel: Optional[str] = None    # e.g. "Cold outreach via WhatsApp"
    first_price_point: Optional[str] = None      # e.g. "$30-50/mo, anchored to 1 employee saved"
    first_proof_point_needed: Optional[str] = None  # e.g. "3 paying customers in 30 days"


class WhyNowVenezuela(BaseModel):
    """5-question framework for Venezuela-specific timing. Required when geography=venezuela."""
    local_friction: Optional[str] = None          # What specific friction exists locally?
    friction_persistence: Optional[str] = None    # Why has this friction persisted?
    who_suffers_most: Optional[str] = None        # Exact segment with acute pain
    recent_change: Optional[str] = None           # What changed recently making this possible now?
    regional_export_potential: Optional[str] = None  # Can this become a LATAM export?


class DecisionFilterResults(BaseModel):
    """Three final gates before build recommendation. 2+ fail → cap score at 5.0."""
    can_sell_fast: Optional[bool] = None     # reach buyer + real interest in < 2 weeks?
    can_build_lean: Optional[bool] = None    # MVP < $2K, < 2 people, < 6 weeks?
    can_compound: Optional[bool] = None      # software, data, network effects, or repeatable dist?

    @computed_field
    @property
    def failures(self) -> int:
        """Count of failed (False) filters. 2+ = cap attractiveness_score."""
        return sum(1 for v in [self.can_sell_fast, self.can_build_lean, self.can_compound]
                   if v is False)

    @computed_field
    @property
    def should_cap_score(self) -> bool:
        return self.failures >= 2


# ─── Main Opportunity Model ───────────────────────────────────────────────────

class Opportunity(BaseModel):
    """
    Opportunity record. Every field serves a decision-making purpose.

    Schema groups:
    - Identity (4): id, name, first_seen, last_updated
    - Geography (4): geography, country, region, portfolio_lane
    - Classification (3): vertical, subvertical, bucket
    - Problem (4): target_customer, problem_statement, trigger_signal, why_now
    - Evidence (3): source_links, evidence_summary, demand_signals
    - Market (7): monetization_model, pricing_benchmark, direct_competitors, indirect_competitors,
                  substitutes, benchmark_companies, market_structure_note
    - Customer (4): customer_pain_level, willingness_to_pay, urgency_of_need, frequency_of_need
    - Complexity (5): regulatory_complexity, technical_complexity, operational_complexity,
                      ai_leverage_potential, distribution_advantage_potential
    - TAM (6): tam, sam, som, tam_method, tam_formula, tam_confidence
    - Assumptions (3): assumptions, risks, kill_reasons
    - Scoring (6): confidence_score, evidence_quality_score, attractiveness_score, execution_difficulty, final_score, decision_filter_results
    - Kill Gate (2): kill_criteria_passed, kill_decision
    - Paths (3): path_to_first_revenue, path_to_1m_arr, path_to_10m_arr
    - Pipeline (3): stage, validation_status, validation_notes
    - Venezuela (2): venezuela_wedge_category, venezuela_lens_applied
    - Action (2): recommendation, next_action
    - Score History (1): score_history
    - Data-Backed Scoring Signals (4): job_posting_count, competitor_negative_review_rate,
                                       news_signal_count, competitor_pricing_data
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    id: str = Field(default_factory=lambda: f"opp_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}")
    name: str
    first_seen: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # ── Geography ────────────────────────────────────────────────────────────
    geography: Literal["global", "latam", "venezuela", "spain", "us", "other"]
    country: Optional[str] = None
    region: Optional[str] = None
    portfolio_lane: Optional[Literal["now", "soon", "strategic", "no"]] = None

    # ── Classification ───────────────────────────────────────────────────────
    vertical: str
    subvertical: Optional[str] = None
    bucket: Optional[Literal["fast_cash", "venture_scale", "latam_asymmetry"]] = None

    # ── Problem ──────────────────────────────────────────────────────────────
    target_customer: str
    problem_statement: str
    trigger_signal: str
    why_now: Optional[str] = None

    # ── Evidence ─────────────────────────────────────────────────────────────
    source_links: List[str] = Field(default_factory=list)
    evidence_summary: str = ""
    demand_signals: List[str] = Field(default_factory=list)

    # ── Market ───────────────────────────────────────────────────────────────
    monetization_model: Optional[str] = None
    pricing_benchmark: Optional[str] = None
    direct_competitors: List[str] = Field(default_factory=list)
    indirect_competitors: List[str] = Field(default_factory=list)
    substitutes: List[str] = Field(default_factory=list)
    benchmark_companies: List[str] = Field(default_factory=list)
    market_structure_note: Optional[str] = None

    # ── Customer ─────────────────────────────────────────────────────────────
    customer_pain_level: Optional[int] = Field(None, ge=1, le=10)
    willingness_to_pay: Optional[int] = Field(None, ge=1, le=10)
    urgency_of_need: Optional[int] = Field(None, ge=1, le=10)
    frequency_of_need: Optional[int] = Field(None, ge=1, le=10)

    # ── Complexity ───────────────────────────────────────────────────────────
    regulatory_complexity: Optional[int] = Field(None, ge=1, le=10)
    technical_complexity: Optional[int] = Field(None, ge=1, le=10)
    operational_complexity: Optional[int] = Field(None, ge=1, le=10)
    ai_leverage_potential: Optional[int] = Field(None, ge=1, le=10)
    distribution_advantage_potential: Optional[int] = Field(None, ge=1, le=10)

    # ── Scoring Dimensions (used by scoring_engine) ───────────────────────────
    pain_severity: Optional[int] = Field(None, ge=1, le=10)
    market_size: Optional[int] = Field(None, ge=1, le=10)
    timing_tailwind: Optional[int] = Field(None, ge=1, le=10)
    monetization_clarity: Optional[int] = Field(None, ge=1, le=10)
    speed_to_mvp: Optional[int] = Field(None, ge=1, le=10)
    capital_efficiency: Optional[int] = Field(None, ge=1, le=10)
    distribution_accessibility: Optional[int] = Field(None, ge=1, le=10)
    competition_intensity: Optional[int] = Field(None, ge=1, le=10)
    defensibility: Optional[int] = Field(None, ge=1, le=10)
    regional_fit: Optional[int] = Field(None, ge=1, le=10)
    founder_fit: Optional[int] = Field(None, ge=1, le=10)
    ai_leverage: Optional[int] = Field(None, ge=1, le=10)
    operational_simplicity: Optional[int] = Field(None, ge=1, le=10)
    regulatory_simplicity: Optional[int] = Field(None, ge=1, le=10)
    revenue_speed_score: Optional[int] = Field(None, ge=1, le=10)  # numeric 1-10: how fast first revenue arrives

    # ── AI Scorer Metadata ────────────────────────────────────────────────────
    ai_scored_at: Optional[str] = None           # ISO date, e.g. "2026-04-02"
    ai_scorer_version: Optional[str] = None      # model ID used for scoring

    # ── Scoring Dimension Reasons (populated by ai_scorer.py) ─────────────────
    pain_severity_reason: Optional[str] = None
    market_size_reason: Optional[str] = None
    timing_tailwind_reason: Optional[str] = None
    willingness_to_pay_reason: Optional[str] = None
    monetization_clarity_reason: Optional[str] = None
    speed_to_mvp_reason: Optional[str] = None
    capital_efficiency_reason: Optional[str] = None
    distribution_accessibility_reason: Optional[str] = None
    competition_intensity_reason: Optional[str] = None
    defensibility_reason: Optional[str] = None
    regional_fit_reason: Optional[str] = None
    founder_fit_reason: Optional[str] = None
    ai_leverage_reason: Optional[str] = None
    operational_simplicity_reason: Optional[str] = None
    regulatory_simplicity_reason: Optional[str] = None
    path_to_first_revenue_reason: Optional[str] = None
    revenue_speed_score_reason: Optional[str] = None

    # ── TAM ──────────────────────────────────────────────────────────────────
    tam: Optional[float] = None   # Total Addressable Market in USD (raw float)
    sam: Optional[float] = None   # Serviceable Addressable Market
    som: Optional[float] = None   # Serviceable Obtainable Market (Year 3 target)
    tam_display: Optional[str] = None        # tam_engine: human-readable, e.g. "$80.0M"
    tam_usd_estimate: Optional[float] = None # tam_engine: alias kept for backward compat
    sam_usd: Optional[float] = None          # tam_engine output alias
    som_usd: Optional[float] = None          # tam_engine output alias
    tam_method: Optional[Literal["bottom_up", "top_down", "proxy", "competitor_revenue"]] = None
    tam_formula: Optional[str] = None        # explicit formula with numbers
    tam_assumptions: List[str] = Field(default_factory=list)
    tam_notes: List[str] = Field(default_factory=list)  # tam_engine supplementary notes
    tam_confidence: Optional[Literal["high", "medium", "low"]] = None

    # ── Risk ─────────────────────────────────────────────────────────────────
    assumptions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    kill_reasons: List[str] = Field(default_factory=list)

    # ── Scoring ──────────────────────────────────────────────────────────────
    confidence_score: Optional[float] = Field(None, ge=0, le=10)
    evidence_quality_score: Optional[float] = Field(None, ge=0, le=10)
    attractiveness_score: Optional[float] = Field(None, ge=0, le=10)
    executability_score: Optional[float] = Field(None, ge=0, le=10)    # scoring_engine Layer 2
    strategic_value_score: Optional[float] = Field(None, ge=0, le=10)  # scoring_engine Layer 3
    execution_difficulty: Optional[float] = Field(None, ge=1, le=10)
    capital_intensity: Optional[float] = Field(None, ge=1, le=10)
    time_to_mvp: Optional[str] = None
    final_score: Optional[float] = Field(None, ge=0, le=10)  # composite after modifiers + caps
    raw_final_score: Optional[float] = Field(None, ge=0, le=10)  # pre-normalization score backup
    decision_filter_results: Optional[DecisionFilterResults] = None  # gates before build rec
    daniels_wedge_score: Optional[float] = Field(None, ge=0, le=10)  # daily_run._enrich_fields

    # ── Kill Gate ────────────────────────────────────────────────────────────
    kill_criteria_passed: Optional[int] = Field(None, ge=0, le=7)
    kill_decision: bool = False  # True = killed before scoring

    # ── Revenue Paths ────────────────────────────────────────────────────────
    path_to_first_revenue: Optional[str] = None
    path_to_1m_arr: Optional[str] = None
    path_to_10m_arr: Optional[str] = None

    # ── Pipeline Stage ───────────────────────────────────────────────────────
    stage: Literal["scout", "validation", "validated", "killed"] = "scout"
    source: Optional[str] = None             # normalization.fill_defaults: "manual", "web", etc.
    validation_status: Optional[Literal["pending", "in_progress", "passed", "failed"]] = None
    validation_notes: Optional[str] = None

    # ── Venezuela-Specific ───────────────────────────────────────────────────
    venezuela_wedge_category: Optional[str] = None
    venezuela_lens_applied: bool = False
    venezuela_wedge_match: Optional[bool] = None     # geo_lens: True if wedge category matched
    wtp_pricing_estimate: Optional[float] = None     # geo_lens: WTP × regional multiplier
    payment_rail_context: Optional[Dict] = None      # geo_lens: {primary_rail, secondary_rail, ...}

    # ── Action ───────────────────────────────────────────────────────────────
    recommendation: Optional[Literal["build", "test", "deep_dive", "watch", "ignore"]] = None
    next_action: Optional[str] = None
    liked_at: Optional[str] = None  # ISO timestamp; set by `opp-os like` (conviction flag)

    # ── Score History ─────────────────────────────────────────────────────────
    score_history: Optional[List[Dict]] = None  # append-only: [{date, score, delta}]

    # ── Data-Backed Scoring Signals (P3a) ────────────────────────────────────
    job_posting_count: Optional[int] = None              # LinkedIn job postings for vertical+geo
    competitor_negative_review_rate: Optional[float] = None  # G2 neg review rate (0.0–1.0)
    news_signal_count: Optional[int] = None              # Tavily news hits last 30 days
    competitor_pricing_data: Optional[List[Dict]] = None  # list[dict] from Firecrawl schema extraction

    # ── Research / Enrichment ─────────────────────────────────────────────────
    kill_reason: Optional[str] = None
    benchmark_archetype: Optional[str] = None
    research_executed_at: Optional[str] = None
    free_research_at: Optional[str] = None
    pain_researched_at: Optional[str] = None          # enrichment step 10 skip guard (30d TTL)
    distribution_researched_at: Optional[str] = None  # enrichment step 11 skip guard (30d TTL)
    apify_researched_at: Optional[str] = None         # enrichment step 11.7 skip guard (14d TTL)
    pain_validation_score: Optional[float] = Field(None, ge=0, le=10)
    exact_customer_phrases: List[str] = Field(default_factory=list)
    pain_evidence_sources: List[str] = Field(default_factory=list)
    workarounds_found: List[str] = Field(default_factory=list)
    distribution_validated: Optional[bool] = None
    top_distribution_channels: List[str] = Field(default_factory=list)
    estimated_cac_logic: Optional[str] = None
    first_10_customer_path: Optional[str] = None
    trust_mechanism_latam: Optional[str] = None

    # ── Pipeline-written fields (declared retroactively, 2026-06-10 audit) ────
    # These were being written to the JSONL by pipeline steps without a model
    # declaration. Pydantic's default extra='ignore' silently DROPS undeclared
    # fields on any dict -> Opportunity -> dict round-trip, so every field the
    # pipeline writes must be declared here.
    market_momentum_score: Optional[float] = None      # derived: job_posting_count -> 0-10 (scoring_engine)
    competitor_weakness_score: Optional[float] = None  # derived: neg_review_rate -> 0-10 (scoring_engine)
    pain_signal_count: Optional[int] = None            # free_research: forum/Reddit pain mentions
    distribution_quality: Optional[float] = None       # derived from distribution_validated (scoring_engine)
    thesis_fit_score: Optional[int] = None             # weekly review: fit vs investment thesis
    willingness_to_pay_raw: Optional[float] = None     # pre-geo-lens WTP (geo_lens keeps original here)
    benchmark_fit_score: Optional[float] = None        # benchmark_engine: archetype match strength
    benchmark_archetype_description: Optional[str] = None  # benchmark_engine: archetype summary
    analog_benchmarks: Optional[List] = None           # benchmark_engine: comparable companies
    sam_usd_estimate: Optional[float] = None           # tam_engine: serviceable addressable market
    som_usd_estimate: Optional[float] = None           # tam_engine: serviceable obtainable market
    tam_rationale: Optional[str] = None                # tam_engine: estimation method note
    whitespace: Optional[Dict] = None                  # deep_dive: competitor gap analysis
    deep_dive_status: Optional[str] = None             # deep_dive pipeline marker
    kill_date: Optional[str] = None                    # ISO date the kill gate fired
    pain_validated_date: Optional[str] = None          # validation pipeline: pain confirmed
    distribution_validated_date: Optional[str] = None  # validation pipeline: channel confirmed
    validation_start_date: Optional[str] = None        # validation pipeline: window start
    validation_deadline: Optional[str] = None          # validation pipeline: window end
    scoring_incomplete: Optional[bool] = None          # True = 0.0 means UNSCORED, not killed

    # ── Conviction Bridge (build command) ───────────────────────────────────
    kickoff_at: Optional[str] = None                   # ISO timestamp: build command invoked
    build_mode: Optional[str] = None                   # "validate" | "build" — determines what files written
    outcome: Optional[str] = None                      # "validated" | "killed" | "shipped" | "revenue"
    outcome_note: Optional[str] = None                 # outcome reason/context
    outcome_at: Optional[str] = None                   # ISO timestamp: outcome recorded

    # ── Evidence coverage (scoring_engine, 2026-06-12 calibration) ───────────
    evidence_coverage: Optional[float] = None          # fraction of collectable evidence actually collected
    low_evidence_flag: Optional[bool] = None           # True = high score (>=7.5) resting on guesswork

    # ── Kill-thesis adversarial pass (Wave 2.1, 2026-06-12) ──────────────────
    kill_thesis: Optional[str] = None                  # strongest argument the opportunity fails
    kill_thesis_strength: Optional[int] = None         # 1-10; >= 7 caps final_score at 5.0
    kill_thesis_evidence: Optional[List] = None        # short cites from inverted searches
    kill_thesis_at: Optional[str] = None               # ISO timestamp: adversarial pass ran

    def to_jsonl(self) -> str:
        """Serialize to JSONL-compatible JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_jsonl(cls, line: str) -> "Opportunity":
        """Deserialize from JSONL line."""
        import json
        return cls.model_validate(json.loads(line))

    @classmethod
    def empty(cls, name: str = "placeholder", geography: str = "global",
              vertical: str = "unknown", target_customer: str = "TBD",
              problem_statement: str = "TBD", trigger_signal: str = "TBD") -> "Opportunity":
        """Create a minimal valid opportunity for testing."""
        return cls(
            name=name, geography=geography, vertical=vertical,
            target_customer=target_customer, problem_statement=problem_statement,
            trigger_signal=trigger_signal,
        )


class PainLibraryEntry(BaseModel):
    """Recurring pain point — opportunities map back to these clusters."""
    pain_id: str
    category: str
    description: str
    geographies: List[str] = Field(default_factory=list)
    affected_segments: List[str] = Field(default_factory=list)
    severity: int = Field(ge=1, le=10)
    frequency: Literal["hourly", "daily", "weekly", "monthly", "occasional"]
    current_workarounds: List[str] = Field(default_factory=list)
    evidence_links: List[str] = Field(default_factory=list)
    opportunities_mapped: List[str] = Field(default_factory=list)


class PersonEntry(BaseModel):
    """People pipeline — execution capacity for opportunities."""
    person_id: str = Field(default_factory=lambda: f"per_{str(uuid.uuid4())[:8]}")
    name: str
    role_type: Literal[
        "operator", "engineer", "designer", "local_partner",
        "distribution_partner", "domain_expert", "cofounder", "advisor"
    ]
    geography: Optional[str] = None
    domain_expertise: List[str] = Field(default_factory=list)
    contact_status: Literal["known", "warm", "cold", "not_yet_contacted"] = "not_yet_contacted"
    linked_opportunities: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class MachineMetrics(BaseModel):
    """Weekly/daily machine performance metrics."""
    date: str  # YYYY-MM-DD
    opportunities_found: int = 0
    opportunities_killed: int = 0
    opportunities_scored: int = 0
    opportunities_promoted_to_validation: int = 0
    opportunities_validated_pass: int = 0
    opportunities_validated_fail: int = 0
    first_customer_contacts: int = 0
    first_revenues: int = 0
    false_positives: int = 0
    top_category_this_run: Optional[str] = None
    top_geo_this_run: Optional[str] = None
    run_duration_seconds: Optional[float] = None
    signals_ingested: int = 0
    deep_dives_produced: int = 0
