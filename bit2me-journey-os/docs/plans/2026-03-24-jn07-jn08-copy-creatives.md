# JN-07 & JN-08 — Copy Packages Completos
**Bit2Me Lifecycle OS | Senior CRM Copywriter**
**Fecha:** 24 de marzo de 2026
**Versión:** 1.0 — Production Ready
**Aprobación requerida:** Diego (legal) antes de envío

---

# PARTE 1 — JN-07: B2M HOLDER CROSS-SELL

**Objetivo:** Cross-sell BTC/ETH a 21.500 usuarios que SOLO tienen B2M. Sin incentivo monetario — solo XP boost en Space Center.
**Segmento activo (login 30d):** 18.610 usuarios (50%)
**Stop condition:** segunda divisa distinta comprada → parar journey.

---

## 1. TABLA DE VARIABLES — JN-07

| Variable | Tipo | Ejemplo | Fallback |
|---|---|---|---|
| {{nombre}} | String | "Carlos" | "inversor" |
| {{b2m_balance}} | String | "1.250 B2M" | "tus B2M" |
| {{space_center_tier}} | Integer (1-7) | "3" | "1" |
| {{xp_boost_amount}} | String | "+500 XP" | "XP extra" |
| {{suggested_asset}} | String | "Bitcoin" o "Ethereum" | "Bitcoin" |
| {{suggested_ticker}} | String | "BTC" o "ETH" | "BTC" |

**Lógica sugerida {{suggested_asset}}:**
- Tier 1-3 → Bitcoin (BTC) — activo de referencia, entrada natural para nuevos diversificadores
- Tier 4-6 → Ethereum (ETH) — perfil más sofisticado, mayor alineación DeFi
- Tier 7 → Bitcoin (BTC) — los más veteranos vuelven al origen, store of value narrative

---

## 2. X1 — IN-APP CARD (Triggered: Space Center screen o Portfolio screen)

*Formato: Card expandible. Disparador: usuario abre Space Center o su Portfolio.*
*Dos variantes según comportamiento de usuario.*

---

### X1-A: Variante Usuario Activo (login últimos 7 días)

**Card headline:**
Misión desbloqueada: diversifica tu portfolio

**Card body:**
Tienes {{b2m_balance}} en B2M. Los inversores de Nivel {{space_center_tier}} que añaden un segundo activo ganan {{xp_boost_amount}} — y abren la siguiente misión del Space Center.

{{suggested_asset}} es el paso natural. ¿Lo añadimos a tu portfolio?

**CTA primario:** Comprar {{suggested_ticker}}
**CTA secundario:** Ver detalles de la misión

**Nota de implementación:** Mostrar XP bar animada con incremento visual al pulsar CTA primario. Icono del activo sugerido visible en la card.

---

### X1-B: Variante Usuario Pasivo (sin login últimos 7 días — triggered al volver)

**Card headline:**
Bienvenido de vuelta, {{nombre}}

**Card body:**
Tu B2M sigue aquí — {{b2m_balance}}. Y hay una misión esperándote en el Space Center.

Añade {{suggested_asset}} a tu portfolio y consigue {{xp_boost_amount}} ahora mismo. Tus compañeros de Nivel {{space_center_tier}} ya están diversificando.

**CTA primario:** Ver mi misión
**CTA secundario:** Comprar {{suggested_ticker}}

**Nota de implementación:** Card con badge "Nueva misión disponible" visible desde pantalla de inicio.

---

## 3. X2 — PUSH NOTIFICATION (D+5 si no hay acción en X1 — 20:30 CET)

*Dos variantes A/B. Enviar a usuarios sin acción en X1.*

---

### X2-A: Variante "XP Urgency"

**Título:** {{nombre}}, tu misión sigue pendiente ⚡

**Cuerpo:** Nivel {{space_center_tier}} + {{suggested_ticker}} = {{xp_boost_amount}} en tu marcador. Solo B2M no es diversificar — los pros de Bit2Me lo saben.

**Deep link:** /space-center/missions

---

### X2-B: Variante "Community Social Proof"

**Título:** Los del Nivel {{space_center_tier}} ya avanzaron

**Cuerpo:** Esta semana, inversores como tú añadieron {{suggested_ticker}} y subieron en el Space Center. Tu B2M está solo — ponle compañía.

**Deep link:** /portfolio/add-asset/{{suggested_ticker}}

**Reglas de envío:**
- Hora: 20:30 CET (hora de alta actividad en app)
- No enviar si usuario ya realizó acción en X1
- No enviar si usuario compró segundo activo en las últimas 24h
- Frecuencia máxima: 1 push en esta journey

---

## 4. X3 — EMAIL (D+10 — no respondedores a X1 ni X2)

### Líneas de asunto (A/B)

**Asunto A:** {{nombre}}, tu Space Center lleva 5 días esperando esta misión
**Preheader A:** {{b2m_balance}} en cartera, cero diversificación — y {{xp_boost_amount}} sin reclamar.

**Asunto B:** El 73% de los Nivel {{space_center_tier}} ya tienen más de un activo
**Preheader B:** Tú tienes B2M. Ellos también tienen {{suggested_ticker}}. Hay una razón.

---

### CUERPO COMPLETO — X3 EMAIL

---

Hola, {{nombre}}

Llevas tiempo construyendo tu posición en B2M. Eso te hace parte de la comunidad Bit2Me de verdad — no de los que llegan, compran algo y se van.

Y precisamente por eso, esto te lo decimos directamente:

**Un solo activo no es un portfolio. Es una apuesta.**

Los inversores que más avanzan en el Space Center — los que suben de Nivel {{space_center_tier}} para arriba — tienen algo en común: no se quedaron solo con B2M.

---

**Por qué {{suggested_asset}}**

No te vamos a dar una conferencia de economía. Solo esto:

- B2M es el token del ecosistema Bit2Me. Estás dentro.
- {{suggested_asset}} es el activo de referencia del mercado cripto.
- Tener los dos no es especular más — es especular mejor.

El riesgo concentrado en un solo activo es mayor que el riesgo distribuido en dos activos sin correlación perfecta. Los que llevan años en esto lo saben de memoria.

---

**Tu misión en el Space Center**

Tienes {{b2m_balance}} en tu cartera. Si añades {{suggested_ticker}} — la cantidad que quieras — desbloqueas la misión de diversificación y consigues {{xp_boost_amount}} en tu marcador.

No es una obligación. Es una misión. Y las misiones las decide cada uno.

Nivel actual: {{space_center_tier}}
XP que ganarías ahora: {{xp_boost_amount}}
Activo sugerido: {{suggested_asset}} ({{suggested_ticker}})

[Comprar {{suggested_ticker}} y reclamar mi XP]

O si prefieres ver primero todos los detalles:

[Ir a mi Space Center]

---

Si ya tienes {{suggested_ticker}} en otra plataforma y quieres traerlo aquí, también cuenta. Consulta cómo transferir activos desde la sección de ayuda.

Un saludo,
El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*

*Has recibido este mensaje porque eres usuario registrado de Bit2Me. Para gestionar tus preferencias de comunicación, visita tu perfil.*

---

## 5. CREATIVE BRIEFS — JN-07

### Brief X1 In-App Card

**Estética:** Dark UI. Fondo #0D0F1A (azul-negro Bit2Me). Gradiente sutil en card: borde izquierdo en dorado B2M (#F0A500).
**Elementos visuales:**
- XP bar animada con contador: nivel actual → nivel siguiente, con incremento en tiempo real al mostrar la card
- Icono del activo sugerido (BTC o ETH) — grande, centrado, con brillo suave
- Badge de nivel Space Center (Tier {{space_center_tier}}) en esquina superior derecha
- Partículas de XP flotando (animación CSS de 2s, sutil)
**Tipografía:** Inter Bold para headline. Inter Regular para body. Tamaños: 18px / 14px.
**CTA:** Botón primario en gradiente naranja-dorado. Botón secundario ghost con borde blanco 40% opacity.
**Tamaño card:** Full-width modal card desde bottom (bottom sheet). Altura: 280px fija.

### Brief X2 Push

**Visual del push (Android rich notification):**
- Icono: Logo B2M con badge de misión (punto naranja)
- Imagen expandida: XP bar con flecha de progreso hacia siguiente nivel
- Color accent: #F0A500

### Brief X3 Email

**Header:** Banner oscuro (#0D0F1A) con logo Bit2Me en blanco + icono Space Center en dorado
**Estructura visual:** 600px max-width. Single column. Fondo blanco para body text.
**Módulo central:** "Tu misión" — card oscura con XP bar, nivel, y activo sugerido con icono
**CTA button:** #F0A500 (dorado B2M). Texto en negro. Border-radius 6px. 200px width.
**Footer:** Gris claro #F5F5F5. Texto legal en 10px, color #888.

---

## 6. TESTS A/B — JN-07

### Test 1 — X2 Push: XP Urgency vs Community Social Proof

**Hipótesis:** La prueba social ("otros de tu nivel ya avanzaron") supera a la urgencia de XP para usuarios pasivos de blockchain, que responden mejor a normas de comunidad que a escasez virtual.
**Métrica primaria:** CTR push → apertura app
**Métrica secundaria:** Segunda divisa comprada en 48h post-push
**Split:** 50/50
**Duración mínima:** 7 días o 1.000 aperturas por variante

### Test 2 — X3 Email: Asunto personalización vs Social Proof numérico

**Hipótesis:** El asunto con porcentaje concreto ("el 73% de los Nivel X") genera más aperturas que el asunto con nombre + días de espera, porque la comparación social activa FOMO de comunidad más fuerte que la referencia temporal.
**Métrica primaria:** Open rate
**Métrica secundaria:** Click rate en CTA principal
**Split:** 50/50
**Duración mínima:** 48h desde envío (tasa de apertura estabilizada)

### Test 3 — X1 Card: CTA primario "Comprar BTC/ETH" vs "Ver mi misión"

**Hipótesis:** Usuarios en Space Center screen tienen mayor intención declarada de progresar en el juego, por lo que el CTA orientado a misión ("Ver mi misión") convierte mejor que el CTA transaccional directo.
**Aplicar en:** Solo X1-A (usuarios activos)
**Métrica primaria:** Tasa de clic en CTA dentro de card
**Métrica secundaria:** Compra completada en 72h
**Split:** 50/50
**Nota:** Testear en Space Center screen únicamente. En Portfolio screen, mantener CTA transaccional como control.

---

## 7. NOTAS PARA DIEGO (LEGAL) — JN-07

**Revisión legal requerida antes de activación.**

**Puntos específicos a validar:**

1. **Sin promesas de rentabilidad financiera.** Todo el copy de JN-07 usa lenguaje de gamificación (XP, misiones, niveles). No aparecen proyecciones de retorno, APY, ni comparativas de precio. Revisar que el footer MiCA es suficiente para cubrir la mención a "diversificación de riesgo" en el email X3.

2. **Frase a revisar en X3:** "El riesgo concentrado en un solo activo es mayor que el riesgo distribuido en dos activos sin correlación perfecta." — Este es un enunciado de gestión de riesgo, no de asesoramiento. Confirmar si requiere matización adicional o si el disclaimer de footer cubre.

3. **"Los que llevan años en esto lo saben de memoria"** — Expresión coloquial de comunidad, sin afirmación de resultado. Sin objeción prevista, pero Diego debe confirmar.

4. **XP boost:** Confirmar que los beneficios virtuales del Space Center (XP, niveles) no se consideran "beneficio económico" bajo MiCA ni requieren valoración contable separada.

5. **Social proof porcentaje en asunto B:** "El 73% de los Nivel X ya tienen más de un activo" — verificar que el dato sea real en BigQuery antes de envío. Diego debe revisar que el uso de datos agregados de comportamiento de usuarios cumple con la política de privacidad. Sustituir por dato real o retirar si no es verificable.

6. **Footer obligatorio:** Presente en X3. X1 y X2 no requieren footer completo por ser in-app/push, pero deben respetar el tono de "activo de alto riesgo" sin minimizarlo.

---
---

# PARTE 2 — JN-08: STABLECOIN PARKERS EARN

**Objetivo:** Convertir 14.319 holders de USDT/USDC a productos Earn.
**Stop condition:** earn_active = true → parar journey.
**Regla de silencio S2:** Si BTC cambia >5% en 24h (al alza o baja), NO enviar S2 push ese día.

---

## 1. TABLA DE VARIABLES — JN-08

| Variable | Tipo | Ejemplo | Fallback |
|---|---|---|---|
| {{nombre}} | String | "Elena" | "inversor" |
| {{stablecoin_type}} | String | "USDT" o "USDC" | "tus stablecoins" |
| {{stablecoin_balance}} | String | "EUR 850" | omitir |
| {{earn_apy_usdt}} | String | "4,8% APY" | "un APY competitivo" |
| {{earn_apy_usdc}} | String | "4,6% APY" | "un APY competitivo" |
| {{yield_annual_eur}} | String | "EUR 41 al año" | omitir (usar genérico) |
| {{earn_apy_dynamic}} | String | APY según stablecoin tipo | "un APY competitivo" |

**Regla de yield copy:**
- Si {{yield_annual_eur}} >= EUR 15/año → mostrar cifra específica: "Tu saldo generaría aproximadamente {{yield_annual_eur}} en recompensas anuales."
- Si {{yield_annual_eur}} < EUR 15/año → usar genérico: "Tu {{stablecoin_type}} puede generar recompensas con el mismo nivel de estabilidad."
- Si {{stablecoin_balance}} no disponible → omitir bloque de cálculo de yield completamente.

---

## 2. ÁRBOL DE DECISIÓN — YIELD COPY

```
¿stablecoin_balance disponible?
├── NO → usar solo "un APY competitivo" + beneficio genérico
└── SÍ → calcular yield_annual_eur
    ├── yield_annual_eur >= 15 → mostrar cifra específica + earn_apy_dynamic
    └── yield_annual_eur < 15 → usar genérico (no mostrar cifra pequeña)
```

**Nota para Katy:** La variable {{yield_annual_eur}} debe ser calculada en BigQuery antes del envío. Fórmula: (stablecoin_balance_eur × earn_apy / 100). Redondear a EUR sin decimales.

---

## 3. S1 — EMAIL EDUCACIONAL (Semana 1)

### Línea de asunto

**Asunto:** Tu {{stablecoin_type}} está parado. Esto es lo que significa eso.
**Preheader:** No es una crítica — es una observación de alguien que sabe por qué elegiste estables.

---

### CUERPO COMPLETO — S1 EMAIL

---

Hola, {{nombre}}

Tener {{stablecoin_type}} en tu cartera no es un error. Es una decisión.

Elegiste estabilidad sobre volatilidad. Elegiste preservar valor sobre perseguir rentabilidad. Eso es una postura de inversión perfectamente válida — y en ciertos momentos del mercado, es la más inteligente.

Sabemos que no necesitas que te expliquemos lo que es una stablecoin.

Pero hay algo que quizás todavía no has explorado en Bit2Me: que tu {{stablecoin_type}} puede seguir siendo estable y, al mismo tiempo, generar recompensas.

---

**Cómo funciona Earn en Bit2Me**

Earn es el producto de rendimiento de Bit2Me para stablecoins y otros activos digitales.

La mecánica es directa:
- Activas Earn en tu {{stablecoin_type}}
- Tu saldo comienza a acumular recompensas diariamente
- Sigues teniendo acceso a tu saldo (sin períodos de bloqueo forzado)
- El APY actual para {{stablecoin_type}} es {{earn_apy_dynamic}}

No cambiamos tu activo. No lo convertimos en otra cosa. Tu {{stablecoin_type}} sigue siendo {{stablecoin_type}}.

---

**Lo que genera en números concretos**

[BLOQUE CONDICIONAL — mostrar solo si yield_annual_eur >= EUR 15]

Con tu saldo actual, estarías generando aproximadamente {{yield_annual_eur}} en recompensas anuales al {{earn_apy_dynamic}}.

No es una promesa — el APY es variable y puede cambiar. Pero es el orden de magnitud real con los datos que tenemos hoy.

[FIN BLOQUE CONDICIONAL]

[BLOQUE FALLBACK — mostrar si yield_annual_eur < EUR 15 o saldo no disponible]

La diferencia entre un saldo parado y un saldo en Earn no es enorme en términos absolutos cuando el capital es pequeño. Pero el hábito de activar rendimiento sobre saldos estables es lo que distingue a inversores que optimizan de los que no lo hacen.

[FIN BLOQUE FALLBACK]

---

**Riesgos que debes conocer**

Earn no es una cuenta bancaria. Antes de activarlo, ten en cuenta:

- El APY es variable. Puede subir o bajar sin previo aviso.
- Los productos de rendimiento implican riesgo de contraparte y de protocolo.
- Bit2Me no garantiza el rendimiento ni la devolución del capital.
- El importe mínimo para activar Earn puede variar por activo.

Si tienes dudas sobre si Earn encaja con tu perfil, consulta la documentación completa antes de activar.

---

**Sin prisa**

No te pedimos que decidas hoy. Este email es informativo.

Si quieres ver exactamente cómo funciona Earn antes de activarlo, puedes leer la guía completa o explorar el producto en la app sin comprometer nada.

[Explorar Earn en mi cuenta]
[Leer la guía completa de Earn]

Un saludo,
El equipo de Bit2Me

---

*Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital.*

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*

*Para gestionar tus preferencias de comunicación, visita tu perfil.*

---

## 4. S2 — PUSH NOTIFICATION (D+7 — con regla de silencio BTC)

*Una única variante. No enviar si BTC ha cambiado >5% en las últimas 24h.*

---

**Regla de silencio documentada para Katy / Álvaro:**

```
CONDICIÓN DE ENVÍO S2:
- abs(btc_price_change_24h) < 5%
- usuario.earn_active = false
- días desde S1 >= 7
- push recibidos esta semana por este usuario en JN-08 = 0
Si alguna condición falla → NO ENVIAR. Reintentar al día siguiente.
Máximo 1 reintento. Si BTC sigue >5% en D+8 → saltar S2, pasar a S3 en fecha programada.
```

---

**Título:** {{nombre}}, tu {{stablecoin_type}} puede trabajar hoy

**Cuerpo:** {{earn_apy_dynamic}} sobre stablecoins. Sin cambiar tu activo. Sin volatilidad. Activa Earn en 2 minutos.

**Deep link:** /earn/activate/{{stablecoin_type}}

**Nota de implementación:** Push enviado solo en días de baja volatilidad de mercado. El mensaje intencionalmente no menciona precio de BTC ni cripto volátil — el usuario elige estables, respetamos ese contexto.

---

## 5. S3 — EMAIL CIERRE SUAVE (D+21 — no activaron Earn)

### Línea de asunto

**Asunto:** Última vez que mencionamos esto, {{nombre}}
**Preheader:** Tu {{stablecoin_type}} puede seguir donde está. Solo queríamos que supieras la opción.

---

### CUERPO COMPLETO — S3 EMAIL

---

Hola, {{nombre}}

En las últimas semanas te hemos contado cómo funciona Earn en Bit2Me y qué puede hacer por tu {{stablecoin_type}}.

No lo has activado. Y está perfectamente bien.

Hay muchas razones válidas para mantener tu {{stablecoin_type}} sin rendimiento activo: estás esperando el momento adecuado, tienes pendiente leer más sobre los riesgos, prefieres tenerlo totalmente líquido sin ninguna dependencia adicional, o sencillamente has decidido que no es lo que buscas ahora mismo.

Todas son decisiones respetables.

---

**Una última cosa antes de cerrar el tema**

Si en algún momento cambias de opinión, Earn sigue disponible en tu cuenta. No caduca, no tiene fecha límite, y el proceso de activación tarda menos de dos minutos.

El APY actual para {{stablecoin_type}} es {{earn_apy_dynamic}}.

[Activar Earn cuando quiera]

---

**¿Hay algo que no te ha quedado claro?**

Si tienes alguna pregunta sobre Earn que no encontraste respuesta en la guía o en la app, puedes escribirnos directamente. Nuestro equipo responde en menos de 24 horas.

[Contactar con soporte]

---

No te enviaremos más mensajes sobre Earn a menos que haya un cambio relevante en el producto que debas conocer.

Gracias por ser parte de Bit2Me.

El equipo de Bit2Me

---

*Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital.*

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Paseo de la Castellana 141, 28046 Madrid, España*

*Para gestionar tus preferencias de comunicación, visita tu perfil.*

---

## 6. CREATIVE BRIEFS — JN-08

### Brief S1 Email — Tono Editorial Financiero

**Estética general:** Limpia, profesional, sin ruido visual. Inspiración: newsletter financiero de calidad, no app de gaming.
**Paleta:** Fondo blanco (#FFFFFF). Texto principal #1A1A2E. Accent color: verde oscuro #1B5E20 (estabilidad, no cripto-neón).
**Header:** Banner estrecho (80px). Fondo #1A1A2E con logo Bit2Me en blanco. Sin gradientes llamativos.
**Tipografía:** Georgia para el primer párrafo (tono editorial). Inter para el resto. H2 en negrita 20px. Body 16px, line-height 1.6.
**Módulo de yield (si aplica):** Card con fondo gris muy claro (#F7F7F7), borde izquierdo 3px en verde #1B5E20. Tipografía monospace para la cifra de EUR (simula terminal financiero).
**CTA buttons:** Dos CTAs de igual peso visual. Ghost buttons con borde #1A1A2E. Sin color relleno. Texto en #1A1A2E.
**Sección de riesgos:** Tipografía 13px, color #666. Box con fondo #FFF9C4 (amarillo muy suave) y borde izquierdo naranja #F57F17 — distinguible pero no alarmante.
**Footer:** Separador fino. Texto legal 10px #999.
**Sin:** emojis, iconos de cohetes, gráficas de velas, countdown timers, badges de oferta.

### Brief S2 Push — Minimalista Confiable

**Visual:** Sin imagen expandida. Solo texto. Icono: logo Bit2Me sin badge adicional.
**Tono visual:** Como si llegara de un gestor, no de un bot.
**Longitud:** Título máx 50 caracteres. Cuerpo máx 90 caracteres (sin truncar en iOS).

### Brief S3 Email — Cierre Limpio

**Mismo sistema visual que S1.** Ajuste: eliminar módulo de yield detallado. Simplificar a una sola columna de texto + dos CTAs. Añadir separador visual antes del párrafo "Una última cosa" para marcar el tono de cierre.

---

## 7. TESTS A/B — JN-08

### Test 1 — S1 Email: Asunto directo vs Asunto empático

**Variante control (asunto actual):** "Tu {{stablecoin_type}} está parado. Esto es lo que significa eso."
**Variante test:** "{{nombre}}, hay una opción que quizás no has explorado todavía"
**Hipótesis:** El asunto control es más disruptivo e intrigante para usuarios financieramente sofisticados (que no necesitan ser tratados con guantes). El asunto test es más empático pero puede parecer vago. Esperamos que el control gane en open rate entre usuarios USDC (mayor balance, más sofisticados). Puede perder entre USDT (mayor volumen, perfil más diverso).
**Segmentar resultados por:** USDT vs USDC por separado
**Métrica:** Open rate, click rate en CTA "Explorar Earn"
**Split:** 50/50
**Duración:** 72h desde envío

### Test 2 — S3 Email: Cierre explícito vs Cierre abierto

**Variante control (copia actual):** "Última vez que mencionamos esto" — cierre explícito de journey
**Variante test:** Sin mención al "última vez". Misma información, tono de check-in suave: "¿Todavía no has activado Earn?"
**Hipótesis:** El cierre explícito puede generar urgencia de decisión ("si no es ahora, ¿cuándo?") pero también puede percibirse como presión. El check-in suave puede tener menor conversión pero mejor NPS (no genera friccción).
**Métrica primaria:** earn_active en 7 días post S3
**Métrica secundaria:** Tasa de unsubscribe por email
**Split:** 50/50
**Nota:** Priorizar métrica secundaria si la diferencia en conversión es <1%. Proteger la relación con este segmento de alto valor (AUC EUR 664-1.784 promedio).

---

## 8. NOTAS PARA DIEGO (LEGAL) — JN-08

**REVISIÓN LEGAL PRIORITARIA — Journey con producto de rendimiento.**

**Puntos específicos a validar:**

1. **Disclaimer Earn — aparece DOS veces en S1 y S3:** Inmediatamente antes del footer MiCA. Diego debe confirmar que la posición del disclaimer (antes del footer, no al final) es suficiente o si debe aparecer en posición más prominente (antes del bloque de APY).

2. **Frase "tu USDT sigue siendo USDT":** Confirmar que esta afirmación es técnicamente correcta según la mecánica de Earn en Bit2Me (¿hay conversión temporal de activo en el producto Earn?). Si hay cualquier transformación del activo, esta frase debe eliminarse.

3. **APY variable — mención explícita de variabilidad:** En S1 y S3 se menciona expresamente que "el APY es variable y puede cambiar sin previo aviso." Diego confirmar que este nivel de disclosure es suficiente bajo MiCA para mencionar APY concreto en el cuerpo del email.

4. **Yield calculation copy:** La frase "estarías generando aproximadamente {{yield_annual_eur}} en recompensas anuales" usa "aproximadamente" de forma intencional para no constituir proyección de beneficio. Diego revisar si el uso de una cifra concreta (aunque sea aproximada) requiere cualificación adicional bajo MiCA Art. 22 (comunicaciones de marketing).

5. **S2 Push — mención de APY en 90 caracteres:** "{{earn_apy_dynamic}} sobre stablecoins" — ¿requiere disclaimer aunque sea en push? Si push no puede incluir disclaimer, revisar si la mención de APY en push está permitida bajo MiCA o si debemos usar lenguaje neutro ("genera recompensas") sin cifra.

6. **Silencio en días de alta volatilidad BTC:** Documentar que la regla de silencio es una decisión de negocio para proteger la experiencia de usuario, no un requisito regulatorio. Diego confirmar que esta regla no tiene implicaciones regulatorias adicionales.

7. **USDC vs USDT — diferencias de riesgo:** ¿Requiere el disclaimer diferenciar entre los riesgos de USDT (Tether) y USDC (Circle)? Los perfiles de riesgo de emisor son distintos. Si Diego considera necesario, añadir nota en footer específica para cada stablecoin.

8. **Footer S3 — "no te enviaremos más mensajes sobre Earn":** Confirmar que esta promesa de no contacto sobre un producto específico no crea obligación legal. Alternativa si hay problema: "reduciremos la frecuencia de comunicaciones sobre Earn."

---
---

# APÉNDICE — RESUMEN DE FLUJOS

## JN-07 Flujo de Decisión

```
Usuario: first_mov_currency = B2M, assets_purchased <= 1
│
├── D+0: X1 In-App Card (Space Center o Portfolio screen)
│   ├── Variante A: Usuario activo (login <7d)
│   └── Variante B: Usuario pasivo (sin login >7d)
│
├── ¿Compró segundo activo? → SÍ → STOP
│
├── D+5: X2 Push (20:30 CET)
│   ├── A/B: XP Urgency vs Community Social Proof
│   └── No enviar si ya compró segundo activo
│
├── ¿Compró segundo activo? → SÍ → STOP
│
└── D+10: X3 Email
    ├── A/B: Asunto personalización vs Social Proof numérico
    └── MiCA footer obligatorio
```

## JN-08 Flujo de Decisión

```
Usuario: USDT o USDC, auc_eur >= 50, earn_active = false
│
├── Semana 1: S1 Email educacional (sin presión)
│   └── A/B: Asunto directo vs Asunto empático
│
├── ¿earn_active = true? → SÍ → STOP
│
├── D+7: ¿abs(BTC_change_24h) < 5%?
│   ├── SÍ → S2 Push
│   └── NO → Esperar 24h. Reintentar D+8. Si sigue >5% → saltar S2.
│
├── ¿earn_active = true? → SÍ → STOP
│
└── D+21: S3 Email (cierre suave)
    ├── A/B: Cierre explícito vs Check-in suave
    └── Earn disclaimer + MiCA footer obligatorio
```

---

*Documento preparado por: Bit2Me Lifecycle OS*
*Fecha: 24 de marzo de 2026*
*Siguiente paso: Revisión por Diego (legal). Post-aprobación: Katy configura CleverTap.*
