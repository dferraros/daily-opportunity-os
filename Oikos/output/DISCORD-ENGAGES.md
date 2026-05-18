# Oikos Protocol — Discord Engages Campaign
**Deliverable:** Phase 4 of 6 | GTM Execution System
**Last updated:** 2026-05-18
**Owner:** Daniel Ferraro (solo marketer)
**Status:** READY TO EXECUTE — with prerequisite decision

---

## 0. PREREQUISITE: DISCORD SERVER DECISION

**Current state:** discord.gg/xTahMDXbRC — server exists, status unknown.

**One-marketer reality check:** Running an active Discord community requires daily moderation. Daniel cannot simultaneously manage X (daily posts + reply monitoring), Telegram (3x/week + AMA), Galxe campaign, and Discord — all solo.

### Decision Framework

| Option | When to choose | Trade-off |
|--------|----------------|-----------|
| **Activate Discord now** | If Discord already has 50+ members with engagement signals | Splits attention; risks both channels being weak |
| **Activate Discord in Phase 2** | If Discord is empty or dormant | Focused Phase 1 on Telegram; Discord becomes the "Level 2 hub" |
| **Close Discord, consolidate** | If Discord is completely empty and no one is using the link | Simplest path; redirect all traffic to Telegram |

**Recommended path (solo marketer constraint):**
- Check Discord server state FIRST (member count, last message date)
- If < 10 active members: archive Discord, redirect link to Telegram in all posts
- If 10-50 members with recent activity: keep live, post weekly update only, no Engages campaign until Phase 2
- If 50+ active members: proceed with Discord Engages campaign as written below

**Why Telegram > Discord for Phase 1:**
- Telegram requires less moderation overhead
- BNB Chain DeFi community skews Telegram-first
- Engages bot is Discord-only — you need a live Discord before Engages makes sense

---

## 1. DISCORD ENGAGES OVERVIEW

**Tool:** Discord Engages (engages.gg)
**Cost:** Free for server operators
**Limitation:** Discord-only (cannot do on-chain contract verification — that's Galxe's job)
**Role in GTM:** Warm retention and community depth INSIDE Discord — not cold acquisition
**Integration with Galxe:** Galxe brings users in; Engages keeps them engaged after

**Core use case for Oikos:**
- Reward active community members for education, discussion, and referrals
- Create role progression that signals protocol understanding depth
- Run quests that drive Telegram → Discord migration for the most engaged Galxe completers

---

## 2. ROLE STRUCTURE

### 5 Community Roles (Progressive)

| Role | Trigger | Perks |
|------|---------|-------|
| **Lurker** | Join server | None — entry state |
| **Learner** | Complete Quest 1-2 | Access to #mechanics-deep-dive channel |
| **Builder** | Complete Quest 1-4 | Access to #creator-lounge, priority in AMAs |
| **Founder** | Complete all 5 quests OR Galxe Tier 3 completer | Oikos Founder badge, first look at token launches |
| **Moderator** | Invited by Daniel after 60+ days Builder status | Moderation powers, private mod channel |

**Role structure rationale:**
- Simple enough to manage solo
- Progressive access creates incentive to advance
- "Founder" role is the most valuable — it represents the actual founding cohort, not an honorary title

### Role Assignment
- Lurker → Learner: Automatic via Engages on Quest 2 completion
- Learner → Builder: Automatic via Engages on Quest 4 completion
- Builder → Founder: Automatic for quest completers; Manual for Galxe Tier 3 holders (verify via wallet address cross-check)
- Founder → Moderator: Manual, always Daniel's decision

---

## 3. FIVE-QUEST SEQUENCE

### Quest 1: Welcome Gate
**Name:** "Read the Room"
**Type:** Information verification
**Task:**
1. Read the #protocol-intro channel (Engages tracks time-on-channel)
2. Answer 1 question in #quest-submissions: "What is the Oikos solvency invariant?"
3. React to the pinned welcome message with ✓
**Completion reward:** Learner role unlock
**Estimated completion:** 60% of new joins
**Purpose:** Filters people who actually read vs. those who auto-join

### Quest 2: Mechanics Proof
**Name:** "Understand the Floor"
**Type:** Knowledge demonstration
**Task:**
1. Reply to the #floor-explained thread with your plain-English explanation of "why the floor only goes up"
2. Receive 3 positive reactions from other community members on your reply
**Completion reward:** Access to #mechanics-deep-dive
**Estimated completion:** 30% of Quest 1 completers
**Purpose:** Forces community to teach each other (teaching = deepest learning; also generates community content)

### Quest 3: Creator Economics
**Name:** "The Creator Math"
**Type:** Creative task
**Task:**
1. Post in #creator-lounge: "If you launched a token on Oikos, what would your community be building?"
2. Keep it under 3 sentences — idea pitch format
**Completion reward:** Builder role unlock + priority AMA question slot
**Estimated completion:** 50% of Quest 2 completers
**Purpose:** Surfaces actual token launch intent — these are Daniel's direct outreach targets

### Quest 4: Community Contribution
**Name:** "Add Value"
**Type:** Ongoing contribution
**Task:** Earn 5 "community points" by:
- Answering another member's mechanics question (1 point each, verified by mod/Daniel)
- Sharing an X post from @oikos_cash in the #share-and-discuss channel (1 point each)
- Introducing a new member who completes Quest 1 (3 points each)
**Duration:** Rolling 14-day window
**Completion reward:** "Founder Track" confirmed
**Purpose:** Creates flywheel — active members drive new member acquisition

### Quest 5: Protocol Interaction
**Name:** "Touch the Protocol"
**Type:** On-chain action (manual verification via Galxe cross-check)
**Task:**
1. Complete Galxe Tier 2 or Tier 3 (connect BNB wallet, verify credentials)
2. Post your Galxe completion proof in #galxe-completions channel
3. Daniel or mod verifies and manually assigns Founder role
**Completion reward:** Founder role + permanent Founder badge in Discord
**Estimated completion:** All Galxe Tier 2+ completers who join Discord
**Purpose:** Links Galxe on-chain verification with Discord role progression

---

## 4. CHANNEL STRUCTURE

### Minimum viable channel setup (solo-manageable)

```
📢 INFORMATION
   #announcements          (read-only, Daniel posts)
   #protocol-intro         (read-only, pinned explainer)
   #rules                  (read-only)

💬 COMMUNITY
   #general                (open discussion)
   #questions              (protocol mechanics Q&A)
   #share-and-discuss      (X posts, news, research)
   #quest-submissions      (Quest 1-4 answers go here)

🏗️ BUILDERS [Learner+ access]
   #mechanics-deep-dive    (CLAMM, elastic supply, technical)
   #creator-lounge         (token launch ideas, creator Q&A)
   #galxe-completions      (Galxe proof submissions → Founder role)

🔐 FOUNDERS [Founder role only]
   #founders-lounge        (direct access to Daniel, first look at launches)
   #early-builders         (token launch coordination)

🛠️ INTERNAL [Mod only]
   #mod-log
```

**Anti-overwhelm rule:** Do not create channels you cannot moderate. Better to have 4 active channels than 12 empty ones. Start with Information + Community (6 channels total). Add Builder channels only when Galxe campaign launches.

---

## 5. INTEGRATION CHECKLIST

Before Engages campaign launches:

### Discord Server Setup
- [ ] Verify discord.gg/xTahMDXbRC is accessible and Daniel has admin
- [ ] Create channel structure from Section 4 (minimum: 6 channels)
- [ ] Write and pin #protocol-intro message (3 paragraphs: what Oikos is, why it's different, how to get started)
- [ ] Write and pin #rules message (copy from Telegram rules, adapt for Discord)
- [ ] Set up role colors and icons in Discord Server Settings
- [ ] Create an attractive server icon (Brand Kit v1.0)

### Engages Bot Setup
- [ ] Go to engages.gg → Connect Discord server
- [ ] Configure 5 quests from Section 3
- [ ] Map rewards: Quest 2 → Learner role, Quest 4 → Builder role, Quest 5 → Founder role
- [ ] Test each quest with a personal account before going live
- [ ] Enable Discord auto-join notification in #general

### Galxe ↔ Discord Integration
- [ ] After Galxe campaign launches: post "Join our Discord for Founder status" in Galxe Space
- [ ] Create Discord invite link in Galxe campaign description
- [ ] Manual process: Galxe Tier 2+ completers who join Discord → Daniel assigns Founder role within 24 hours of proof in #galxe-completions

### X and Telegram Cross-Promotion
- [ ] Add Discord link to @oikos_cash X bio (alongside Telegram)
- [ ] Post Discord invite in Telegram weekly updates (Weeks 5-8)
- [ ] Note in all posts: "Discord for deep-dive mechanics / Telegram for community news"

---

## 6. CONTENT PER STAGE

### Pre-launch (Weeks 1-6): Discord in standby
- Post 1 update per week in #announcements only
- Use Discord invite link in X and Telegram to begin soft member acquisition
- No Engages quests running yet

### Galxe launch week (Week 7): Discord activates
- Enable all Engages quests
- Post welcome message in #general: "Discord is now fully live. Quest system active. Galxe completers: claim Founder role in #galxe-completions."
- Pin quest guide in #quest-submissions

### Post-Galxe (Week 8+): Community mode
- Weekly AMA in #founders-lounge (Founder-only first hour, then open)
- Monthly "creator showcase" — Quest 3 respondents who developed their idea further
- Ongoing Quest 4 cycle resets every 14 days

---

## 7. MODERATOR HANDBOOK (DISCORD)

For Phase 1: Daniel is sole moderator. This section applies when recruiting from Founder role holders.

### Mod Responsibilities
- Verify Quest 1 and Quest 2 answers for quality (not just completion)
- Assign Learner/Builder roles where Engages automation misses
- Watch #questions for unanswered questions older than 24 hours — answer or tag Daniel
- Delete spam/scam in all channels immediately (Discord bot can auto-delete links from accounts < 7 days)

### Auto-Moderation Setup (Mee6 or Carl-bot — free tier)
- Anti-spam: delete identical messages sent within 5 seconds
- Block links from accounts < 7 days old (except in #share-and-discuss)
- Auto-role new members as "Lurker" on join

### Escalation: Same matrix as Telegram (Section 6 of TELEGRAM-PLAYBOOK.md)
- Price questions → Redirect to mechanics
- Rug accusations → Audit link + solvency invariant explanation
- Builder/launch inquiries → DM Daniel immediately
- Partnership/media → Daniel always, urgent

---

## 8. SUCCESS METRICS (PHASE 1 — 8 WEEKS)

| Metric | Minimum | Target |
|--------|---------|--------|
| Discord members | 50 | 200 |
| Quest 1 completions | 20 | 80 |
| Quest 3 completions (creator ideas) | 5 | 25 |
| Quest 5 completions (Founder) | 5 | 20 |
| Founder role holders | 5 | 20 |
| Avg. messages/day in #general | 3 | 10 |

**North star:** Quest 5 completions = real users who have connected a wallet, completed Galxe, and engaged in Discord. These are the first 20 people who understand Oikos end-to-end.

---

## 9. WHAT ENGAGES BOT CANNOT DO

Important limitations — do not design quests around these:

- **Cannot verify on-chain contract interactions** — this is Galxe's job (use Galxe for Tier 3 on-chain verification)
- **Cannot verify wallet balance without an external integration** — use Galxe + manual cross-check instead
- **Cannot run cross-server quests** — Engages is bound to a single Discord server
- **Cannot gate based on NFT holdings without Collab.Land** — if needed later, add Collab.Land alongside Engages

For all on-chain gating: Galxe is the tool. Engages handles community behavior and Discord role management only.

---

*Deliverable status: COMPLETE | Next: KOL-OUTREACH.md*
