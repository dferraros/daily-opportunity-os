# Oikos Protocol GTM — Requirements
**Project:** Oikos Protocol Go-To-Market Execution System
**Version:** 1.0 | **Date:** 2026-05-18
**Owner:** Daniel Ferraro

---

## Acceptance Criteria by Phase

### REQ-01: X Content System

| ID | Requirement | Test |
|----|------------|------|
| REQ-01-01 | 24 posts scheduled across 8 weeks (3/week: Mon 09:00, Wed 14:00, Fri 09:00 CET) | Count posts in calendar |
| REQ-01-02 | Zero external links in main post body — all URLs in first reply | Manual spot check, 3 random posts |
| REQ-01-03 | Every post ends with a direct, answerable question | Read posts 1, 8, 16, 24 |
| REQ-01-04 | Algorithm scoring rubric applied to every post (min score 7/10 to publish) | Scoring sheet populated before publish |
| REQ-01-05 | No investment language: "invest," "returns," "profit," "guaranteed" absent | grep/search all post copy |
| REQ-01-06 | No price discussion or OKS price targets | grep for "$" and "price" in post copy |
| REQ-01-07 | Visual brief exists for all 4 template types | Check output/X-CONTENT-SYSTEM.md §4 |
| REQ-01-08 | Reply strategy covers all 6 comment types including FUD and price questions | Check output/X-CONTENT-SYSTEM.md §5 |

**Pass condition:** All 8 checked. Publish gate: REQ-01-01 through REQ-01-06 are blocking.

---

### REQ-02: Telegram Playbook

| ID | Requirement | Test |
|----|------------|------|
| REQ-02-01 | Rose Bot installed with 3-message welcome sequence (0s / 30s / 5min) | Send test join, verify 3 messages received |
| REQ-02-02 | 6 community rules pinned in t.me/oikoscash | Open channel, verify pinned message |
| REQ-02-03 | Weekly template exists for Mon/Wed/Fri | Check output/TELEGRAM-PLAYBOOK.md §4 |
| REQ-02-04 | Buybot NOT active during Phase 1 (OKS volume < $500/day threshold) | Confirm no buybot in group settings |
| REQ-02-05 | Outreach list contains minimum 5 external Telegram groups to engage | Check output/TELEGRAM-PLAYBOOK.md §5 |
| REQ-02-06 | Moderator escalation matrix defined (price / FUD / rug / builder / media) | Check output/TELEGRAM-PLAYBOOK.md §6 |
| REQ-02-07 | 8-week member targets set (W1=25 / W4=150 / W8=300+) | Verify targets in playbook |

**Pass condition:** All 7 checked. REQ-02-01 and REQ-02-02 must be complete before Week 1 posting.

---

### REQ-03: Galxe Campaign

| ID | Requirement | Test |
|----|------------|------|
| REQ-03-01 | Budget correctly allocated: $300 deposit + $350 verification + $350 USDC = $1,000 | Check budget table — no OKS as reward currency |
| REQ-03-02 | 3-tier architecture implemented: social→wallet→on-chain | Verify Tier 1/2/3 credential gates in Galxe dashboard |
| REQ-03-03 | Sybil gate uses BAB Token (NOT Gitcoin Passport) at Tier 2 | Confirm credential type in Galxe campaign config |
| REQ-03-04 | Tier 1 quiz includes 3 mandatory questions about Oikos mechanics | Check quiz in Galxe campaign |
| REQ-03-05 | Manual approval gate enabled for Tier 3 USDC distribution | Verify manual gate toggle is ON in Galxe |
| REQ-03-06 | Galxe Space verification submitted at least 7 days before campaign launch | Check submission timestamp |
| REQ-03-07 | BNB Chain Project Spotlight submitted after Space is verified | Confirmation email / Galxe dashboard |
| REQ-03-08 | No referral multiplier mechanics in any tier | Verify campaign settings |

**Pass condition:** All 8 checked. REQ-03-01, REQ-03-03, REQ-03-05 are non-negotiable.

---

### REQ-04: Discord Engages Campaign

| ID | Requirement | Test |
|----|------------|------|
| REQ-04-01 | Discord server state assessed BEFORE any Engages setup (< 10 / 10-50 / 50+ decision) | Document server member count + decision in STATE.md |
| REQ-04-02 | 5-quest sequence configured in Engages (only if Discord has 50+ members) | Test each quest with personal account |
| REQ-04-03 | Role structure implemented: Lurker→Learner→Builder→Founder→Moderator | Verify role names in Discord server settings |
| REQ-04-04 | Minimum 6-channel structure created before Engages launch | Count channels: #announcements, #protocol-intro, #rules, #general, #questions, #quest-submissions |
| REQ-04-05 | On-chain verification NOT attempted via Engages (Galxe handles this) | No on-chain credential configured in Engages |
| REQ-04-06 | Galxe Tier 2+ completers cross-referenced for Founder role assignment | Manual process documented in mod handbook |

**Pass condition:** REQ-04-01 is the prerequisite gate. If Discord < 10 members, REQ-04-02 through REQ-04-06 are deferred and archived.

---

### REQ-05: Micro-KOL Outreach

| ID | Requirement | Test |
|----|------------|------|
| REQ-05-01 | KOL outreach does NOT start before Week 7 GTM (Galxe live with real completions) | Check timestamp of first formal pitch DM |
| REQ-05-02 | 10-target shortlist built using documented search methodology (Section 3) | Tracking sheet populated with 10 rows before first DM |
| REQ-05-03 | Background check completed for each target (ZachXBT list, rug history) | "Background check" column filled in tracking sheet |
| REQ-05-04 | Minimum 7 days of warm engagement before cold DM | "Warm engagement" date vs "Outreach sent" date delta ≥ 7 days |
| REQ-05-05 | Every paid arrangement has written disclosure contract BEFORE content publishes | Signed contract file exists; public disclosure in content |
| REQ-05-06 | Milestone cash cap: $350 max per KOL. No upfront payment. | Check arrangement type in tracking sheet |
| REQ-05-07 | Co-launch model pitched FIRST before cash offers for Tier C targets | Verify template used in outreach (Template 2) |
| REQ-05-08 | Maximum 3 active KOL conversations simultaneously | Tracking sheet "Response: Interested" count ≤ 3 at any time |

**Pass condition:** REQ-05-01 and REQ-05-05 are non-negotiable legal/sequencing requirements.

---

### REQ-06: GTM Master & Infrastructure

| ID | Requirement | Test |
|----|------------|------|
| REQ-06-01 | CoinGecko correction submitted on Day 1 (blocks all outbound content) | Screenshot of submission + timestamp |
| REQ-06-02 | X Premium subscribed for @oikos_cash before first post | Account settings confirm subscription |
| REQ-06-03 | X bio rewritten to current Oikos positioning (not synthetic assets) | Read current bio on X |
| REQ-06-04 | Quill Audit report URL publicly accessible | Verify URL loads without authentication |
| REQ-06-05 | DappBay listing linked in all KOL and media outreach templates | Check Templates 1, 2, 3 in KOL-OUTREACH.md |
| REQ-06-06 | 4 visual templates produced before Week 1 posting | Files exist: Thread Opener Card, Comparison Table, Mechanism Diagram, Data Card |
| REQ-06-07 | "Fully decentralized" claim NOT used until DAO formally established | grep "fully decentralized" across all content |
| REQ-06-08 | OKS discussed only as governance/utility token, never as investment vehicle | Review all post copy and outreach templates |

**Pass condition:** REQ-06-01, REQ-06-02, REQ-06-03 must be complete before ANY public content is published.

---

## Legal Constraints (Hard Stop Conditions)

The following conditions, if violated, require immediate content removal and legal review:

| ID | Constraint | Enforcement |
|----|-----------|-------------|
| LEGAL-01 | No investment advice language in any channel | Daniel reviews all copy before publish |
| LEGAL-02 | KOL disclosure contract required before any paid arrangement | No exceptions; contract file must exist |
| LEGAL-03 | Public disclosure on all paid KOL content ("Paid partnership with Oikos Protocol") | Visible in post content |
| LEGAL-04 | No price predictions, targets, or "when moon" language | Immediate removal if found |
| LEGAL-05 | No false technical claims about protocol mechanics | All mechanic claims sourced from protocol-mechanics.md |

---

*REQUIREMENTS v1.0 | 2026-05-18 | Linked to: output/OIKOS-GTM-MASTER.md*
