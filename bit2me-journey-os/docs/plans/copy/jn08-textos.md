# JN-08 — Stablecoin Parkers Earn: Textos

---

## S0 — Email (D+0)

**Asunto A:** Tus {{stablecoin}} generan 0% ahora. Podrían generar {{earn_apy}}%.
**Asunto B:** {{stablecoin_balance}} {{stablecoin}} parados. {{earn_apy}}% disponible en Earn.
**Preheader:** Sin lock-up. Retira cuando quieras.

---

Hola {{nombre}},

Tienes {{stablecoin_balance}} {{stablecoin}} en tu cuenta. Ahora mismo generan 0%.

Earn ofrece {{earn_apy}}% APY sobre tu saldo. Sin lock-up: retiras cuando quieras, sin penalización.

Con tu saldo actual, eso es aproximadamente EUR {{yield_mensual}} al mes.

[Activar Earn] → bit2me://earn/{{stablecoin}}

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

## S1 — In-app (D+3, login reciente)

**Header:** Genera {{earn_apy}}% con tus {{stablecoin_balance}} {{stablecoin}}.
**Body:** Sin lock-up. Retira cuando quieras.
**CTA:** Activar Earn → bit2me://earn/{{stablecoin}}

---

## S2 — Push (D+5, CONDICIONAL — solo si BTC movimiento >5% en 24h)

**Título:** BTC {{direction}} {{change}}%
**Cuerpo:** Tienes {{stablecoin_balance}} {{stablecoin}} listos.
**Deep link:** bit2me://market/BTC

NOTA: Si no hay señal BTC >5% en 24h, NO enviar este push.

---

## S3 — Email (D+10)

**Asunto A:** EUR {{yield_anual}} al año. Sin hacer nada.
**Asunto B:** Cálculo: qué genera tu saldo con Earn en 1, 6 y 12 meses
**Preheader:** Números exactos para tu saldo actual.

---

Hola {{nombre}},

Qué generaría tu saldo de {{stablecoin_balance}} {{stablecoin}} con Earn al {{earn_apy}}% APY:

| Período | Rendimiento estimado |
|---------|---------------------|
| 1 mes | EUR {{yield_mensual}} |
| 6 meses | EUR {{yield_6m}} |
| 12 meses | EUR {{yield_anual}} |

Sin lock-up. Retiras cuando quieras.

[Activar Earn] → bit2me://earn/{{stablecoin}}

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

## S4 — In-app (D+15, login + no Earn activo)

**Header:** Tus {{stablecoin_balance}} {{stablecoin}} en Earn: EUR {{yield_mensual}}/mes.
**Body:** Retira cuando quieras.
**CTA:** Activar ahora → bit2me://earn/{{stablecoin}}

---

## S5 — Email (D+21)

**Asunto:** Tus stablecoins, tu decisión.
**Preheader:** Último recordatorio. Sin presión.

---

Hola {{nombre}},

Si ahora mismo no quieres activar Earn, está bien.

El APY sigue disponible cuando quieras. Tu saldo no va a ningún sitio y no tienes que hacer nada.

Si en algún momento cambias de idea, lo tienes aquí.

[Leer más sobre Earn] → bit2me://earn

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

## QA Checklist

- [ ] Segmento validado: USDT y/o USDC en cartera + sin Earn activo
- [ ] S2 push solo se envía con señal BTC >5% en 24h confirmado en lógica de disparo
- [ ] Push opt-out guardrail: parar si opt-out >1% del segmento
- [ ] Holdout 10% aplicado
- [ ] Diego aprueba todos los textos antes de activación
