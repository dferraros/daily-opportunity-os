# JN-07 — B2M Holder Cross-Sell: Textos

---

## S0 — In-app (D+0)

**Header:** Eres holder de B2M.
**Body:** El 73% también tienen Bitcoin. Diversifica desde EUR 5.
**CTA:** Explorar BTC → bit2me://buy/BTC?amount=5

---

## S1 — Push (D+3)

**Título:** B2M + BTC en Space Center
**Cuerpo:** Holders B2M + BTC suben más rápido en Space Center.
**Deep link:** bit2me://space-center

---

## S2 — Email (D+7)

**Asunto A:** El siguiente paso para un holder de B2M como tú
**Asunto B:** B2M + BTC: la combinación que eligen el 73% de los holders
**Preheader:** Tu B2M no se toca. Solo añades Bitcoin.

---

Hola {{nombre}},

El 73% de los holders de B2M en Bit2Me también tienen Bitcoin en su cartera.

No es que sustituyan uno por el otro. Son activos con perfiles distintos: B2M tiene una función dentro del ecosistema Bit2Me, Bitcoin es el activo con mayor liquidez y adopción global.

Tener los dos no significa vender tu B2M. Significa añadir una capa de diversificación.

Puedes empezar desde EUR 5. Tu B2M no se toca.

[Añadir BTC] → bit2me://buy/BTC

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S3 — In-app (D+12)

**Header:** Prueba BTC con EUR 5.
**Body:** Tu B2M no se toca. Solo añades.
**CTA:** Comprar EUR 5 BTC → bit2me://buy/BTC?amount=5

---

## S4 — Email (D+18)

**Asunto:** B2M + BTC: por qué tener los dos
**Preheader:** Una comparativa rápida.

---

Hola {{nombre}},

Una comparativa directa:

**B2M**
Token nativo de Bit2Me. Ventajas dentro del ecosistema: descuentos en fees, acceso a Space Center, staking. Alta correlación con la actividad de la plataforma.

**Bitcoin**
Activo con mayor capitalización del mercado crypto. Adopción institucional creciente. Actúa como referencia del mercado global.

¿Por qué los dos? Porque diversifican riesgo. Un activo de ecosistema y un activo de referencia de mercado tienen dinámicas distintas.

Empezar con EUR 5 en BTC no cambia tu posición en B2M.

[Ver comparativa] → bit2me://academy

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S5 — Push (D+25)

**Título:** BTC hoy
**Cuerpo:** BTC a EUR {{btc_price}} hoy. Añade EUR 5 junto a tu B2M.
**Deep link:** bit2me://buy/BTC

---

## S6 — Email (D+30)

**Asunto:** Automatiza diversificación: EUR 5/semana en BTC
**Preheader:** Una compra semanal automática. Sin decisiones.

---

Hola {{nombre}},

Una forma de diversificar sin tener que estar pendiente del mercado: DCA automático en Bitcoin.

Configuras una compra de EUR 5 por semana y Bit2Me lo gestiona por ti. Tu B2M se queda como está. Solo añades exposición a BTC de forma gradual.

Además, mantener B2M y BTC juntos acelera tu progreso en Space Center.

[Configurar DCA] → bit2me://dca/setup

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## QA Checklist

- [ ] Segmento validado: solo B2M holders con 0-1 activos distintos a B2M
- [ ] Sin incentivos monetarios en ningún mensaje (solo XP Space Center)
- [ ] B2M sell-off guardrail activo: parar journey si ventas B2M >2% del segmento
- [ ] Holdout 10% aplicado
- [ ] Diego aprueba todos los textos antes de activación
