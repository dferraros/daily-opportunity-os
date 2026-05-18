# Oikos Protocol — Galxe Campaign
**Deliverable:** Phase 3 of 6 | GTM Execution System
**Last updated:** 2026-05-18
**Owner:** Daniel Ferraro (solo marketer)
**Status:** READY TO EXECUTE

---

## 1. CAMPAIGN OVERVIEW

**Platform:** Galxe (galxe.com) — 22M+ users, #1 web3 community platform
**Architecture:** 3-tier progressive quest (social → wallet → on-chain)
**Budget:** $1,000 total (corrected breakdown below)
**Duration:** 4 weeks (launch in GTM Week 7, per X content calendar)
**Goal:** Acquire 200-400 qualified BNB Chain users who understand Oikos mechanics; gate for quality not quantity

### Budget Breakdown (CORRECTED — use these numbers everywhere)

| Line Item | Cost | Notes |
|-----------|------|-------|
| Space deposit (refundable) | $300 | Required to create Galxe Space |
| Space verification fee | $350/year | Annual, NOT $300 — official Galxe pricing |
| USDC reward pool | $350 | Distributed across Tier 2 and Tier 3 completions |
| **Total** | **$1,000** | Matches allocated budget exactly |

**Critical note:** Do NOT use OKS as the reward currency. At current price ($0.000061), $350 = 5.7M OKS tokens. Distributing 5.7M tokens to quest farmers sends a catastrophic signal (high float release, low price signal). Use USDC exclusively.

---

## 2. SYBIL RESISTANCE STRATEGY

### Required Credentials (Tier 1 gate)
**BAB Token (Binance Account Bound)**
- Free to mint on BNB Chain
- Soulbound (non-transferable)
- Verifies: KYC'd Binance user on BNB Chain
- Why this works: genuine BNB Chain user base, not Ethereum farmers, natural audience match

**Galxe Score Level 1** (secondary)
- Measures overall Galxe participation history
- Level 1 = minimal but real on-chain footprint
- Filters: brand-new accounts created to farm this quest

### NOT used: Gitcoin Passport
Too much friction for target users (BNB Chain DeFi users, not Ethereum ecosystem participants). BAB Token is the correct sybil gate for this audience.

### Anti-Farmer Reasoning
- BAB Token: requires Binance KYC — real person, real BNB Chain address
- Tier 3 requires on-chain contract interaction: cannot be botted without actual gas spend and protocol usage
- Galxe's default anti-sybil layer also runs automatically (device fingerprinting, behavior analysis)
- Expected farmer attrition: 60-70% of Tier 1 completions will not advance to Tier 3. This is acceptable — Tier 3 is the target cohort.

---

## 3. THREE-TIER QUEST ARCHITECTURE

### Tier 1: Social Awareness (Low friction — maximum reach)
**Label:** "Discover Oikos"
**Goal:** Introduction + contact acquisition
**Estimated completions:** 200-400
**Time to complete:** 5-10 minutes

**Credentials required to enter:**
- None (open entry)

**Tasks:**
1. Follow @oikos_cash on X — credential: Twitter Follow
2. Retweet the Galxe announcement post — credential: Twitter Retweet
3. Join t.me/oikoscash on Telegram — credential: Telegram Join (manual verification or Galxe bot)
4. Complete a 3-question quiz about Oikos mechanics — credential: Galxe Quiz
   - Q1: "What is the solvency invariant on Oikos?" → Answer: The protocol always holds enough liquidity to repurchase 100% of circulating supply at floor price
   - Q2: "What percentage of newly minted supply goes to creators at each shift event?" → Answer: ~4.75%
   - Q3: "What network is Oikos deployed on?" → Answer: BNB Smart Chain

**Reward for Tier 1 completion:**
- Oikos Whitelist NFT (non-monetary — early access priority badge)
- Entry to Tier 2 unlock

**Why a quiz:** Filters for users who read the Oikos description before completing. One quiz question eliminates 20-30% of pure farmers who auto-submit without reading. Remaining completions are more qualified.

---

### Tier 2: Wallet Verification (Medium friction — filters for BNB Chain presence)
**Label:** "Prove You're BNB"
**Goal:** Verify real BNB Chain on-chain presence
**Estimated completions:** 50-100 (15-30% of Tier 1)
**Time to complete:** 15-20 minutes

**Credentials required to enter:**
- Galxe Score Level 1
- BAB Token on BNB Chain wallet

**Tasks:**
1. Connect BNB Chain wallet to Galxe — credential: Wallet connect
2. Hold BAB Token in connected wallet — credential: BAB Token holder (on-chain verification)
3. Have at least 1 prior BNB Chain transaction — credential: Galxe can query `eth_getTransactionCount` equivalent

**Reward for Tier 2 completion:**
- Oikos Pioneer NFT (Galxe-minted, soulbound) — permanent record of being a founding community member
- $0 monetary value intentionally — status signal, not financial incentive
- Entry to Tier 3 unlock

---

### Tier 3: On-Chain Interaction (High friction — qualifies for USDC reward)
**Label:** "Use the Protocol"
**Goal:** Actual protocol interaction — first user acquisition
**Estimated completions:** 15-40 (10-25% of Tier 2)
**Time to complete:** 30-60 minutes + gas

**Credentials required to enter:**
- Tier 2 completion (Oikos Pioneer NFT held)

**Tasks:**
1. Connect wallet at oikos.cash — credential: View function query on BNB Chain
   - Galxe can call a `view` function on the Oikos smart contract to verify wallet has connected
   - OKS contract: 0x18aCf236eB40c0d4824Fb8f2582EBbEcD325Ef6a (BNB Smart Chain)
2. Either: Hold minimum OKS tokens (e.g., 100 OKS, ~$0.006) OR interact with the protocol (join liquidity, use any protocol function)
   - Galxe credential: ERC-20 balance snapshot (Galxe supports BNB Chain ERC-20 balance queries)
3. Share one thing you learned about Oikos in the Galxe Space discussion

**Reward for Tier 3 completion:**
- USDC from reward pool
- Distribution: $350 USDC ÷ estimated 25 completions = $14 USDC per completion
- If fewer than 15 complete: increase per-completion payout. If more than 40 complete: pro-rata split with $350 cap

**USDC distribution mechanics:**
- Top up Galxe Space with $350 USDC before campaign launch
- Galxe handles distribution automatically on credential verification
- Daniel verifies Tier 3 completions manually before approving distribution (Galxe allows manual approval gate)

---

## 4. GALXE SPACE SETUP INSTRUCTIONS

### Step 1: Create Galxe Space (Week 6, before campaign launch)
1. Go to galxe.com → Create Space
2. Space name: "Oikos Protocol"
3. Space description: "DeFi token launchpad on BNB Chain. Unruggable by design. Build your token on math, not promises."
4. Upload: Oikos logo, brand colors (from Notion Brand Kit v1.0)
5. Submit $300 Space deposit (refundable against future quest spend)
6. Submit $350 verification fee → receive "Verified Project" badge (takes 1-5 business days — submit 2 weeks before launch)

### Step 2: Configure Credentials
Before creating the quest, set up each credential type:
- **Twitter Follow credential:** Connect @oikos_cash account to Galxe Space admin
- **Telegram Join credential:** Connect t.me/oikoscash (requires Galxe bot in Telegram group — add @galxe_bot as admin)
- **Galxe Quiz credential:** Create via Galxe no-code quiz builder (max 10 questions, 3 correct answers required = pass)
- **BAB Token credential:** Select from Galxe's existing on-chain credential library (pre-built for BNB Chain)
- **ERC-20 Balance credential:** Configure for OKS contract address on BNB Chain, minimum balance = 100 OKS

### Step 3: Create the Campaign
1. Galxe dashboard → New Campaign
2. Set dates: 4-week window starting GTM Week 7
3. Configure 3 tiers as separate "tasks" with credential gates between them
4. Set reward: Tier 1 = NFT (Galxe-minted), Tier 2 = NFT (Galxe-minted), Tier 3 = USDC
5. Upload $350 USDC reward fund to Galxe escrow before go-live
6. Enable manual approval gate for Tier 3 USDC distribution
7. Preview and test entire flow with a personal wallet before publishing

### Step 4: Submit for BNB Chain Project Spotlight
- After Space is verified, submit to Galxe's "BNB Chain" featured category
- BNB Chain Spotlight submissions: galxe.com/BNBChain (or submit via BNB Chain BD contact — Walter @lclwalter can facilitate)
- BNB Chain Spotlight dramatically increases organic discovery within Galxe's ecosystem
- No additional cost — editorial decision by Galxe/BNB Chain partnership team
- Prepare: 1-paragraph project summary, logo, one key metric (DappBay listing is the credibility anchor)

---

## 5. CAMPAIGN TIMING

| Week | Activity |
|------|----------|
| Week 5 (GTM) | Submit Galxe Space verification ($350) — allow 5-7 business days |
| Week 5 (GTM) | Pay Space deposit ($300), create Space, configure credentials |
| Week 6 (GTM) | Test full quest flow with test wallet |
| Week 6 (GTM) | Fund USDC reward pool ($350) |
| Week 6 (GTM) | Submit BNB Chain Project Spotlight application |
| Week 7 (GTM) | Campaign goes live — X announcement + Telegram announcement |
| Weeks 7-8 | Monitor, respond to completion questions in Galxe Space discussion |
| Week 8 end | Campaign closes — Tier 3 manual approval, USDC distribution |
| Week 9 | Post-campaign report: completions by tier, cost per acquisition |

---

## 6. ANTI-FARMING TACTICS

Beyond the sybil gates:

**1. Quiz randomization:** Galxe quiz allows randomized question order. Enable this to prevent copy-paste farming from Telegram.

**2. Manual Tier 3 review:** Before approving USDC distribution, review wallet addresses for:
- Account age < 7 days: flag for manual inspection
- Identical completion patterns with other flagged wallets: reject
- No prior BNB Chain history except the quest transactions: reject

**3. Tier 3 discussion requirement:** The "share one thing you learned" task creates a friction barrier that pure farmers skip. It also generates authentic content about Oikos in the Galxe Space — double value.

**4. No referral multipliers:** Do NOT add "refer 3 friends for bonus" mechanics. Referral multipliers are the #1 farmer magnet. Quality acquisition requires friction, not gamification of spreading.

---

## 7. CONTENT REQUIREMENTS FOR CAMPAIGN LAUNCH

### Required before go-live:
1. **Campaign banner** (1200×628px) — visual showing 3 tiers, "Unruggable by Design," BNB Chain logo
2. **Quest description copy** — Used inside Galxe (max 500 words):
```
Oikos is a DeFi token launchpad on BNB Chain where the floor price only goes up — mathematically.

Unlike PumpFun-style platforms where creators earn 0.025% and liquidity can be drained, Oikos uses CLAMM architecture with a mathematical solvency invariant: the protocol always holds enough reserves to buy back 100% of supply at floor price.

Creator economics: ~4.75% of newly minted supply goes to token creators at each shift event. Perpetual. Not a one-time launch fee.

Complete this quest to understand how Oikos works and qualify for the founding user cohort.

Level 1: Follow and learn (5 min) → whitelist priority
Level 2: Verify your BNB Chain presence (15 min) → Pioneer NFT
Level 3: Use the protocol (30 min) → USDC from reward pool

Only real BNB Chain users. BAB Token required for Level 2.
```

3. **X announcement post** — W7-M from X Content Calendar (already written)
4. **Telegram announcement** — Adapt X announcement for Telegram format (remove thread structure, add direct Galxe link)

---

## 8. SUCCESS METRICS

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| Tier 1 completions | 100 | 250 | 400 |
| Tier 2 completions | 15 | 50 | 100 |
| Tier 3 completions | 5 | 20 | 40 |
| Tier 1→3 conversion | 5% | 8% | 12% |
| Cost per Tier 3 user | $70 | $17 | $8.75 |
| BNB Chain Spotlight approval | — | Yes | — |
| Telegram joins from Galxe | 25 | 100 | 200 |
| X follows from Galxe | 50 | 150 | 300 |

**North star:** Tier 3 completions. These are the users who have connected a wallet and interacted with the protocol. This is the founding user cohort — the 15-40 people who Oikos's earliest token launches will be built around.

**Cost-per-acquisition benchmark:** $350 USDC for 20 Tier 3 users = $17.50 per protocol user. For a DeFi protocol in early phase, this is competitive with paid acquisition channels.

---

## 9. POST-CAMPAIGN ACTIONS

After campaign closes:

1. Export Tier 3 wallet addresses — add to creator outreach list for Phase 5 (KOL Outreach)
2. Export Tier 2 wallet addresses — add to Discord Engages whitelist (Phase 4)
3. Post-campaign report post on X: completion rates, what users learned, what's next
4. DM every Tier 3 completer directly (Telegram or X): "You completed Level 3. Here's what being an early Oikos builder means..."
5. Evaluate: was USDC reward sufficient to drive Tier 3? If <10 completions, reconsider Tier 3 task difficulty before next campaign.

---

*Deliverable status: COMPLETE | Next: DISCORD-ENGAGES.md*
