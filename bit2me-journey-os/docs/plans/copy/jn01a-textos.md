# JN-01-A — Second Trade Accelerator: Textos de Copy

---

## S0 — In-app modal (D+0, 0-5 seg post-trade)

**Header:** Tu primera inversión está hecha
**Body:** Tu cartera Bit2Me: {{portfolio_value}} EUR en {{asset_name}} ({{cantidad}})
**CTA primario:** Ver mi cartera → bit2me://portfolio
**CTA secundario:** Explorar más activos → bit2me://market

---

## S1 — In-app card (D+0, 2-4h o siguiente apertura)

### Variante A — Blue chip (BTC / ETH / SOL)

**Header:** El siguiente paso natural
**Body:** El 73% de los inversores que empiezan con {{asset}} también compran {{suggested}}. Desde EUR 1.
**CTA primario:** Ver {{suggested}} → bit2me://buy/{{suggested}}

### Variante B — Meme coin (PEPE / DOGE / SHIB)

**Header:** Equilibra tu cartera
**Body:** Los traders activos combinan activos de alto riesgo con BTC o ETH. Tu cartera: 100% {{asset}}.
**CTA primario:** Explorar activos estables → bit2me://market

---

## S2 — Push (D+1, 9-10h)

### Variante A — Precio sube

**Título:** Tu cartera hoy
**Cuerpo:** Tu cartera: {{portfolio_value}} EUR (+{{change_pct}}%). Toca para ver el detalle.
**Deep link:** bit2me://portfolio

### Variante B — Precio baja menos del 5%

**Título:** Tu cartera hoy
**Cuerpo:** Tu cartera: {{portfolio_value}} EUR. Algunos inversores promedian cuando bajan los precios.
**Deep link:** bit2me://trade

### Variante C — Precio baja más del 5%

**Título:** 3 activos subiendo hoy en Bit2Me
**Cuerpo:** Descubre qué está moviendo el mercado hoy.
**Deep link:** bit2me://market

---

## S2.5 — SMS (D+2, 11h — solo non-responders con SMS consent)

{{nombre}}, tienes EUR 3 de crédito en Bit2Me. Caduca en 48h. Úsalo en cualquier compra. bit2me.com/trade

---

## S3 — Push + In-app (D+3, 18h)

### Push

**Título:** Tu crédito de EUR 3 caduca mañana
**Cuerpo:** Úsalo ahora en cualquier compra. Sin mínimo.
**Deep link:** bit2me://trade

### In-app

**Header:** EUR 3 de crédito. Caduca en 24h.
**Body:** Úsalo en cualquier activo del mercado. Sin importe mínimo.
**CTA primario:** Usar mi crédito → bit2me://trade

---

## S4 — Email (D+5, 10h)

**Asunto A:** Tu cuenta Bit2Me te espera, {{nombre}}
**Asunto B:** Tu cartera de {{asset}}: {{change_pct}}% esta semana
**Asunto C:** {{nombre}}, hay activos subiendo esta semana
**Preheader:** Tu primera inversión sigue ahí. Descubre qué está pasando en el mercado.

---

Hola {{nombre}},

Hace unos días hiciste tu primera inversión en Bit2Me. Tu cartera actual de {{asset_name}} está en **{{portfolio_value}} EUR** ({{change_pct}}% esta semana).

**Esta semana en el mercado:**

- {{market_asset_1}} ha subido {{market_pct_1}}% en los últimos 7 días
- {{market_asset_2}} acumula {{market_pct_2}}% en el mes
- El volumen global de trading cripto sube por tercer día consecutivo

El siguiente paso natural para muchos inversores es diversificar. **{{suggested}}** es uno de los activos más comprados por usuarios que empezaron con {{asset_name}}. Puedes empezar desde EUR 1, sin compromiso.

**Explora {{suggested}} y el resto del mercado en Bit2Me.**

[Explorar activos] → bit2me://market

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

---

## EXIT — In-app encuesta (D+7)

**Header:** ¿Qué te ayudaría a invertir de nuevo?
**Opciones:**
- a) Menos comisiones
- b) Más información
- c) Sin presupuesto
- d) Otra

---

## QA — 10 Checks

1. ¿Todas las variables dinámicas tienen fallback definido (ej. si {{portfolio_value}} es null)?
2. ¿El SMS solo se envía a usuarios con SMS consent activo?
3. ¿El crédito de EUR 3 existe en el sistema antes de que salga S2.5 y S3?
4. ¿El deep link bit2me://buy/{{suggested}} funciona si {{suggested}} no está disponible en la región del usuario?
5. ¿La variante C de S2 (baja >5%) no menciona la cartera del usuario para evitar agraviar la pérdida?
6. ¿El email S4 tiene versión de texto plano configurada en CleverTap?
7. ¿La encuesta EXIT no se dispara si el usuario ya realizó una segunda compra antes de D+7?
8. ¿Los asuntos A/B/C del email están correctamente asignados en el A/B test con reparto 33/33/33?
9. ¿El footer MiCA está presente en todos los emails y no es modificable desde plantillas?
10. ¿El journey tiene condición de salida si el usuario realiza una segunda compra en cualquier punto antes del exit?
