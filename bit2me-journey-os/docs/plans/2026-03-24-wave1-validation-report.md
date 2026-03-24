# Wave 1 Validation Report
**Date:** 2026-03-24
**Files reviewed:** 4
**Validator:** Automated cross-check (7-point framework + MiCA compliance)

---

## Executive Summary

| Category | Count |
|----------|-------|
| Total issues found | 14 |
| BLOCKERS (must fix before sending to Diego) | 3 |
| Warnings (fix before CleverTap setup) | 7 |
| Notes (low priority) | 4 |

**Overall posture:** The copy quality is high. The MiCA self-checks embedded in each document are thorough and mostly accurate. The blockers are operational (unfilled placeholders, missing sample-size justification) not compliance failures. No prohibited words were found in final copy. The documents are sendable to Diego once the 3 blockers are resolved.

---

## Per-File Report

### JN-01-A — Second Trade Accelerator

**Status:** PASS WITH WARNINGS

| Check | Status | Issue | Fix Required |
|-------|--------|-------|-------------|
| MiCA Compliance | ✅ | No prohibited words. Disclaimer present in both emails (S3, S4). Art. 66 addressed via journey entry condition. | None — flag D-01 already pre-flagged for Diego. |
| Email Sequence | ⚠️ | Minor: fallback for `{{nombre}}` resolves to "inversor" — also used as a MiCA-adjacent word ("Invierte solo lo que puedas permitirte perder" in footer). Isolated, no real confusion risk. Broader: S3 preheader directly continues the subject line ("{{first_trade_asset}} ya está. Ahora viene {{suggested_asset}}.") — this partially repeats the S3 Subject A ("tu cartera tiene una pieza pendiente") angle. Not an exact repeat but very close in content. | Consider making the S3 preheader more distinct — e.g., focus on community angle ("El 73% de usuarios que empezaron con {{first_trade_asset}} también tienen {{suggested_asset}}.") rather than the asset sequence already telegraphed in the subject. |
| A/B Test Rigor | ⚠️ | AB-JN01A-01 and AB-JN01A-02 both have n=150 total (75/variant). Minimum specified in the framework is 500/variant. At ~75 users/day and 2-day accumulation, these tests are severely underpowered for reliable conclusions on CTR. AB-JN01A-05 meets the 500 minimum. | Add explicit note: "AB-01 and AB-02 are directional only — insufficient power for decision-making at n=75/variant. Accumulate data for 7 days (n≈525/variant) before reading results." Or adjust to run these tests across the full 7-day window. |
| Marketing Psychology | ✅ | Loss aversion + social proof framing correctly applied. No guilt language. Urgency in S4 is real (product-gated by `{{incentivo_activo}}`). | None. |
| Campaign Execution | ✅ | Send times specified. Stop conditions documented with 60-second SLA. Weekend suppression noted. Holdout (10%) referenced. All fallbacks have defined behaviors. | None. |
| Creative Briefs | ✅ | All 4 touchpoints have distinct briefs. Dimensions specified. AI prompts in English. | None. |
| Content Structure | ✅ | All required sections present. No placeholder text. Diego flags section is thorough (D-01 to D-06). | None. |

**BLOCKERS:**
None.

**WARNINGS:**
- W-01: A/B tests AB-01 and AB-02 are underpowered at n=75/variant. Add "directional only" caveat or extend accumulation window to 7 days before reading results.
- W-02: S3 preheader angle is too close to Subject A. Differentiate to improve preview text value.

---

### JN-02A — Sleeper to Trader

**Status:** PASS WITH WARNINGS

| Check | Status | Issue | Fix Required |
|-------|--------|-------|-------------|
| MiCA Compliance | ⚠️ | One issue found: A5 email subject line B reads "Llevas {{last_trade_date}} sin operar, {{nombre}}. Eso está a punto de cambiar." — The phrase "eso está a punto de cambiar" can be read as an implicit prediction about the user's future behaviour under market conditions, and Diego may flag it as directional framing. More importantly, the fallback for this subject is "Han pasado meses. El mercado ha cambiado. ¿Y tú?" — the "¿Y tú?" ending is a direct behavioural challenge that touches the boundary of inducing action. Not a hard violation, but a pre-flag is warranted. | Add to Diego flags: (a) "Eso está a punto de cambiar" — consider replacing with "Cuando quieras, está aquí." (b) fallback "¿Y tú?" — consider "El mercado sigue activo." |
| Email Sequence | ⚠️ | A5 email body has no formal sign-off name ("El equipo de Bit2Me" or similar). The body ends with a secondary note ("¿Prefieres seguir a tu ritmo?...") and then immediately transitions to footer — no warm closing line. All other touchpoints (JN-01-A, JN-02B, JN-03) include a closing salutation. | Add "Un saludo, El equipo de Bit2Me" before the footer in A5. |
| A/B Test Rigor | ✅ | T1 and T3 have 1,000/variant. T2, T4 have 500/variant. T5 has 700/variant. All meet or exceed the 500 minimum. Hypotheses are single-variable and specific. Metrics are defined. | None. |
| Marketing Psychology | ⚠️ | A2 Power Variant body: "Un trader de tu nivel no para tanto tiempo." — This uses peer-comparison framing that can slide into shame/guilt territory ("you should have acted"). The validation framework explicitly prohibits guilt language. It's a borderline case — the intention is identity activation, but the phrasing implies the user is failing their identity. | Revise to: "Un trader de tu nivel sabe cuándo volver." — Same identity activation, removes the implicit criticism. Flag for Diego separately. |
| Campaign Execution | ✅ | Send time specified (20:30 CET for push, 10:00 CET for email). Stop conditions defined (trade, earn, price alert, DCA). Art. 66 suppression rule present (portfolio drop >10% → pause journey). Holdout referenced. | None. |
| Creative Briefs | ✅ | Four distinct briefs. Dimensions correct. AI prompts in English. | None. |
| Content Structure | ✅ | All sections present. Diego flags table is complete. Pre-send checklist for Katy is thorough. | None. |

**BLOCKERS:**
None.

**WARNINGS:**
- W-03: A5 Subject B fallback "¿Y tú?" is borderline inducing language — pre-flag for Diego.
- W-04: A2 Power body "no para tanto tiempo" is guilt-adjacent. Fix: "sabe cuándo volver."
- W-05: A5 email is missing closing salutation before footer.

---

### JN-02B — Sleeper to Earn / DCA

**Status:** BLOCKED

| Check | Status | Issue | Fix Required |
|-------|--------|-------|-------------|
| MiCA Compliance | ⚠️ | Earn disclaimer ("Los productos de rendimiento implican riesgo...") is present inline in B3 and B5 HIGH emails. However, it appears BEFORE the EU disclaimer footer — not as part of the footer. The document specifies EU disclaimer "fuente >=12px, ancho completo." The Earn-specific disclaimer does not specify its own minimum font size, creating an implementation risk where the Earn disclaimer could be rendered in small print separate from the standard footer protections. Additionally: in B3 body there is a `[FECHA — COMPLETAR ANTES DE ENVÍO]` placeholder left unfilled. This is a BLOCKER — if sent as-is, users would see the literal placeholder text. | (1) Specify that the Earn disclaimer must also render at >=12px. (2) Fill the date placeholder for the incentive before any send or document submission to Diego. |
| Email Sequence | ⚠️ | B3 B-HIGH email has two concurrent subject line A/B tests (subject line test AB-JN02B-03 AND CTA test AB-JN02B-05) proposed for the same email. Running two tests simultaneously on the same touchpoint conflates variables and invalidates both results. | Separate the CTA test (AB-05) onto B4 or B5 instead. B3 should run only one variable at a time. |
| A/B Test Rigor | ⚠️ | AB-JN02B-03, -04, -06 specify n=400/variant (below the 500 minimum). Test -06 is 300/variant (40% below minimum). This is partly justified by segment size (~4,000 total split HIGH/LOW), but the documents should acknowledge this limitation explicitly. | Add: "Tests -03, -04, -06 are underpowered relative to the 500/variant standard. Treat as directional. Minimum runtime 14 days before reading. No winner declaration below p=0.05." |
| Marketing Psychology | ✅ | Endowment effect framing is correct and consistent. No fear-of-loss language about funds. Urgency is tied to real incentives only. B5 deliberately de-escalates — good practice. | None. |
| Campaign Execution | ✅ | Send times present. Stop conditions documented (opt-out via "No me interesa" CTA creates explicit exit). Art. 66 rule stated (portfolio drop >10%). Holdout implicit (referenced in document structure). | None. |
| Creative Briefs | ✅ | Five distinct briefs (B1 HIGH, B1 LOW, B2 push HIGH/LOW, B3 header HIGH/LOW, B4 variation). Dimensions specified. AI prompts in English. | None. |
| Content Structure | ❌ | BLOCKER: B3 email and B4 incentive copy both contain `[FECHA — COMPLETAR ANTES DE ENVÍO]` as a literal placeholder. Additionally, the footer of all emails contains `CIF [completar]` and `Dirección fiscal [completar]` — these are unfilled legal identifiers that must be present in commercial emails under Spanish commercial law and LSSICE. These are not optional formatting notes — they are required fields. | Fill all three placeholder types before document is submitted to Diego: (1) incentive expiry dates, (2) CIF (Sociedad de Valores — confirm number with Legal/Finance), (3) registered address (currently Calle Príncipe de Vergara 112 is used in JN-01-A; JN-02B uses the same address in body but leaves footer with `[completar]`). |

**BLOCKERS:**
- BLOCKER-01 (HIGH): `[FECHA — COMPLETAR ANTES DE ENVÍO]` placeholder is present in B3 and B4. Cannot be submitted to Diego or loaded into CleverTap in this state. Fill or gate behind product confirmation of incentive dates.
- BLOCKER-02 (HIGH): Footer contains `CIF [completar]` and `Dirección fiscal [completar]`. Required legal fields under LSSICE. Fill before submission. Use CIF and address from JN-01-A footer (already populated there with "Paseo de la Castellana 141, 28046 Madrid") — confirm canonical address with Legal.

**WARNINGS:**
- W-06: Concurrent A/B testing of subject line AND CTA on B3 conflates variables. Move CTA test to B5.
- W-07: Tests -03, -04, -06 are underpowered. Add explicit "directional only" caveat.

---

### JN-03 — Deep Dormant Reactivation

**Status:** PASS WITH WARNINGS

| Check | Status | Issue | Fix Required |
|-------|--------|-------|-------------|
| MiCA Compliance | ✅ | EXCELLENT: The "zero EUR absolute values in D1/D2" rule is enforced at the document level as a named REGLA ABSOLUTA. No EUR values appear in D1 or D2 in any variant. Only % with explicit time period (12 months / since last login). EU disclaimer present in D1 and D2 (full text, >=12px specified). Art. 66 Variante B in D3 explicitly removes "Operar ahora" CTA. | None. |
| Email Sequence | ⚠️ | D2 is gated on "NOT opened D1" — this is correct deliverability practice. However, the document does not specify what happens to users who OPENED D1 but did NOT click. These users are not covered by D2 (since they opened D1) and are not converted (no click). They fall into a gap — no follow-up is defined for "opened but did not convert" from D1. For a 46k dormant audience where open rate of 15-20% is expected (~7-9k opens), this is a meaningful cohort. | Define a D2B or a D1-click-only fallback: users who opened D1 but did not click should receive a variant of D2 (perhaps a shorter "reminder with different CTA angle") on D+14 rather than being dropped from the journey. |
| A/B Test Rigor | ⚠️ | AB-JN03-03 (D3 CTA test "Operar ahora" vs "Activar Earn") has a minimum sample of only 200 logins. This is well below the 500/variant minimum and is noted in the document as "min 200 logins" without a caveat. D3 is a post-login in-app touchpoint dependent on reactivated users, so sample accumulation will be slow — this constraint is real. However, the document should explicitly state this limitation. | Add: "AB-JN03-03 is highly underpowered at N=200. This is a structural constraint of the in-app post-login trigger. Treat as exploratory only. Do not use to make product decisions without supplemental data from BigQuery cohort analysis." |
| Marketing Psychology | ✅ | Curiosity gap framing is precise and correct for this segment. No alarm/panic language. No EUR values in D1/D2 avoids the "calculation-of-exit" effect correctly identified in Copy Rationale. D3 Variante B handles loss scenario correctly (no % shown, neutral CTAs). | None. |
| Campaign Execution | ✅ | Batch schedule with send dates and advance conditions is the most operationally complete of all four documents. Anti-withdrawal monitoring thresholds table is excellent. Stop conditions are clear and owned (Katy, Marta, Daniel). ZeroBounce pre-send checklist is thorough. | None. |
| Creative Briefs | ✅ | All three D-touchpoints have distinct creative briefs. D3 has two visual variants (A and B/C). Dimensions specified. AI prompts in English. | None. |
| Content Structure | ✅ | No unfilled placeholders. All required sections present. Diego flags table covers all compliance elements. The explicit "Piezas a aprobar" section with deadline (Jue 27 Mar) is well-structured for Diego's review. | None. |

**BLOCKERS:**
None.

**WARNINGS:**
- W-08: "Opened D1 but did not click" cohort has no defined follow-up path. Add a D2B touchpoint or extend D2 eligibility.
- W-09: AB-JN03-03 (D3 CTA test) at N=200 is exploratory only — add explicit caveat in document.

---

## Cross-Journey Issues

### Issue X-01: Inconsistent footer address across documents (WARNING)
JN-01-A footer uses "Paseo de la Castellana 141, 28046 Madrid." JN-02A footer uses "Calle Príncipe de Vergara 112, Madrid." JN-03 uses "Calle Príncipe de Vergara 112, Madrid 28002." JN-02B leaves the address as `[completar]`. There must be ONE canonical registered address used in all commercial emails. Confirm with Legal which is the official CNMV-registered address and standardize across all four documents before submission to Diego.

### Issue X-02: Art. 66 suppression signal — not confirmed as built (WARNING)
All four journeys reference the Art. 66 MiCA rule (suppress if portfolio down >10% in 30 days). However, across JN-02A and JN-02B, the implementation is described as "implement as audience filter in CleverTap" or "confirmar con Álvaro que existe una señal de supresión." This signal has not been confirmed as existing in the data layer. If it is not built, **all four journeys are blocked at the infrastructure level regardless of copy approval.** This is the single highest regulatory risk item across the wave.
- Action: Álvaro must confirm the `portfolio_change_30d` signal exists in CleverTap profile data or BigQuery Gold Layer before any journey launches.

### Issue X-03: "Invierte" in MiCA footer (NOTE)
The MiCA footer used across all documents ends with "Invierte solo lo que puedas permitirte perder." The word "Invierte" (imperative form of "invertir") appears here — which is one of the words on the prohibited-word scan list. This specific usage is a standard CNMV/MiCA-mandated disclaimer phrase (direct translation of "invest only what you can afford to lose") and is not commercial inducement. However, since the scan was requested to flag ALL occurrences, this is noted: the word appears ONLY in the compliance footer, not in any commercial copy body. This is correct and compliant. No fix required — but Diego should confirm this is the canonical approved disclaimer text.

### Issue X-04: Holdout reference inconsistency (NOTE)
JN-01-A explicitly states "El 10% holdout global (zero messages) se mantiene separado de todos los variants." JN-02A references it indirectly in the pre-send checklist. JN-02B does not explicitly reference holdout. JN-03 references it in Diego approval table as "Informativo — sin implicación legal." For statistical validity of all cross-journey analysis, the holdout must be consistent. Recommend adding an explicit holdout statement to JN-02B.

---

## Ready for Diego?

| File | Status | Caveats |
|------|--------|---------|
| JN-01-A | YES | Flags D-01 to D-06 are already pre-documented in the file. Diego can review as-is. |
| JN-02A | YES WITH CAVEATS | Recommend fixing W-04 (guilt language in A2 Power) and W-03 (Subject B fallback "¿Y tú?") before submission. Not blockers — but Diego will flag them anyway. |
| JN-02B | NO | Must resolve BLOCKER-01 (date placeholders) and BLOCKER-02 (CIF + address in footer) before submission. The document as written cannot be submitted for legal review with unfilled required fields. |
| JN-03 | YES WITH CAVEATS | Strong document. Recommend adding the "opened but not clicked" cohort handling (W-08) before submission as Diego may ask about it. Otherwise ready. |

---

## Action Items for Daniel
*Priority ordered — must complete before Wave 1 launch*

### P0 — Before any document goes to Diego or CleverTap

1. **Confirm Art. 66 suppression signal exists** (owner: Álvaro): All 4 journeys depend on a `portfolio_change_30d` or equivalent suppression signal in CleverTap. If this does not exist in the data layer, the journeys cannot launch regardless of copy approval. Get written confirmation from Álvaro this week.

2. **Fill JN-02B date placeholders**: B3 and B4 contain `[FECHA — COMPLETAR ANTES DE ENVÍO]`. Confirm incentive dates with Product (Katy coordinates) and fill before submission. Do not submit JN-02B to Diego with empty fields.

3. **Standardize footer address**: Confirm canonical CNMV-registered address with Legal. Apply consistently to all 4 documents. JN-02B footer also needs CIF filled. This is a legal requirement under LSSICE — not optional.

### P1 — Before CleverTap setup (after Diego approval)

4. **Revise JN-02A A2 Power body**: "Un trader de tu nivel no para tanto tiempo" → "Un trader de tu nivel sabe cuándo volver." Removes guilt framing before Diego review.

5. **Add closing salutation to JN-02A A5 email**: Body currently ends with secondary note and jumps to footer. Add "Un saludo, El equipo de Bit2Me" before footer.

6. **Separate A/B tests on JN-02B B3**: Do not run subject line test AND CTA test simultaneously on the same email. Move CTA test (AB-JN02B-05) to B4 or B5.

7. **Add "directional only" caveat to underpowered tests**: JN-01-A AB-01/02 (n=75/variant), JN-02B AB-03/04/06 (n=300-400/variant), JN-03 AB-03-03 (n=200). All need explicit notation that results are directional, not decision-grade.

### P2 — Before Wave 1 analysis (after launch)

8. **Define D2B for JN-03 "opened but did not click" cohort**: ~7-9k users expected to open D1 but not click. Define whether they receive D2 on D+14 or are treated as "soft converts" requiring a separate path.

9. **Add explicit holdout statement to JN-02B**: Reference the 10% global holdout the same way JN-01-A does, for analytical consistency.

10. **Confirm CleverTap template engine supports `{% if %}` conditional logic** (owner: Katy): Required for incentive blocks in JN-01-A and JN-02B. This is flagged in JN-01-A as D-06 but needs a concrete YES/NO answer before any template is built.

---

*Report generated: 2026-03-24*
*Reviewed by: Automated 7-point framework validator*
*Distribution: Daniel Ferraro (owner), Diego Barreira (legal gate — after P0 items resolved)*
