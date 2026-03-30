# PBW 2026 — Crypto Health Score MVP Brief for Engineering Handoff

**From:** Daniel Ferraro, Head of Growth
**To:** Engineering lead
**Date:** 2026-03-29
**Event:** Paris Blockchain Week, April 15-16, Carrousel du Louvre, Paris
**Budget:** EUR 3-5K internal dev (no external agency)
**Deadline:** Brief delivered March 31 → Build starts April 1 → LIVE by April 10

---

## Overview

The Crypto Health Score is the primary booth engagement mechanic at PBW. It gives a B2C visitor a 60-second interactive experience that produces a personalized "Crypto Portfolio Health Score" — a number from 0-100 with a strength, a gap, and a CTA to Bit2Me's PBW offer.

This tool is the single best way to stop a visitor at the booth, create a conversation, and capture a warm lead. Without it, booth engagement is passive (look at a banner, maybe scan a QR). With it, every visitor walks away with a personalized output that is shareable and memorable.

**This brief does NOT need Diego approval before build starts.** The tool contains no offer copy. The MiCA-relevant text is in the "gap" recommendations — these must be configurable (see Section 8 for the critical Diego review note).

---

## Section 1: What It Is

| Parameter | Value |
|-----------|-------|
| Type | Interactive mobile web tool — NOT a native app |
| Hosted on | bit2me.com/pbw/health OR pbw.bit2me.com/health (Dev to confirm preferred path) |
| Purpose | Marketing engagement tool that generates a personalized "Crypto Portfolio Health Score" |
| NOT | A financial product, investment advisor, or portfolio analysis service |
| Login required | No |
| Email required | No |
| PII collected by tool | None — fully anonymous until user clicks CTA to /pbw |
| Platform | Mobile web: iPhone Safari + Android Chrome (both required, not optional) |

**Framing for all communications about this tool:** "A marketing tool that produces a personalized report." Do not describe it as a financial analysis tool or portfolio audit in any internal or external communication.

---

## Section 2: The 5 Questions

One screen per question. All multiple choice. No free text entry. No back button between questions (forward-only flow to keep the 60-second target).

Progress indicator at top: "Question X of 5" with a simple progress bar.

### Question 1 — Experience

**Question text:** "How long have you been investing in crypto?"

| Option | Display text |
|--------|-------------|
| A | Less than 1 year |
| B | 1-3 years |
| C | More than 3 years |

---

### Question 2 — Portfolio Composition

**Question text:** "What is your portfolio split?"

| Option | Display text |
|--------|-------------|
| A | Mostly BTC/ETH |
| B | Mix of altcoins |
| C | DeFi/NFT heavy |

---

### Question 3 — Rebalancing Behavior

**Question text:** "How often do you rebalance your portfolio?"

| Option | Display text |
|--------|-------------|
| A | Never |
| B | Quarterly |
| C | Monthly |
| D | Weekly |

---

### Question 4 — Custody

**Question text:** "Where do you hold your assets?"

| Option | Display text |
|--------|-------------|
| A | On an exchange |
| B | Hardware wallet (self-custody) |
| C | Split between both |

---

### Question 5 — Regulatory Awareness

**Question text:** "Are you using a MiCA-regulated exchange?"

| Option | Display text |
|--------|-------------|
| A | Yes |
| B | No |
| C | I don't know |

---

## Section 3: Scoring Logic

Simple weighted sum. No ML, no external API, no database lookup. All scoring runs client-side in browser memory.

### Point Values per Answer

| Question | Answer | Points | Rationale |
|----------|--------|--------|-----------|
| Q1 — Experience | Less than 1 year | 10 | Early stage |
| Q1 — Experience | 1-3 years | 20 | Developing |
| Q1 — Experience | More than 3 years | 25 | Experienced |
| Q2 — Composition | Mostly BTC/ETH | 25 | Lower risk profile |
| Q2 — Composition | Mix of altcoins | 15 | Moderate risk |
| Q2 — Composition | DeFi/NFT heavy | 10 | Higher risk profile |
| Q3 — Rebalancing | Never | 5 | Passive / no management |
| Q3 — Rebalancing | Quarterly | 15 | Reasonable cadence |
| Q3 — Rebalancing | Monthly | 20 | Active management |
| Q3 — Rebalancing | Weekly | 15 | Active but may signal overtrading |
| Q4 — Custody | Exchange only | 10 | Single point of failure |
| Q4 — Custody | Hardware wallet | 20 | Self-sovereign |
| Q4 — Custody | Split both | 25 | Diversified custody |
| Q5 — MiCA | Yes | 25 | Regulatory aware |
| Q5 — MiCA | No | 10 | Some awareness |
| Q5 — MiCA | I don't know | 5 | Low regulatory awareness |

### Normalization Formula

Maximum possible raw points = 25 (Q1) + 25 (Q2) + 20 (Q3) + 25 (Q4) + 25 (Q5) = **120 raw points**

`Final Score = round((raw_points / 120) * 100)`

Examples:
- Maximum score: 120/120 × 100 = **100**
- Minimum score: 10/120 × 100 ≈ **8**
- Average expected: ~55-65 (based on typical crypto investor profile)

---

## Section 4: Output Screen

The result screen displays after question 5 is submitted. It is the highest-value screen in the entire tool — design should prioritize this.

### Visual Elements

| Element | Specification |
|---------|--------------|
| Score dial / gauge | Visual arc or gauge showing 0-100. Needle or fill animates to the score on load (CSS animation preferred). |
| Color coding | 0-40 = red zone; 41-70 = yellow/amber zone; 71-100 = green zone |
| Score display | Large number: "Your Score: [number] / 100" |
| Strength line | "Your Strength: [configurable text based on score + answers]" |
| Gap line | "Your Gap: [configurable text based on score + answers]" |
| CTA button | "Improve Your Score — Trade Fee-Free for 60 Days" → links to `https://bit2me.com/pbw` |
| Share button | "Share Your Score" → see Section 5 |

### Configurable Text — Score Brackets

**CRITICAL: All output text in this section MUST be stored as a configurable JSON file or CMS field — NOT hardcoded strings in the application.** Diego may require changes to "gap" text before April 15. We cannot deploy a code change on booth day. See Section 8 for details.

**Green bracket (71-100):**
- Strength: "Long-term holder with strong custody discipline and regulatory awareness."
- Gap: "Your portfolio looks mature. Consider whether your current exchange offers the full MiCA compliance layer your strategy deserves."

**Yellow bracket (41-70):**
- Strength: "Active investor with a diversified approach."
- Gap: "A few adjustments could significantly strengthen your position — starting with custody diversification and using a MiCA-regulated exchange."

**Red bracket (0-40):**
- Strength: "You're building your crypto foundation."
- Gap: "Focus on two things first: custody diversification and moving to a MiCA-regulated exchange for full EU consumer protection."

**Additional logic (answer-specific override):**
If Q5 answer = "No" or "I don't know", append to gap text: "Trading on a MiCA-authorized exchange like Bit2Me gives you EU consumer protection that unregulated exchanges cannot provide."

---

## Section 5: Share Mechanic

The share mechanic is the viral distribution layer. A score that is shareable creates organic reach. Budget for design time on this screen.

### Implementation

**Primary: Web Share API (native mobile share sheet)**
```javascript
navigator.share({
  title: 'My Crypto Health Score',
  text: 'My Crypto Health Score is [X]/100! How does yours compare? #PBW2026 @bit2me',
  url: 'https://bit2me.com/pbw/health'
})
```

**Fallback: Twitter intent URL (for desktop + browsers that don't support Web Share API)**
```
https://twitter.com/intent/tweet?text=My+Crypto+Health+Score+is+[X]%2F100!+Check+yours+at+bit2me.com%2Fpbw%2Fhealth+%23PBW2026+%40bit2me
```

### Share Privacy

The share contains only the score number (0-100). It does NOT share:
- Individual question answers
- Any portfolio data
- Any PII

The URL shared points to `bit2me.com/pbw/health` — so every share drives new visitors to the tool, who then hit the CTA to `/pbw`.

---

## Section 6: Analytics

Every tool completion fires a CleverTap event. No PII is captured by the tool itself — the analytics are behavioral only.

### CleverTap Event: `health_score_completed`

| Property | Value | Notes |
|----------|-------|-------|
| `score` | Integer 0-100 | Normalized final score |
| `q1_answer` | String | Text of selected option (e.g., "More than 3 years") |
| `q2_answer` | String | Text of selected option |
| `q3_answer` | String | Text of selected option |
| `q4_answer` | String | Text of selected option |
| `q5_answer` | String | Text of selected option |

### Additional Tracking Metrics

These do not need to be in CleverTap — a simple analytics layer (or Google Analytics 4 event) is sufficient:

| Metric | Why it matters |
|--------|---------------|
| Completions per day (booth days) | Tells us booth traffic conversion |
| Average score | Audience segmentation insight |
| Share button click-through rate | Viral coefficient indicator |
| CTA button click-through rate | Direct conversion signal |
| Drop-off by question (Q1-Q5) | Identifies which question kills engagement |

---

## Section 7: Technical Requirements

| Requirement | Value |
|-------------|-------|
| Platform | Mobile web — iPhone Safari 16+ and Android Chrome 110+ required |
| NOT native app | No download, no app store, no React Native |
| Page weight | Total under 500KB (venue Wi-Fi is unreliable; heavy pages will fail at the booth) |
| No external API calls | Scoring is client-side only — no server round-trip on question submit |
| JS framework | Existing Bit2Me stack preferred. If using React, server-side render for fast first load. No jQuery. |
| CSS animation | Score dial animation in CSS, not JS animation libraries |
| Offline fallback | Not required, but graceful error if CleverTap event fails (do not block the result screen) |
| Dev stack | Internal build only — no external agency |
| Budget | EUR 3-5K internal dev cost |
| Timeline | Brief delivered March 31 → Build starts April 1 → Live by April 10 |

---

## Section 8: Diego Review Note

**Engineering team: read this before writing the output text.**

The "gap" recommendation text on the results screen — especially lines like "Consider moving to a MiCA-regulated exchange" — may constitute investment or financial advice under Diego's interpretation of MiCA marketing rules.

**Mitigation: Build all output text as configurable copy.**

Store all text displayed on the results screen (Strength line, Gap line, CTA text) in a **JSON config file** or a **CMS field** that can be edited without a code deployment. This means:
- If Diego flags the "gap" language before April 10: Daniel updates the config file, and new text is live in < 1 hour, with no code change and no deployment.
- If Diego approves the language as-is: no action needed, the default text ships.

**Do not hardcode any output text strings directly in the application component.** Every string that appears on the result screen should come from a config source.

**Timeline for Diego briefing:** Daniel will brief Diego on the Health Score concept by March 31 to get an early compliance signal. If Diego flags a concern before April 5, there is still time to adjust. If Diego flags a concern after April 10 and text is hardcoded, we have a code deploy on booth day — unacceptable.

**Brief Diego on the concept, not the implementation.** He does not need to see code — he needs to see the 3-4 output text lines (Strength + Gap) and confirm whether they constitute financial advice under his interpretation of MiCA.

---

## Section 9: Handoff Checklist

- [ ] Brief sent to engineering lead (March 29-31)
- [ ] Engineering confirms feasibility within 10-day window (March 31)
- [ ] Design brief sent to design team for 6 screens: Q1, Q2, Q3, Q4, Q5, Results (March 31)
- [ ] Diego briefed on Health Score concept for early compliance signal (March 31)
- [ ] Output text stored in configurable JSON / CMS — NOT hardcoded (confirmed before build starts)
- [ ] Build starts (April 1)
- [ ] Scoring logic implemented and unit tested with known inputs → expected outputs (April 5)
- [ ] Normalization formula `(raw / 120) * 100` verified with edge cases: min score, max score (April 5)
- [ ] Output text configurable — confirm by updating one line in config without code deploy (April 7)
- [ ] Mobile testing on iPhone Safari + Android Chrome (April 9)
- [ ] CleverTap `health_score_completed` event firing with all 6 properties on completion (April 9)
- [ ] Share mechanic working: Web Share API on mobile + Twitter intent fallback on desktop (April 9)
- [ ] CTA "Improve Your Score" links correctly to bit2me.com/pbw (April 9)
- [ ] LIVE and booth-ready (April 10)

---

## Appendix: Screen Flow (6 Screens)

```
[Screen 1: Q1 — Experience]
    ↓ user taps answer
[Screen 2: Q2 — Portfolio Split]
    ↓ user taps answer
[Screen 3: Q3 — Rebalancing]
    ↓ user taps answer
[Screen 4: Q4 — Custody]
    ↓ user taps answer
[Screen 5: Q5 — MiCA Awareness]
    ↓ user taps answer
[Screen 6: Results]
    → Score gauge animates in
    → Strength + Gap lines appear
    → CTA button: "Improve Your Score — Trade Fee-Free for 60 Days" → bit2me.com/pbw
    → Share button: "Share Your Score"
    → health_score_completed fires to CleverTap
```

**Design note:** The results screen is the payoff. The 5 question screens should be clean and minimal. All visual investment goes into Screen 6 — the score dial, the color coding, the personalized text, and the CTA.

---

## Appendix: Example Scoring Scenarios

| Profile | Q1 | Q2 | Q3 | Q4 | Q5 | Raw | Normalized | Bracket |
|---------|----|----|----|----|----|----|------------|---------|
| Expert (max) | 3yr+ (25) | BTC/ETH (25) | Monthly (20) | Split (25) | Yes (25) | 120 | 100 | Green |
| Beginner (near min) | <1yr (10) | DeFi/NFT (10) | Never (5) | Exchange (10) | No (10) | 45 | 38 | Red |
| Mid-tier typical | 1-3yr (20) | Mix (15) | Quarterly (15) | Split (25) | No (10) | 85 | 71 | Green |
| Experienced, unregulated | 3yr+ (25) | BTC/ETH (25) | Monthly (20) | Hardware (20) | No (10) | 100 | 83 | Green |
