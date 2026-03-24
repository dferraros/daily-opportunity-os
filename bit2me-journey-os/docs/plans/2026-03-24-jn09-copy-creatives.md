# JN-09 — Purchase-Sell Churn Prevention
## Copy Package & Creative Briefs
**Version:** 1.0 — 2026-03-24
**Status:** DRAFT — Pending Diego Legal Review
**Author:** CRM Team / Lifecycle OS
**MiCA Compliance:** Art. 66 — CRITICAL. See Section 9.

---

## 1. Dynamic Variables & P&L Routing Logic

### 1.1 Variable Definitions

| Variable | Source | Example Value | Fallback |
|---|---|---|---|
| {{nombre}} | CRM profile — first name | "Carlos" | "inversor" |
| {{sold_asset}} | sell event — asset name | "Bitcoin" | "tu activo" |
| {{sold_amount_eur}} | sell event — EUR value at execution | "EUR 340" | omit field |
| {{pnl_pct}} | calculated — (sold - purchase) / purchase | "+12.4%" or "-8.2%" | omit field |
| {{pnl_eur}} | calculated — sold_amount - purchase_amount | "+EUR 42" or "-EUR 28" | omit field |
| {{remaining_balance_eur}} | portfolio snapshot post-sell | "EUR 215" | omit — never show if triggers panic |
| {{suggested_next_asset}} | algo recommendation — top mover | "Ethereum" | "ETH" |
| {{earn_apy_for_remaining}} | Earn product rate for remaining balance | "4.8% APY" | "un APY competitivo" |

### 1.2 P&L Routing Table

| Condition | Variant | Tone | Financial CTAs Allowed |
|---|---|---|---|
| pnl_pct > 0 | GAIN | Celebratory, peer energy | Earn, diversify, next buy |
| pnl_pct >= -10% AND pnl_pct <= 0 | LOSS-SMALL | Calm, steady | View portfolio only. No reinvestment push |
| pnl_pct < -10% | LOSS-LARGE | Warm, zero pressure | Ver portfolio OR Retirar ONLY — Art. 66 MiCA strict |

### 1.3 Routing Decision Flow

```
sell event received
  └─ is_full_position_sell = true?
       └─ purchase_date >= 30 days ago?
            └─ remaining_balance_eur > 10?
                 └─ account_status = enabled?
                      └─ calculate pnl_pct
                           ├─ pnl_pct > 0           → GAIN variant
                           ├─ -10% <= pnl_pct <= 0  → LOSS-SMALL variant
                           └─ pnl_pct < -10%        → LOSS-LARGE variant (Art. 66 active)
```

---

## 2. R1 — Push Notification (Real-Time, < 5 min after sell)

**Channel:** CleverTap push (iOS + Android)
**Timing:** Trigger fires within 5 minutes of sell event confirmation
**Char limits:** Title max 50 chars — Body max 90 chars
**Universal rule:** "Retirar" deep-link available via notification settings / account menu. Not in push body (space constraint) but accessible.

---

### 2.1 GAIN Variant — Push

**Version A (emphasis: next move)**

- Title: `¡Bien hecho, {{nombre}}! +{{pnl_eur}} en {{sold_asset}}`
- Body: `Tienes saldo libre. ¿Lo pones a trabajar o exploras {{suggested_next_asset}}?`

*Character count — Title: ~42 chars (with values) — Body: ~70 chars*

**Version B (emphasis: Earn)**

- Title: `{{nombre}}, tu {{sold_asset}} generó {{pnl_pct}} 🎯`
- Body: `Tu saldo puede generar {{earn_apy_for_remaining}} mientras decides qué hacer. Actívalo ya.`

*Character count — Title: ~44 chars (with values) — Body: ~88 chars*

**Fallback (no pnl data):**
- Title: `Venta ejecutada, {{nombre}}`
- Body: `Tu saldo está listo. ¿Qué quieres hacer ahora con él?`

---

### 2.2 LOSS-SMALL Variant — Push

**Single version (no A/B — sensitive tone, consistency required)**

- Title: `Venta completada, {{nombre}}`
- Body: `Tu saldo sigue aquí. Los mercados fluctúan — tu cuenta está lista cuando quieras.`

*Character count — Title: 28 chars — Body: 80 chars*

**Fallback (same):**
- Title: `Venta completada, {{nombre}}`
- Body: `Tu saldo sigue aquí. Tu cuenta está lista cuando quieras.`

---

### 2.3 LOSS-LARGE Variant — Push (Art. 66 MiCA — ZERO financial product mentions)

**Single version — strictly informational**

- Title: `Venta registrada, {{nombre}}`
- Body: `Tu saldo restante está seguro en tu cuenta. Sin prisa. Aquí cuando lo necesites.`

*Character count — Title: 28 chars — Body: 78 chars*

**Fallback (same structure):**
- Title: `Venta registrada, {{nombre}}`
- Body: `Tu cuenta está en orden. Sin prisa. Aquí cuando lo necesites.`

---

## 3. R2 — In-App Card (Next app open, same or next session)

**Channel:** CleverTap in-app message — card format
**Timing:** Next app open after sell event (same session or next login, within 24h window)
**Format:** Card — Title + Body + CTA Primary + CTA Secondary (always "Retirar")
**Note:** CTA Secondary "Retirar" is MANDATORY in ALL variants — no exceptions.

---

### 3.1 GAIN Variant — In-App Card

**Version A (Diversify)**

- **Title:** `Lo hiciste bien, {{nombre}}`
- **Body:** `Tu operación en {{sold_asset}} cerró con {{pnl_pct}} de ganancia ({{pnl_eur}}). El mercado sigue abierto. ¿Quieres explorar {{suggested_next_asset}} u otras oportunidades?`
- **CTA Primary:** `Ver mercados`
- **CTA Secondary:** `Retirar fondos`

**Version B (Earn)**

- **Title:** `{{pnl_eur}} ganados en {{sold_asset}}. ¿Y ahora?`
- **Body:** `Tu saldo libre puede estar generando {{earn_apy_for_remaining}} en Earn mientras decides tu próximo movimiento. Sin compromiso de permanencia.`
- **CTA Primary:** `Activar Earn`
- **CTA Secondary:** `Retirar fondos`

*Earn disclaimer required if Version B is shown — see Section 4.3*

---

### 3.2 LOSS-SMALL Variant — In-App Card

**Single version**

- **Title:** `Tu saldo sigue contigo, {{nombre}}`
- **Body:** `Has vendido tu posición en {{sold_asset}}. Los mercados tienen altibajos — es parte del proceso. Tu cuenta sigue activa y tu saldo disponible.`
- **CTA Primary:** `Ver mi portfolio`
- **CTA Secondary:** `Retirar fondos`

---

### 3.3 LOSS-LARGE Variant — In-App Card (Art. 66 MiCA — strict)

**Single version — warm, zero pressure, zero financial advice**

- **Title:** `Entendemos, {{nombre}}`
- **Body:** `Tu posición en {{sold_asset}} ha sido vendida. Tu saldo restante está seguro aquí. No hay ninguna prisa — toma el tiempo que necesites.`
- **CTA Primary:** `Ver mi portfolio`
- **CTA Secondary:** `Retirar fondos`

**DIEGO FLAG — Art. 66:** Esta tarjeta no menciona ningún producto financiero, rentabilidad, ni sugiere ninguna acción de compra o reinversión. Los únicos CTAs son consulta de portfolio o retirada. Cumple Art. 66 MiCA estrictamente.

---

## 4. R3 — Email (2h after sell, only if no R1/R2 engagement)

**Channel:** Email (CleverTap email module)
**Timing:** 2h after sell event — only sends if user has NOT engaged with R1 push or R2 in-app card
**Condition:** send_r3 = true ONLY IF (r1_clicked = false AND r2_engaged = false)
**Footer required:** EU regulatory footer — Paseo de la Castellana 141, 28046 Madrid, España
**Earn disclaimer:** Required in GAIN variant only if APY is mentioned

---

### 4.1 GAIN Variant — Email

**Subject A:** `{{nombre}}, {{sold_asset}} te dejó {{pnl_pct}}. ¿Qué hacemos ahora?`
**Subject B:** `+{{pnl_eur}} ganados. Tu próximo movimiento está aquí.`
**Preheader:** `Tu saldo está listo. Hay opciones que quizás no habías considerado.`

---

**BODY:**

Hola, {{nombre}}.

Tu venta de {{sold_asset}} se completó con éxito.

Resultado: **{{pnl_pct}}** — o lo que es lo mismo, **{{pnl_eur}}** de ganancia sobre tu inversión original.

Ahora tienes saldo disponible. Algunas ideas de qué puedes hacer:

**Explorar {{suggested_next_asset}}**
El mercado sigue activo. Si quieres diversificar o mantener exposición a cripto, {{suggested_next_asset}} es una de las opciones más consultadas ahora mismo en Bit2Me.

**Poner tu saldo a trabajar con Earn**
Si aún no has decidido tu próximo movimiento, Earn te permite obtener {{earn_apy_for_remaining}} sobre tu saldo disponible. Sin compromiso de permanencia mínima.

*Earn es un producto de recompensas. La tasa APY es variable y no garantizada. Consulta las condiciones completas en bit2me.com/earn.*

O simplemente **mantén tu saldo** en la cuenta hasta que estés listo. No hay prisa.

[Ver mercados] [Activar Earn] [Retirar fondos]

---

Un saludo,
El equipo de Bit2Me

---

*Bit2Me es un proveedor de servicios de activos virtuales registrado en el Banco de España. Este mensaje es informativo y no constituye asesoramiento financiero. Las operaciones con criptomonedas conllevan riesgo de pérdida parcial o total del capital.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*Para dejar de recibir estas comunicaciones: [Cancelar suscripción]*

---

### 4.2 LOSS-SMALL Variant — Email

**Subject A:** `Tu venta de {{sold_asset}} está completada, {{nombre}}`
**Subject B:** `{{nombre}}, tu saldo sigue aquí`
**Preheader:** `Todo en orden. Tu cuenta sigue activa y tu saldo disponible.`

---

**BODY:**

Hola, {{nombre}}.

Tu venta de {{sold_asset}} se ha ejecutado correctamente.

Tu saldo está disponible en tu cuenta. No hay nada que tengas que hacer ahora mismo — todo sigue en orden.

Los mercados de criptomonedas tienen volatilidad. Es algo con lo que conviven todos los inversores, independientemente de su experiencia. Lo importante es que tu cuenta está activa y accesible en todo momento.

**¿Qué puedes hacer ahora?**

Puedes revisar tu portfolio para ver la composición actual de tus activos, o retirar tu saldo si así lo prefieres. La decisión es tuya.

[Ver mi portfolio] [Retirar fondos]

---

Un saludo,
El equipo de Bit2Me

---

*Bit2Me es un proveedor de servicios de activos virtuales registrado en el Banco de España. Este mensaje es informativo y no constituye asesoramiento financiero. Las operaciones con criptomonedas conllevan riesgo de pérdida parcial o total del capital.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*Para dejar de recibir estas comunicaciones: [Cancelar suscripción]*

---

### 4.3 LOSS-LARGE Variant — Email (Art. 66 MiCA — STRICT)

**Subject A:** `Tu venta está registrada, {{nombre}}`
**Subject B:** `{{nombre}}, tu saldo está seguro`
**Preheader:** `Nada urgente. Tu cuenta está en orden y aquí cuando la necesites.`

---

**BODY:**

Hola, {{nombre}}.

Tu venta de {{sold_asset}} se ha completado y está registrada en tu cuenta.

Queremos que sepas que tu saldo restante está seguro y disponible. No hay ninguna urgencia.

Entendemos que las operaciones no siempre salen como uno espera. Es una parte real de los mercados de activos digitales. No te escribimos para darte consejos ni para pedirte que hagas nada en concreto.

Si quieres revisar el estado de tu portfolio, puedes hacerlo cuando quieras. Y si prefieres retirar tu saldo, también está disponible sin coste adicional.

Tu cuenta sigue abierta y tu dinero es tuyo.

[Ver mi portfolio] [Retirar fondos]

---

Un saludo,
El equipo de Bit2Me

---

*Bit2Me es un proveedor de servicios de activos virtuales registrado en el Banco de España. Este mensaje es informativo y no constituye asesoramiento financiero. Las operaciones con criptomonedas conllevan riesgo de pérdida parcial o total del capital.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*Para dejar de recibir estas comunicaciones: [Cancelar suscripción]*

**DIEGO FLAG — Art. 66:** Este email no menciona ningún producto de inversión, rentabilidad, estrategia de compra, DCA ni ningún otro producto financiero. Los únicos CTAs son portfolio view y retirada. Cumplimiento estricto Art. 66 MiCA confirmado. Pendiente revisión legal antes de activación.

---

## 5. Creative Briefs

### 5.1 GAIN — Push / In-App Card

**Format:** Push notification visual + in-app card banner
**Dimensions:** Push: platform native (iOS 1024x1024 icon, Android adaptive icon) — In-app card: 1080x540px (2:1 ratio)
**Mood:** Energetic, clean, peer celebration. Think: trading floor green moment. Not flashy, not Vegas. Smart money energy.
**Color palette:** Deep navy (#0A1628) background — Electric green (#00E676) for P&L number — White text — Bit2Me orange (#FF6B2B) for CTA
**Typography:** Bold headline — P&L number oversized and prominent — Body text light weight
**Visual elements:** Subtle upward chart line or abstract upward arrow. No coin/rocket imagery. Premium feel.

**AI image generation prompt (English):**
"Minimalist financial app notification card, dark navy background #0A1628, large bold green percentage number center, abstract clean upward trending line graph, white sans-serif typography, electric green accent #00E676, orange CTA button, no cryptocurrency coins, no rockets, premium fintech aesthetic, 1080x540px, flat design"

---

### 5.2 GAIN — Email

**Format:** HTML email header banner
**Dimensions:** 600px wide x 200px tall
**Mood:** Calm success. Professional but warm. The feeling after a good decision, not a party.
**Color palette:** White background — Bit2Me dark blue (#0A1628) for text — Green (#00D97E) for P&L highlight — Orange (#FF6B2B) for CTA
**Visual elements:** Clean horizontal layout. Left: personalized P&L callout. Right: subtle abstract chart. Bit2Me logo top left.

**AI image generation prompt (English):**
"Clean minimal email header banner 600x200px, white background, dark blue left section with bold green profit percentage text, right section with subtle abstract upward chart illustration, professional fintech style, no coins no cryptocurrency logos, Bit2Me brand colors navy and orange, white space dominant, corporate yet warm"

---

### 5.3 LOSS-SMALL — All Channels

**Format:** Push + in-app card + email header
**Dimensions:** Same as GAIN specs above
**Mood:** Neutral steadiness. Like a calm friend who acknowledges things without drama. No green numbers. No celebration. No warning red.
**Color palette:** Soft grey background (#F5F7FA) — Dark text (#1A1A2E) — Bit2Me blue (#0A4C9E) for accents — Neutral grey for secondary elements
**Visual elements:** Clean account balance icon or simple shield icon (security, stability). No charts. No directional arrows.

**AI image generation prompt (English):**
"Calm reassuring fintech app card, light grey background #F5F7FA, dark navy text, simple clean shield or wallet icon center, no charts no arrows no profit loss indicators, neutral professional tone, Bit2Me blue accent #0A4C9E, minimal white space design, 1080x540px, corporate trustworthy aesthetic"

---

### 5.4 LOSS-LARGE — All Channels (Art. 66 Active)

**Format:** Push + in-app card + email header
**Dimensions:** Same as above
**Mood:** Human warmth. Zero urgency. Zero financial imagery. The visual equivalent of "we're here, no rush."
**Color palette:** Warm white (#FAFAF8) — Soft charcoal text (#2C2C2C) — Muted blue (#6B8CAE) — No green, no red anywhere in the creative
**Visual elements:** Abstract soft texture or simple open-door silhouette. No financial charts, no coins, no balance indicators. Absolute visual calm.
**CRITICAL:** No upward/downward arrows. No charts. No percentage visuals. No coin imagery. Any visual that implies financial direction is prohibited under the same spirit as Art. 66.

**AI image generation prompt (English):**
"Warm minimal app notification card, soft warm white background, muted blue-grey tones, abstract gentle texture or simple open doorway silhouette, zero financial imagery, no charts no arrows no coins no graphs, human warmth and calm atmosphere, soft charcoal typography, 1080x540px, non-directional completely neutral fintech aesthetic"

---

## 6. A/B Test Register

### Test 01 — GAIN Push: Next Move vs Earn

| Field | Detail |
|---|---|
| Test ID | JN09-AB-001 |
| Channel | Push notification |
| Variant A | Title emphasizes next asset — body: "¿Lo pones a trabajar o exploras {{suggested_next_asset}}?" |
| Variant B | Title emphasizes Earn — body: "Tu saldo puede generar {{earn_apy_for_remaining}}" |
| Primary metric | Tap-through rate (CTR) |
| Secondary metric | Conversion to Earn activation or new buy within 48h |
| Sample size | Min 50 GAIN events per variant (100 total) before reading |
| Duration | Until significance reached or 30 days |
| Kill condition | If either variant CTR < 1%, pause and review |
| Owner | Katy (CleverTap) |

---

### Test 02 — GAIN Email: Subject line frame

| Field | Detail |
|---|---|
| Test ID | JN09-AB-002 |
| Channel | Email |
| Variant A | Subject: "{{nombre}}, {{sold_asset}} te dejó {{pnl_pct}}. ¿Qué hacemos ahora?" |
| Variant B | Subject: "+{{pnl_eur}} ganados. Tu próximo movimiento está aquí." |
| Primary metric | Open rate |
| Secondary metric | Click-to-open rate on [Ver mercados] CTA |
| Sample size | Min 50 GAIN email sends per variant |
| Duration | Until significance or 30 days |
| Kill condition | Open rate < 15% for both → escalate subject copy |
| Owner | Katy (CleverTap) |

---

### Test 03 — LOSS-SMALL In-App: CTA label test

| Field | Detail |
|---|---|
| Test ID | JN09-AB-003 |
| Channel | In-app card |
| Variant A | CTA Primary: "Ver mi portfolio" |
| Variant B | CTA Primary: "Ver mi saldo" |
| Primary metric | CTA tap rate |
| Secondary metric | Withdrawal rate post-tap (must NOT increase vs control) |
| Sample size | Min 30 LOSS-SMALL events per variant |
| Duration | Until significance or 30 days |
| Kill condition | If "Ver mi saldo" increases withdrawal rate vs "Ver mi portfolio" by >10%, revert to A |
| Owner | Katy (CleverTap) |

---

### Test 04 — GAIN In-App: Diversify vs Earn CTA

| Field | Detail |
|---|---|
| Test ID | JN09-AB-004 |
| Channel | In-app card |
| Variant A | CTA: "Ver mercados" (diversify frame) |
| Variant B | CTA: "Activar Earn" (earn frame) |
| Primary metric | CTA tap rate |
| Secondary metric | Earn activation rate / new buy within 72h |
| Sample size | Min 50 GAIN events per variant |
| Duration | Until significance or 30 days |
| Kill condition | Withdrawal rate increases > control +10% in either variant |
| Owner | Katy (CleverTap) |

---

## 7. Fallback & P&L Routing Table

### 7.1 Variable Fallback Hierarchy

| Variable | Primary | Fallback L1 | Fallback L2 |
|---|---|---|---|
| {{nombre}} | CRM first name | "inversor" | — |
| {{sold_asset}} | Event asset name | "tu activo" | omit from sentence |
| {{sold_amount_eur}} | Event EUR value | omit field | — |
| {{pnl_pct}} | Calculated % | omit % reference | switch to generic copy |
| {{pnl_eur}} | Calculated EUR | omit EUR reference | switch to generic copy |
| {{remaining_balance_eur}} | Portfolio snapshot | omit — never substitute | — |
| {{suggested_next_asset}} | Algo output | "ETH" | "Ethereum" |
| {{earn_apy_for_remaining}} | Earn rate API | "un APY competitivo" | omit Earn offer |

### 7.2 Full Fallback Copy (when pnl data unavailable)

**GAIN — Push fallback:**
- Title: `Tu venta en {{sold_asset}} se completó, {{nombre}}`
- Body: `Tienes saldo disponible. ¿Qué quieres hacer ahora?`

**LOSS-SMALL — Push fallback:** (same as primary — no pnl data needed in this variant)
- Title: `Venta completada, {{nombre}}`
- Body: `Tu saldo sigue aquí. Tu cuenta está lista cuando quieras.`

**LOSS-LARGE — Push fallback:** (same as primary — intentionally no pnl data shown)
- Title: `Venta registrada, {{nombre}}`
- Body: `Tu saldo restante está seguro en tu cuenta. Sin prisa.`

### 7.3 P&L Routing Edge Cases

| Edge Case | Handling |
|---|---|
| pnl_pct = exactly 0 (breakeven) | Route to LOSS-SMALL |
| pnl_pct unavailable (data lag) | Hold send up to 15 min. If still unavailable, route to LOSS-SMALL as safe default |
| remaining_balance_eur <= 10 | Journey does NOT trigger (exit condition) |
| remaining_balance_eur unavailable | Do NOT show balance. Use variant copy without balance reference |
| User initiates withdrawal before R1 fires | Cancel all pending sends. Exit to win-back journey |
| User executes new buy before R2 fires | Cancel R2 and R3. Journey terminates — re-engaged |

---

## 8. Kill Switch Monitoring Table

| Metric | Baseline (control) | Warning Threshold | Kill Threshold | Action |
|---|---|---|---|---|
| Withdrawal rate — GAIN variant | TBD at launch | Control +10% | Control +20% | Pause ALL JN-09 GAIN sends. Escalate to Daniel. |
| Withdrawal rate — LOSS-SMALL variant | TBD at launch | Control +10% | Control +20% | Pause ALL JN-09 LOSS-SMALL sends. Escalate. |
| Withdrawal rate — LOSS-LARGE variant | TBD at launch | Control +5% | Control +15% | Immediate pause. Escalate to Daniel + Diego. |
| Unsubscribe rate (email) | Platform avg ~0.3% | 0.6% | 1.0% | Pause email channel. Review tone and frequency. |
| Complaint / spam rate (email) | Platform avg ~0.05% | 0.1% | 0.2% | Immediate pause. Review all email copy. |
| Push opt-out rate | Platform avg ~1% | 2% | 3% | Pause push. Review frequency and tone. |
| R3 email open rate (LOSS-LARGE) | Expected ~18% | <12% | <8% | Review subject lines. Consider suppressing email for this variant. |

**Kill switch owner:** Daniel Ferraro
**Monitoring cadence:** Daily during first 30 days post-launch. Weekly thereafter.
**Escalation path:** Daniel → Diego (if legal concern) → Pablo Campos (if withdrawal rate hits kill threshold)

---

## 9. Diego Approval Notes — Legal & MiCA Compliance

### 9.1 Art. 66 MiCA — LOSS-LARGE Variant

**This is the highest legal sensitivity variant in the entire journey.**

ALL LOSS-LARGE touchpoints (R1 push, R2 in-app card, R3 email) comply with Art. 66 MiCA by design:

- Zero mention of buying, investing, DCA, cost-averaging, or any financial product
- Zero mention of potential returns, APY, yields, or any performance indicator
- Zero urgency language
- CTAs are limited exclusively to: "Ver mi portfolio" and "Retirar fondos"
- "Retirar fondos" is always visible and always functional
- Language is declarative and informational only ("Tu saldo está seguro")
- No comparative market language ("ahora es buen momento", "el mercado va a subir")

**Diego: please confirm this interpretation of Art. 66 is sufficient, or flag additional constraints.**

### 9.2 GAIN Variant — Earn Disclaimer

The GAIN variant (R2 in-app card Version B and R3 email) mentions Earn APY. The following disclaimer is required:

*"Earn es un producto de recompensas. La tasa APY es variable y no garantizada. Consulta las condiciones completas en bit2me.com/earn."*

This disclaimer MUST appear:
- In the in-app card body (below Earn mention, before CTA)
- In the email body (below Earn section, before CTAs)
- It is NOT required in push notifications (character limit and format)

**Diego: please confirm disclaimer wording is compliant or provide revised text.**

### 9.3 Prohibited Language — Full List Applied

The following substitutions have been applied throughout ALL copy:

| Prohibited | Used instead |
|---|---|
| "invertir" | "operar" / "explorar" / "actuar" |
| "rendimiento" | "APY" (with disclaimer) |
| "beneficios" | "recompensas" / "ganancia" (factual, not forward-looking) |
| "depositar" | "añadir" / "transferir" |
| "garantizado" | removed entirely — APY described as variable |
| Guaranteed returns language | removed entirely |
| "ahora es el momento" (market timing) | removed entirely |

### 9.4 Regulatory Footer — Email

Present in ALL three email variants:

*"Bit2Me es un proveedor de servicios de activos virtuales registrado en el Banco de España. Este mensaje es informativo y no constituye asesoramiento financiero. Las operaciones con criptomonedas conllevan riesgo de pérdida parcial o total del capital."*

*Paseo de la Castellana 141, 28046 Madrid, España*

### 9.5 "Retirar" Availability — All Channels

Per journey spec: the option to withdraw is always present and functional.

- **R1 Push:** Withdrawal accessible via account menu (deep-link available on tap if platform allows; otherwise CTA leads to app home with visible withdrawal path)
- **R2 In-App Card:** "Retirar fondos" is the mandatory secondary CTA in ALL variants — including GAIN
- **R3 Email:** "Retirar fondos" button present in ALL email variants as standalone CTA

**Diego: no additional action required on this point unless you identify a channel-specific concern.**

### 9.6 Sign-off Checklist for Diego

- [ ] Art. 66 compliance confirmed — LOSS-LARGE variant (R1, R2, R3)
- [ ] Earn disclaimer wording approved — GAIN variant (R2 Version B, R3 email)
- [ ] Prohibited language substitutions approved
- [ ] Regulatory footer wording approved
- [ ] "Retirar" visibility requirement confirmed as met across channels
- [ ] Kill switch thresholds reviewed (Section 8) — legal concern if withdrawal rate spikes

---

*Document prepared by: CRM / Lifecycle OS Team*
*For legal review: Diego Barreira*
*Date: 2026-03-24*
*Journey: JN-09 — Purchase-Sell Churn Prevention*
*Version: 1.0 DRAFT*
