# JN-03: Deep Dormant Reactivation — Copy & Creatives
**Plan:** 02-04 | **Sprint:** 1 | **Priority:** P2 (P0 for AUC recovery — EUR 19.5M pool)
**Segment:** 46,000 users with balance, 365d+ no login
**Channel:** Email-only (D1, D2) + In-app post-login (D3)
**Author:** Daniel Ferraro | **Date:** 2026-03-24
**Status:** DRAFT — Pending Diego review

---

## Dynamic Variables Master List

| Variable | Descripción | Fallback |
|----------|-------------|----------|
| `{{nombre}}` | Nombre del usuario | `inversor` |
| `{{primary_asset_held}}` | Activo principal del portfolio (ej: "Bitcoin", "Ethereum") | `tus criptos` |
| `{{asset_price_change_pct_12m}}` | % de cambio del activo principal en los últimos 12 meses | Omitir referencia de precio |
| `{{asset_price_change_pct_since_last_login}}` | % de cambio desde último login | Omitir referencia de precio |
| `{{last_login_date_formatted}}` | Descripción de cuándo fue el último login (ej: "hace más de un año") | `hace tiempo` |
| `{{tier_label}}` | Etiqueta del tier del usuario | `inversor` |
| `{{days_since_login}}` | Número de días sin login | Omitir |
| `{{last_login_month}}` | Mes y año del último login (ej: "febrero de 2025") | `hace más de un año` |

---

## Tier Configuration

| Tier | Rango AUC (EUR) | Label en email | Orden de envío | Notas |
|------|-----------------|---------------|---------------|-------|
| Tier 1 | >= 1,000 | Inversor VIP | Primero (Batch 1 + 2) | Máxima atención. Tono ligeramente más exclusivo. |
| Tier 2 | 200 – 999 | Inversor | Segundo (Batch 2 + 3) | Tono estándar. |
| Tier 3 | 50 – 199 | Inversor | Tercero (Batch 3 + 4) | Tono estándar. Mayor volumen. |
| Tier 4 | < 50 | — | SUPRIMIDO PERMANENTEMENTE | No enviar. Riesgo de deliverability no justificado. |

---

## Batch Send Schedule

| Batch | Fecha objetivo | Tamaño | Tier | Condición para avanzar al siguiente |
|-------|---------------|--------|------|-------------------------------------|
| Batch 1 | Mié 2 Abr | 2,000 | Tier 1 (top AUC, 365–500d dormancy) | Bounce <1.5% / Spam <0.05% / Open >15% |
| Batch 2 | Vie 4 Abr | 5,000 | Tier 1 resto + Tier 2 top AUC | Métricas acumuladas: bounce <2%, sin throttling ISP |
| Batch 3 | Semana 3 | 12,000 | Tier 2 resto + Tier 3 top AUC | Mismos thresholds + sin entradas en blocklist |
| Batch 4 | Semana 4 | ~Resto (~15k-20k) | Tier 3 resto | Mismos thresholds |
| NUNCA | — | — | Tier 4 (AUC < 50 EUR) | Suprimidos permanentemente |

> **Nota crítica:** Lista de 46k debe validarse con ZeroBounce antes del Batch 1. Esperar eliminación del 15–25% (estimación: ~34k–39k enviables).

---

## D1 — Email: "Portfolio Pulse" (Day 0 — envío inicial)

> **Objetivo:** Despertar curiosidad. Que abran y hagan click en "Ver mi cuenta". Nada más.
> **REGLA ABSOLUTA:** Cero EUR absolutos. Solo % de cambio con período explícito.

---

### D1 — Tier 1 (VIP — AUC >= EUR 1,000)

**Subject Line A:**
`{{primary_asset_held}} ha cambiado un {{asset_price_change_pct_12m}}% en el último año. ¿Has visto tu posición?`

*(Fallback si sin datos de precio:)*
`Han pasado más de 12 meses. Tu portfolio de cripto sigue activo.`

**Subject Line B:**
`Tu cuenta Bit2Me lleva {{last_login_date_formatted}} esperándote.`

*(Fallback:)*
`Tu cuenta Bit2Me lleva más de un año esperándote.`

**Preheader:**
`El mercado no se detuvo mientras no estabas. Tu posición tampoco.`
*(max 90 caracteres — 63 chars)*

---

**Cuerpo completo (Tier 1 — VIP):**

```
Asunto: {{primary_asset_held}} ha cambiado un {{asset_price_change_pct_12m}}% en el último año. ¿Has visto tu posición?
De: Bit2Me <cuenta@correo.bit2me.com>
Preheader: El mercado no se detuvo mientras no estabas. Tu posición tampoco.

───────────────────────────────────────
[IMAGEN CABECERA: 600x300px — ver Creative Brief D1 abajo]
───────────────────────────────────────

Hola {{nombre}},

{{last_login_date_formatted}} que no entras a tu cuenta.

No te escribimos para presionarte. Te escribimos porque el mercado
ha seguido moviéndose, y tu portfolio también.

En los últimos 12 meses, {{primary_asset_held}} acumula un
{{asset_price_change_pct_12m}}% de variación. Desde la última vez
que visitaste tu cuenta, tu posición ha cambiado un
{{asset_price_change_pct_since_last_login}}%.

Tu cuenta está activa. Tus activos siguen donde los dejaste.

¿Quieres ver cómo está tu portfolio hoy?

[BOTÓN CTA — 44x44px mínimo]
  → VER MI CUENTA

Un saludo,
El equipo de Bit2Me

───────────────────────────────────────
¿No quieres recibir más emails? Puedes darte de baja aquí.
Bit2Me · Calle Príncipe de Vergara 112, Madrid 28002 · España

[DISCLAIMER MiCA — font >=12px, ancho completo]
Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo
que puedas permitirte perder.
───────────────────────────────────────
```

**Versión fallback completa (sin datos de precio disponibles):**

```
Hola {{nombre}},

Hace más de un año que no entras a tu cuenta de Bit2Me.

En ese tiempo, el mercado de criptoactivos ha vivido semanas de todo tipo:
nuevos máximos históricos en varios activos, nuevas regulaciones en Europa,
y proyectos que cambiaron de forma.

Tu cuenta sigue activa. Tus activos siguen donde los dejaste.

Si tienes curiosidad por ver cómo está tu posición hoy, solo tienes que
entrar. No hace falta hacer nada más.

[BOTÓN CTA]
  → VER MI CUENTA

Un saludo,
El equipo de Bit2Me
```

---

### D1 — Tier 2 / Tier 3 (Standard — AUC EUR 50–999)

**Subject Line A:**
`{{primary_asset_held}} no ha estado quieto. ¿Sabes cómo está tu posición?`

*(Fallback si sin datos de precio:)*
`Tu cuenta de cripto lleva {{last_login_date_formatted}} sin actividad.`

**Subject Line B:**
`Hace {{last_login_date_formatted}} que no entras. Esto es lo que pasó en cripto.`

*(Fallback:)*
`Hace más de un año que no entras a Bit2Me. Te contamos qué pasó.`

**Preheader:**
`Tu cuenta está activa y tus activos siguen ahí. Echa un vistazo cuando quieras.`
*(80 chars)*

---

**Cuerpo completo (Tier 2/3 — Standard):**

```
Asunto: {{primary_asset_held}} no ha estado quieto. ¿Sabes cómo está tu posición?
De: Bit2Me <cuenta@correo.bit2me.com>
Preheader: Tu cuenta está activa y tus activos siguen ahí. Echa un vistazo cuando quieras.

───────────────────────────────────────
[IMAGEN CABECERA: 600x300px — ver Creative Brief D1 abajo]
───────────────────────────────────────

Hola {{nombre}},

Han pasado {{last_login_date_formatted}} desde tu última visita a Bit2Me.

El mundo cripto no esperó. En el último año, {{primary_asset_held}} acumuló
un {{asset_price_change_pct_12m}}% de variación. Ethereum, Bitcoin, y la
mayoría de activos tuvieron momentos importantes: máximos históricos, nuevas
regulaciones europeas bajo MiCA, y un mercado que sigue madurando.

Tu cuenta sigue activa. Tus activos están donde los dejaste.

Si tienes un momento, échale un vistazo. No hace falta hacer nada más.

[BOTÓN CTA — 44x44px mínimo]
  → VER MI CUENTA

Un saludo,
El equipo de Bit2Me

───────────────────────────────────────
¿No quieres recibir más emails? Puedes darte de baja aquí.
Bit2Me · Calle Príncipe de Vergara 112, Madrid 28002 · España

[DISCLAIMER MiCA — font >=12px, ancho completo]
Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo
que puedas permitirte perder.
───────────────────────────────────────
```

---

**MiCA check D1:** ✅ No EUR absolutos. Solo % de cambio con período explícito (12 meses / "desde último login"). Sin lenguaje de "rendimiento" o "beneficios". Sin comparativa con competidores. Framing: curiosidad y movimiento, no urgencia ni pérdida de fondos.

---

### Creative Brief — D1 Email Header Image

- **Dimensiones:** 600x300px (email header, 2x para retina: 1200x600px)
- **Formato:** JPG o PNG sin transparencia (compatibilidad email)
- **Visual:** Vista aérea nocturna de una ciudad con luz cálida (Madrid/Barcelona reconocible opcional). En primer plano, un gráfico de línea de precio elegante y minimalista que sube y baja — no claramente alcista ni bajista, representando "movimiento" neutro. El gráfico es semitransparente, superpuesto sobre la ciudad.
- **Mood:** Sereno, sofisticado, intemporal. Como mirar por la ventana después de un viaje largo. No alarmante. No eufórico.
- **Paleta:** Azul marino profundo (#0B1929) con destellos de luz naranja/ámbar de la ciudad. El gráfico en blanco o azul claro.
- **Text overlay:** Solo logo Bit2Me (esquina superior izquierda, versión blanca). Ningún texto de campaña en la imagen (el copy va en el body).
- **Dark mode:** Imagen funciona tanto en fondo blanco como oscuro.
- **AI image prompt (English):**
  `Aerial nighttime view of a European city with warm amber city lights, calm and cinematic. Overlaid with a minimal white line chart representing price movement — neither clearly up nor down. Deep navy blue atmosphere. Sophisticated, serene, and timeless. No text. Photorealistic. Email header format, wide aspect ratio 2:1.`

---

## D2 — Email: "¿Qué pasó mientras no estabas?" (D+7 — Solo No-Abrieron D1)

> **Objetivo:** Segunda oportunidad con ángulo diferente. D1 era sobre su activo y posición. D2 es sobre qué ha pasado en el mundo cripto — más editorial, más narrativo. La misma soft CTA.
> **REGLA:** Subject line completamente distinto de D1. Body puede compartir estructura pero opener diferente.
> **ENVÍO:** Solo a usuarios que NO abrieron D1 (filtro en CleverTap: "not opened D1").

---

### D2 — Tier 1 (VIP — AUC >= EUR 1,000)

**Subject Line A:**
`Mientras no estabas: {{primary_asset_held}} acumula un {{asset_price_change_pct_12m}}% en 12 meses.`

*(Fallback:)*
`Mientras no estabas: lo que pasó en cripto este año.`

**Subject Line B:**
`Un año de cripto resumido. Tu cuenta sigue activa.`

**Preheader:**
`Nuevas reglas en Europa, nuevos máximos, nuevas oportunidades. Y tu posición, intacta.`
*(86 chars)*

---

**Cuerpo completo (Tier 1 — VIP):**

```
Asunto: Un año de cripto resumido. Tu cuenta sigue activa.
De: Bit2Me <cuenta@correo.bit2me.com>
Preheader: Nuevas reglas en Europa, nuevos máximos, nuevas oportunidades. Y tu posición, intacta.

───────────────────────────────────────
[IMAGEN CABECERA: 600x300px — ver Creative Brief D2 abajo]
───────────────────────────────────────

Hola {{nombre}},

No hace falta que hayas seguido el mercado para entender lo que pasó.
Te lo resumimos.

En el último año:

→ Bitcoin alcanzó nuevos máximos históricos y volvió a ser portada
  de prensa internacional.

→ Ethereum completó actualizaciones clave que cambiaron su estructura
  de costes y consumo energético.

→ Europa adoptó MiCA, el reglamento más completo del mundo para
  criptoactivos, que convierte a España en uno de los mercados más
  regulados y seguros del sector.

→ {{primary_asset_held}}, el activo que tienes en tu portfolio,
  acumuló un {{asset_price_change_pct_12m}}% de variación en 12 meses.

Tu cuenta está activa. Tu posición sigue ahí.

¿Quieres ver dónde estás hoy?

[BOTÓN CTA]
  → VER MI CUENTA

Un saludo,
El equipo de Bit2Me

───────────────────────────────────────
¿No quieres recibir más emails? Puedes darte de baja aquí.
Bit2Me · Calle Príncipe de Vergara 112, Madrid 28002 · España

[DISCLAIMER MiCA — font >=12px, ancho completo]
Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo
que puedas permitirte perder.
───────────────────────────────────────
```

---

### D2 — Tier 2 / Tier 3 (Standard — AUC EUR 50–999)

**Subject Line A:**
`Esto pasó en cripto mientras no estabas. Tu cuenta: activa.`

**Subject Line B:**
`Resumen de un año en cripto. Tu posición sigue ahí.`

**Preheader:**
`MiCA, nuevos máximos, y tu {{primary_asset_held}} con un año de historia.`
*(72 chars — fallback: "Un año de cripto y tu cuenta esperándote.")*

---

**Cuerpo completo (Tier 2/3 — Standard):**

```
Asunto: Esto pasó en cripto mientras no estabas. Tu cuenta: activa.
De: Bit2Me <cuenta@correo.bit2me.com>
Preheader: MiCA, nuevos máximos, y tu {{primary_asset_held}} con un año de historia.

───────────────────────────────────────
[IMAGEN CABECERA: 600x300px — ver Creative Brief D2 abajo]
───────────────────────────────────────

Hola {{nombre}},

Si llevas un tiempo sin entrar a tu cuenta de Bit2Me, seguramente
te hayas perdido bastante.

Aquí va un resumen rápido de lo que pasó:

→ El mercado vivió uno de sus años más activos, con varios activos
  principales alcanzando precios históricos.

→ La Unión Europea aprobó MiCA, el marco regulatorio de criptoactivos
  más robusto del mundo. Bit2Me es una entidad registrada en la CNMV
  como proveedor de servicios de criptoactivos.

→ {{primary_asset_held}}, el activo principal de tu portfolio, varió
  un {{asset_price_change_pct_12m}}% en los últimos 12 meses.

Tu cuenta sigue activa. Tus activos están donde los dejaste.

Si tienes un momento, entra a ver tu posición. Es todo lo que te pedimos.

[BOTÓN CTA]
  → VER MI CUENTA

Un saludo,
El equipo de Bit2Me

───────────────────────────────────────
¿No quieres recibir más emails? Puedes darte de baja aquí.
Bit2Me · Calle Príncipe de Vergara 112, Madrid 28002 · España

[DISCLAIMER MiCA — font >=12px, ancho completo]
Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como
proveedor de servicios de criptoactivos. Las criptomonedas son activos
de alto riesgo. El valor de tu portfolio puede subir o bajar
significativamente. Rentabilidades pasadas no garantizan resultados
futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo
que puedas permitirte perder.
───────────────────────────────────────
```

---

**MiCA check D2:** ✅ No EUR absolutos. % de cambio con período explícito (12 meses). El resumen editorial de mercado (MiCA, máximos históricos) es informativo y no induce a compra ni venta. Sin lenguaje de urgencia sobre fondos. Sin comparativa con competidores. Cumple Art. 66 MiCA (no se fomenta compra tras posible bajada no explicitada).

---

### Creative Brief — D2 Email Header Image

- **Dimensiones:** 600x300px (2x para retina: 1200x600px)
- **Formato:** JPG o PNG sin transparencia
- **Visual:** Línea del tiempo horizontal flotante, como una cinta tipográfica minimalista con pequeños iconos o hitos del año (sin texto específico de precio ni de activo). Fondo oscuro profundo con partículas de luz (como una lluvia de píxeles muy sutil). El estilo es "cápsula del tiempo abierta".
- **Mood:** Narrativo, editorial, templado. Como la portada de una revista de análisis. No urgente, no alarmante.
- **Paleta:** Fondo negro/azul muy oscuro (#060E1A). Línea del tiempo en blanco o dorado sutil. Toques de naranja Bit2Me en los hitos si aplica al brand.
- **Text overlay:** Solo logo Bit2Me blanco en esquina superior izquierda. Sin copy en imagen.
- **Dark mode:** Compatible con clientes email en modo oscuro.
- **AI image prompt (English):**
  `Minimalist dark background with a subtle horizontal timeline floating in space, representing the passage of time over one year. Small glowing dots mark moments on the timeline. Deep space blue-black (#060E1A) background with very subtle particle effect. Gold or white accents. Editorial, calm, sophisticated. No text, no numbers, no brand logos. Wide 2:1 aspect ratio. Email header format.`

---

## D3 — In-App Message: "Bienvenido de vuelta" (Post-Login Trigger)

> **Trigger:** Usuario hace login después de haber recibido D1 o D2 (evento `user_login` en CleverTap, dentro del journey).
> **Este es el momento de conversión.** Ahora SÍ podemos mostrar el valor en EUR porque el usuario eligió entrar.
> **Pantalla:** Portfolio screen (pantalla principal post-login).
> **Tipo:** Full-width card (375x220px mínimo, adaptable).

---

### D3 — Variante A: Asset con ganancia (price_change > 0)

```
──────────────────────────────────────────
[IMAGEN/BACKGROUND: ver Creative Brief D3 - Variante A]

  Bienvenido de vuelta, {{nombre}}.

  Tu {{primary_asset_held}} ha subido un
  {{asset_price_change_pct_since_last_login}}%
  desde la última vez que entraste.

  Tu portfolio hoy vale:
  ┌─────────────────────┐
  │  EUR {{portfolio_value_eur}}  │
  └─────────────────────┘

  ¿Qué quieres hacer con él?

  [BOTÓN PRIMARIO]   → Operar ahora
  [BOTÓN SECUNDARIO] → Ver portfolio

──────────────────────────────────────────
```

**Versión alternativa CTA si Earn disponible (preferir sobre "Operar ahora"):**
```
  [BOTÓN PRIMARIO]   → Activar Earn  (+{{earn_apy_rate}}% APY*)
  [BOTÓN SECUNDARIO] → Ver portfolio

  *APY variable. Implica riesgo. Lee condiciones en bit2me.com/earn
```

---

### D3 — Variante B: Asset con pérdida (price_change < 0)

> **CRÍTICO:** Nunca liderar con la pérdida. Framing: tu activo sigue aquí, intacto, esperando.
> **Art. 66 MiCA:** No sugerir trading inmediato tras caída de precio. CTA "Operar ahora" PROHIBIDO en esta variante.

```
──────────────────────────────────────────
[IMAGEN/BACKGROUND: ver Creative Brief D3 - Variante B]

  Bienvenido de vuelta, {{nombre}}.

  Tu {{primary_asset_held}} sigue aquí,
  esperándote.

  Tu portfolio hoy:
  ┌─────────────────────┐
  │  EUR {{portfolio_value_eur}}  │
  └─────────────────────┘

  Todo sigue en orden.

  [BOTÓN PRIMARIO]   → Ver portfolio
  [BOTÓN SECUNDARIO] → Explorar Bit2Me

──────────────────────────────────────────
```

---

### D3 — Variante C: Sin datos de precio (fallback)

```
──────────────────────────────────────────
[IMAGEN/BACKGROUND: ver Creative Brief D3 - Variante B/C]

  Bienvenido de vuelta, {{nombre}}.

  Tu portfolio te ha estado esperando.

  Tu saldo actual:
  ┌─────────────────────┐
  │  EUR {{portfolio_value_eur}}  │
  └─────────────────────┘

  ¿Qué quieres hacer hoy?

  [BOTÓN PRIMARIO]   → Ver portfolio
  [BOTÓN SECUNDARIO] → Descubrir Earn

──────────────────────────────────────────
```

---

### D3 — Lógica de selección de variante (implementar en CleverTap)

| Condición | Variante | CTA Primario | CTA Secundario |
|-----------|----------|-------------|----------------|
| `asset_price_change_pct_since_last_login` > 0 + Earn disponible | A-Earn | "Activar Earn (+X% APY*)" | "Ver portfolio" |
| `asset_price_change_pct_since_last_login` > 0 + Earn no disponible | A-Trade | "Operar ahora" | "Ver portfolio" |
| `asset_price_change_pct_since_last_login` < 0 | B | "Ver portfolio" | "Explorar Bit2Me" |
| Variable no disponible | C | "Ver portfolio" | "Descubrir Earn" |

> **Nota operativa Variante B:** En ningún caso mostrar el porcentaje de caída en el card. Mostrar solo el EUR actual sin contexto comparativo. Cumple Art. 66 MiCA.

---

### D3 — Earn Disclaimer (solo si se menciona Earn o APY en cualquier variante)

```
*Los productos de rendimiento implican riesgo. El APY mostrado es variable
y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la
devolución del capital. Lee las condiciones completas en bit2me.com/earn
antes de participar.
```

---

**MiCA check D3:** ✅ EUR absolutos solo in-app, tras decisión voluntaria de login. % de cambio con período implícito (desde último login — período conocido por el usuario). Variante B cumple Art. 66 MiCA: no induce a operar tras caída de precio, CTA neutral. Earn disclaimer incluido cuando aplica. Sin comparativa con competidores.

---

### Creative Brief — D3 In-App Card

- **Dimensiones:** 375x220px mínimo (full-width en mobile, 2x para retina: 750x440px)
- **Formato:** PNG con transparencia o diseño nativo en CleverTap
- **Visual Variante A (ganancia):** Fondo con degradado de azul marino a verde esmeralda muy sutil en la parte superior. Un círculo luminoso central (como el sol apareciendo en el horizonte) con un icono simbólico del activo (logo BTC/ETH, etc.) en blanco. Sensación de amanecer, descubrimiento, "bienvenido de vuelta a algo positivo".
- **Visual Variante B/C (pérdida o fallback):** Fondo azul marino plano y sereno. El mismo círculo luminoso pero en tono blanco neutro. Sin verde. Sin rojo. La sensación es de calma y estabilidad: "todo sigue en orden".
- **Mood:** Bienvenida cálida. Como abrir la puerta de tu casa después de un viaje.
- **Text overlay:** El copy del card se renderiza dinámicamente sobre la imagen de fondo. El fondo debe ser suficientemente oscuro para que texto blanco sea legible (contraste mínimo AA).
- **AI image prompt — Variante A (English):**
  `Abstract warm background for a mobile app card. Deep navy blue (#0B1929) transitioning to a subtle emerald green glow at the top center. A glowing white circle in the upper center, like sunlight breaking through clouds. Clean, modern, welcoming. No text. No charts. No numbers. Mobile card format, wide rectangle 16:9.`
- **AI image prompt — Variante B/C (English):**
  `Abstract calm background for a mobile app card. Deep navy blue (#0B1929), flat and serene. A soft white luminous circle centered at top. No green. No red. Conveys stability, trust, and continuity. Clean, modern. No text. No charts. Mobile card format, wide rectangle 16:9.`

---

## A/B Test Register

| Test ID | Variante A | Variante B | Hipótesis | Métrica primaria | Decisión en |
|---------|-----------|-----------|-----------|-----------------|-------------|
| AB-JN03-01 | D1 Subject A (precio/% explícito) | D1 Subject B (tiempo/cuenta dormante) | El ángulo de precio activa más curiosidad que el ángulo temporal | Open rate D1 | Batch 1 (N=2,000 — 1k por rama) |
| AB-JN03-02 | D2 Subject A ("mientras no estabas" + %) | D2 Subject B ("resumen del año") | El framing narrativo supera al framing de dato de precio en no-abrieron D1 | Open rate D2 | Batch 2 (N=5,000) |
| AB-JN03-03 | D3 CTA primario "Operar ahora" | D3 CTA primario "Activar Earn" | Earn tiene mayor intención de retención que trading en dormantes reactivados | Click D3 + Earn activation D+7 | Post-login (N=min 200 logins) |
| AB-JN03-04 | D1 enviado a las 10:00h | D1 enviado a las 19:00h | Dormantes responden mejor en horario de tarde (consulta casual vs trabajo) | Open rate D1 | Batch 2 (N=5,000) |
| AB-JN03-IMPL-01 | Tier 1 (AUC >= 1k) | Tier 2 (AUC 200–999) | Usuarios de mayor AUC tienen mayor tasa de reactivación | Reactivation rate D+30 | Post-Batch 2 análisis |
| AB-JN03-IMPL-02 | 365–500d dormancy | 500d+ dormancy | Los menos dormidos responden mejor que los muy dormidos | Reactivation rate D+30 | Post-Batch 3 análisis |

> **Nota:** Tests AB-JN03-IMPL-01 y AB-JN03-IMPL-02 son tests implícitos por estructura de batches — no requieren configuración adicional en CleverTap, solo análisis por segmento en Marta/BigQuery post-campaña.

---

## Anti-Withdrawal Monitoring Thresholds

| Métrica | Umbral normal | Umbral de alarma | Umbral de STOP | Acción | Owner |
|---------|--------------|-----------------|----------------|--------|-------|
| Withdrawal rate journey vs holdout | Igual o menos | > holdout +5% | > holdout +10% | +5%: Alarma a Daniel. +10%: PAUSAR TODO | Marta (diario) |
| AUC retirado del cohort JN-03 (14d acumulado) | < EUR 100k | EUR 100k–500k (monitorización intensiva) | > EUR 500k | STOP ALL JN-03 | Marta → Daniel (P0) |
| Hard bounce por batch | < 1.5% | 1.5–3% (revisar lista) | > 3% | STOP ALL | Katy |
| Spam complaint por batch | < 0.05% | 0.05–0.15% (revisar copy) | > 0.15% | STOP ALL | Katy |
| Gmail Postmaster reputation | High/Medium | Low (revisar antes de siguiente batch) | Bad | STOP ALL | Álvaro |
| Open rate D1 Batch 1 | > 15% | 10–15% (revisar copy/hora de envío) | < 10% (Batch 2 en pausa hasta revisión) | Revisar antes de avanzar | Daniel |

> **Protocolo de alarma:** Cualquier métrica en umbral STOP — Katy/Marta detiene envíos en CleverTap inmediatamente y notifica a Daniel en los 15 minutos siguientes. No esperar al siguiente standup.

---

## Fallback Logic

| Variable | Condición de fallback | Texto de reemplazo | Impacto en copy |
|----------|----------------------|-------------------|-----------------|
| `{{nombre}}` | Campo vacío o nulo | `inversor` | Saludo: "Hola inversor," |
| `{{primary_asset_held}}` | No disponible o portfolio diversificado sin activo principal claro | `tus criptos` | "tus criptos no han estado quietas." / "tus activos llevan 12 meses de historia." |
| `{{asset_price_change_pct_12m}}` | No disponible (fallo API o activo sin 12m de historial) | Omitir párrafo completo de precio | Usar versión fallback de cuerpo (editorial de mercado sin % específico) |
| `{{asset_price_change_pct_since_last_login}}` | No disponible | Omitir frase de % desde login | En D3 Variante A: omitir línea "ha subido X%", usar Variante C |
| `{{last_login_date_formatted}}` | No disponible | `hace más de un año` | Sustitución automática |
| `{{last_login_month}}` | No disponible | `hace más de un año` | Sustitución automática |
| `{{tier_label}}` | No disponible | `inversor` | Solo afecta saludo opcional en versiones futuras |
| `{{portfolio_value_eur}}` | Solo en D3 — no disponible | BLOQUEAR envío de D3 hasta disponible (P0 dependency — Álvaro deadline Mié 26) | D3 no puede lanzarse sin este dato |
| `{{earn_apy_rate}}` | No disponible | Omitir mención a Earn y APY | No mostrar CTA "Activar Earn" — usar CTA "Ver portfolio" en su lugar |

---

## Copy Rationale

### Psicología de reconexión: curiosidad por encima de urgencia

Los 46,000 usuarios de este segmento no están inactivos por falta de interés en cripto — están inactivos porque el costo de re-enganche (recordar contraseña, navegar a la app, "¿qué hago ahora?") superó su motivación en algún momento. No son usuarios que abandonaron cripto por desencanto; son usuarios que simplemente dejaron de tener una razón cotidiana para abrir la app.

**Principios aplicados:**

**1. Efecto dotación (Endowment Effect)**
Los activos ya son suyos. "Tu Bitcoin", "tu {{primary_asset_held}}", "tu posición". Nunca "hay criptos esperando" como si fueran ajenas. La propiedad psicológica activa la motivación de protección y curiosidad sobre lo propio, sin generar ansiedad por perder algo.

**2. Curiosity gap**
D1 abre un gap de información: "el mercado se movió mientras no estabas". El usuario no sabe cuánto ni en qué dirección. Solo puede cerrarlo haciendo click. No decimos si ganó o perdió — eso lo descubre al entrar. Este gap es más potente que cualquier número absoluto.

**3. Identidad de holder**
No llamamos al usuario "cliente inactivo". Le devolvemos su identidad como participante en cripto — "tu posición", "tu {{primary_asset_held}}". Esto activa motivación intrínseca desde una posición de protagonismo, no de culpa por haber estado ausente.

**4. Reciprocidad implícita**
Bit2Me ha custodiado sus activos durante 365+ días sin coste adicional para el usuario. D1 y D2 no piden nada a cambio de esa custodia — simplemente informan. Este goodwill implícito reduce la resistencia al click y el tono defensivo.

**5. Mere exposure effect**
El objetivo de D1 no es la conversión — es que abran el email. El de D2 no es que operen — es que hagan click. El de D3 ya es conversión porque el usuario cruzó el umbral de manera voluntaria (login). Cada touchpoint tiene un objetivo de un solo paso, y ese único paso es siempre el más pequeño posible.

**6. Framing de movimiento, no de valor absoluto**
Decir "tu portfolio varió un X% en 12 meses" activa la curiosidad sin revelar el resultado emocional. Decir "tienes EUR 424" activa inmediatamente el cálculo de si merece la pena mantener, transferir o retirar. El primero abre la conversación; el segundo la cierra prematuramente con una posible decisión de salida.

### Por qué D3 es el momento de conversión, no D1 ni D2

Un usuario dormido 365+ días necesita reconstruir su relación con la plataforma antes de tomar cualquier decisión financiera. D1 y D2 son la reconexión emocional — el recordatorio de que tienen algo ahí y de que el mundo siguió. D3 es cuando el usuario, habiendo elegido voluntariamente volver, está en el estado mental correcto para ver su valor real y evaluar opciones. Mostrar EUR en email sería equivalente a entregar el estado de cuenta bancario a alguien que acaba de despertar de un año de viaje — la primera reacción es procesar, no actuar positivamente sobre la información.

---

## Diego Approval Notes

### Flags de cumplimiento para revisión legal

| Elemento | Regla aplicada | Estado | Notas para Diego |
|----------|---------------|--------|-----------------|
| EUR absolutos en D1/D2 | PROHIBIDO — anti-withdrawal protocol + MiCA anti-manipulación | ✅ No aparecen en ninguna variante | Verificar que ningún subject ni preheader contenga EUR. Confirmar que versión HTML no inyecta EUR por error en variables. |
| % de cambio en D1/D2 | Permitido con período explícito (>=12 meses) | ✅ Período explícito en todas las menciones | "en los últimos 12 meses" / "desde {{last_login_date_formatted}}" — ambas frases con período declarado. |
| Palabras prohibidas MiCA | "invertir", "rendimiento", "beneficios", "ingresos pasivos", "depositar", "intereses" | ✅ Ninguna aparece en copy | Sustituidas por: "operar", "APY", "recompensas", "añadir". Revisar versiones HTML finales. |
| Disclaimer MiCA footer | Obligatorio en TODOS los emails, font >=12px, ancho completo, no suprimible visualmente | ✅ Incluido en D1 y D2 | Verificar que la plantilla HTML respete font >=12px y que no se comprima en móvil. |
| Earn disclaimer | Obligatorio cuando se menciona Earn o APY en cualquier mensaje | ✅ Incluido en D3 Variante A cuando aplica | Si S3 (Earn intro) se activa, verificar que incluye disclaimer completo. |
| Art. 66 MiCA (no inducir compra tras caída) | D3 Variante B no tiene CTA "Operar ahora" ni muestra % de caída | ✅ Variante B usa CTA neutro "Ver portfolio" | Confirmar que lógica de selección de variante está implementada en CT antes de launch. |
| Framing de urgencia sobre fondos | PROHIBIDO — kill switch copy | ✅ Ningún email usa "tu dinero está en riesgo" o similar | Revisar especialmente preheaders y subject lines de todas las variantes. |
| Comparativa con competidores | PROHIBIDO — kill switch copy | ✅ Ninguna referencia a competidores | — |
| Unsubscribe link | Obligatorio (RGPD + LSSICE) | ✅ Incluido en footer de ambos emails | Confirmar enlace funcional en QA antes de Batch 1. |
| Remitente | cuenta@correo.bit2me.com | Pendiente configuración técnica (Álvaro) | Confirmar que el nombre del remitente visible sea "Bit2Me" y no la dirección técnica. |
| Holdout / split comunicacional | 10% usuarios sin comunicación para validez estadística | Informativo — sin implicación legal | — |

### Piezas a aprobar (4 piezas totales — deadline Jue 27 Mar)

1. **D1 — "Portfolio Pulse"** — 2 variantes de subject x 2 tiers (4 subjects) + 2 cuerpos + fallbacks
2. **D2 — "¿Qué pasó mientras no estabas?"** — 2 variantes de subject x 2 tiers (4 subjects) + 2 cuerpos
3. **D3 — In-app "Bienvenido de vuelta"** — 3 variantes (ganancia / pérdida / fallback)
4. **Disclaimer MiCA footer** — confirmar versión vigente con Legal (texto propuesto incluido en este documento)

---

## ZeroBounce Pre-Send Checklist

### Pasos de validación antes de Batch 1 (deadline: Vie 28 Mar)

| Paso | Acción | Owner | Criterio de paso |
|------|--------|-------|-----------------|
| 1 | Exportar lista de 46,000 emails desde BigQuery con filtros: `account_status='enabled' AND auc_eur>0 AND last_login_date < CURRENT_DATE()-365 AND fraud_flag=false` | Marta | Lista en CSV, sin duplicados, con columnas: email, auc_eur, days_since_login, primary_asset |
| 2 | Eliminar Tier 4 (AUC < 50 EUR) de la lista ANTES de enviar al validador | Marta | Lista resultante: solo Tier 1-3 (~34k–42k usuarios) |
| 3 | Subir lista completa a ZeroBounce (confirmar créditos disponibles con Álvaro) | Álvaro | Confirmación de upload y estimación de tiempo de procesado |
| 4 | Esperar resultado completo del validador (normalmente 24–48h) | — | No proceder hasta tener resultado al 100% |
| 5 | Eliminar de la lista todos los emails clasificados como: `invalid`, `catch-all`, `spam-trap`, `abuse`, `do-not-mail` | Marta | Solo `valid` y `unknown` con ZeroBounce Score >=0.7 pasan |
| 6 | Calcular % de remoción. Si > 30%, pausar y analizar con Álvaro antes de continuar (puede indicar problema en datos fuente) | Daniel | < 30% removidos. Si >30%: revisión de datos fuente antes de avanzar. |
| 7 | Segmentar lista validada por Tier (1–3) y por AUC descendente dentro de cada tier | Marta | Archivo final con columnas: email, tier, auc_eur, days_dormant — ordenado por Tier y AUC desc |
| 8 | Aislar Batch 1: top 2,000 usuarios Tier 1, con 365–500 días de dormancy, ordenados por AUC descendente | Marta | Segmento Batch 1 creado en CT o CSV separado para importación manual |
| 9 | Verificación manual de muestra aleatoria (10 usuarios): confirmar que datos de CleverTap coinciden con BigQuery para `primary_asset_held` y `days_since_login` | Marta | 10/10 coherentes. Si hay discrepancias, escalar a Álvaro antes de launch. |
| 10 | Confirmar que subdomain cuenta@correo.bit2me.com tiene: SPF configurado / DKIM configurado / DMARC configurado / 2 semanas de warming con transaccionales completadas | Álvaro | Los 4 checks en verde. Herramienta recomendada: MXToolbox para validación. |
| 11 | Gmail Postmaster Tools: confirmar domain reputation >= "Medium" para el subdomain antes del primer envío de marketing | Álvaro | Reputation: High o Medium. Si "Low": esperar 72h con más transaccionales antes de avanzar. |
| 12 | Sign-off final GO/NO-GO Batch 1 | Daniel | Confirmación escrita en Lark thread JN-03 |

---

*Documento generado: 2026-03-24 | Versión: 1.0 DRAFT*
*Próximo paso: Revisión Diego (copy approval) — deadline Jue 27 Mar*
*GO/NO-GO Batch 1 — Mié 2 Abr*
*Owner: Daniel Ferraro | Execution: Katy (CT) | Data: Marta + Álvaro | Legal gate: Diego*
