# JN-04 — Verified Never Operated: Textos

---

## TRACK WARM (4,300 usuarios — login <30 días)

---

### S0 — In-app card (D+0, app open)

**Header:** Ya verificaste tu cuenta.
**Body:** Solo falta un paso: tu primer depósito. Empieza desde EUR 10.
**CTA:** Depositar ahora → bit2me://deposit

---

### S1 — In-app contextual (D+0, en /market)

**Header:** ¿Te interesa {{asset_viewed}}?
**Body:** Deposita y compra desde EUR 1.
**CTA:** Depositar para comprar → bit2me://deposit

---

### S2 — Push (D+1, 10h)

**Título:** Tu cuenta está lista
**Cuerpo:** BTC hoy: EUR {{btc_price}}. Deposita y compra desde EUR 1.
**Deep link:** bit2me://deposit

---

### S3 — Email (D+3, 10h)

**Asunto A:** 3 formas de añadir fondos a tu cuenta
**Asunto B:** SEPA, tarjeta o Bizum: elige cómo depositar
**Preheader:** Depósito en minutos. Elige el método que prefieras.

---

Hola {{nombre}},

Tu cuenta Bit2Me está verificada y lista. Solo necesitas añadir fondos para hacer tu primera compra.

Tienes tres formas de hacerlo:

**Transferencia SEPA**
Desde cualquier cuenta bancaria europea. Disponible en 1-2 días hábiles. Sin comisión de Bit2Me. Mínimo EUR 10.

**Tarjeta de crédito o débito**
Visa o Mastercard. Disponible al instante. Mínimo EUR 10.

**Bizum**
Solo para cuentas bancarias españolas. Disponible al instante. Mínimo EUR 10.

[Añadir fondos] → bit2me://deposit

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S4 — In-app modal (D+5, app open)

**Header:** {{nombre}}, el 67% empieza con Bitcoin.
**Body:** Deposita EUR 10 y haz tu primera compra en menos de 2 minutos.
**CTA primario:** Depositar EUR 10 → bit2me://deposit?amount=10
**CTA secundario:** Ahora no

---

### S5 — Push (D+7, 10h)

**Título:** Esta semana en Bit2Me
**Cuerpo:** {{num_weekly_depositors}} personas depositaron esta semana. Tu cuenta sigue esperándote.
**Deep link:** bit2me://deposit

---

### S6 — Email (D+10, 10h)

**Asunto:** Tu primer depósito con 0% comisión en tu primera compra
**Preheader:** Sin comisión hasta EUR 50. Solo esta semana.

---

Hola {{nombre}},

Esta semana tu primera compra en Bit2Me tiene 0% de comisión, hasta EUR 50.

Para aprovecharla solo tienes que hacer tu primer depósito. Desde EUR 10, con el método que prefieras: transferencia SEPA, tarjeta o Bizum.

Una vez depositado, elige el activo y compra. En menos de 2 minutos puedes tener tu primera posición.

[Depositar y comprar sin comisión] → bit2me://deposit

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S7 — Email (D+14, 10h)

**Asunto:** Seguimos aquí cuando estés listo
**Preheader:** Sin presión. Recursos para cuando quieras empezar.

---

Hola {{nombre}},

No hay ninguna prisa.

Tu cuenta Bit2Me seguirá activa y verificada cuando decidas dar el siguiente paso. No tienes que hacer nada para mantenerla.

Si quieres aprender más antes de depositar, la academia de Bit2Me tiene guías para entender cómo funciona Bitcoin, qué son los diferentes activos y cómo gestionar el riesgo.

[Explorar la academia] → bit2me://academy

Seguimos aquí.

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## TRACK COOLING (12,560 usuarios — login 90-365 días)

---

### S0 — Push (D+0)

**Título:** Tu cuenta Bit2Me sigue activa
**Cuerpo:** Hace {{days_since_login}} días que no abres Bit2Me. Tu cuenta verificada sigue lista.
**Deep link:** bit2me://home

---

### S1 — Email (D+3)

**Asunto:** Tu cuenta Bit2Me sigue activa — y verificada
**Preheader:** Todo sigue en su sitio. Vuelve cuando quieras.

---

Hola {{nombre}},

Tu cuenta Bit2Me sigue activa y verificada. No has perdido nada, no tienes que volver a verificarte ni hacer ningún trámite adicional.

Cuando quieras retomar, solo tienes que acceder a la app o la web.

[Volver a la app] → bit2me://home

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S2 — Email (D+7)

**Asunto:** BTC ha {{btc_7d_change}}% esta semana. Tu cuenta está lista.
**Preheader:** Mercado en movimiento. Tu cuenta verificada, esperando.

---

Hola {{nombre}},

Esta semana en el mercado:

- Bitcoin: {{btc_7d_change}}% en 7 días
- Ethereum: {{eth_7d_change}}% en 7 días
- {{top_mover}}: activo más destacado de la semana

Tu cuenta Bit2Me está verificada y lista para operar cuando quieras.

[Ver el mercado] → bit2me://market

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S3 — Email + Push (D+12)

**Email Asunto:** Tu primer depósito con 0% comisión
**Preheader:** Sin comisión hasta EUR 50. Esta semana.

---

Hola {{nombre}},

Tu primera compra en Bit2Me tiene 0% de comisión hasta EUR 50.

Solo necesitas hacer tu primer depósito desde EUR 10 para aprovecharlo. Transferencia SEPA, tarjeta o Bizum.

[Depositar ahora] → bit2me://deposit

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

**Push Título:** 0% comisión primera compra
**Push Cuerpo:** Solo hoy. Deposita y tu primera compra sin comisión hasta EUR 50.
**Deep link:** bit2me://deposit

---

### S4 — Email (D+18)

**Asunto:** Sin prisas. Aquí tienes recursos para cuando estés listo.
**Preheader:** Guías, vídeos y todo lo que necesitas para empezar.

---

Hola {{nombre}},

Entendemos que empezar en crypto puede generar dudas. No hay ninguna prisa.

La academia de Bit2Me tiene guías en español sobre cómo funciona Bitcoin, cómo gestionar el riesgo, qué son las stablecoins y mucho más. Todo gratuito, sin necesidad de operar.

Cuando estés listo, tu cuenta sigue aquí.

[Explorar guías] → bit2me://academy

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## TRACK COLD (84,170 usuarios — sin login >365d, email-only)

---

### S0 — Email simple (D+0)

**Asunto:** Hola {{nombre}}, ¿sigues interesado en crypto?
**Preheader:** Hace tiempo que no coincidimos. ¿Todo bien?

---

Hola {{nombre}},

Hace tiempo que no sabemos nada de ti.

Tu cuenta Bit2Me sigue activa. No ha cambiado nada desde tu lado.

¿Hay algo en lo que podamos ayudarte?

[Ver mi cuenta] → bit2me://home

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S1 — Email (D+7, solo si abrió S0)

**Asunto:** Mucho ha cambiado en crypto desde tu última visita
**Preheader:** Un resumen de lo más importante.

---

Hola {{nombre}},

Desde tu última visita han pasado cosas relevantes en el mundo crypto:

- **Regulación MiCA en Europa:** Las criptomonedas tienen ahora un marco regulatorio oficial en la UE. Bit2Me opera bajo esta regulación como entidad registrada en la CNMV.
- **Mercado en 2025-2026:** Bitcoin superó máximos históricos y el mercado ha experimentado ciclos significativos.
- **Nuevos activos disponibles:** Bit2Me ha ampliado su catálogo con nuevos tokens y productos.

Tu cuenta sigue activa y verificada.

[Explorar] → bit2me://market

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S2 — Email (D+14, si abrió S0 o S1)

**Asunto:** Tu cuenta verificada sigue activa. Deposita desde EUR 10.
**Preheader:** Un solo paso para empezar.

---

Hola {{nombre}},

Tu cuenta Bit2Me sigue activa y verificada. No tienes que volver a hacer ningún trámite.

El único paso que queda es tu primer depósito. Desde EUR 10, con transferencia SEPA, tarjeta o Bizum.

[Depositar] → bit2me://deposit

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

### S3 — Non-openers

SUPRIMIR PERMANENTEMENTE

---

## QA Checklist

- [ ] WARM/COOLING/COLD correctamente segmentados por días desde último login
- [ ] Fee waiver 0% primera compra hasta EUR 50 confirmado con Producto
- [ ] "67% empieza con Bitcoin" validado con dato real
- [ ] Re-KYC para usuarios >365d sin actividad verificado con Compliance
- [ ] Holdout 10% aplicado por track
- [ ] Footer MiCA presente en todos los emails
- [ ] Diego aprueba todos los textos antes de activación
- [ ] ZeroBounce pre-validación aplicada al track COLD antes del envío
