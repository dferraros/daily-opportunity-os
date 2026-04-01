# Daily Opportunity OS

## Mission
Find real businesses worth building. Not interesting ideas — decisive opportunities with evidence, economics, and execution logic.

## Non-Negotiables
- Every daily run produces Global, LATAM, and Venezuela sections. No exceptions.
- Venezuela is a permanent focus, not a filter.
- Facts, assumptions, and judgment must always be separated.
- TAM, SAM, SOM, and scoring formulas must be explicit.
- Reject low-signal, generic, saturated, or low-defensibility ideas.
- Prefer fewer, stronger opportunities.
- Outputs must be operator-grade, concise, and Notion-ready.
- All key outputs saved as markdown, CSV, and JSON.

## Investment Thesis
An opportunity is worth pursuing if it matches ALL of:
1. Spanish-speaking markets first (Spain, Venezuela, Colombia, Mexico, Argentina)
2. Clear monetization path in under 90 days
3. Low regulatory drag (or regulatory arbitrage as the wedge)
4. Distribution via content, community, partnerships, or performance marketing
5. Strong fit with operator skillset: growth, CRM, lifecycle, data, product marketing

Score anything failing 2+ thesis criteria below 5.0 attractiveness_score.
Auto-reject anything failing 3+.

## Kill Gate (runs BEFORE scoring — 7 binary questions)
2+ failures = kill_decision = True. Do not score. Move to ignore list.
1. Can I explain the pain in 1 sentence?
2. Can I name a specific buyer?
3. Can I reach that buyer cheaply (CAC < 3x monthly revenue)?
4. Is there a realistic first revenue path in < 90 days?
5. Can an MVP be built in 2-6 weeks?
6. Is the market big enough if this works (TAM > $10M)?
7. Do I have a wedge (edge, timing, or distribution advantage)?

## Three Decision Filters (final gate before build recommendation)
If 2+ fail, cap attractiveness_score at 5.0 and drop recommendation to "watch":
1. Can I sell this fast? (reach buyer + get real interest in < 2 weeks)
2. Can I build this lean? (MVP < $2K, < 2 people, < 6 weeks)
3. Can this compound? (software, data, network effects, or repeatable distribution)

## Portfolio Lanes
Every opportunity belongs to exactly one lane:
- **Now**: Test in 14-30 days — fast cash, service or software-enabled
- **Soon**: Needs more proof but attractive — 60-90 day horizon
- **Strategic**: Big play, slower, high upside — 6-18 month horizon
- **No**: Rejected — reason logged, never just dropped

## Bucket Classification
Every opportunity classified as exactly one:
- **fast_cash**: Low capital, first revenue < 90 days, service or software-enabled
- **venture_scale**: TAM > $100M, fundable, slower validation
- **latam_asymmetry**: Market friction creates edge others ignore — especially Venezuela

## Geography Rules
1. Run global scan first
2. Run LATAM-specific ranking (adjust pricing, trust, payment rails)
3. Run Venezuela-specific ranking (apply Venezuela adjustments hardcoded in geo_lens.py)
4. Identify cross-border opportunities: VE/LATAM -> Spanish-speaking LATAM
5. Identify diaspora opportunities: Venezuelans abroad
Do NOT apply US pricing assumptions to LATAM or Venezuela.

## Venezuela Adjustments (auto-applied by geo_lens.py)
- WTP: 0.25x vs US baseline
- SaaS pricing: $3-15/month (not $30-99)
- Payment rails: Zelle, USDT, Binance P2P
- Distribution: WhatsApp-first, TikTok organic second
- Informal commerce: ~55% of activity is off-platform
- Trust signal: referral > brand always

## Daniel's Wedges (score opportunities against these — 6 dimensions)
An opportunity with < 2 matching wedges is flagged as "founder-fit risk":
1. Growth & GTM edge — 10+ years lifecycle, CRM, paid, organic, A/B
2. Narrative & positioning edge — can frame and sell a story fast
3. LATAM + Spanish-speaking intuition — Venezuela, Spain, Colombia patterns
4. Fintech & crypto adjacency — Bit2Me operations, payment rails
5. Speed to prototype — can build MVP-level systems fast with Claude Code
6. Distribution instincts — WhatsApp funnels, performance, community, referral

## Venezuela Structural Wedges
Map every Venezuela opportunity to one of these:
- payments_and_collections
- remittances_and_diaspora_finance
- smb_software_informal_operators
- retail_inventory_working_capital
- logistics_coordination
- commerce_trust_layers
- creator_monetization
- cross_border_service_businesses
- diaspora_finance_and_commerce
- ai_labor_replacement_tools

Wedge matches score +1.5 on regional_fit.

## Distribution-First Rule
For every opportunity, answer:
1. How does Daniel reach the first 10 customers?
2. What is the likely CAC in this geography?
3. What is the primary distribution channel?
Always include a trust-building mechanism for LATAM/VE.

## Weekly Quotas
The machine is not working if these don't ship weekly:
- 30-50 raw signals ingested
- 10 structured opportunities created
- 3 deep dives produced
- 1-2 real market validations run
- 1 build candidate promoted every 2-4 weeks

## Weekly Decision Ritual (every Friday)
Produce exactly 4 outputs — no more, no less:
1. Top 3 opportunities to move to validation
2. Top 3 opportunities to discard with logged kill reasons
3. Top 3 rising signals (score increased from last week)
4. 1 conviction area to double down on for 30 days

## Services Track
Scout these business model types in parallel with pure product:
- productized_service (repeatable scope + fixed price)
- agency_plus_software (agency that builds toward software margin)
- concierge_first (manual first, automate later)
- done_for_you (high-touch, high-margin ops)
Services often reach first revenue 3x faster than SaaS.

## Quality Standard
An opportunity is only strong if it has:
- A real, nameable problem
- Evidence of demand (not assumed)
- Clear monetization logic
- Reachable customers in this geography
- Adequate market size
- A timing tailwind
- A feasible MVP path
- Distribution clarity

## Working Style
- Use web research aggressively via native Claude Code web search
- Use subagents for scoped research (geo, TAM, competitive)
- Use skills for repeatable workflows
- Save structured outputs after every run
- Never lose research — auto-save to JSONL on SessionEnd hook
- Keep every commit atomic and meaningful
