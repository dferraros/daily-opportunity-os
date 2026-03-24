# JN-09 — Purchase-Sell Churn Prevention: Textos

---

## S0 — In-app modal (0-5 min post-venta)

### [GANANCIA]

**Header:** Has vendido {{asset}} con +{{pnl}}%.
**Body:** ¿Qué hacer con tus EUR {{balance}}?
**CTA1:** Reinvertir → bit2me://market
**CTA2:** Activar Earn → bit2me://earn
**CTA3:** DCA automático → bit2me://dca
**CTA4 (visible pero no destacado):** Retirar → bit2me://withdraw

---

### [PÉRDIDA <10%]

**Header:** Has cerrado tu posición en {{asset}}.
**Body:** Tus EUR {{balance}} están disponibles. El DCA puede reducir el impacto de la volatilidad en futuras compras.
**CTA1:** Configurar DCA → bit2me://dca
**CTA2:** Activar Earn → bit2me://earn
**CTA4 (visible):** Retirar → bit2me://withdraw

---

### [PÉRDIDA >10%]

**Header:** Posición cerrada.
**Body:** Tus EUR {{balance}} están disponibles. Si quieres entender mejor la gestión de riesgo, tenemos recursos en la academia.
**CTA1:** Explorar guía de riesgo → bit2me://academy
**CTA2 (siempre visible):** Retirar → bit2me://withdraw

NOTA: NO push de reinversión en este caso (Art. 66 MiCA)

---

## S1 — Push (D+1)

### [GANANCIA]

**Título:** Tus EUR {{balance}} disponibles
**Cuerpo:** ¿Listo para el siguiente paso?
**Deep link:** bit2me://market

---

### [PÉRDIDA <10%]

**Título:** DCA: convierte la volatilidad en oportunidad
**Cuerpo:** Compra automática desde EUR 5/sem.
**Deep link:** bit2me://dca

---

### [PÉRDIDA >10%]

NO ENVIAR

---

## S2 — Email (D+3)

### [GANANCIA]

**Asunto A:** Tienes EUR {{balance}} en Bit2Me. 3 opciones.
**Asunto B:** {{nombre}}, ¿qué harías con {{balance}} EUR?
**Preheader:** Earn, DCA o diversificar. Tú decides.

---

Hola {{nombre}},

Vendiste {{asset}} con una ganancia de +{{pnl}}%. Tus EUR {{balance}} están disponibles ahora mismo.

Tienes tres opciones:

**Earn**
Genera {{earn_apy}}% APY sobre tu saldo en EUR o stablecoins. Sin lock-up. Retira cuando quieras.

**DCA automático**
Configura una compra recurrente desde EUR 5 por semana. Entra al mercado de forma sistemática, sin tener que tomar decisiones cada vez.

**Diversificar en otro activo**
Explora el catálogo de Bit2Me y añade exposición a otros activos.

[Activar Earn] → bit2me://earn
[Configurar DCA] → bit2me://dca
[Explorar mercado] → bit2me://market

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

### [PÉRDIDA <10%]

**Asunto A:** Tienes EUR {{balance}} en Bit2Me. 2 opciones.
**Asunto B:** {{nombre}}, tus EUR {{balance}} disponibles
**Preheader:** Earn o DCA. Sin decisiones complicadas.

---

Hola {{nombre}},

Tu posición en {{asset}} está cerrada. Tus EUR {{balance}} están disponibles.

Dos opciones para tu saldo:

**Earn**
Genera {{earn_apy}}% APY sobre tu saldo. Sin lock-up. Retira cuando quieras.

**DCA automático**
Vuelve al mercado con compras automáticas desde EUR 5 por semana. El DCA distribuye el riesgo de entrada a lo largo del tiempo.

[Activar Earn] → bit2me://earn
[Configurar DCA] → bit2me://dca

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

### [PÉRDIDA >10%]

**Asunto:** Inversión responsable: guía de gestión de riesgo

---

Hola {{nombre}},

Tu posición en {{asset}} está cerrada. Tus EUR {{balance}} están disponibles.

Si te interesa, tenemos recursos sobre gestión de riesgo en la academia de Bit2Me:

- Cómo diversificar una cartera
- Qué es la gestión de posiciones
- Cómo funciona el stop-loss
- La importancia de no invertir más de lo que puedes perder

[Explorar guía de riesgo] → bit2me://academy

Cuando quieras volver al mercado, tu cuenta sigue activa.

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S3 — Push (D+7)

### [GANANCIA + PÉRDIDA <10%]

**Título:** EUR {{balance}} parados 7 días
**Cuerpo:** Earn: EUR {{yield_7d}} de rendimiento semanal.
**Deep link:** bit2me://earn

---

### [PÉRDIDA >10%]

NO ENVIAR

---

## QA Checklist

- [ ] Trigger real-time <5 min desde evento de venta confirmado con Infra
- [ ] Cálculo P&L correcto: ganancia vs pérdida <10% vs pérdida >10%
- [ ] Art. 66 MiCA verificado: sin push de reinversión en pérdida >10%
- [ ] CTA "Retirar" siempre visible en todos los modales S0
- [ ] Holdout 10% aplicado por variante
