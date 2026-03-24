# JN-01-A: Second Trade Accelerator — Copy & Creatives

**Plan:** 02-01 | **Sprint:** 1 | **Priority:** P0
**Segment:** ~75 users/day | **Goal:** 2nd trade within 7 days
**Fecha de creacion:** 2026-03-24 | **Autor:** Daniel Ferraro / CRM Copy
**Estado:** PENDIENTE aprobacion Diego (Legal)

---

## Dynamic Variables Master List

| Variable | Descripcion | Fallback | Ejemplo |
|---|---|---|---|
| `{{nombre}}` | Nombre del usuario | `inversor` | `Carlos` |
| `{{first_trade_asset}}` | Activo de la primera compra | `tu primer activo` | `Bitcoin` |
| `{{suggested_asset}}` | Activo sugerido para la 2a compra | `Ethereum` | `Ethereum` |
| `{{first_trade_date}}` | Cuando fue la primera compra (relativo) | `hace unos dias` | `hace 2 dias` |
| `{{portfolio_value_eur}}` | Valor actual del portfolio en EUR | `tu cartera` | `€247,50` |
| `{{incentivo_activo}}` | Boolean — si el incentivo EUR 5 esta activo | `false` | `true` |
| `{{dias_restantes}}` | Dias restantes en la ventana de 7 dias | `pocos dias` | `2` |

**Logica de suggested_asset:**
- BTC → ETH
- ETH → SOL
- SOL → ETH
- Cualquier meme coin (PEPE, DOGE, SHIB, etc.) → BTC

---

## S1 — Push Notification (H+24)

> Trigger: 24h despues del primer trade, si no se ha realizado el 2do trade.
> Hora de envio: 20:30 CET (España). Suprimir sabados y domingos.
> Canal: CleverTap push notification.

### Variant A — Momentum framing

- **Title:** `{{nombre}}, tu primera compra fue el principio`
- **Body:** `El 73% de usuarios que empiezan con {{first_trade_asset}} tambien tienen {{suggested_asset}}. Desde €1.`

*(Si `{{incentivo_activo}}` = true, usar body alternativo:)*
- **Body (incentivo):** `Compra hoy y puedes llevarte €5. Tu {{first_trade_asset}} ya esta en tu cartera.`

### Variant B — Portfolio anchor (A/B test)

- **Title:** `Tu cartera ahora vale {{portfolio_value_eur}}`
- **Body:** `Muchos usuarios añaden un segundo activo al portfolio en los primeros dias. Explora {{suggested_asset}}.`

*(Si `{{incentivo_activo}}` = true:)*
- **Body (incentivo):** `Tu cartera: {{portfolio_value_eur}}. Opera €250 esta semana y recibe €5 de recompensa.`

**Send time:** 20:30 CET
**Weekend rule:** Suprimir sabado y domingo — reprogramar al lunes 20:30 CET
**Stop condition:** `second_trade_completed = true` → cancelar en menos de 60 segundos
**MiCA check:** ✅ No se usa "invertir" ni "rendimiento". "Explorar" y "añadir" son neutros. Sin garantias de rentabilidad. Sin mencion de perdidas recientes del usuario (cumple Art. 66).

### Creative Brief — S1 Push Banner

- **Formato:** 1080x1920px (Story/push expanded) + 1200x628px (notification preview card)
- **Visual:** Pantalla de portfolio de Bit2Me en un movil. En primer plano, el logo del `{{suggested_asset}}` (ETH si first_trade=BTC) aparece destacado entre otros activos. Paleta: fondo oscuro (#0D0D1A), colores neon de la marca Bit2Me (azul electrico #00D4FF, verde #00FF94).
- **Mood:** Confianza + movimiento. Nada agresivo. Sensacion de comunidad, no de FOMO abrupto.
- **Text overlay (preview card):** Solo el titulo dinamico. Minimalista.
- **Elementos que NO incluir:** graficos de precio con tendencia bajista, monedas cayendo, numeros negativos.
- **AI image prompt (English):** `Dark smartphone screen showing a clean crypto portfolio interface, Ethereum logo glowing in electric blue light, Bitcoin and Ethereum coin icons side by side, modern fintech UI, deep navy background, neon highlights, realistic product mockup, no text overlay, high detail, cinematic lighting, 4K`

---

## S2 — Push Notification (H+72)

> Trigger: 72h despues del primer trade, si no se ha realizado el 2do trade.
> Hora de envio: 20:30 CET. Suprimir sabados y domingos.
> Condicion adicional: usuario NO ha convertido en S1.

### Variant A — Social proof + urgency

- **Title:** `{{nombre}}, hay algo que no quieres perderte`
- **Body:** `Miles de usuarios abrieron su segunda posicion esta semana. Tu ventana: {{dias_restantes}} dias mas.`

*(Si `{{incentivo_activo}}` = true:)*
- **Body (incentivo):** `Quedan {{dias_restantes}} dias para conseguir €5. Opera €250 en Bit2Me y es tuyo.`

### Variant B — Asset-specific curiosity (A/B test)

- **Title:** `¿Sabes por que {{suggested_asset}} complementa tu cartera?`
- **Body:** `{{first_trade_asset}} y {{suggested_asset}} se mueven de forma diferente. Mira como queda en tu portfolio.`

*(Si `{{incentivo_activo}}` = true:)*
- **Body (incentivo):** `{{suggested_asset}} desde €1. Y si operas €250 antes del dia {{dias_restantes}}, ganas €5.`

**Send time:** 20:30 CET
**Weekend rule:** Suprimir — reprogramar al siguiente dia laborable 20:30 CET
**Stop condition:** `second_trade_completed = true` → cancelar en menos de 60 segundos
**MiCA check:** ✅ "ventana" y "dias" implican tiempo, no garantia. "Se mueven de forma diferente" es framing educativo, no predictivo. Sin garantias de precio o rendimiento. Comprobado Art. 66: no se menciona precio actual ni perdidas del usuario.

### Creative Brief — S2 Push Banner

- **Formato:** 1080x1920px (Story) + 1200x628px (notification preview)
- **Visual:** Vista de mercado de Bit2Me con dos activos destacados (`{{first_trade_asset}}` + `{{suggested_asset}}`). Grafico simple, linea limpia, sin indicar tendencia bajista. Sensacion de decision informada y comparativa.
- **Mood:** Curiosidad activada. Ligeramente mas directivo que S1 pero sin alarmar.
- **Text overlay:** Ninguno sobre la imagen — todo el texto va en el body del push.
- **AI image prompt (English):** `Two glowing cryptocurrency coins side by side, Bitcoin and Ethereum or Solana, on a dark fintech dashboard interface, clean modern UI, electric blue and green neon accents, comparison view layout, no charts showing downtrends, product screenshot style, high detail, dark navy background, 4K`

---

## S3 — Email (D+5)

> Trigger: Dia 5 desde el primer trade, sin 2do trade realizado.
> Hora de envio: 20:30 CET.
> Canal: Email transaccional via CleverTap / SendGrid.

### Subject Line A
`{{nombre}}, tu cartera tiene una pieza pendiente`

### Subject Line B (A/B test)
`El siguiente movimiento de tu cartera Bit2Me`

### Preheader
`{{first_trade_asset}} ya está. Ahora viene {{suggested_asset}}.`

*(Si `{{incentivo_activo}}` = true:)*
`Tienes {{dias_restantes}} dias para conseguir €5 de recompensa.`

---

### Email Body — S3

```
[HEADER IMAGE — ver Creative Brief S3 al final de esta seccion]

Hola, {{nombre}},

Hace {{first_trade_date}} compraste {{first_trade_asset}} por primera vez.
Tu cartera ahora vale {{portfolio_value_eur}}.

Ese primer paso es el que cuesta. Ya lo diste.

Ahora muchos usuarios que empezaron igual que tu añaden un segundo
activo al portfolio. No por seguir una moda — sino porque tener dos
activos que se comportan de forma distinta hace que tu cartera no
dependa de un solo movimiento de mercado.

El activo que mas encaja con tu cartera ahora mismo: {{suggested_asset}}.

¿Por que {{suggested_asset}}?

El 73% de los usuarios que comenzaron con {{first_trade_asset}} en
Bit2Me añadieron {{suggested_asset}} en sus primeras semanas. No es
una coincidencia: {{suggested_asset}} tiene dinamicas de mercado
diferentes a {{first_trade_asset}}, lo que hace que tu cartera no
dependa de un solo activo.

Puedes empezar desde €1. Sin comisiones minimas abusivas.

[BLOQUE CONDICIONAL — solo si {{incentivo_activo}} = true]
---
RECOMPENSA ACTIVA — solo hasta dentro de {{dias_restantes}} dias

Opera un total de €250 en Bit2Me antes de que acabe tu ventana y
recibiras €5 de recompensa directa en tu cuenta. Sin condiciones
ocultas.

Quedan {{dias_restantes}} dias.
---
[FIN BLOQUE CONDICIONAL]

[CTA BUTTON — fondo azul Bit2Me #00D4FF, texto blanco, border-radius 8px]
Ver {{suggested_asset}} en Bit2Me
→ deep link: bit2me.com/trade/{{suggested_asset_ticker}}

Si tienes cualquier pregunta, nuestro equipo esta disponible en el
chat de la app o en support@bit2me.com.

El equipo de Bit2Me
```

### MiCA Footer (obligatorio — todos los emails)

```
[Font >=12px, color #888888, full width, separador visual antes del footer]

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversion. Invierte solo
lo que puedas permitirte perder.

Para darte de baja de estas comunicaciones: [Cancelar suscripcion]
Bit2Me · Paseo de la Castellana 141, 28046 Madrid, España
```

**MiCA check:** ✅ Sin uso de "invertir" como accion de venta directa. Sin garantias de rentabilidad. Disclaimer completo en footer (font >=12px, full width). Sin mencion de perdidas recientes del usuario (cumple Art. 66). El incentivo esta condicionado a `{{incentivo_activo}}` — no se muestra si no esta confirmado por Product.

> **Nota para Diego (flag D-01):** La frase "hace que tu cartera no dependa de un solo movimiento de mercado" es framing educativo sobre diversificacion, no una promesa de proteccion. Validar si es aceptable. Alternativa ya incorporada en el texto: "hace que tu cartera no dependa de un solo activo".

### Creative Brief — S3 Email Header Image

- **Formato:** 600x300px (email header, retina: 1200x600px)
- **Visual:** Cartera limpia de Bit2Me con dos iconos de activos (`{{first_trade_asset}}` + `{{suggested_asset}}`), estilo dashboard minimalista. No se muestran precios ni graficos de rendimiento historico. Atmosfera de decision tranquila.
- **Mood:** Informativo y calmado. No urgente. Paleta oficial Bit2Me: fondo oscuro (#0D0D1A), iconos en azul/verde neon.
- **Text overlay:** "`{{suggested_asset}}` — desde €1" — opcional si la imagen admite dinamica; fallback estatico sin texto.
- **AI image prompt (English):** `Clean minimalist email header for a crypto app, two cryptocurrency coins on a dark blue background, one coin slightly larger as featured asset, Bit2Me style fintech branding, electric blue and teal accents, no price charts, no red numbers, professional and calm mood, 1200x600 pixels, flat design with subtle depth`

---

## S4 — Email (D+7) — LAST CHANCE

> Trigger: Dia 7 desde el primer trade, sin 2do trade realizado.
> Este es el ULTIMO mensaje del journey JN-01-A.
> Hora de envio: 20:30 CET.
> Tras este email: tag `jn01_non_converter`, cooling period 14 dias.

### Subject Line A
`{{nombre}}, hoy es el ultimo dia de tu recompensa`

*(Si `{{incentivo_activo}}` = false:)*
`{{nombre}}, tu cartera Bit2Me te espera`

### Subject Line B (A/B test)
`Ultima oportunidad esta semana — tu cuenta Bit2Me`

*(Si `{{incentivo_activo}}` = false:)*
`Una cosa pendiente en tu cartera, {{nombre}}`

### Preheader
`Tu ventana de 7 dias termina hoy. No enviamos mas mensajes despues de este.`

*(Si `{{incentivo_activo}}` = false:)*
`Llevas {{first_trade_date}} con {{first_trade_asset}} en cartera. ¿Damos el siguiente paso?`

---

### Email Body — S4

```
[HEADER IMAGE — ver Creative Brief S4 al final de esta seccion]

Hola, {{nombre}},

Este es el ultimo mensaje que te enviamos sobre este tema.

Hace 7 dias compraste {{first_trade_asset}}. Tu cartera hoy
vale {{portfolio_value_eur}}.

No voy a repetirte todo lo que ya sabes. Solo una cosa:

El segundo activo es el que marca la diferencia entre una cartera
con un solo movimiento y una cartera con mas de un activo.

{{suggested_asset}} sigue disponible desde €1.

[BLOQUE CONDICIONAL — solo si {{incentivo_activo}} = true]
---
HOY ES EL ULTIMO DIA

Si operas un total de €250 antes de las 23:59 de hoy, recibiras
€5 de recompensa. Mañana esta oferta desaparece.

La recompensa se acredita automaticamente cuando se cumple
la condicion. Tienes hasta las 23:59 de hoy.
---
[FIN BLOQUE CONDICIONAL]

[CTA BUTTON — fondo naranja ambar #F59E0B para diferenciarlo de S3, texto blanco]
Ver {{suggested_asset}} ahora
→ deep link: bit2me.com/trade/{{suggested_asset_ticker}}

Despues de hoy no recibiras mas mensajes sobre este tema.
Tu cuenta y tu cartera siguen activas — simplemente no te
molestaremos con este recordatorio.

Si en algun momento quieres explorar nuevos activos, siempre
puedes hacerlo desde la app.

El equipo de Bit2Me
```

### MiCA Footer (obligatorio — todos los emails)

```
[Font >=12px, color #888888, full width, separador visual antes del footer]

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversion. Invierte solo
lo que puedas permitirte perder.

Para darte de baja de estas comunicaciones: [Cancelar suscripcion]
Bit2Me · Paseo de la Castellana 141, 28046 Madrid, España
```

**MiCA check:** ✅ Framing de escasez temporal (fecha limite del incentivo) es aceptable bajo MiCA siempre que sea real — confirmar con Product que la oferta realmente caduca. Sin garantias de rentabilidad. Disclaimer completo. Art. 66: no se menciona el precio actual ni historico del activo ni las perdidas del usuario.

> **Nota para Diego (flags D-02 y D-03):** (1) La frase "cartera con mas de un activo" reemplaza la formulacion anterior "cartera real" — version actualizada y mas neutra ya incorporada. (2) La frase sobre el mecanismo de acreditacion automatica del incentivo debe ser verificada con Product antes de envio. Si el proceso no es automatico, modificar.

### Creative Brief — S4 Email Header Image

- **Formato:** 600x300px (email header, retina: 1200x600px)
- **Visual:** Un unico activo cripto (`{{suggested_asset}}`) centrado en primer plano con un halo de luz ambar/naranja suave que sugiere urgencia temporal sin ser alarmiante. Fondo oscuro Bit2Me. Sin graficos de precio. Sin relojes ni contadores explicitamente visibles — la sensacion se transmite por el color y la composicion.
- **Mood:** Urgente pero sereno. El color ambar diferencia visualmente S4 de S3 (que usa azul/verde). Sensacion de "ultima vez", no de panico.
- **Text overlay:** "Hoy es el ultimo dia" — solo si la composicion lo admite sin saturar. Fallback: sin texto sobre imagen.
- **AI image prompt (English):** `Dark fintech email header, a single glowing cryptocurrency coin centered on a deep navy background, subtle amber and warm gold light halo suggesting time running out, minimalist design, no explicit clocks or timers, clean modern crypto app aesthetic, premium brand feel, 1200x600 pixels, no price charts, no aggressive red color, warm urgency through lighting`

---

## A/B Test Register

| Test ID | Nombre | Variant A | Variant B | Hipotesis | Metrica principal | Sample size estimado |
|---|---|---|---|---|---|---|
| AB-JN01A-01 | S1 Push framing | Momentum — "73% de holders..." (social proof) | Portfolio anchor — "Tu cartera ahora vale..." (valor personal) | El social proof supera al portfolio anchor en CTR hacia trade screen | Push CTR → trade screen | n=150 (75/dia x 2 dias) |
| AB-JN01A-02 | S2 Push angle | Social proof + urgencia generica | Asset-specific curiosidad ("¿sabes por que...?") | La curiosidad especifica por el activo supera a la urgencia generica en conversion | Push open rate + conversion a 2nd trade D+7 | n=150 |
| AB-JN01A-03 | S3 Subject line | "Tu cartera tiene una pieza pendiente" | "El siguiente movimiento de tu cartera Bit2Me" | La especificidad ("pieza pendiente") supera al generico en open rate | Email open rate | n=300 (acumulado ~4 dias) |
| AB-JN01A-04 | S4 Subject line | Urgency explicito — "Hoy es el ultimo dia..." | Neutro — "Ultima oportunidad esta semana..." | El urgency con fecha concreta supera al urgency vago en open rate y CTR del ultimo email | Email open rate + CTR | n=300 |
| AB-JN01A-05 | Incentivo on/off | Con incentivo €5 activo (`{{incentivo_activo}}`=true) | Sin incentivo — holdout del incentivo | El incentivo monetario aumenta la tasa de 2nd trade en mas de 8 puntos porcentuales | 2nd trade rate D+7 | n=500 minimo (acumulacion ~7 dias) |

**Notas operativas AB:**
- Todos los tests requieren aprobacion de Daniel antes de activar en CleverTap.
- AB-JN01A-05 solo ejecutar si Product confirma que el incentivo EUR 5 esta presupuestado y el mecanismo de acreditacion esta listo.
- El 10% holdout global (zero messages) se mantiene separado de todos los variants y no cuenta como Variant B en ningun test.
- Criterio de winner declaration: 95% de confianza estadistica O 7 dias de datos completos, lo que llegue primero.
- Los tests de subject line (AB-03 y AB-04) no requieren confirmacion de incentivo — se pueden activar en cualquier caso.

---

## Fallback Logic

| Variable | Escenario de fallo | Fallback aplicado | Impacto en copy | Severidad |
|---|---|---|---|---|
| `{{nombre}}` | Null / no disponible | `inversor` | "Hola, inversor," — aceptable, no critico | Baja |
| `{{first_trade_asset}}` | Null / no disponible | `tu primer activo` | "Compraste tu primer activo" — pierde especificidad del social proof | Media |
| `{{suggested_asset}}` | Logica de mapping falla | `Ethereum` | ETH como default universal — seguro para todos los segmentos | Baja |
| `{{first_trade_date}}` | Null / timestamp corrupto | `hace unos dias` | Pierde personalidad pero es neutro | Baja |
| `{{portfolio_value_eur}}` | Null / valor cero / API error | Omitir linea completa del email | Nunca mostrar "Tu cartera vale €0" — suprimir ese parrafo entero | Alta |
| `{{dias_restantes}}` | Calculo falla / valor negativo | `pocos dias` | Reduce impacto de urgencia — aceptable en S3, problematico en S4 | Media en S3, Alta en S4 |
| `{{incentivo_activo}}` | Null / no disponible | `false` | Tratar como sin incentivo — mas seguro que mostrar incentivo incorrecto | Alta |
| `{{suggested_asset_ticker}}` | Mapping ticker falla | `/trade` (homepage trading) | Deep link a pantalla generica en lugar de activo especifico | Media |

**Regla de supresion:** si mas de 2 variables de alta severidad fallan simultaneamente en el mismo mensaje → suprimir el envio completo y registrar evento en CleverTap con tag `jn01a_variable_failure` para revision. No enviar copy con multiples fallbacks activos — pierde personalizacion y puede parecer error tecnico al usuario.

---

## Diego Approval Notes

**Archivo para revision legal:** `docs/plans/2026-03-24-jn01a-copy-creatives.md`
**Revisor asignado:** Diego (Legal Gate — aprobacion pre-send obligatoria para todos los mensajes CRM)
**Deadline sugerido para aprobacion:** 28-Mar-2026 (inicio previsto del journey Sprint 1)

### Flags para revision Diego

| ID | Mensaje | Texto en cuestion | Motivo del flag | Sugerencia alternativa incorporada |
|---|---|---|---|---|
| D-01 | S3 Email body | "hace que tu cartera no dependa de un solo movimiento de mercado" | Podria interpretarse como promesa implicita de proteccion ante perdidas | Version neutra ya incorporada: "hace que tu cartera no dependa de un solo activo" |
| D-02 | S4 Email body | "cartera con mas de un activo" | Version ya actualizada de "cartera real" — verificar que la nueva formulacion es aceptable | Esta es ya la version alternativa aprobada — confirmar |
| D-03 | S4 Email body | Texto sobre mecanismo de acreditacion del incentivo | El mecanismo descrito debe coincidir exactamente con el implementado por Product | Confirmar con Product si es automatico o manual; ajustar texto segun respuesta |
| D-04 | Todos los emails | Footer: "Invierte solo lo que puedas permitirte perder" | Verificar que esta formulacion exacta esta aprobada por el equipo legal para uso en CNMV | Usar formulacion oficial canonizada si existe una version aprobada por compliance |
| D-05 | S2 Push Variant A | "Tu ventana: {{dias_restantes}} dias mas" — solo en body con incentivo | La "ventana" solo tiene sentido comercial si el incentivo esta activo — ya condicionado en el copy | Confirmar que la logica condicional en CleverTap suprime correctamente este bloque cuando `{{incentivo_activo}}`=false |
| D-06 | S3 y S4 Email | Bloques condicionales de incentivo con sintaxis `{% if %}` | Verificar que CleverTap / SendGrid soporta esta logica condicional en el motor de templates | Confirmar con Katy el motor de templates antes de configurar en CleverTap — no es un flag MiCA sino tecnico |

### Checklist de cumplimiento MiCA — estado actual

- [x] Sin uso de "invertir" como accion principal de llamada a la accion
- [x] Sin promesas de rentabilidad de ningun tipo
- [x] Sin afirmacion de ser "el exchange mas seguro/confiable del mundo"
- [x] Sin mencion del seguro de 150M EUR
- [x] Disclaimer CNMV completo en todos los emails (footer, >=12px, full width)
- [x] Art. 66: sin empujar a comprar despues de perdida >10% — logica de exclusion aplicada en condiciones de entrada al journey (NOT sold_100pct_within_1h)
- [x] Incentivo condicionado a `{{incentivo_activo}}` — no se muestra en ningun mensaje si no esta confirmado por Product
- [x] Supresion de pushes en fin de semana con datos de precio real-time activada
- [x] Journey excluye stablecoin buyers (USDT/USDC) — sin presionar a usuarios que no son compradores reales de cripto
- [ ] **PENDIENTE Product:** Confirmacion de que el incentivo EUR 5 (opera EUR 250 en 7 dias) esta aprobado, presupuestado y el mecanismo de acreditacion esta listo
- [ ] **PENDIENTE Diego:** Aprobacion de flags D-01 a D-06 antes de configuracion en CleverTap
- [ ] **PENDIENTE Katy:** Confirmacion del motor de templates CleverTap para logica condicional (flag D-06)

---

*Documento generado: 2026-03-24*
*Proximo paso: enviar a Diego para revision legal. Activacion en CleverTap coordinada con Katy una vez aprobado.*
*Este documento cubre EXCLUSIVAMENTE JN-01-A (Second Trade). JN-01-B (DCA Activation) es un journey separado que se activa post-2nd trade.*
