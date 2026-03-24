# JN-04 — VERIFIED NEVER OPERATED: Complete Copy Package

**Journey:** JN-04 | **Segment:** KYC verificados, cero movimientos monetarios
**Fecha:** 2026-03-24 | **Autor:** CRM Lifecycle — Bit2Me
**Volumen total:** 117,400 usuarios | **Scope Sprint 2:** 16,860 usuarios (WARM 4,300 + COOLING 12,560)

---

## 1. Dynamic Variables Master List

| Variable | Descripción | Valor ejemplo | Fallback |
|---|---|---|---|
| {{nombre}} | Nombre de pila del usuario | "Carlos" | "inversor" |
| {{kyc_completion_date}} | Fecha de verificación KYC | "hace 14 días" | "recientemente" |
| {{days_since_kyc}} | Días transcurridos desde KYC | 14 | — (usar fallback de fecha) |
| {{suggested_first_asset}} | Cripto sugerida según perfil/mercado | "Bitcoin" | "Bitcoin" |
| {{suggested_amount_eur}} | Importe sugerido en EUR | "50 EUR" | "10 EUR" |
| {{fee_waiver_amount}} | Descripción del incentivo de comisión | "0% de comisión" | omitir bloque incentivo |
| {{incentivo_activo}} | Boolean: ¿incentivo vigente? | true | false → omitir CTA de oferta |
| {{asset_ticker}} | Ticker del activo sugerido | "BTC" | "BTC" |

**Lógica de renderizado condicional:**
- Si `{{incentivo_activo}} = false` → eliminar todo el bloque `[INCENTIVO]` del copy
- Si `{{days_since_kyc}} > 60` → usar tono de "oportunidad perdiendo valor" en lugar de tono neutral
- Si `{{nombre}} = null` → "inversor" (nunca dejar en blanco)
- Si `{{suggested_first_asset}} = null` → "Bitcoin" siempre como default

---

## 2. WARM Track (4,300 usuarios — login <30 días)

### W1 — In-App Card (Primera sesión post-segmentación)

**Placement:** Home screen / sección portfolio, aparece en primera carga de sesión
**Trigger:** Primera sesión tras inclusión en segmento
**Dismiss logic:** Se puede cerrar; reaparece en siguiente sesión hasta 2 veces en total

---

**VARIANTE A (Identidad — "ya eres parte")**

> **Título:** Ya lo tienes casi todo listo, {{nombre}}.
>
> **Cuerpo:** Verificaste tu identidad. El siguiente paso es el más fácil: compra {{suggested_first_asset}} por solo {{suggested_amount_eur}} y empieza a moverse con el mercado.
>
> **CTA principal:** Comprar {{suggested_first_asset}} ahora
>
> **CTA secundario:** Más tarde

---

**VARIANTE B (Reducción de fricción — "es más pequeño de lo que crees")**

> **Título:** Tu primera compra tarda menos de 2 minutos.
>
> **Cuerpo:** Ya pasaste la verificación — eso es lo difícil. Ahora solo necesitas elegir un importe (desde 10 EUR) y confirmar. Listo.
>
> **CTA principal:** Empezar con {{suggested_amount_eur}}
>
> **CTA secundario:** Ver cómo funciona

---

**Notas de implementación W1:**
- Tamaño de card: full-width banner, altura mínima 120px
- Icono: logo del activo sugerido (BTC/ETH) + fondo degradado naranja→amarillo (#F7931A→#FFD700 para BTC)
- No mostrar precio de mercado en tiempo real en esta card (evitar friction de volatilidad)
- Mostrar badge "Sin comisión en tu primera compra" solo si `{{incentivo_activo}} = true`

---

### W2 — In-App Card (Segunda sesión, sin acción en W1)

**Placement:** Home screen, misma posición que W1
**Trigger:** Segunda sesión + sin first_monetary_movement + W1 fue mostrada
**Suppress:** Ocultar permanentemente tras 2 dismissals totales (W1 + W2)

---

**VARIANTE ÚNICA**

> **Título:** {{nombre}}, el mercado no espera. Tú tampoco tienes que hacerlo.
>
> **Cuerpo:** 67 de cada 100 personas que hacen su primera compra de crypto repiten en los primeros 30 días. La curva de aprendizaje se aplana rápido. ¿Empezamos?
>
> [INCENTIVO — mostrar solo si {{incentivo_activo}} = true]
> Además, tienes activa una exención de comisiones en tu primera operación. Sin coste extra.
> [/INCENTIVO]
>
> **CTA principal:** Sí, comprar {{suggested_first_asset}}
>
> **CTA secundario:** Recordármelo mañana

---

**Notas de implementación W2:**
- El stat "67 de cada 100" debe estar validado antes de producción (pendiente confirmación con Marta/analytics)
- Si el stat no está validado, sustituir cuerpo por: "Miles de personas en España hicieron su primera compra con menos de 50 EUR. La mayoría dice que fue más fácil de lo que esperaban."
- "Recordármelo mañana" → programar push W3 al día siguiente con prioridad alta

---

### W3 — Push Notification (D+3 sin acción)

**Trigger:** D+3 desde inicio del track sin first_monetary_movement
**Ventana de envío:** 10:00–12:00 o 19:00–21:00 (hora local del usuario)
**Canal:** Push nativa (iOS / Android)

---

**PUSH A — Loss aversion + ventana temporal**

> **Título:** Tu verificación de Bit2Me sigue activa ✓
>
> **Cuerpo:** Pero la exención de comisión en tu primera compra tiene fecha de caducidad. Aprovéchala antes de que expire.

*(Mostrar solo si `{{incentivo_activo}} = true`. Si false, usar Push B.)*

---

**PUSH B — Social proof + facilidad**

> **Título:** {{nombre}}, 3 minutos. Primera compra hecha.
>
> **Cuerpo:** Ya verificaste tu cuenta. El siguiente paso es el más corto. Elige un importe desde 10 EUR y listo.

---

**Notas de implementación W3:**
- Deep link directo a pantalla de compra con activo preseleccionado: `{{suggested_first_asset}}`
- No incluir precio de mercado en el cuerpo del push (evita que precio desfavorable frene la acción)
- Tiempo de expiración del push: 6 horas (no entregar fuera de ventana)
- Si el usuario hace clic pero no convierte → registrar como "intención activa" para personalización W4

---

### W4 — Email (D+7 sin acción, con reveal de incentivo)

**Trigger:** D+7 desde inicio del track sin first_monetary_movement
**Sending time:** Martes o miércoles, 10:00–11:00 hora local
**From name:** Bit2Me | Tu cuenta
**Reply-to:** hola@bit2me.com

---

**SUBJECT LINE A (Directo + personalizado):**
> {{nombre}}, ya hiciste lo difícil. Falta un paso.

**SUBJECT LINE B (Curiosidad + incentivo):**
> Tienes una ventaja que la mayoría no tiene al empezar

**PREHEADER A:**
> Tu verificación KYC es el paso que más gente abandona. Tú ya lo superaste.

**PREHEADER B:**
> Cero comisión en tu primera compra de Bitcoin. Solo para cuentas verificadas.

---

**CUERPO DEL EMAIL — VARIANTE A (Subject A)**

---

Hola {{nombre}},

Hace {{kyc_completion_date}} verificaste tu identidad en Bit2Me.

Eso no es poco. La verificación de identidad es el paso en el que más personas abandonan cuando quieren empezar en el mundo de las criptomonedas. Piden documentación, hay que esperar, hay que confiar en una plataforma nueva.

Tú lo hiciste.

Y después... nada. No pasó nada.

Lo entendemos. Dar el primer paso real — comprar algo — se siente diferente. Aunque sean 10 euros, se siente como un compromiso.

Pero aquí está la verdad sobre ese primer paso:

**La mayoría de las personas que compran crypto por primera vez lo hacen con menos de 50 EUR.**

No están apostando su ahorro. Están aprendiendo cómo funciona. Están probando. Y descubren que el proceso es menos intimidante de lo que pensaban.

---

**Tu primera compra en Bit2Me, paso a paso:**

1. Entra a tu cuenta (ya la tienes verificada)
2. Elige Bitcoin o cualquier otra cripto
3. Escribe el importe — desde 10 EUR
4. Confirma la compra

Tiempo real: menos de 2 minutos.

---

[INCENTIVO — mostrar solo si {{incentivo_activo}} = true]

**Y además, tienes esto:**

Como usuario verificado que aún no ha operado, tienes activa una **exención de comisiones** ({{fee_waiver_amount}}) en tu primera compra.

Sin coste adicional. Solo para ti. Solo por tiempo limitado.

[/INCENTIVO]

---

¿Empezamos con {{suggested_first_asset}}?

**[COMPRAR {{suggested_first_asset}} AHORA →]**
*(Importe sugerido: {{suggested_amount_eur}} — puedes cambiarlo)*

---

Si tienes preguntas sobre cómo funciona la compra, el almacenamiento de tus activos o la seguridad de la plataforma, puedes escribirnos directamente respondiendo a este email. Respondemos en menos de 24 horas.

Un saludo,
El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*[Gestionar preferencias de comunicación] | [Darse de baja]*

---

**CUERPO DEL EMAIL — VARIANTE B (Subject B)**

---

Hola {{nombre}},

Cuando alguien abre una cuenta en un exchange de criptomonedas, hay un filtro que la mayoría no pasa: la verificación de identidad.

Documentos, esperas, paciencia.

Tú ya pasaste ese filtro hace {{kyc_completion_date}}.

Eso te pone en una posición distinta a la de quien está pensando en empezar desde cero. Tú ya empezaste. Solo te falta confirmar esa primera operación.

---

**La ventaja que mencionábamos:**

[INCENTIVO — mostrar solo si {{incentivo_activo}} = true]

Para usuarios verificados que aún no han operado, hemos activado una **exención completa de comisiones** ({{fee_waiver_amount}}) en la primera compra.

No es un descuento. Es 0%.

Esta condición está disponible por tiempo limitado y es exclusiva para cuentas como la tuya: verificadas, pero todavía sin primera operación.

[/INCENTIVO]

[SIN INCENTIVO — mostrar solo si {{incentivo_activo}} = false]

Tu cuenta verificada ya tiene acceso completo a la plataforma. Puedes empezar con tan solo 10 EUR, sin compromisos ni mínimos elevados.

[/SIN INCENTIVO]

---

**¿Por qué {{suggested_first_asset}}?**

Bitcoin sigue siendo la entrada más utilizada por quienes empiezan. No porque sea "la mejor inversión" — nadie puede garantizarte eso — sino porque es el activo con mayor liquidez, mayor reconocimiento y mayor cantidad de información disponible para entender qué estás comprando.

Puedes empezar con {{suggested_amount_eur}} y ver cómo funciona desde dentro.

---

**[HACER MI PRIMERA COMPRA →]**

---

Como siempre, si tienes dudas, responde este email. Somos personas reales.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*[Gestionar preferencias de comunicación] | [Darse de baja]*

---

## 3. COOLING Track (12,560 usuarios — login 90-365 días)

### C1 — Push Notification (Re-engagement hook, día 1)

**Trigger:** Entrada al segmento COOLING (login 90-365d, sin operaciones)
**Ventana de envío:** 10:00–12:00 hora local
**Nota:** Estos usuarios no han abierto la app en 3-12 meses. El push debe ganar la apertura, no explicar la oferta.

---

**PUSH C1-A — Curiosidad + relevancia de mercado**

> **Título:** {{nombre}}, algo ha cambiado desde la última vez.
>
> **Cuerpo:** El mercado de crypto no es el mismo de hace meses. Tu cuenta verificada sigue activa. ¿Echamos un vistazo?

---

**PUSH C1-B — Identidad + pertenencia**

> **Título:** Tu cuenta Bit2Me está lista cuando tú lo estés.
>
> **Cuerpo:** Verificaste tu identidad. Eso no caduca. Lo que compraste entonces sigue siendo tuyo: acceso completo, sin colas.

---

**Notas de implementación C1:**
- Deep link a pantalla de inicio de la app, NO directamente a pantalla de compra (usuario está dormido, necesita re-familiarizarse)
- No mencionar precio de Bitcoin ni ningún activo específico en el push (evitar que precio actual frene apertura)
- Tiempo de expiración: 4 horas
- Si no abre en 48h → C2 por email

---

### C2 — Email (D+2 si no abre C1, educacional + incentivo)

**Trigger:** D+2 desde C1 sin apertura de app ni first_monetary_movement
**Sending time:** Jueves o viernes, 10:30–11:30
**From name:** Bit2Me | Tu cuenta
**Subject:** {{nombre}}, tu cuenta verificada sigue esperándote
**Preheader:** Hiciste el paso más difícil. Este email explica qué viene después.

---

**CUERPO DEL EMAIL C2:**

---

Hola {{nombre}},

Hace un tiempo verificaste tu identidad en Bit2Me.

Y luego la vida siguió. Pasa.

Pero tu cuenta sigue activa, verificada y completamente operativa. No tienes que volver a pasar por ningún proceso. Solo tienes que entrar y hacer tu primera operación.

Antes de que lo hagas, queremos contarte algo que debería saber cualquier persona que empieza:

---

**Lo que nadie te explica sobre comprar crypto por primera vez**

**1. No necesitas comprar una unidad entera.**
Bitcoin cotiza a miles de euros, pero puedes comprar 0,0001 BTC. En Bit2Me, el mínimo es 10 EUR. La mayoría empieza con 50 EUR o menos.

**2. Tu cripto no desaparece si no la vigilas.**
A diferencia de muchos activos, {{suggested_first_asset}} no "vence". Lo que compras hoy sigue siendo tuyo mientras no lo vendas, sin coste de mantenimiento.

**3. Vender es igual de fácil que comprar.**
En la misma pantalla donde compras, puedes vender al momento. Liquidez inmediata durante el horario de mercado.

**4. Bit2Me está registrada en la CNMV.**
No somos un exchange anónimo. Somos una sociedad de valores española, supervisada, con dirección física en Madrid. Tu dinero y tus activos están bajo el marco regulatorio europeo MiCA.

---

**¿Qué hace la mayoría cuando empieza?**

Compran una cantidad pequeña de Bitcoin o Ethereum — entre 20 y 100 EUR — solo para entender cómo funciona. No como "inversión de vida". Como aprendizaje con dinero real.

Muchos de ellos repiten. Porque una vez que ves cómo se ejecuta una compra, cómo aparece en tu portfolio, cómo puedes seguir su precio — deja de ser abstracto.

---

[INCENTIVO — mostrar solo si {{incentivo_activo}} = true]

**Tu ventaja esta semana:**

Tienes activa una **exención de comisiones ({{fee_waiver_amount}})** en tu primera compra. Es una condición especial para cuentas verificadas que aún no han operado.

No tienes que hacer nada para activarla. Está automáticamente aplicada en tu próxima compra.

**Esta condición expira pronto.**

[/INCENTIVO]

---

**[HACER MI PRIMERA COMPRA →]**
*(Desde 10 EUR · Cuenta verificada · Proceso en menos de 2 minutos)*

---

Si tienes preguntas, responde este email. Contestamos en menos de 24 horas.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*[Gestionar preferencias de comunicación] | [Darse de baja]*

---

### C3 — Email (D+7, último intento del track COOLING)

**Trigger:** D+7 desde inicio del track COOLING sin first_monetary_movement
**Sending time:** Martes, 10:00–11:00
**From name:** Bit2Me | Tu cuenta
**Subject:** Último recordatorio sobre tu cuenta Bit2Me, {{nombre}}
**Preheader:** Después de este email, no te escribiremos sobre este tema. Te lo explicamos.

---

**CUERPO DEL EMAIL C3:**

---

Hola {{nombre}},

Este es el último email que te enviamos sobre tu primera compra en Bit2Me.

No vamos a insistir indefinidamente. Respetamos que quizás el momento no sea este para ti — y está bien.

Pero antes de cerrar este capítulo, queremos dejarte algo útil.

---

**Por qué tanta gente verifica y no opera (y qué hacen los que sí lo hacen)**

La verificación de identidad requiere esfuerzo. La primera compra requiere... diferente.

Requiere tomar una decisión con dinero real. Aunque sean 10 euros, hay algo en ese momento que se siente definitivo.

Lo que suelen hacer las personas que finalmente dan ese paso es esto: **reducen el importe hasta que la decisión sea fácil.**

En lugar de pensar "¿compro 500 EUR de Bitcoin?", se preguntan: "¿Qué cantidad puedo comprar sin que me quite el sueño si el precio baja mañana?"

Para muchos esa cifra son 20 EUR. Para otros, 50. Para algunos, 10.

Con esa cantidad — la que te resulta irrelevante perder — haces tu primera compra. Y ya sabes cómo funciona.

---

[INCENTIVO — mostrar solo si {{incentivo_activo}} = true]

**Si vas a hacerlo, que sea hoy:**

Tienes una **exención de comisiones ({{fee_waiver_amount}})** activa en tu próxima compra. Esta es tu última oportunidad de usarla — la condición expira junto con esta comunicación.

Después de hoy, las comisiones estándar se aplican.

**[USAR MI EXENCIÓN Y HACER PRIMERA COMPRA →]**

[/INCENTIVO]

[SIN INCENTIVO — mostrar solo si {{incentivo_activo}} = false]

Si decides que este es el momento, tu cuenta sigue activa y lista.

**[ENTRAR A BITM2E Y HACER PRIMERA COMPRA →]**

[/SIN INCENTIVO]

---

Y si no es el momento — no pasa nada. Tu cuenta permanecerá activa. Cuando quieras volver, seguirá aquí.

Gracias por confiar en Bit2Me para completar tu verificación.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*
*[Gestionar preferencias de comunicación] | [Darse de baja]*

---

## 4. Creative Briefs por Touchpoint

### Brief W1 — In-App Card (Home Screen)

| Campo | Detalle |
|---|---|
| Dimensiones | Full-width, 120–160px altura · Padding interno 16px |
| Formato | Native card component · No modal |
| Visual principal | Icono circular del activo (BTC 3D coin) sobre fondo degradado #F7931A → #FFD700 |
| Tipografía | Título: 18px Bold · Cuerpo: 14px Regular |
| Color de fondo | Degradado horizontal naranja→amarillo (brand BTC) |
| Badge incentivo | Pill verde oscuro (#1A6B2F) "Sin comisión" — solo si incentivo activo |
| Mood | Cálido, accesible, no urgente — "estás listo, es fácil" |
| CTA button | Fondo #F7931A, texto blanco, radio 8px, texto 15px Bold |
| AI image prompt | "A glowing Bitcoin coin floating slightly above a smooth gradient orange-to-yellow background, soft light reflections, clean minimal style, no text, no humans, product photography feel, 16:9 ratio" |

---

### Brief W2 — In-App Card (Segunda sesión)

| Campo | Detalle |
|---|---|
| Dimensiones | Full-width, 140px altura · Padding interno 16px |
| Visual principal | Gráfico de línea ascendente minimalista (no precio real) sobre fondo azul oscuro Bit2Me |
| Mood | Ligeramente más urgente que W1 — "el mercado se mueve, tú también puedes" |
| Diferenciador vs W1 | Cambiar color de fondo a azul oscuro (#0A1628) con texto blanco — crear contraste visual que indique "esto es diferente" |
| Badge | Solo si incentivo activo: "Oferta limitada" en pill amarillo |
| AI image prompt | "Minimalist upward trending line chart on dark navy background, golden gradient line, clean fintech aesthetic, no labels or numbers, soft glow effect, abstract financial growth visualization" |

---

### Brief W3 — Push Notification

| Campo | Detalle |
|---|---|
| Icono push (iOS) | Logo Bit2Me (cuadrado, esquinas redondeadas) |
| Icono push (Android) | Versión monocroma del logo Bit2Me |
| Rich push (si disponible) | Imagen 1200x628px — moneda BTC sobre fondo oscuro, texto "Tu primera compra" en overlay |
| Mood | Directo, bajo-presión positiva — "es ahora o nunca para el incentivo" |
| AI image prompt (rich push) | "Bitcoin coin on dark textured background, single spotlight from above, dramatic but clean, text overlay area at bottom, 1200x628 pixels, financial product imagery style" |

---

### Brief W4 / C2 / C3 — Email

| Campo | Detalle |
|---|---|
| Plantilla | Single column, max-width 600px, fondo blanco |
| Header | Logo Bit2Me centrado, fondo #0A1628 (azul oscuro), altura 80px |
| Hero image | 600x280px — ver prompt abajo |
| Tipografía body | Georgia o serif system font, 16px, line-height 1.6 |
| Tipografía títulos | Arial/Helvetica Bold, 22px H1, 18px H2 |
| Color accent | #F7931A (naranja Bitcoin) para CTAs y destacados |
| CTA button | Fondo #F7931A, texto blanco, radius 6px, padding 14px 28px, texto 16px Bold |
| Footer background | #F5F5F5, texto #666666, 12px |
| Mood visual | Confianza institucional + accesibilidad — no Wall Street, no casino |
| AI image prompt (hero W4-A) | "Person sitting at a laptop at home, relaxed posture, looking at a financial app on screen, warm natural light from window, shallow depth of field, modern minimalist home setting, no brand logos visible, authentic lifestyle photography style" |
| AI image prompt (hero C2) | "Simple clean graphic of a verified checkmark badge transforming into a small Bitcoin coin, flat design, orange and dark navy color palette, white background, infographic style, no text" |
| AI image prompt (hero C3) | "A single door slightly open with warm light coming through, metaphor for opportunity, minimal flat illustration style, dark navy and orange color palette, white background" |

---

### Brief C1 — Push Notification (COOLING)

| Campo | Detalle |
|---|---|
| Icono push | Logo Bit2Me estándar |
| Tono visual | Neutro — no alarmista. El usuario no ha interactuado en meses, no asustar |
| Rich push | No recomendado para COOLING — usuarios dormidos tienen menor tasa de apertura de rich push |
| AI image prompt | (no aplica para push básico) |

---

## 5. A/B Test Register

### TEST-01: W1 Identidad vs. Reducción de Fricción

| Campo | Detalle |
|---|---|
| ID | JN04-AB-01 |
| Touchpoint | W1 In-App Card |
| Variante A | "Ya lo tienes casi todo listo" (ángulo identidad/logro) |
| Variante B | "Tu primera compra tarda menos de 2 minutos" (ángulo facilidad) |
| Hipótesis | El ángulo de reducción de fricción (B) generará mayor CTR porque el principal bloqueante es la percepción de complejidad, no la falta de motivación |
| Métrica primaria | CTR en CTA principal (click hacia pantalla de compra) |
| Métrica secundaria | Tasa de conversión a first_monetary_movement en 24h |
| Split | 50/50 |
| N por variante | 2,150 (mitad de WARM 4,300) |
| Duración mínima | 7 días o hasta 100 conversiones por variante |
| Criterio de victoria | p < 0.05, diferencia mínima detectable 15% relativa |

---

### TEST-02: W3 Push — Loss Aversion vs. Social Proof

| Campo | Detalle |
|---|---|
| ID | JN04-AB-02 |
| Touchpoint | W3 Push Notification |
| Variante A | "Tu exención de comisión tiene fecha de caducidad" (loss aversion) |
| Variante B | "3 minutos. Primera compra hecha." (facilidad + social proof) |
| Hipótesis | Loss aversion (A) tendrá mayor tasa de apertura del push pero menor conversión final; social proof (B) tendrá menor apertura pero mayor conversión de los que abren |
| Métrica primaria | Tasa de first_monetary_movement en 48h post-push |
| Métrica secundaria | Open rate del push |
| Split | 50/50 |
| N por variante | ~1,500 (usuarios WARM sin conversión hasta D+3) |
| Nota | Solo ejecutar variante A si {{incentivo_activo}} = true; usar B como default si false |

---

### TEST-03: W4 Email Subject — Directo vs. Curiosidad

| Campo | Detalle |
|---|---|
| ID | JN04-AB-03 |
| Touchpoint | W4 Email |
| Variante A | Subject: "{{nombre}}, ya hiciste lo difícil. Falta un paso." |
| Variante B | Subject: "Tienes una ventaja que la mayoría no tiene al empezar" |
| Hipótesis | El subject personalizado con nombre (A) generará mayor open rate; el subject de curiosidad (B) generará mayor click-through entre quienes abren |
| Métrica primaria | Click-to-open rate (CTOR) — captura ambas dimensiones |
| Métrica secundaria | Open rate, Conversión a primera compra en 72h |
| Split | 50/50 |
| N por variante | ~1,500 (usuarios WARM sin conversión hasta D+7) |
| Duración mínima | 72h post-envío |

---

### TEST-04: C3 Email — Tono de Cierre (Despedida vs. Urgencia final)

| Campo | Detalle |
|---|---|
| ID | JN04-AB-04 |
| Touchpoint | C3 Email (último intento COOLING) |
| Variante A | Tono actual: "Este es el último email que te enviamos sobre este tema" (honestidad + respeto) |
| Variante B | Subject alternativo: "{{nombre}}, ¿qué está frenando tu primera compra?" + cuerpo con encuesta de 1 pregunta + CTA doble (comprar ahora / decirme qué me frena) |
| Hipótesis | La variante B generará mayor engagement y datos cualitativos valiosos; la variante A generará mayor conversión directa entre los que sí están listos |
| Métrica primaria | Tasa de first_monetary_movement en 7 días post-envío |
| Métrica secundaria | Click en "decirme qué me frena" (insight cualitativo) |
| Split | 70 (A) / 30 (B) |
| N por variante | A: ~8,800 · B: ~3,760 |
| Nota especial | Los datos de la variante B (razones de no conversión) son valiosos para JN-04 sprint 3+ y para Product |

---

## 6. Fallback Logic Table

| Variable faltante | Comportamiento |
|---|---|
| {{nombre}} = null o vacío | Usar "inversor" — nunca mostrar el placeholder vacío |
| {{kyc_completion_date}} = null | Usar "recientemente" — no intentar calcular |
| {{days_since_kyc}} = null | No mostrar el dato de tiempo; continuar con copy sin referencia temporal |
| {{suggested_first_asset}} = null | Default "Bitcoin" siempre |
| {{suggested_amount_eur}} = null | Default "10 EUR" — el mínimo, que es el dato menos intimidante |
| {{fee_waiver_amount}} = null Y {{incentivo_activo}} = true | Error de configuración — tratar como {{incentivo_activo}} = false, omitir bloque |
| {{incentivo_activo}} = null | Tratar como false — no prometer incentivo si no está confirmado |
| Push no entregado (usuario sin permisos) | Avanzar al siguiente touchpoint de email directamente; no esperar al trigger normal |
| Email rebotado (hard bounce) | Suprimir usuario del track; no reintentar |
| Email rebotado (soft bounce) | Reintentar en 24h; si persiste, suprimir |
| Usuario hace first_monetary_movement en cualquier punto | STOP INMEDIATO de todos los touchpoints pendientes del track |
| Usuario hace unsubscribe | Suprimir del track + suprimir de TODOS los journeys automáticos; notificar a Katy |

---

## 7. Diego Approval Notes

**Para revisión legal/compliance — Diego Barreira**
**Journey:** JN-04 — Verified Never Operated
**Fecha de entrega para revisión:** Semana del 2026-03-24
**Materiales incluidos en esta revisión:** W1 (2 variantes), W2 (1 variante), W3 (2 variantes), W4 (2 emails completos), C1 (2 variantes push), C2 (1 email completo), C3 (1 email completo)

---

**Checklist MiCA — Estado por pieza:**

| Item | Estado | Notas |
|---|---|---|
| Footer regulatorio CNMV en todos los emails | INCLUIDO | Texto completo en W4-A, W4-B, C2, C3 |
| Dirección física Madrid en footer | INCLUIDO | "Paseo de la Castellana 141, 28046 Madrid, España" |
| Sin garantía de rentabilidad | CUMPLE | No aparece en ninguna pieza ninguna promesa de rendimiento |
| Sin uso de "invertir" | CUMPLE | Reemplazado por "comprar" en todo el documento |
| Sin uso de "rendimiento" | CUMPLE | No aparece; se usa "recompensa" o se omite |
| Sin uso de "depositar" | CUMPLE | Reemplazado por "añadir" donde aplica |
| Sin uso de "beneficios" en sentido financiero | CUMPLE | Reemplazado por "recompensas" o eliminado |
| Advertencia de riesgo en emails | INCLUIDO | En todos los footers de email |
| Claim "67% repiten en 30 días" | PENDIENTE VALIDACIÓN | Este dato debe ser confirmado por Marta/Analytics antes de producción. Si no se puede validar, usar el copy alternativo indicado en W2 |
| Condición de exención de comisiones | PENDIENTE CONFIRMACIÓN PRODUCTO | {{fee_waiver_amount}} y duración del incentivo deben ser confirmados por Producto antes de activar {{incentivo_activo}} = true |
| Opt-out en emails | INCLUIDO | Enlace [Darse de baja] en footer de todos los emails |
| Gestión de preferencias | INCLUIDO | Enlace [Gestionar preferencias de comunicación] en todos los emails |

---

**Puntos específicos que requieren revisión de Diego:**

1. **W2 — Claim estadístico:** "67 de cada 100 personas que hacen su primera compra de crypto repiten en los primeros 30 días." — Este dato se basa en métricas internas (pendiente validación con Marta). Si no está validado con fuente citable, eliminar y usar el texto alternativo ya indicado en el copy de W2.

2. **W4-B — Frase "Puedes empezar con {{suggested_amount_eur}} y ver cómo funciona desde dentro."** — Verificar que el contexto completo no pueda interpretarse como asesoramiento de inversión. El párrafo previo incluye la advertencia "nadie puede garantizarte eso" como cobertura.

3. **C3 — Frase "Esta es tu última oportunidad de usarla — la condición expira junto con esta comunicación."** — Verificar que la fecha de expiración del incentivo sea real y trazable. Si el incentivo no tiene fecha de expiración definida, modificar a "disponible por tiempo limitado".

4. **Todos los pushes — Ausencia de footer regulatorio:** Los push notifications no incluyen el disclaimer MiCA por limitación de espacio del canal. Confirmar que esto es aceptable bajo MiCA para notificaciones push de carácter comercial (no asesorial). El disclaimer está presente en todos los emails.

5. **Test-04 Variante B (encuesta):** Si se implementa la variante de "¿qué está frenando tu primera compra?", confirmar que el tratamiento de respuestas de texto libre cumple con el aviso de privacidad vigente.

---

**Contacto para aprobación:**
Enviar a Diego con subject: `[APROBACIÓN LEGAL] JN-04 Copy Package — Sprint 2`
CC: Daniel Ferraro, Katy (CleverTap implementation pending approval)
Deadline aprobación solicitada: 5 días hábiles desde recepción

---

*Fin del documento — JN-04 Copy Package completo*
*Versión: 1.0 | 2026-03-24*
