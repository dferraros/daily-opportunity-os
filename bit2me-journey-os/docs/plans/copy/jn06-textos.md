# JN-06 — Active Never-Transacted: Textos

---

## S0 — In-app contextual (D+0, adaptado a pantalla activa)

### [En /market]

**Header:** ¿Te interesa {{asset}}?
**Body:** Desde EUR 1.
**CTA:** Comprar {{asset}} → bit2me://buy/{{asset}}

---

### [En /portfolio vacío]

**Header:** El 67% empieza con Bitcoin.
**Body:** Primera compra desde EUR 1. Sin comisión.
**CTA:** Comprar BTC → bit2me://buy/BTC

---

### [En /earn]

**Header:** Rendimiento sin operar.
**Body:** Earn desde EUR 10. {{earn_apy}}% APY.
**CTA:** Activar Earn → bit2me://earn

---

### [En /home]

**Header:** Esta semana en cripto:
**Body:** {{top_mover}} +{{pct}}% en 7 días.
**CTA:** Ver mercado → bit2me://market

---

## S1 — Push (D+1)

**Título:** {{asset}} hoy
**Cuerpo:** {{asset}} hoy: EUR {{precio}}. Tu cuenta está lista.
**Deep link:** bit2me://buy/{{asset}}

---

## S2 — Email (D+4)

**Asunto A:** Tu guía para empezar a invertir en crypto
**Asunto B:** 3 pasos para tu primera compra en Bit2Me
**Preheader:** Sin complicaciones. En 5 minutos.

---

Hola {{nombre}},

Empezar en crypto no tiene que ser complicado. Tres pasos:

**1. Deposita desde EUR 10**
Transferencia SEPA, tarjeta o Bizum. En minutos.

**2. Elige un activo**
Bitcoin, Ethereum o cualquier otro del catálogo. Puedes explorar el mercado antes de decidir.

**3. Compra desde EUR 1**
Sin mínimo alto. Sin complicaciones.

Si prefieres empezar sin operar, Earn te permite generar {{earn_apy}}% APY sobre tu saldo sin necesidad de hacer trading.

[Mi primera compra] → bit2me://buy/BTC
[Activar Earn] → bit2me://earn

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S3 — In-app modal + Push (D+8)

### In-app modal

**Header:** Primera compra: 0% comisión.
**Body:** Hasta EUR 50. Sin coste.
**CTA primario:** Comprar → bit2me://buy/BTC
**CTA secundario:** Todavía explorando

---

### Push

**Título:** 0% comisión primera compra
**Cuerpo:** Hasta EUR 50. Solo hasta agotar oferta.
**Deep link:** bit2me://buy/BTC

---

## S4 — EXIT (D+14)

Si el usuario operó → sale del journey hacia JN-01.
Si no operó → cooldown 30 días. No se envía ningún mensaje.

---

## QA Checklist

- [ ] Segmento validado: verificado, login <30d, sin first_monetary_movement
- [ ] In-app contextual configurado por pantalla activa en CleverTap
- [ ] Fee waiver 0% primera compra hasta EUR 50 confirmado con Producto
- [ ] Holdout 10% aplicado
- [ ] Diego aprueba todos los textos antes de activación
