# JN-02A: Sleeper to Trader — Copy & Creatives

**Plan:** 02-02 | **Sprint:** 1 | **Prioridad:** P0 (co-prioridad con JN-01-A)
**Segmento:** ~7,400 usuarios | **Goal:** Primera operación tras 90d+ de inactividad
**Fecha de creación:** 2026-03-24 | **Canales:** In-app card · Push · Email
**Coste de incentivo:** EUR 0 | **Stop conditions:** Trade, Earn, Price alert, DCA

---

## Dynamic Variables Master List

| Variable | Descripción | Fallback |
|---|---|---|
| `{{nombre}}` | Nombre de pila del usuario | `"inversor"` |
| `{{auc_eur}}` | Valor total del portfolio en EUR (ej. "EUR 340") | Omitir la línea que lo menciona |
| `{{primary_asset_held}}` | Activo principal en cartera (ej. "Bitcoin") | `"tus criptos"` |
| `{{last_trade_date}}` | Tiempo desde última operación (ej. "hace 4 meses") | `"hace tiempo"` |
| `{{price_change_7d_pct}}` | Variación del precio del activo principal en 7d (ej. "+12.4%") | Omitir referencia al precio |
| `{{portfolio_change_eur}}` | Variación en EUR del portfolio en 7d (ej. "EUR +47") | Omitir |
| `{{suggested_next_trade}}` | Activo sugerido para próxima operación (ej. "BTC") | `"BTC"` |
| `{{trader_level}}` | Nivel del trader: `"power"` (≥5 ops) o `"explorer"` (1-4 ops) | `"explorer"` |

---

## A1 — In-App Card (First Login — Portfolio/Market Screen)

> **Trigger:** `portfolio_screen_view` OR `market_screen_view` — primera sesión del journey
> **Suppress after:** 2 dismissals
> **Timing:** Inmediato al primer login que activa el journey

---

### Power Trader Variant (`trader_level = "power"`)

**Card Title:** `{{primary_asset_held}} lleva {{price_change_7d_pct}} esta semana`
*(fallback si no hay price_change: "El mercado se ha movido mucho" — max 40 chars)*

**Card Body:** `Llevas {{last_trade_date}} sin operar, pero tu criterio sigue aquí. ¿Qué ve el mercado que tú aún no has actuado?`
*(max 80 chars — ajuste dinámico con variables)*

**CTA Button:** `Ver mercado ahora`
*(max 20 chars)*

**Secondary action:** `Más tarde`

---

### Explorer Variant (`trader_level = "explorer"`)

**Card Title:** `{{primary_asset_held}} ha cambiado desde tu última operación`
*(fallback: "El crypto no para — tú tampoco tienes que hacerlo" — max 40 chars)*

**Card Body:** `Has operado antes. Llevas {{last_trade_date}} parado. El mercado tiene nuevas oportunidades esperando.`
*(max 80 chars)*

**CTA Button:** `Explorar mercado`
*(max 20 chars)*

**Secondary action:** `Más tarde`

---

**Trigger:** `portfolio_screen_view` OR `market_screen_view`
**Suppress after:** 2 dismissals
**MiCA check:** ✅ No garantías, no menciona "rendimiento". "Oportunidades" en contexto informativo. Sin valor en EUR absoluto en CTA. `{{portfolio_change_eur}}` no se usa aquí para no presionar sobre pérdidas potenciales.

**Creative Brief — In-App Illustration A1:**

- **Dimensiones:** 375×220px @2x retina (750×440px master)
- **Visual:** Gráfico de velas (candlestick) del activo principal en miniatura, con una flecha de tendencia ascendente suave. Fondo oscuro (#0D0F1A — dark mode de Bit2Me). Un punto de luz en el último precio (círculo blanco difuso) sugiere movimiento reciente.
- **Mood:** Tecnológico, limpio, mercado vivo. No celebratorio ni alarmista. Curioso.
- **Text overlay:** Solo el título de la card — tipografía blanca semibold, alineada izquierda sobre el gráfico con overlay degradado oscuro en la mitad inferior.
- **Color accent:** Verde #00D67E para la flecha y el punto de precio (Bit2Me green).
- **AI image prompt (English):** "Minimalist dark mode cryptocurrency candlestick chart card illustration, single upward price movement curve in bright green (#00D67E) on deep dark background (#0D0F1A), clean white price indicator dot with soft glow, no text, flat vector style, 375x220px mobile card format, professional fintech aesthetic, no logos"

---

## A2 — In-App Card (2nd Open — Escalated)

> **Trigger:** Segunda sesión del usuario tras haber visto A1 (o haberla descartado)
> **Suppress after:** 2 dismissals totales entre A1 + A2
> **Angulo:** Diferente al A1 — enfoque en su portfolio actual, no en el mercado

---

### Power Trader Variant

**Card Title:** `Tu portfolio: {{auc_eur}}. ¿Trabajando o dormido?`
*(fallback sin auc_eur: "Tu saldo lleva meses sin moverse" — max 40 chars)*

**Card Body:** `Tienes {{primary_asset_held}} en cartera. {{last_trade_date}} sin una sola operación. Un trader de tu nivel sabe cuándo volver.`
*(max 80 chars — ajuste dinámico)*

**CTA Button:** `Operar ahora`
*(max 20 chars)*

**Secondary action:** `Recordarme luego`

---

### Explorer Variant

**Card Title:** `Tu portfolio lleva {{last_trade_date}} pausado`
*(fallback: "Tu cartera lleva tiempo en pausa" — max 40 chars)*

**Card Body:** `{{primary_asset_held}} ha tenido movimiento. Quizás es momento de revisar tu posición y dar el siguiente paso.`
*(max 80 chars)*

**CTA Button:** `Revisar posición`
*(max 20 chars)*

**Secondary action:** `Más tarde`

---

**MiCA check:** ✅ "¿Trabajando o dormido?" es metáfora coloquial del dinero — no promete rendimiento. Mostrar `{{auc_eur}}` está permitido (usuario activo, login <30d). No se usan "rendimiento", "intereses" ni garantías.

> **Nota para Diego (A2):** "¿Trabajando o dormido?" podría interpretarse como insinuación de dinero trabajando. Alternativa conservadora: "Tu cartera lleva {{last_trade_date}} sin moverse" — revisar en aprobación.

**Creative Brief — In-App Illustration A2:**

- **Dimensiones:** 375×220px @2x retina
- **Visual:** Representación abstracta de una cartera/wallet con dos estados visuales: mitad izquierda en gris/apagado (activo dormido), mitad derecha iluminada con el logo del activo principal (BTC, ETH, etc.) brillando en verde. Efecto visual de "despertar".
- **Mood:** Contraste dormido/activo. Urgencia suave. No agresivo.
- **Text overlay:** Ninguno — el título de la card va sobre degradado oscuro en parte inferior.
- **Color accent:** Gris #4A4E6B (dormido) → verde #00D67E (activo). Transición de izquierda a derecha.
- **AI image prompt (English):** "Abstract cryptocurrency wallet illustration showing two halves: left half desaturated gray sleeping coins, right half glowing green active Bitcoin logo, smooth gradient transition in the center, dark background #0D0F1A, flat vector minimalist fintech style, mobile card 375x220px, no text, no logos except subtle coin symbol"

---

## A3 — Push Notification (D+7, sin engagement con A1/A2)

> **Trigger:** D+7 desde activación del journey si no ha habido interacción con A1 ni A2
> **Send time:** 20:30 CET (pico de uso nocturno, confirmado en datos Bit2Me)
> **Personalización:** `{{primary_asset_held}}` + `{{price_change_7d_pct}}`

---

### Variant A — Price Momentum (usar cuando `price_change_7d_pct` disponible y > 0)

**Title:** `{{primary_asset_held}} +{{price_change_7d_pct}} esta semana`
*(ej: "Bitcoin +12.4% esta semana" — max 50 chars)*

**Body:** `Llevas {{last_trade_date}} mirando el mercado sin operar. Otros traders de Bit2Me ya se han movido.`
*(max 90 chars)*

---

### Variant B — Identity/FOMO (usar cuando `price_change_7d_pct` no disponible o < 0)

**Title:** `{{nombre}}, el mercado no espera`
*(fallback: "El mercado no espera" — max 50 chars)*

**Body:** `Tu última operación fue {{last_trade_date}}. El crypto sigue moviéndose. ¿Cuándo es tu próximo movimiento?`
*(max 90 chars)*

---

**Send time:** 20:30 CET
**Deep link:** Directo a pantalla de mercado con `{{suggested_next_trade}}` preseleccionado
**MiCA check:** ✅ Variant A usa solo % (opción conservadora para push aunque active sleepers permiten EUR). "Otros traders ya se han movido" = social proof cualitativo genérico. Variant B no implica retorno ni garantía.

> **Nota para Diego (A3):** "Otros traders de Bit2Me ya se han movido" es social proof cualitativo. Si se requiere dato cuantificable, alternativa: "Miles de usuarios de Bit2Me operaron esta semana."

**Creative Brief — Push Banner (Rich Push):**

- **Dimensiones:** 1200×628px para rich push preview (iOS/Android media attachment)
- **Visual:** Gráfico lineal de precio del activo en los últimos 7 días con tendencia visible. Si `price_change_7d_pct` > 0: línea verde ascendente. Si < 0 o fallback: gráfico neutro azul con foco en símbolo del activo grande y centrado.
- **Mood:** Urgencia suave, informativa, no alarmista.
- **Text overlay:** Logo de Bit2Me en esquina superior derecha (blanco, pequeño). Sin más texto — el OS muestra título y body.
- **AI image prompt (English):** "Clean cryptocurrency price chart for push notification banner, simple green ascending line graph on dark #0D0F1A background, Bitcoin/crypto symbol subtly on the right, Bit2Me white logo small top-right corner, no text, 1200x628px landscape, professional fintech, flat minimal style"

---

## A4 — In-App Card (ONCE PER LIFETIME — tras entrega de A3)

> **Trigger:** Primer login tras envío confirmado de A3 (independientemente del CTR del push)
> **Regla CRITICA:** Se muestra UNA SOLA VEZ en toda la vida del usuario en este journey
> **Proposito:** Maximo impacto. El mensaje más relevante y persuasivo del journey.
> **Angulo:** Combina identidad de trader + valor real de su portfolio + fricción mínima

---

### Power Trader Variant

**Card Title:** `Traders como tú no esperan más tiempo`
*(max 40 chars)*

**Card Body:** `Tienes {{auc_eur}} en {{primary_asset_held}}. Llevas {{last_trade_date}} sin hacer nada. Una operación. Solo una. ¿Listo?`
*(fallback sin auc_eur: "Tu cartera lleva {{last_trade_date}} sin una sola operación. Un movimiento puede cambiarlo." — max 80 chars)*

**CTA Button:** `Hacer mi operación`
*(max 20 chars)*

**Secondary action:** `No, gracias`
*(esta dismissal cuenta como salida — no se vuelve a mostrar)*

---

### Explorer Variant

**Card Title:** `Una operación puede reactivar tu cartera`
*(max 40 chars)*

**Card Body:** `{{primary_asset_held}} sigue en tu portfolio. Llevas {{last_trade_date}} observando. El siguiente paso puede ser pequeño.`
*(max 80 chars)*

**CTA Button:** `Empezar a operar`
*(max 20 chars)*

**Secondary action:** `Ahora no`
*(salida definitiva del journey A4)*

---

**MiCA check:** ✅ "Reactivar tu cartera" es metáfora de acción del usuario, no promesa financiera. "El siguiente paso puede ser pequeño" = autonomía, sin presión. Sin mencionar rendimiento ni garantía.

> **Nota para Diego (A4):** Verificar que "Una operación puede reactivar tu cartera" no se interprete como consejo de inversión. Alternativa conservadora: "Una operación para retomar el ritmo."

**Creative Brief — In-App Illustration A4:**

- **Dimensiones:** 375×220px @2x retina (hero image de la card lifetime — debe ser notablemente más impactante que A1/A2)
- **Visual:** Silueta abstracta/estilizada (sin cara) de una persona frente a múltiples pantallas con gráficos crypto. Sensación de control y maestría. Fondo oscuro con destellos de verde en los gráficos. Ambiente de "sala de trading" minimalista y tech.
- **Mood:** Aspiracional. Empowering. Este es el momento del regreso al mercado.
- **Text overlay:** Ninguno en la imagen — el título de la card va en la UI nativa.
- **AI image prompt (English):** "Abstract minimalist silhouette of a person confidently standing in front of multiple trading screens showing green crypto charts, dark ambient tech environment, deep dark blue-black background, neon green accent lights #00D67E, cinematic composition, flat vector illustration, fintech professional aesthetic, no text, no faces, 375x220px card format, hero image quality"

---

## A5 — Email (D+14 non-responders a A1–A4)

> **Trigger:** D+14 si el usuario no ha generado ningún stop condition (trade, earn, alert, DCA)
> **Segmento:** Usuarios que no respondieron a ninguno de los touchpoints anteriores
> **Send time:** Martes o miércoles, 10:00 CET
> **Asunto split test:** Ver A/B Test Register

---

### Subject Line A (Price Momentum)
`{{nombre}}, {{primary_asset_held}} lleva {{price_change_7d_pct}} en 7 días`
*(fallback: "El crypto que tienes en cartera se ha movido esta semana")*

### Subject Line B (Identity/Challenge)
`Llevas {{last_trade_date}} sin operar, {{nombre}}. Eso está a punto de cambiar.`
*(fallback: "Han pasado meses. El mercado ha cambiado. ¿Y tú?")*

### Preheader
`Tu cartera en Bit2Me sigue activa. El mercado también. Solo falta un paso.`
*(max 90 chars)*

---

### Email Body

---

**[HEADER IMAGE — ver Creative Brief abajo]**

---

**Hola, {{nombre}}**
*(fallback: "Hola")*

El mercado de criptoactivos no para. Y tú tampoco eres de los que paran.

Pero llevamos {{last_trade_date}} sin verte operar en Bit2Me. Tu cartera sigue aquí — **{{auc_eur}} en {{primary_asset_held}}** *(omitir si no hay auc_eur)* — observando cómo el mercado se mueve.

La pregunta no es si vas a volver a operar. La pregunta es cuándo.

---

**¿Qué ha pasado en el mercado desde tu última operación?**

El crypto ha tenido semanas de alta volatilidad. Los traders más activos de Bit2Me han seguido cada movimiento. Tu activo principal — **{{primary_asset_held}}** — ha registrado **{{price_change_7d_pct}}** en los últimos 7 días.
*(omitir este párrafo de precio si `price_change_7d_pct` no está disponible)*

Los mercados no te esperan, pero Bit2Me sí.

---

**Un movimiento. Eso es todo lo que necesitas.**

No tienes que reinventarte ni hacer un análisis exhaustivo. Una operación — por pequeña que sea — te devuelve al ritmo. Muchos traders de Bit2Me vuelven con una sola compra de **{{suggested_next_trade}}** para retomar el pulso del mercado.

*(Para `trader_level = "power"`:)*
> Tienes el historial, tienes el criterio. Solo le falta al mercado verte de vuelta.

*(Para `trader_level = "explorer"`:)*
> Ya has dado el primer paso antes. El siguiente es igual de sencillo.

---

**[CTA BUTTON — centrado, full-width mobile, fondo #00D67E, texto #0D0F1A]**

`Operar en Bit2Me →`

*(deep link a pantalla de mercado con `{{suggested_next_trade}}` preseleccionado)*

---

*¿Prefieres seguir a tu ritmo? Tu portfolio en Bit2Me siempre estará esperándote.*

*(Línea de desuscripción: "Si no quieres recibir más comunicaciones de este tipo, [cancela aquí].")*

---

**[FOOTER — full width, font ≥12px, color #666666]**

Bit2Me Sociedad de Valores, S.A. · Calle Príncipe de Vergara 112, Madrid, España
[Política de privacidad] · [Términos y condiciones] · [Cancelar suscripción]

---

### MiCA Footer



Un saludo,
**El equipo de Bit2Me**

**[DISCLAIMER — footer, font ≥12px, full width, color #666666]**

> Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

**Creative Brief — Email Header Image:**

- **Dimensiones:** 600×280px (email header estándar), versión mobile 375×175px
- **Visual:** Composición dividida en dos zonas: zona izquierda muestra un gráfico de precios crypto abstracto (velas + línea de precio) con la línea de tiempo extendiéndose hacia la derecha. Zona derecha: espacio claro con el símbolo del activo principal brillando sutilmente (BTC/ETH según `primary_asset_held`). Una línea temporal conecta ambas zonas — sugiriendo "antes y ahora".
- **Mood:** Narrativa de tiempo. Regreso. No urgencia agresiva — el momento es ahora.
- **Text overlay:** Tagline opcional en zona derecha: *"El mercado sigue. Vuelve."* — tipografía Bit2Me, blanco, semibold. *(Evaluar con Diego si es demasiado directivo como consejo de acción)*
- **Color palette:** #0D0F1A fondo, #00D67E acento en gráficos, #FFFFFF tipografía, #1E2235 zona derecha ligeramente más clara.
- **AI image prompt (English):** "Email header banner for crypto trading app re-engagement, split composition: left side shows abstract candlestick price chart with time axis extending right, right side shows softly glowing Bitcoin/cryptocurrency symbol, connecting timeline line between both zones, dark background #0D0F1A, green accent #00D67E for price movements, white typography area on right, 600x280px landscape, professional fintech flat design, no logos, minimal text space reserved"

---

## A/B Test Register

| # | Qué testear | Variant A | Variant B | Hipótesis | Métrica principal | Tamaño mínimo |
|---|---|---|---|---|---|---|
| T1 | Asunto email A5 | Price momentum ("{{primary_asset_held}} lleva {{price_change_7d_pct}}") | Identity challenge ("Llevas {{last_trade_date}} sin operar") | El precio supera al challenge en Open Rate; identity supera en CTR | Open Rate + CTR | 1,000 por rama |
| T2 | CTA principal A1 (Power) | "Ver mercado ahora" | "¿Qué me he perdido?" | Curiosity gap vs. acción directa — el gap puede reducir fricción en primera interacción | CTR in-app card | 500 por rama |
| T3 | Angle A3 push | Variant A (precio positivo) | Variant B (identidad / precio no disponible) | El precio positivo convierte mejor que identidad en push cuando está disponible | CTR push → trade | 1,000 por rama (segmentar por disponibilidad de variable) |
| T4 | Tonalidad A4 Power | "Traders como tú no esperan más tiempo" | "Solo una operación. ¿La hacemos?" | Peer framing vs. low-commitment ask — el segundo puede reducir intimidación | CTR → trade completion | 500 por rama |
| T5 | Send time A5 email | Martes 10:00 CET | Miércoles 19:00 CET | Prime time matutino entre semana vs. tarde de máxima intención | Open Rate + CTR | 700 por rama |

---

## Fallback Logic

| Variable faltante | Acción |
|---|---|
| `{{nombre}}` no disponible | Usar "inversor" en card/push; omitir saludo personalizado en email, usar "Hola" |
| `{{auc_eur}}` no disponible | Omitir cualquier mención al valor del portfolio; no construir CTA sobre ello |
| `{{primary_asset_held}}` no disponible | Usar "tus criptos" en copy; email header usa BTC genérico |
| `{{last_trade_date}}` no disponible | Usar "hace tiempo" — nunca dejar el placeholder visible |
| `{{price_change_7d_pct}}` no disponible o < 0 | Omitir completamente la referencia al precio; usar Variant B en A3; omitir bloque de precio en email |
| `{{portfolio_change_eur}}` no disponible | Omitir el dato — no es crítico para el copy |
| `{{suggested_next_trade}}` no disponible | Usar "BTC" como fallback universal |
| `{{trader_level}}` no disponible | Usar Explorer variant (tono más inclusivo como default seguro) |

**Regla Art. 66 MiCA:** Si en el momento de envío el portfolio del usuario ha caído >10% en los últimos 30 días, el journey debe PAUSARSE para ese usuario hasta recuperación. Implementar como audience filter en CleverTap antes de cada touchpoint — no a nivel de plantilla.

---

## Copy Rationale

**Por qué este copy convierte — psicología conductual aplicada:**

**1. Identidad de trader activada ("eres un trader")**
El copy Power usa consistentemente el frame "traders como tú", activando la identidad preexistente. El compromiso con la identidad pasada ("he sido trader") reduce la fricción para retomar el comportamiento — el usuario no "empieza", "vuelve". Más fácil de hacer que de evitar.

**2. Curiosity gap en vez de instrucción directa**
Especialmente en A1 y A3 Variant B, el copy no dice "opera ahora". Pregunta: "¿Qué ve el mercado que tú aún no has actuado?" El cerebro no puede cerrar un gap abierto — genera motivación intrínseca de resolverlo (Loewenstein, 1994). El usuario se autoconvence.

**3. Social proof calibrado, no agresivo**
"Otros traders de Bit2Me ya se han movido" usa social proof sin inventar datos ni generar ansiedad desproporcionada. Los sleepers son "watchers" por definición — ya tienen el hábito de observar. El social proof empuja desde observación a acción sin forzar.

**4. Reducción del compromiso percibido**
"Una operación. Solo una." y "El siguiente paso puede ser pequeño" aplican el principio de reducción de umbral de entrada. El mayor bloqueante de los sleepers no es conocimiento ni acceso — es la inercia. El copy la rompe minimizando el tamaño percibido del primer movimiento.

**5. Arco temporal en email**
La estructura del email A5 comienza en el presente activo del mercado, retrocede al pasado del usuario, y termina en el futuro posible. Este arco temporal recalibra la percepción de urgencia sin usar palabras prohibidas ni crear presión artificial.

**6. Momentum de precio como ancla racional**
Para usuarios con `price_change_7d_pct` positivo, el dato es el mejor argumento disponible — no hay copy más persuasivo que un número real y verificable. La variante de precio usa la ventana de movimiento del mercado como detonador temporal concreto.

---

## Diego Approval Notes — Compliance Review

**Banderas para revisión legal antes del deploy:**

| Flag | Touchpoint | Texto en cuestión | Riesgo potencial | Alternativa propuesta |
|---|---|---|---|---|
| FLAG-01 | A3 Variant A | "Otros traders de Bit2Me ya se han movido" | Social proof cualitativo — podría interpretarse como comparación implícita de resultados | Alternativa: "Miles de usuarios de Bit2Me operaron esta semana" (si dato es verificable) |
| FLAG-02 | A4 Power | "Hacer mi operación" (CTA en primera persona) | Apropiación de la decisión del usuario — estándar en UX pero confirmar | Riesgo bajo — mantener salvo indicación contraria |
| FLAG-03 | A5 Email Body | "Los traders más activos de Bit2Me han seguido cada movimiento" | Implicación de acceso privilegiado o ventaja | Texto ya ajustado a "seguido" (neutro) — mantener |
| FLAG-04 | Email Header overlay | "El mercado sigue. Vuelve." | Potencialmente directivo como recomendación de acción | Alternativa: omitir texto overlay — la imagen sola es suficiente |
| FLAG-05 | A2 Power title | "¿Trabajando o dormido?" | Metáfora del dinero trabajando — implícitamente sugiere rendimiento | Alternativa: "Tu cartera lleva {{last_trade_date}} sin moverse" |
| FLAG-06 | Todos | Uso de `{{auc_eur}}` en mensajes | Mostrar valor de portfolio en EUR en comunicaciones | Confirmar con Diego que criterio `last_login < 30d` es suficiente para calificar como "usuario activo" bajo MiCA |
| FLAG-07 | Explorer A4 | "Una operación puede reactivar tu cartera" | Podría interpretarse como consejo de acción financiera | Alternativa: "Una operación para retomar el ritmo" |

---

**Pre-send checklist para Katy (CleverTap):**

- [ ] Audience filter: excluir usuarios con portfolio_change_30d < -10% (Art. 66 MiCA)
- [ ] Audience filter: excluir usuarios con account_status != 'enabled'
- [ ] Audience filter: excluir usuarios con auc_eur >= 10,000 (whale exclusion — J12)
- [ ] Audience filter: excluir usuarios en journey J12, J5 (B2B) o con stop condition activa
- [ ] Fallback variables activadas en CleverTap para todos los campos listados en Variable Master List
- [ ] Deep link configurado: pantalla de mercado con `{{suggested_next_trade}}` preseleccionado
- [ ] Test send a lista interna (Daniel + Diego + Katy) antes de producción
- [ ] A4 configurado como "mostrar UNA SOLA VEZ por usuario" — verificar flag en CleverTap
- [ ] A/B test T1 (email subject) activado con distribución 50/50 y holdout de control

---

*Documento generado: 2026-03-24 | Version: 1.0 | Siguiente revisión: post-Diego approval*
*Owner: Daniel Ferraro — Head of Growth, Bit2Me*
*Ejecución: Katy Gildemeister (CleverTap) | Legal: Diego (aprobación pre-send obligatoria)*
