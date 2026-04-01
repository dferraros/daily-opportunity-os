# Gemini Meeting Transcripts — Key Extracts Feb 2026

## Growth Strategy Weekly (Feb 24, 2026)
**Attendees:** Daniel Ferraro, Patri Gargallo, Diego Barreira, Pablo Campos (COO)

### Loan Journey — DECIDED
- **Priority:** Loan selected over Card (more revenue, better traceability)
- **Format:** email + push + in-app (full journey)
- **Duration:** ~1 month, review after week 1
- **Launch:** Thursday (Feb 26) — first 1 language to test
- **Target:** LC users who NEVER requested a loan + have collateral crypto (BTC, ETH, SOL, XRP) with minimum balance
- **Segmentation types:**
  1. Quick liquidity seekers (€200-300 small loans, fast need)
  2. Large investment loans (hipoteca, coche, vacaciones)
  3. Reactivation: inactive users → Loan as re-entry point (can collateralize without selling)
  4. Users with XRP in wallet (specific push: "colateralize your XRP")
  5. Users who did Loan before but haven't used new collaterals (SOL, XRP)
- **Native banner:** Loan in first view of ALL clusters
- **Incentive needed:** Not just info — fee discount or LTV milestone push if user takes first loan that month
- **Portugal angle:** Long-term holder (1yr no tax on gains) + Loan = potentially huge for PT market
- **Documentation:** "Loan Growth GTM" space in Confluence (Patri adding Diego to group)
- **Hypothesis required:** EVERY journey needs clear hypothesis upfront. All tracking must be feasible with existing events.
- **Diego creates:** Long content (emails + in-apps) + legal brief. Daniel provides segment data by 5pm today.

### Brokerage Push A/B Tests
- **Target:** Smart Holders (c6/c7) — enter app constantly = perfect test cluster
- **Approaches:** "educativos básicos" vs "educativos pro"
- **Phase 1:** Test with different links. Phase 2: change text.
- **UX concern:** Purchase page is "anti-UX" (complex commissions display, payment methods). Diego flagged this.
- **Dashboard:** Daniel speaking with Data to define A/B testing dashboard.

### Landing Tool Issue
- Leif chose a non-optimizable landing tool that was paid without consulting. Now migrating to block-based tool.
- Dani (developer/PM) confirmed new tool is standardized.

### Pro Traceability Blocker
- Pro product has no full traceability — Growth can't measure Pro tests effectively.
- Patri using this as leverage to push Product team to add traceability.
- Policy: no tests without measurement capability.

### Process Updates
- Calendar: journeys prepared during week, launched Monday (not end of week)
- Patri will define meeting process for cross-dept alignment (before Council)
- Patri removing Daniel from Pro meeting; moving Katy dashboard call to tomorrow

---

## Weekly LifeCycle (Feb 19, 2026)
**Attendees:** Daniel Ferraro, S. Rut (Salvia), Màxim Agusti Olius, Pablo Campos (joined ~11:10), Álvaro Muñoz De Dios De Paz (observer)

### Key Discussions

**Salvia — Banned Users Analysis (CleverTap):**
- Semi-automatic classification of banned users. Panel in Click (CleverTap).
- Banned users profile: tend to be <30 years old, many from Italy and Portugal.
- Volume operated by good users: ~€350 avg.
- Common pattern: low-quality referrer registers + immediately invites others = created account just for that.

**Màxim — CleverTap Panel Orientation:**
- Salvia walked Màxim through CleverTap filters (complex UX — filters hidden in dropdowns).
- Filters available: sin balance/con balance, "No válidos" etc.
- Recommended time periods for analysis: NOT just 2 weeks. Best: 1 year, 6 months, minimum 1 quarter. Currently only 12-month view exists — need 1/3/6 month filters added.

**Daniel — LC Framework Work:**
- Shared screen: working on LC framework (definitions + hoja de lifecycle).
- Key concept being developed: **"Monthly Monetizer"** — changing FM definition from "first 7 days monetizable action" to broader window.
- FM = "momento de activación económico. que real usuario" — not just first purchase, but first real economic activation.
- Data advances on panels: no advances that week (Marta was sick, Pablo Talamantes had personal issue).

**Pablo Campos (joined 11:10) + Álvaro:**
- Team still new — "no tenemos un plan de trabajo todavía como tal"
- Pablo wants organized regular LC meetings → LC roadmap + each person's topics
- Álvaro role: "me va a ayudar mucho en lo que es el multilink" — COO coordination support across 40 parallel items
- Joan + Màxim: help with research, analysis, internal search
- **Data = #1 concern** → starting "dailies de data" with David Sales every day until data situation is clear. David Sales prioritizes. Team: Marta + David Sales in the data dailies.
- Salvia has many "links" (parallel responsibilities) → Pablo working to give Salvia more availability for LC
- "Yo tengo la confianza de David Sales" for data prioritization

**Space Center:**
- Pablo's long-term vision: Space Center = lifecycle gamification (levels 1-5, integrated loyalty)
- "Nil" = original creator of Space Center, left the company
- Salvia maintained Space Center after Nil left
- Being redesigned: look & feel + internal management platform
- Álvaro question: what are the directives for changing the loyalty system?

---

## Product Business Sprint — Brokerage (Feb 24, 2026)
**Attendees:** Daniel Ferraro, Pablo Paredes, Juan Fornell

### Key Data Points
- 8,000 new users registered last week (may be monthly — unclear)
- Portugal: 160 registrations → 27 purchases (16.9% conversion rate)
- Cluster algorithm: ML algorithm run WEEKLY by Data team, based on business variables JuanF provided
- Clusters require certain user behaviors before classification (e.g., cluster 6/7 only for users with activity)

### Poly (AI Agent — Pablo Paredes)
- Built with Claude + Anthropic research + Replit
- Co-built with Jesús (DB tables description + relationships)
- Has 12 tools + table relationships + context
- Goal: single powerful agent (not multi-agent team) — cost decision
- Tables are set up but data not yet filled (API connection pending)
- Pablo studying Anthropic research docs for agent orchestration
- Name "Poly" — coincides with Polymarket but Pablo doesn't mind
- JuanF will share Monday analyses with proposals each week

---

## Review Acciones Revenue Brokerage B2C (Feb 5, 2026)
**Attendees:** Juan Fornell, Daniel Ferraro, Pablo Paredes, Pablo Campos

### Key Segments + Revenue Potential
- **Advanced Brokerage users (non-trading):** €17/user avg, 41K potential total
- **Smart Holders (c6/c7):** 8,800 users, high avg ticket, growing proportion of buys vs sells, €600K potential
- **DCA users:** 2,400 configured DCA → only 800 actually bought (lack of funds)
- C8 = whales, 90.91% Loan revenue. NEVER mass push. Personal relationship required.

### Critical Rules
- ALL actions need control group for incrementality measurement
- Balance data = manual download from Qlik dashboard (not in CleverTap)
- Cross-product segments (Brokerage + Loan) done manually via dashboard downloads

---

## Growth AccionesTODO parte1 (Feb 9, 2026)
**Attendees:** Pablo Campos, Patri Gargallo, Daniel Ferraro, Diego Barreira, Isabel Sánchez

### A/B Test Leadership Structure (Pablo decision)
- **Daniel:** Full leadership for A/B test vision + structuring
- **Patri:** Cross-area oversight (ADQ, LC, GTM)
- **DavidD:** GTM playbook lead (changes weekly)
- Goal: 1 test this week, 2 next week, scale up

### User Flow (canonical per ISA Figma)
- Adquisición → Registro y Verificación → Primera Compra
- Channels ordered by volume: Direct (highest), SEO/Organic, Paid

### Open Questions
- Referidos: Diego needed clarity on budget decisions
- New org chart: to be presented that Monday (Feb 9)

---

## Planteamiento Tests A/B (Feb 10, 2026)
**Attendees:** Daniel Ferraro, Patri Gargallo

### Segmentation for CleverTap
- Cluster data from Marta's LC sheet (Brokerage clusters, not global)
- KYC incomplete users in verification journey: wait 10-15 days before secondary impact
- CleverTap limitations: language + A/B can't run simultaneously → forces ES/PT/EN splits

---

## Campaña Referidos (Feb 10, 2026)
**Attendees:** Diego Barreira, S. Rut (Salvia)

### Referidos Strategy Context
- Binance offers €100 per referral but with complex fee conditions → misleading
- Need to define proper referral conditions + terms
- Space Center is the referral platform
- Daniel = expert in crypto referral programs
- Salvia owns referral execution
- Working backwards: campaigns launching without strategy foundation

---

## Journeys Activación Figma (Feb 12, 2026)
**Attendees:** Patri Gargallo, Pablo Garcia, Diego Barreira

### Journey Structure
- Transactional communications: generic for all users (no channel segmentation — too complex)
- Verification journey: ~10 days duration
- Goal: journey of first purchase segmented by acquisition channel (not yet built)
- DB/code not ready for channel segmentation in CleverTap
- ISA built original journey maps in Figma
