# JN-05 — EUR Depositors First Crypto: Textos

---

## TRACK ACTIVE (1,110 usuarios — login <30d)

---

### S0 — In-app portfolio (D+0)

**Header:** Tienes EUR {{balance}} disponibles.
**Body:** Hoy podrías comprar {{btc_amount}} BTC.
**CTA:** Comprar BTC → bit2me://buy/BTC

---

### S1 — Push (D+1)

**Título:** Tu saldo parado
**Cuerpo:** Tus EUR {{balance}} llevan {{days_idle}} días parados.
**Deep link:** bit2me://portfolio

---

### S2 — In-app home (D+3)

**Header:** ¿No sabes qué comprar?
**Body:** DCA: EUR {{weekly_dca}}/semana en BTC. Automático y sin decisiones.
**CTA:** Configurar DCA → bit2me://dca/setup

---

### S3 — Email (D+5)

**Asunto A:** Tus EUR {{balance}} podrían estar generando rendimiento
**Asunto B:** Earn o crypto: dos opciones para tu saldo
**Preheader:** Tienes opciones. Te las explicamos en 2 minutos.

---

Hola {{nombre}},

Tienes EUR {{balance}} en tu cuenta Bit2Me. Hay dos opciones para ponerlos a trabajar:

**Earn**
Genera {{earn_apy}}% APY directamente sobre tu saldo en EUR. Sin lock-up. Retira cuando quieras. Ideal si quieres rendimiento sin exposición al mercado.

**Comprar crypto**
Compra Bitcoin u otro activo desde EUR 1. Tu saldo actual te permitiría comprar {{btc_amount}} BTC hoy.

[Activar Earn] → bit2me://earn
[Comprar BTC] → bit2me://buy/BTC

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

### S4 — In-app modal (D+8)

**Header:** Primera compra crypto: 0% comisión.
**Body:** Hasta EUR 50. Sin coste en tu primer trade.
**CTA primario:** Comprar → bit2me://buy/BTC
**CTA secundario:** Ahora no

---

### S5 — Push (D+12)

**Título:** Último recordatorio
**Cuerpo:** Tus EUR {{balance}} siguen disponibles.
**Deep link:** bit2me://portfolio

---

## TRACK DORMANT (3,260 usuarios — login >90d)

---

### S0 — Email (D+0)

**Asunto A:** Tienes EUR {{balance}} en Bit2Me. Están parados.
**Asunto B:** Tu saldo lleva {{days_idle}} días sin moverse
**Preheader:** Un recordatorio sobre tu cuenta.

---

Hola {{nombre}},

Tienes EUR {{balance}} en tu cuenta Bit2Me. Llevan {{days_idle}} días sin moverse.

Cuando quieras, tienes dos opciones:

Comprar crypto desde EUR 1, o activar Earn para generar rendimiento sobre tu saldo.

[Ver mi saldo] → bit2me://portfolio

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S1 — Email (D+3)

**Asunto:** La inflación fue del {{inflation_rate}}%. Tus EUR pierden valor.
**Preheader:** El dinero parado pierde poder adquisitivo. Dos opciones.

---

Hola {{nombre}},

La inflación en España en el último año fue del {{inflation_rate}}%. El dinero parado pierde poder adquisitivo con el tiempo.

Tienes EUR {{balance}} en tu cuenta Bit2Me. Dos opciones para proteger ese saldo:

**Bitcoin**
Activo con oferta limitada. Compra desde EUR 1.

**Earn**
{{earn_apy}}% APY sobre tu saldo. Sin lock-up.

[Proteger mi saldo] → bit2me://buy/BTC

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S2 — Email (D+7)

**Asunto:** 2 opciones para tus EUR {{balance}}
**Preheader:** Sin complicaciones. Solo 2 opciones.

---

Hola {{nombre}},

Tus EUR {{balance}} siguen en tu cuenta. Dos opciones simples:

**Earn**
{{earn_apy}}% APY. Sin lock-up. Retira cuando quieras.

**Comprar crypto**
Bitcoin o cualquier otro activo desde EUR 1.

[Activar Earn] → bit2me://earn
[Comprar BTC] → bit2me://buy/BTC

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

### S3 — Push (D+10)

**Título:** Tus EUR {{balance}}
**Cuerpo:** Invierte desde EUR 1 o {{earn_apy}}% con Earn.
**Deep link:** bit2me://earn

---

### S4 — Email + SMS (D+14)

**Email Asunto:** 0% comisión primera compra
**Preheader:** Sin comisión hasta EUR 50.

---

Hola {{nombre}},

Tu primera compra de crypto en Bit2Me tiene 0% de comisión hasta EUR 50.

Tienes EUR {{balance}} disponibles en tu cuenta. Solo tienes que elegir el activo y comprar.

[Comprar sin comisión] → bit2me://buy/BTC

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

**SMS (solo balance >EUR 1.000):**
{{nombre}}, primera compra crypto sin comisión hasta EUR 50. bit2me.com/buy

---

### S5 — Email (D+21)

**Asunto:** Tu dinero sigue aquí
**Preheader:** Sin prisa. Aquí cuando estés listo.

---

Hola {{nombre}},

Tus EUR {{balance}} siguen en tu cuenta. No hay ninguna prisa.

Cuando estés listo para dar el siguiente paso, todo sigue en su sitio.

[Explorar] → bit2me://home

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## QA Checklist

- [ ] Segmento validado: EUR en cuenta + cero compras crypto confirmadas
- [ ] Withdrawal monitoring diario activado para detectar salidas de saldo
- [ ] Copy de inflación aprobado por Diego antes de activar S1 DORMANT
- [ ] Earn disponible para saldos EUR confirmado con Producto
- [ ] SMS solo para saldos >EUR 1.000 confirmado en segmentación
- [ ] Holdout 10% aplicado por track
- [ ] Fee waiver 0% primera compra hasta EUR 50 confirmado con Producto
- [ ] Diego aprueba todos los textos antes de activación
