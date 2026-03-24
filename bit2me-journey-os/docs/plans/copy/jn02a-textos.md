# JN-02A — Sleeper to Trader: Textos de Copy

---

## A1 — In-app contextual (D+0, en portfolio_view)

**Header:** Tu {{primary_asset}} esta semana
**Body:** Tu {{primary_asset}} se movió {{asset_7d_change}}% en 7 días. Último precio: EUR {{asset_price}}. Tu posición: EUR {{position_value}}.
**CTA primario:** Operar {{asset}} → bit2me://buy/{{asset}}
**CTA secundario:** Crear alerta de precio → bit2me://alerts/{{asset}}

---

## A2 — In-app bottom sheet (D+0+, en asset_detail_view)

**Header:** ¿Quieres que te avisemos cuando {{asset}} llegue a un precio concreto?
**Body:** Te mandamos una notificación en cuanto se alcance el precio que tú elijas.
**Pre-fill sugerido:** precio actual +5% (alerta de subida) / precio actual -5% (alerta de bajada)
**CTA primario:** Crear alerta → bit2me://alerts/setup?asset={{asset}}&price={{target_price}}

---

## A3 — Push (D+3, 10h)

**Título:** Tu {{primary_asset}} esta semana
**Cuerpo:** Tu {{primary_asset}} está en EUR {{asset_price}} ({{asset_7d_change}}% en 7d). Toca para ver tu posición.
**Deep link:** bit2me://portfolio

---

## A4 — In-app interstitial (D+7, 3ª sesión sin acción)

**Header:** Llevas {{days_since_last_trade}} días observando.
**Body:** Sabemos que estás esperando el momento. ¿Qué te ayudaría?
**Opciones:**
- Crear alerta de precio → bit2me://alerts
- Operar ahora → bit2me://trade
- Configurar compra recurrente → bit2me://dca
- Solo estoy mirando → dismiss

---

## A5 — Email (D+10, 10h)

**Asunto A:** Resumen semanal: qué pasó con {{primary_asset}} y tu portfolio
**Asunto B:** Tu {{primary_asset}} se movió. Tu portfolio también.
**Asunto C:** Esta semana en cripto: {{top_mover}} +{{top_mover_pct}}%
**Preheader:** Un vistazo rápido a tu cartera y al mercado esta semana.

---

Hola {{nombre}},

Esta semana **{{primary_asset}}** se movió **{{asset_7d_change}}%**. Tu posición actual vale **{{position_value}} EUR**.

**Esta semana en el mercado:**

- {{top_mover}} lidera las subidas con +{{top_mover_pct}}% en 7 días
- El mercado global mantiene tendencia de mayor volumen de operaciones

Tienes varias opciones desde tu cuenta:

- **Operar ahora** si crees que es el momento
- **Crear una alerta de precio** y que Bit2Me te avise cuando llegue a tu nivel
- **Configurar una compra recurrente (DCA)** para invertir de forma automática y reducir la exposición a la volatilidad

Tu cartera lleva activa. Solo necesita una orden tuya.

[Ver mi portfolio] → bit2me://portfolio

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

---

## A6 — Push (D+14, 10h — solo total non-responders)

**Título:** Tu saldo podría trabajar para ti
**Cuerpo:** Tu saldo de EUR {{auc_eur}} podría generar {{earn_apy}}% en Earn.
**Deep link:** bit2me://earn

---

## QA — 10 Checks

1. ¿A1 solo se dispara en portfolio_view y no en otras pantallas del flujo de onboarding?
2. ¿El bottom sheet A2 no aparece si el usuario ya tiene una alerta activa sobre ese activo?
3. ¿Las variables {{asset_7d_change}} y {{asset_price}} se actualizan con datos del día del envío, no con datos cacheados del día de entrada al journey?
4. ¿El interstitial A4 tiene un límite de frecuencia para no aparecer más de una vez por sesión?
5. ¿La opción "Solo estoy mirando" en A4 cierra el interstitial sin enviar el usuario a ningún destino ni registrar como conversión?
6. ¿El email A5 tiene versión de texto plano configurada en CleverTap?
7. ¿Los tres asuntos del email A5 están en A/B test con reparto 33/33/33?
8. ¿A6 (push Earn) solo sale si {{auc_eur}} > 0 y el producto Earn está disponible para el usuario?
9. ¿El journey tiene condición de salida si el usuario realiza cualquier operación de trading en cualquier punto del flujo?
10. ¿El footer MiCA está presente en todos los emails y no es modificable desde plantillas?
