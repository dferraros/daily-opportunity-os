# JN-02B: Sleeper to Earn — Copy & Creatives
**Plan:** 02-03 | **Sprint:** 1 | **Priority:** P1
**Segment:** ~4,000 usuarios | Split: B-HIGH (>=EUR 500) → Earn | B-LOW (<EUR 500) → DCA
**Fecha de redacción:** 2026-03-24
**Estado:** Pendiente revisión Diego (Legal)

---

## Dynamic Variables Master List

| Variable | Descripción | Fallback |
|---|---|---|
| `{{nombre}}` | Nombre de pila del usuario | "inversor" |
| `{{auc_eur}}` | Saldo total en custodia, formateado (ej. "340 EUR") | "tu saldo" |
| `{{primary_asset_held}}` | Activo principal en cartera (ej. "Bitcoin") | "tus criptomonedas" |
| `{{earn_apy}}` | APY actual de Earn para el activo principal (ej. "4,5%") | "un APY competitivo" |
| `{{yield_eur}}` | Estimación de recompensas anuales en EUR (ej. "45 EUR") | omitir cifra, usar copia genérica |
| `{{suggested_dca_amount}}` | Importe sugerido de compra recurrente (ej. "25 EUR/mes") | "10 EUR/mes" |
| `{{incentivo_earn_activo}}` | Boolean — si el incentivo +1% APY extra está activo | false |
| `{{incentivo_dca_activo}}` | Boolean — si el incentivo sin comisión en primer DCA está activo | false |

---

## Yield Copy Decision Tree

> Regla MiCA: solo mostrar cifras de recompensas si el rendimiento anual estimado es significativo.
> `earn_annual_yield = auc_eur * earn_apy`

| Umbral earn_annual_yield | Variante de copia a usar | Ejemplo |
|---|---|---|
| >= EUR 50/año | **ESPECÍFICA:** "Tu saldo de {{auc_eur}} podría generar {{yield_eur}} EUR en recompensas al año" | auc=1.200 EUR, APY=4,5% → 54 EUR |
| >= EUR 15/año y < EUR 50/año | **RANGO:** "Tu saldo podría generar más de {{yield_eur}} EUR en recompensas al año" | auc=500 EUR, APY=4,5% → 22,5 EUR |
| < EUR 15/año | **GENÉRICA OBLIGATORIA:** "Activa Earn y pon tu saldo a trabajar" — SIN cifras | auc=200 EUR, APY=4,5% → 9 EUR |
| APY no disponible | **GENÉRICA:** "Consigue recompensas en {{primary_asset_held}} con Earn" | — |

**Nota implementación:** Calcular `earn_annual_yield` server-side antes de renderizar. Si la variable `{{yield_eur}}` no puede calcularse, forzar variante genérica.

---

## B1 — In-App Card (Primer login — pantalla Portfolio)

> **Trigger:** `portfolio_screen_view` tras login
> **Supresión:** ocultar tras 3 dismissals acumulados o conversión

---

### B-HIGH Variant (auc >= EUR 500)

**Card Title:** `Tu {{primary_asset_held}} podría estar trabajando`
*(max 40 chars — 41 con variable; truncar si nombre de activo >8 chars)*

**Card Body — variante yield ESPECÍFICA (>= EUR 50/año):**
`{{auc_eur}} parado no hace nada. Activa Earn y obtén hasta {{yield_eur}} EUR en recompensas al año.`

**Card Body — variante yield RANGO (EUR 15-49/año):**
`Tu saldo podría generar más de {{yield_eur}} EUR en recompensas al año. Solo tienes que activar Earn.`

**Card Body — variante GENÉRICA (<EUR 15/año):**
`Tienes {{auc_eur}} en tu cartera. Pon tus criptomonedas a trabajar con Earn y obtén recompensas.`

**CTA Principal:** `Activar Earn`
*(max 20 chars)*

**CTA Secundario:** `Más tarde`

**Incentivo condicional** `{{#if incentivo_earn_activo}}`:
Añadir badge sobre el botón: `+1% APY extra — primeros 30 días`

**Disclaimer condensado** (debajo del CTA, fuente 10px mínimo):
`APY variable. Implica riesgo. Lee condiciones en bit2me.com/earn`

**MiCA check:** ✅ Sin palabras prohibidas. Sin garantías implícitas. Disclaimer visible.

---

### B-LOW Variant (auc EUR 50–499)

**Card Title:** `Empieza a construir tu cartera`
*(30 chars)*

**Card Body:**
`Configura una compra recurrente desde {{suggested_dca_amount}} y haz que tu hábito trabaje por ti. Sin complicaciones.`

**CTA Principal:** `Configurar compra recurrente`
*(28 chars — si el espacio no lo permite, usar: `Empezar ahora`)*

**CTA Secundario:** `Más tarde`

**Incentivo condicional** `{{#if incentivo_dca_activo}}`:
Añadir badge: `Sin comisión en tu primera compra recurrente`

**Disclaimer condensado** (debajo del CTA, fuente 10px mínimo):
`Las criptomonedas son activos de riesgo. El valor puede bajar. No es asesoramiento de inversión.`

**MiCA check:** ✅ DCA no menciona APY — no aplica disclaimer de Earn. Aplica disclaimer general de riesgo.

---

### Creative Brief — In-App Card Illustration

**Dimensiones:** 375×220px card + versión @2x (750×440px) para retina

**B-HIGH Illustration:**
- Visual: Representación abstracta de un engranaje o mecanismo en movimiento, construido con iconos de criptomonedas (Bitcoin dorado, Ethereum plateado). Los engranajes están girando activamente — movimiento implícito, no literal.
- Fondo: Gradiente oscuro azul marino (#0D1B2A → #1A2F4B). Sensación premium, sofisticada.
- Elemento central: El icono del activo principal del usuario brilla con un halo sutil (glow effect en amber/dorado). El resto de la tarjeta está en tonos fríos.
- Mood: Confianza, sofisticación, activación latente. "Esto ya es tuyo, solo falta encenderlo."
- NO usar: monedas de oro cayendo, gráficos de subida, cohetes, iconos de "dinero fácil"
- AI image prompt (English): "Abstract dark navy gradient background, golden Bitcoin icon at center emitting a soft amber glow, surrounded by silver mechanical gears made of subtle crypto symbols slowly rotating, minimalist fintech aesthetic, premium dark UI card illustration, no text, clean vector style, 375x220px, flat design with depth"

**B-LOW Illustration:**
- Visual: Una línea de progreso ascendente suave (no un gráfico de precios — una barra de hábito, tipo streaks). Pequeños círculos representan compras recurrentes que se van acumulando a lo largo del tiempo en una línea temporal.
- Fondo: Gradiente azul más claro y accesible (#1B3A6B → #2D5F9E). Sensación de crecimiento, accesibilidad.
- Elemento central: Icono de calendario o reloj con monedas apilándose gradualmente — acumulación progresiva.
- Mood: Optimismo, accesibilidad, construcción de hábito. "No necesitas mucho para empezar."
- NO usar: gráficos de precios, imágenes de riqueza, lujo
- AI image prompt (English): "Light navy blue gradient background, simple progress timeline with small circular crypto coin icons accumulating from left to right, minimalist habit-tracking visual, clean fintech illustration style, warm blue tones, no text, flat vector design, accessible and encouraging mood, 375x220px"

---

## B2 — Push Notification (D+3)

> **Condición de envío:** sin engagement en B1 a los 3 días
> **Hora de envío:** 20:30 CET (ventana de mayor apertura histórica LC Bit2Me)
> **Plataforma:** CleverTap — Journey trigger node
> **Límite CleverTap:** Title 50 chars | Body 90 chars

---

### B-HIGH — Variante A

**Title:** `Tu {{primary_asset_held}} está parado, {{nombre}}`
*(46 chars con variable de 7 chars — OK)*

**Body:** `Tienes {{auc_eur}} en tu cartera. Activa Earn y haz que trabajen por ti. Tarda menos de 1 minuto.`

**Body (versión corta si excede 90 chars con variables):** `{{auc_eur}} sin activar Earn es una oportunidad perdida. Actívalo ahora.`

**Deep link:** `bit2me://earn/activate`

---

### B-HIGH — Variante B (A/B)

**Title:** `¿Sabías que tu saldo podría generar recompensas?`
*(49 chars — OK)*

**Body (ajustado 90 chars):** `Earn de Bit2Me: consigue hasta {{earn_apy}} APY en {{primary_asset_held}}. Empieza ya.`

**Deep link:** `bit2me://earn/info`

---

### B-LOW — Variante A

**Title:** `{{nombre}}, ¿ya tienes tu compra recurrente?`
*(44 chars — OK)*

**Body (ajustado):** `Desde {{suggested_dca_amount}}/mes, construye tu cartera crypto mes a mes. Configúralo ya.`

**Deep link:** `bit2me://dca/setup`

---

### B-LOW — Variante B (A/B)

**Title:** `El mejor momento para empezar es hoy`
*(37 chars — OK)*

**Body (ajustado):** `Compra recurrente en crypto desde {{suggested_dca_amount}}. Automático y sin compromiso.`

**Deep link:** `bit2me://dca/info`

---

**MiCA check:** ✅ Variante B HIGH menciona APY — no incluye cifras en EUR de recompensas (solo %). Aceptable en push. Ninguna variante usa palabras prohibidas.

**Creative Brief — Push Banner (Rich Notification):**
- Dimensiones: 1200×628px (Open Graph) + 400×200px (push thumbnail)
- B-HIGH: Fondo oscuro. Icono del activo del usuario (BTC/ETH) con glow amber. Texto superpuesto "Earn" en tipografía Bit2Me. Sin cifras de rendimiento en imagen.
- B-LOW: Fondo azul medio. Icono de calendario y flecha de crecimiento suave. Texto "Compra recurrente" en tipografía Bit2Me.
- Ambos: logo Bit2Me en esquina superior izquierda. Sin textos de precios ni porcentajes en la imagen (evitar actualización manual).
- AI prompt B-HIGH: "Dark navy background, glowing golden Bitcoin coin center, 'Earn' text in modern sans-serif, Bit2Me logo top-left, premium fintech push notification banner, no price charts, 1200x628px"
- AI prompt B-LOW: "Medium blue background, calendar icon with upward growth arrow, 'Compra recurrente' text, Bit2Me logo top-left, accessible fintech push notification banner, optimistic mood, 1200x628px"

---

## B3 — Email (D+7)

> **Condición de envío:** sin conversión (Earn no activado / DCA no configurado) a D+7
> **Plataforma:** CleverTap Email Journey
> **Hora de envío:** 10:00 CET (martes o miércoles preferido)

---

### B-HIGH Email

**Subject A:** `{{nombre}}, tu {{primary_asset_held}} podría estar generando recompensas`

**Subject B:** `{{auc_eur}} parados: ¿y si los pones a trabajar?`

**Preheader:** `Earn de Bit2Me te permite obtener recompensas en crypto. Sin mover nada de tu cartera.`

---

**CUERPO DEL EMAIL — B-HIGH:**

---

Hola, {{nombre}}.

Tienes {{auc_eur}} en tu cartera de Bit2Me — y llevan un tiempo ahí, quietos.

No hay nada malo en eso. Pero existe una opción que quizás no hayas explorado todavía: **Earn**.

**¿Qué es Earn?**

Earn es el producto de Bit2Me que te permite obtener recompensas en criptomonedas por mantener activos en tu cartera. No tienes que vender. No tienes que mover nada. Solo activar.

*[VARIANTE YIELD ESPECÍFICA — si earn_annual_yield >= EUR 50/año]:*
Con tu saldo actual de **{{auc_eur}}**, podrías obtener hasta **{{yield_eur}} EUR** en recompensas al año, a un APY de {{earn_apy}}.*

*[VARIANTE RANGO — si earn_annual_yield entre EUR 15-49/año]:*
Con tu saldo actual, podrías generar **más de {{yield_eur}} EUR** en recompensas al año.*

*[VARIANTE GENÉRICA — si earn_annual_yield < EUR 15/año]:*
Con Earn, tus criptomonedas trabajan por ti en lugar de quedarse paradas.*

**¿Cómo funciona?**

1. Vas a tu cartera en Bit2Me
2. Seleccionas el activo que quieres activar en Earn
3. Confirmas — en menos de 2 minutos

Tus criptomonedas siguen siendo tuyas. Puedes desactivar cuando quieras.

---

*[BLOQUE CONDICIONAL — solo si incentivo_earn_activo = true]:*

**Oferta especial — solo por tiempo limitado**

Si activas Earn antes del {{fecha_fin_incentivo}}, obtendrás **+1% APY adicional durante los primeros 30 días**. Condiciones en bit2me.com/earn.

---

**[BOTÓN CTA] Activar Earn ahora →**
`bit2me://earn/activate`

¿Tienes dudas? Escríbenos a soporte@bit2me.com o visita nuestro centro de ayuda.

Un saludo,
El equipo de Bit2Me

---

*Los productos de rendimiento implican riesgo. El APY mostrado ({{earn_apy}}) es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.*

---

**FOOTER EU DISCLAIMER (fuente >=12px, ancho completo):**

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

[Darte de baja de comunicaciones comerciales] | [Ver en el navegador] | [Preferencias de privacidad]
Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España

---

**MiCA check B-HIGH email:** ✅
- Sin "rendimiento", "intereses", "beneficios", "ingresos pasivos"
- APY siempre con asterisco y disclaimer completo inmediatamente debajo del CTA
- Yield en EUR solo si >= EUR 15/año (lógica condicional en plantilla)
- Disclaimer de Earn y EU disclaimer presentes
- Sin garantías implícitas ("podrías obtener", no "obtendrás")

---

### B-LOW Email

**Subject A:** `{{nombre}}, empieza con {{suggested_dca_amount}} al mes — sin complicaciones`

**Subject B:** `La forma más sencilla de construir tu cartera crypto`

**Preheader:** `Configura una compra recurrente en minutos. Automática, flexible, sin compromiso mínimo.`

---

**CUERPO DEL EMAIL — B-LOW:**

---

Hola, {{nombre}}.

Hay una pregunta que muchos inversores en crypto se hacen: ¿cuándo es el mejor momento para comprar?

La respuesta honesta: nadie lo sabe con certeza. Pero hay una estrategia que elimina ese problema.

**Compra recurrente: compra de forma sistemática, no emocional.**

La compra recurrente (también llamada DCA, o promedio de coste) consiste en adquirir una cantidad fija de crypto a intervalos regulares — da igual si el precio sube o baja. Así reduces el impacto de la volatilidad a lo largo del tiempo.

En Bit2Me puedes configurarlo en menos de 2 minutos:

1. Elige el activo que quieres comprar (Bitcoin, Ethereum, o cualquier otro)
2. Decide el importe — desde **{{suggested_dca_amount}}/mes**
3. Elige la frecuencia: diaria, semanal o mensual
4. Listo — funciona de forma automática

Tu cartera actual de **{{auc_eur}}** es el punto de partida. La compra recurrente es cómo crece.

---

*[BLOQUE CONDICIONAL — solo si incentivo_dca_activo = true]:*

**Sin comisión en tu primera compra recurrente**

Configura tu primera compra recurrente ahora y la primera transacción es **sin comisión**. Oferta hasta {{fecha_fin_incentivo}}. Condiciones en bit2me.com/dca.

---

**[BOTÓN CTA] Configurar mi compra recurrente →**
`bit2me://dca/setup`

¿Tienes preguntas sobre cómo funciona? Visita nuestra [Guía de compra recurrente] o escríbenos.

Un saludo,
El equipo de Bit2Me

---

**FOOTER EU DISCLAIMER (fuente >=12px, ancho completo):**

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

[Darte de baja de comunicaciones comerciales] | [Ver en el navegador] | [Preferencias de privacidad]
Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España

---

**MiCA check B-LOW email:** ✅
- DCA framing no menciona APY ni rendimientos garantizados
- "puede reducir el impacto de la volatilidad" — lenguaje prudente, no promisorio
- EU disclaimer completo presente
- Sin disclaimer de Earn (no aplica — email no menciona Earn)
- "comprar" en lugar de "invertir" — VERIFICADO

---

### Creative Brief — Email Header (Banner superior)

**Dimensiones:** 600×280px (desktop estándar) + versión mobile 375×180px

**B-HIGH Header:**
- Visual: Composición dividida en dos mitades. Izquierda: icono estático de Bitcoin/activo principal del usuario, apagado, gris azulado. Derecha: el mismo icono en dorado con glow. Un interruptor de "activar" entre las dos mitades — metáfora de encendido.
- Paleta: fondo #0D1B2A, iconos en #F7931A (BTC) o el color del activo, interruptor en verde #00D47E (color Earn de Bit2Me)
- Headline superpuesto: "Pon tu {{primary_asset_held}} a trabajar" (renderizado dinámico o versión genérica si no es posible)
- Mood: activación, potencial dormido listo para encenderse
- NO incluir cifras de APY o EUR en la imagen (se actualizan en el body del email)
- AI prompt: "Split composition email banner: left side grey muted Bitcoin icon off-state, right side glowing golden Bitcoin icon on-state, power toggle switch between them, dark navy background #0D1B2A, green accent #00D47E, premium fintech email header, 600x280px, no text overlay, clean vector"

**B-LOW Header:**
- Visual: Línea de tiempo horizontal simple. En el extremo izquierdo: una moneda pequeña. En el extremo derecho, tras 12 puntos que representan meses: una pila de monedas más alta. Flecha de progresión suave (no gráfico de precios — más como una guía de camino).
- Paleta: fondo #1B3A6B, monedas en dorado y plateado, línea de tiempo en #4A9EF5
- Headline superpuesto: "Construye tu cartera, paso a paso"
- Mood: crecimiento gradual, accesible, sin presión
- AI prompt: "Horizontal timeline email banner: single coin on left, growing stack of coins on right, 12 milestone dots along timeline, soft upward arc, medium blue background #1B3A6B, gold and silver coins, fintech accessible illustration style, 600x280px, no price charts, encouraging and calm mood"

---

## B4 — In-App Card (Supresión tras 3 dismissals — mostrar una vez más)

> **Trigger:** siguiente login tras B3 email enviado, si no hay conversión
> **Supresión:** no mostrar si ya se ha dismissido 3 veces total en el journey
> **Tono:** urgencia moderada — el incentivo está a punto de caducar (si activo)

---

### B-HIGH Variant — B4

**Card Title:** `Aún no has activado Earn, {{nombre}}`
*(37 chars con nombre de 6 chars — OK)*

**Card Body — con incentivo activo:**
`Tu saldo lleva tiempo parado. El +1% APY extra caduca pronto. Última oportunidad de activar.`

**Card Body — sin incentivo:**
`Tus {{auc_eur}} en {{primary_asset_held}} podrían estar generando recompensas. Actívalas hoy.`

**CTA Principal:** `Activar Earn`

**CTA Secundario:** `No me interesa`
*(si el usuario pulsa esto, marcar como opt-out del journey y no enviar B5)*

**Disclaimer condensado:** `APY variable. Implica riesgo. bit2me.com/earn`

**MiCA check:** ✅ Sin garantías. Disclaimer visible. Urgencia legítima (incentivo real o saldo inactivo).

---

### B-LOW Variant — B4

**Card Title:** `Tu primera compra recurrente te espera`
*(38 chars — OK)*

**Card Body — con incentivo activo:**
`La compra sin comisión caduca pronto. Configura tu compra recurrente desde {{suggested_dca_amount}} hoy.`

**Card Body — sin incentivo:**
`Aún puedes configurar tu compra recurrente. Desde {{suggested_dca_amount}}/mes, automático y flexible.`

**CTA Principal:** `Configurar ahora`

**CTA Secundario:** `No me interesa`
*(opt-out del journey — no enviar B5)*

**Disclaimer condensado:** `Las criptomonedas son activos de riesgo. No es asesoramiento de inversión.`

**MiCA check:** ✅ Sin promesas de rendimiento en copy DCA. Disclaimer de riesgo presente.

---

**Creative Brief — B4 In-App Card:**
Mismas dimensiones que B1 (375×220px + @2x). Variación visual:
- B-HIGH: añadir un elemento de timer/reloj sutil en esquina superior derecha si incentivo activo. El glow del activo es más intenso que en B1 — urgencia visual.
- B-LOW: mismo timeline de B1 pero con un punto parpadeante en el primer hito — "tu primer paso está aquí".
- Ambos: mantener paleta y estilo de B1. No cambiar el lenguaje visual del journey.

---

## B5 — Email (D+21 — Último intento, solo no respondedores)

> **Condición de envío:** sin conversión a D+21, usuario no ha pulsado "No me interesa" en B4
> **Objetivo:** cierre suave del journey — no forzar, mantener marca positiva
> **Tono:** más ligero, sin presión. Recordatorio final, no ultimátum.
> **Hora de envío:** 10:00 CET

---

### B-HIGH Final Email

**Subject A:** `Una última cosa antes de cerrar, {{nombre}}`

**Subject B:** `Tu {{primary_asset_held}} sigue esperando — sin prisa`

**Preheader:** `Si en algún momento quieres activar Earn, aquí tienes todo lo que necesitas saber.`

---

**CUERPO — B-HIGH FINAL:**

---

Hola, {{nombre}}.

Te hemos escrito un par de veces sobre Earn y quizás no era el momento adecuado. Sin problema.

Solo quería dejarte esta nota breve por si es útil en algún momento.

**Earn sigue disponible cuando tú quieras.**

Tus {{auc_eur}} en {{primary_asset_held}} pueden activarse en Earn en cualquier momento — sin fecha límite, sin presión. Si decides probarlo, el proceso tarda menos de 2 minutos y puedes desactivar cuando quieras.

Lo que ofrece Earn:
- Recompensas en el mismo activo que ya tienes
- APY variable — actualmente {{earn_apy}} en {{primary_asset_held}}*
- Sin penalización por salir — tus activos siguen siendo tuyos

Si tienes dudas sobre cómo funciona, nuestra guía está aquí: bit2me.com/earn/guia

**[BOTÓN CTA] Saber más sobre Earn**
`bit2me://earn/info`

Y si prefieres no recibir más comunicaciones sobre Earn, puedes gestionarlo en tus preferencias.

Un saludo,
El equipo de Bit2Me

---

*Los productos de rendimiento implican riesgo. El APY mostrado ({{earn_apy}}) es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.*

---

**FOOTER EU DISCLAIMER (fuente >=12px, ancho completo):**

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

[Darte de baja] | [Ver en el navegador] | [Preferencias de privacidad]
Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España

---

**MiCA check B-HIGH final:** ✅ Tono informativo, no promisorio. APY mencionado con disclaimer. CTA a "saber más" no a conversión directa — reduce presión. Sin cifras de EUR en recompensas (apropiado para email final).

---

### B-LOW Final Email

**Subject A:** `{{nombre}}, la puerta sigue abierta`

**Subject B:** `Compra recurrente: aquí cuando la necesites`

**Preheader:** `Sin prisa. Si en algún momento quieres configurarlo, esto es todo lo que necesitas.`

---

**CUERPO — B-LOW FINAL:**

---

Hola, {{nombre}}.

Te hemos contado sobre la compra recurrente y quizás ahora mismo no era lo que buscabas. Está bien.

Pero por si acaso: la opción sigue disponible en tu cuenta cuando quieras.

**¿Qué es la compra recurrente y por qué muchos inversores la usan?**

En lugar de intentar adivinar cuándo comprar, la compra recurrente automatiza el proceso: eliges un importe fijo (desde {{suggested_dca_amount}}/mes), una frecuencia, y Bit2Me se encarga del resto.

Sin tener que seguir el mercado. Sin decisiones emocionales. Solo consistencia.

Tu cartera actual de **{{auc_eur}}** ya es un buen punto de partida. La compra recurrente es la forma más sencilla de hacerla crecer con el tiempo.

**[BOTÓN CTA] Ver cómo funciona**
`bit2me://dca/info`

Y si prefieres no recibir más sugerencias sobre compra recurrente, gestiona tus preferencias aquí.

Hasta cuando quieras,
El equipo de Bit2Me

---

**FOOTER EU DISCLAIMER (fuente >=12px, ancho completo):**

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

[Darte de baja] | [Ver en el navegador] | [Preferencias de privacidad]
Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España

---

**MiCA check B-LOW final:** ✅ DCA no implica rendimientos. Sin referencias a precios futuros. Lenguaje de "consistencia" aceptable. EU disclaimer completo.

---

## A/B Test Register

> ⚠️ **NOTA CRÍTICA:** Los tests de B3 (subject line A/B) y B3-CTA (CTA copy A/B) NO deben correr concurrentemente. Lanzar primero el test de subject line (2 semanas, n=500/variante). Solo después lanzar el test de CTA con los ganadores del primer test.


| ID | Touchpoint | Segmento | Variante A | Variante B | Hipótesis | Métrica primaria | Muestra mínima |
|---|---|---|---|---|---|---|---|
| AB-JN02B-01 | B2 Push | B-HIGH | "Tu {{primary_asset_held}} está parado, {{nombre}}" (personalización activo) | "¿Sabías que tu saldo podría generar recompensas?" (genérico curiosidad) | La personalización por activo genera mayor CTR que la curiosidad genérica | CTR push | 500 por variante |
| AB-JN02B-02 | B2 Push | B-LOW | "{{nombre}}, ¿ya tienes tu compra recurrente?" | "El mejor momento para empezar es hoy" | El framing de pregunta directa vs afirmación motivacional | CTR push | 500 por variante |
| AB-JN02B-03 | B3 Email | B-HIGH | Subject: "{{nombre}}, tu {{primary_asset_held}} podría estar generando recompensas" | Subject: "{{auc_eur}} parados: ¿y si los pones a trabajar?" | Personalización de nombre+activo vs endowment framing con saldo | Open rate | 400 por variante |
| AB-JN02B-04 | B3 Email | B-LOW | Subject: "Empieza con {{suggested_dca_amount}} al mes — sin complicaciones" | Subject: "La forma más sencilla de construir tu cartera crypto" | Importe concreto vs promesa de simplicidad | Open rate | 400 por variante |
| AB-JN02B-05 | B3 Email | B-HIGH | CTA: "Activar Earn ahora" | CTA: "Ver cómo funciona Earn" | CTA de conversión directa vs CTA educativo (menor fricción) | Click-to-open rate + conversión | 400 por variante |
| AB-JN02B-06 | B1 In-App | B-HIGH | Card Body: yield específico en EUR (si aplica umbral) | Card Body: solo APY % sin cifra EUR | Yield en EUR vs APY % — qué ancla mejor la percepción de valor | Tap rate en CTA | 300 por variante |

**Notas de implementación A/B:**
- Tests AB-JN02B-01 y AB-JN02B-02 se pueden correr en paralelo (segmentos distintos)
- Test AB-JN02B-05 requiere seguimiento a 14 días post-click (conversión downstream)
- Si variante B de AB-JN02B-06 gana, revisar yield copy decision tree — posible simplificación del modelo
- Significancia estadística mínima: p < 0.05, poder 80%

---

## Fallback Logic

| Variable no disponible | Comportamiento |
|---|---|
| `{{nombre}}` no disponible | Usar "inversor" — nunca dejar campo vacío |
| `{{primary_asset_held}}` no disponible | Usar "tus criptomonedas" |
| `{{auc_eur}}` no calculado en el momento de envío | SUPRIMIR touchpoints B1 y B2 hasta que esté disponible. En B3/B5 email usar "tu saldo en Bit2Me" sin cifra |
| `{{earn_apy}}` no disponible en tiempo real | Usar "un APY competitivo" — NUNCA inventar un porcentaje |
| `{{yield_eur}}` no calculable (APY o saldo no disponibles) | Forzar variante genérica — NUNCA mostrar cifra estimada |
| `{{suggested_dca_amount}}` no calculado | Usar fallback "10 EUR/mes" |
| `{{incentivo_earn_activo}}` = false o no disponible | Ocultar bloque de incentivo completamente — no mostrar placeholder |
| `{{incentivo_dca_activo}}` = false o no disponible | Ocultar bloque de incentivo completamente |
| Usuario en segmento B-HIGH pero auc_eur no confirmado | Tratar como B-LOW hasta confirmación — más seguro regulatoriamente |
| earn_annual_yield no calculable | Usar variante genérica obligatoriamente (regla MiCA) |

**Regla de oro de fallbacks:** en caso de duda, mostrar menos. Nunca inventar cifras. Nunca mostrar el nombre de la variable en bruto al usuario.

---

## Copy Rationale (Behavioral Economics)

### Efecto de dotación (Endowment Effect)
El copy B-HIGH usa consistentemente "tu {{primary_asset_held}}", "tus {{auc_eur}}", "tu saldo". Los activos ya pertenecen al usuario — la pérdida de no activar Earn se enmarca como no sacar partido de algo que ya poseen. Este framing activa la aversión a la pérdida de forma positiva: no es un riesgo nuevo que asumir, es una oportunidad dormida que ya tienen.

### Inercia y fricción percibida
B3 y B5 incluyen explícitamente "menos de 2 minutos" y "puedes desactivar cuando quieras". La principal barrera psicológica para Earn es el compromiso percibido. Reducir la fricción anticipada aumenta la tasa de inicio. El CTA alternativo "Ver cómo funciona" (AB-JN02B-05 variante B) opera en la misma lógica: el paso previo al paso.

### Anclaje de yield (Yield Anchoring)
Para B-HIGH con yield >= EUR 15/año, mostrar la cifra anual en EUR (no solo el %) ancla el valor de forma más tangible. "45 EUR" es más concreto que "4,5% APY" para usuarios no técnicos. La lógica de umbrales previene que cifras pequeñas (< EUR 15) parezcan insignificantes y generen el efecto contrario.

### Consistencia de hábito (B-LOW)
El framing DCA para B-LOW evita el lenguaje de rendimientos y se centra en la identidad: "sin decisiones emocionales", "solo consistencia". Este enfoque apela al self-concept del usuario — no es un esquema de riqueza, es una práctica disciplinada. Mayor alineación con valores de compradores racionales.

### Escalada de urgencia calibrada
B1 (informativo) → B2 (recordatorio con beneficio) → B3 (educación + incentivo) → B4 (urgencia de incentivo si aplica) → B5 (cierre suave). La urgencia se introduce solo cuando hay una razón legítima (incentivo real). B5 deliberadamente reduce la presión — preservar la relación con el usuario es prioritario sobre la conversión de este journey.

### Personalización por activo
Mencionar "Bitcoin", "Ethereum" o el activo real del usuario en lugar de "criptomonedas" genérico activa mayor reconocimiento y relevancia personal. Test AB-JN02B-01 valida esta hipótesis directamente.

---

## Diego Approval Notes — Flags para Revisión Legal

**PRIORIDAD ALTA — Requieren confirmación antes de activación:**

1. **Incentivo Earn +1% APY extra (B-HIGH):** Confirmar con Producto que el incentivo está aprobado y tiene fecha de caducidad definida. El copy usa bloque condicional — si `incentivo_earn_activo = false`, el bloque no se renderiza. Diego debe revisar los T&Cs del incentivo antes de cualquier envío.

2. **Incentivo sin comisión DCA (B-LOW):** Mismo tratamiento. Confirmar que la exención de comisión en primera compra recurrente está aprobada comercialmente y tiene cobertura legal.

3. **Fechas límite de incentivos:** Los emails B3 y B4 hacen referencia a {{fecha_fin_incentivo}}. Estas fechas deben estar confirmadas y ser reales antes del envío. No enviar con placeholder vacío.

**REVISIÓN ESTÁNDAR — Cumplimiento MiCA verificado en redacción:**

4. **Disclaimer de Earn:** Presente en todos los touchpoints que mencionan APY o Earn (B1, B2, B3, B4, B5 B-HIGH). Verificar que el footer de email cumple requisito de fuente >=12px en implementación HTML final.

5. **EU Disclaimer completo:** Presente en todos los emails (B3 B-HIGH, B3 B-LOW, B5 B-HIGH, B5 B-LOW). Verificar implementación HTML — ancho completo, fuente >=12px.

6. **Art. 66 MiCA — Portfolio losses:** El journey JN-02B NO debe activarse ni continuar para usuarios cuyo portfolio haya caído >10% en los 30 días previos al envío de cada touchpoint. Confirmar con Álvaro (Data Infra) que existe una señal de supresión para este caso. Si no existe, bloquear el journey hasta que esté implementada. **Esta es la flag de mayor riesgo regulatorio del journey.**

7. **Palabras prohibidas — lista de control para Diego:**

| Prohibida | Usada en su lugar | Verificado |
|---|---|---|
| "invertir" | "comprar", "adquirir" | ✅ |
| "rendimiento" | "APY", "recompensa" | ✅ |
| "intereses" | "recompensas" | ✅ |
| "beneficios" | "recompensas" | ✅ |
| "ingresos pasivos" | no usado | ✅ |
| "depositar" | "activar", "añadir" | ✅ |
| "gana mientras duermes" | PROHIBIDO — no aparece | ✅ |
| "sin riesgo" | PROHIBIDO — no aparece | ✅ |
| "garantizado" | PROHIBIDO — no aparece | ✅ |
| "dinero fácil" | PROHIBIDO — no aparece | ✅ |

8. **Supresión Art. 66:** Confirmar implementación técnica de la regla de supresión por pérdida de portfolio >10%. Esta es la flag de mayor riesgo regulatorio del journey y debe estar resuelta antes del lanzamiento.

**PROCESO DE APROBACIÓN SUGERIDO:**
1. Diego revisa este documento completo (plazo sugerido: 3 días hábiles)
2. Confirmar incentivos con Producto (Katy coordina)
3. Confirmar supresión Art. 66 con Álvaro
4. Aprobación final de Diego con firma/fecha
5. QA de implementación (variables, disclaimers visibles, supresiones activas)
6. Envío

---

*Documento generado: 2026-03-24 | Redacción: LC Team (Bit2Me) | Revisión pendiente: Diego Barreira (Legal)*
