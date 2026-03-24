# JN-05 — EUR Depositors First Crypto: Copy Package Completo

**Journey:** JN-05 | **Fecha:** 2026-03-24 | **Owner:** Daniel Ferraro — Head of Growth, Bit2Me
**Segmento:** first_mov_currency = 'EUR', total_crypto_purchases = 0, account_status = 'enabled', auc_eur > 10
**Universo:** 4,370 usuarios | EUR 29.3M en cuenta | 0 compras de crypto
**GUARDRAIL:** Si tasa de retirada EUR > 5% vs baseline → STOP inmediato en todos los envíos. Revisión diaria.

---

## 1. Dynamic Variables — Tabla de Variables y Fallbacks

| Variable | Descripción | Ejemplo | Fallback |
|---|---|---|---|
| {{nombre}} | Nombre de pila del usuario | "Ana" | "inversor" |
| {{eur_balance}} | Saldo EUR en cuenta | "EUR 350" | omitir referencia al importe |
| {{suggested_first_asset}} | Activo sugerido (basado en perfil) | "Bitcoin" | "Bitcoin" |
| {{suggested_amount_eur}} | Importe sugerido primera compra — min(saldo/4, 25) | "EUR 50" | "EUR 25" |
| {{weekly_dca}} | Importe DCA semanal — min(saldo/4, 25) | "EUR 25" | "EUR 10" |
| {{incentivo_activo}} | Boolean — exención de comisión activa | true/false | false |
| {{cta_url}} | URL con UTM hacia flujo de compra | bitly tracked | bitly default |

**Lógica de incentivo:** Si {{incentivo_activo}} = true → mostrar bloque "Sin comisión en tu primera compra". Si false → omitir bloque, no mencionar precio.

---

## 2. ACTIVE TRACK (1,110 usuarios — login últimos 30 días)

### A1 — In-App Card (Home / Portfolio Screen)

*Aparece cuando el usuario abre la app y ve su saldo EUR en el portfolio. Máximo 2 líneas de título + 1 línea de subtítulo + CTA.*

---

**A1 — Variante A: Endowment ("tu dinero ya está aquí")**

> **Título:** Tu EUR ya está listo para trabajar
>
> **Subtítulo:** Compra {{suggested_first_asset}} desde {{suggested_amount_eur}}. Puedes vender cuando quieras.
>
> **CTA:** Comprar ahora

*[Si {{incentivo_activo}} = true, añadir badge sobre CTA: "Sin comisión"]*

---

**A1 — Variante B: Curiosidad + reversibilidad**

> **Título:** ¿Qué hace tu EUR aquí parado?
>
> **Subtítulo:** Más de un millón de personas ya tienen {{suggested_first_asset}}. Tú también puedes empezar hoy.
>
> **CTA:** Ver {{suggested_first_asset}}

*[Si {{incentivo_activo}} = true, añadir badge: "Primera compra sin comisión"]*

---

**Notas de diseño A1:**
- Dimensiones: 343 × 120 px (card full-width, iOS + Android)
- No usar precio de mercado en tiempo real (riesgo de caducidad)
- Mostrar solo si saldo EUR > 10 EUR y total_crypto_purchases = 0
- Stop condition: ocultar si total_crypto_purchases > 0

---

### A2 — Push Notification (D+2 si no hay acción en A1)

*Máximo 60 caracteres en título, 120 en cuerpo. Enviado a las 19:00 hora local.*

---

**A2 — Variante A: Pie en la puerta (tiny first step)**

> **Título:** {{nombre}}, un paso pequeño 🟠
>
> **Cuerpo:** Tienes EUR en tu cuenta. Comprar {{suggested_amount_eur}} de Bitcoin tarda menos de 1 minuto.
>
> **Deep link:** → Pantalla de compra rápida ({{suggested_first_asset}})

---

**A2 — Variante B: Social proof**

> **Título:** Hoy lo han hecho 847 personas
>
> **Cuerpo:** Han comprado su primera crypto en Bit2Me. Tu EUR ya está aquí — solo falta un clic.
>
> **Deep link:** → Pantalla de compra rápida

*Nota: cifra "847" = número dinámico de compradores del día anterior. Si no disponible → "Cientos de personas".*

---

**Notas push A2:**
- Horario: 19:00 hora local (mayor tasa de apertura en este segmento)
- No enviar en fin de semana si primera sesión fue laboral (respetar contexto)
- Requiere opt-in de notificaciones push — verificar antes de enviar

---

### A3 — Email (D+5, con cuerpo educacional + incentivo)

**Asunto A:** Tu dinero en EUR lleva {{dias_sin_compra}} días esperando — ¿lo activamos?
**Asunto B:** {{nombre}}, tienes {{eur_balance}} listos. Aquí te explico cómo dar el primer paso

*Preheader: "No hace falta experiencia. No hace falta arriesgar mucho. Solo empezar."*

---

**[CUERPO EMAIL A3]**

Hola {{nombre}},

Llevas un tiempo con euros en tu cuenta de Bit2Me. Eso ya es lo más difícil: traer el dinero a una plataforma de confianza. El siguiente paso es más sencillo de lo que parece.

**¿Por qué muchos esperan antes de comprar su primera crypto?**

La mayoría de las personas que tienen EUR en su cuenta nos dicen lo mismo: "No sé por dónde empezar" o "Tengo miedo de equivocarme." Es completamente normal. Nadie nace sabiendo.

Por eso queremos explicarte cómo funciona en 3 puntos:

**1. Empezar pequeño es válido — y es lo que recomendamos**

No tienes que comprar todo tu saldo de golpe. La mayoría de los inversores empiezan con una cantidad pequeña para aprender cómo funciona. Con {{suggested_amount_eur}} ya puedes comprar una fracción de {{suggested_first_asset}} y ver en tiempo real cómo se mueve tu portfolio.

**2. Puedes vender cuando quieras**

Las criptomonedas son activos líquidos. Si decides vender mañana, puedes hacerlo. No hay permanencia mínima, no hay penalizaciones por salir. El control es tuyo.

**3. {{suggested_first_asset}} es el punto de partida más común**

Bitcoin lleva más de 15 años funcionando y es el activo de referencia del sector. No es una garantía de nada — los precios suben y bajan — pero si quieres entender cómo funciona esto, es el lugar donde la mayoría empieza.

---

*[BLOQUE CONDICIONAL — mostrar solo si {{incentivo_activo}} = true]*

**Además, esta semana: sin comisión en tu primera compra**

Para que el primer paso no te cueste nada extra, hemos eliminado la comisión de tu primera operación de compra. Solo por ser tú, y solo esta semana.

---

**¿Cómo hacerlo? Tres pasos:**

1. Entra en tu cuenta de Bit2Me
2. Ve a "Comprar crypto" y selecciona {{suggested_first_asset}}
3. Introduce {{suggested_amount_eur}} o el importe que prefieras — y confirma

Eso es todo.

**[CTA principal] → Comprar mi primera crypto ahora**

Si tienes dudas, nuestro equipo de soporte está disponible en el chat de la app. No hace falta que lo hagas solo.

Un saludo,
**El equipo de Bit2Me**

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España*
*Para dejar de recibir estos correos, haz clic aquí: [Darme de baja]*

---

**Notas diseño A3:**
- Dimensiones email: 600px ancho, fondo #FFFFFF, acento #F7931A (Bitcoin orange)
- Botón CTA: fondo #F7931A, texto blanco, border-radius 8px, 18px font
- Incluir imagen hero: ilustración abstracta de monedas / gráfico en tono azul-naranja (sin mostrar precio)
- Ratio texto/imagen: mínimo 60/40 para evitar filtros spam

---

### A4 — Email Last Chance (D+10 — solo no abrieron A3)

**Asunto A:** Última vez que te escribimos sobre esto, {{nombre}}
**Asunto B:** ¿Prefieres que no te enviemos más sobre crypto? (y una última propuesta)

*Preheader: "Si no es el momento, lo entendemos. Pero antes de cerrar, mira esto."*

---

**[CUERPO EMAIL A4]**

Hola {{nombre}},

Te hemos escrito un par de veces porque tienes euros en tu cuenta de Bit2Me y aún no has comprado crypto. No vamos a insistir más después de este correo — si no es tu momento, es completamente respetable.

Pero antes de cerrar este capítulo, queremos dejarte una idea concreta.

**La estrategia que usan muchos principiantes: DCA**

DCA significa "Dollar Cost Averaging" — en español, comprar una cantidad fija de forma periódica, independientemente del precio. ¿Por qué funciona para empezar?

Porque elimina la presión de "comprar en el momento perfecto." Nadie sabe cuándo es el mejor momento. Con {{weekly_dca}} a la semana en {{suggested_first_asset}}, en un año habrás construido posición sin haber tenido que adivinar nada.

No es consejo de inversión — es la forma en que la mayoría de la gente gestiona la incertidumbre cuando empieza.

*[BLOQUE CONDICIONAL — mostrar solo si {{incentivo_activo}} = true]*

Y si lo haces esta semana, la primera compra no tiene comisión.

---

Tienes {{eur_balance}} listos en tu cuenta. El resto está en ti.

**[CTA] → Configurar mi primera compra**

Si decides que no es para ti, sin problema: puedes retirar tu EUR cuando quieras.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España*
*Para dejar de recibir estos correos: [Darme de baja]*

---

**Notas diseño A4:**
- Tono más personal, menos visual — texto sobre fondo blanco, sin imagen hero
- CTA color secundario: #1A1A2E (azul oscuro) en lugar del naranja — señal de "último aviso" sin alarmar
- Asegurar que el bloque de baja es prominente — respeta la preferencia del usuario

---

## 3. DORMANT TRACK (3,260 usuarios — sin login >90 días)

### D1 — Email Re-engagement (envío inicial)

**Asunto A:** {{nombre}}, aún tienes {{eur_balance}} en Bit2Me
**Asunto B:** Llevas meses sin entrar — ¿sigues interesado en crypto?

*Preheader: "Todo sigue aquí. Y la crypto tampoco ha desaparecido."*

---

**[CUERPO EMAIL D1]**

Hola {{nombre}},

Hace tiempo que no te vemos por aquí. Tu cuenta sigue activa y tus euros están seguros — no te hemos tocado nada.

Solo queríamos recordarte que tienes {{eur_balance}} en tu cuenta de Bit2Me esperando que decidas qué hacer con ellos.

**¿Qué ha pasado en crypto estos meses?**

Si llevas tiempo sin seguir el sector, es normal perderse el contexto. Lo resumimos rápido:

Bitcoin sigue siendo el activo de referencia. Muchos bancos y fondos institucionales llevan años acumulando posición. No porque sea una apuesta segura — no lo es — sino porque el mercado ha madurado mucho.

Pero lo más importante para ti no es el precio de hoy. Es que tienes la infraestructura lista: cuenta verificada, dinero depositado, plataforma regulada. Lo único que te falta es apretar el botón.

**¿Cuánto arriesgar para empezar?**

Nuestra recomendación para quien empieza: una cantidad pequeña que puedas olvidarte durante un tiempo sin que te afecte. Para muchos usuarios eso es {{suggested_amount_eur}}. Para otros es menos. No hay respuesta incorrecta.

Lo que sí sabemos es que esperar al "momento perfecto" no funciona — nadie lo encuentra.

**[CTA] → Entrar en mi cuenta y echar un vistazo**

No te pedimos que compres ahora mismo. Solo que entres, veas cómo está el mercado, y decidas con calma.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España*
*[Darme de baja] | [Gestionar preferencias]*

---

**Notas diseño D1:**
- Imagen hero: foto lifestyle (persona mirando teléfono, neutral, no eufórica) — transmitir normalidad
- CTA: tono cálido, sin urgencia — este segmento necesita reactivación emocional primero
- No mencionar incentivo de comisión en D1 — primero reconectar, luego convertir

---

### D2 — Email (D+7, ángulo diferente — solo no abrieron D1)

**Asunto A:** Una pregunta directa, {{nombre}}
**Asunto B:** ¿Qué necesitas para dar el primer paso con crypto?

*Preheader: "No queremos adivinar. Te lo preguntamos."*

---

**[CUERPO EMAIL D2]**

Hola {{nombre}},

Te escribimos con una pregunta directa: ¿qué es lo que te ha frenado hasta ahora?

Llevamos tiempo viendo los mismos patrones. Las razones más comunes que nos dan:

**"No sé lo suficiente todavía"**
La mayoría de las personas que tienen crypto tampoco sabían nada antes de comprar la primera vez. El conocimiento viene con la práctica, no al revés. Nadie espera saber conducir antes de subirse al coche.

**"El mercado está muy volátil"**
Siempre lo está. Eso es inherente a los activos de alto riesgo — y también es parte de su potencial. La clave no es el timing, es el tamaño de la posición. Empezar pequeño reduce el estrés.

**"No sé qué comprar"**
Si no tienes preferencias, {{suggested_first_asset}} es donde empieza la mayoría. Es el activo con más historia, más liquidez y más referencias disponibles para aprender.

**"No quiero perder mi dinero"**
Es la razón más honesta y la más válida. Por eso existe el principio de "no invertir más de lo que puedas permitirte perder." Tus {{eur_balance}} no tienen que ir todos a crypto. Ni la mitad. Ni un cuarto. Solo lo que, si desapareciera mañana, no te cambiaría la vida.

---

Sea cual sea tu razón, la puerta sigue abierta.

*[BLOQUE CONDICIONAL — mostrar solo si {{incentivo_activo}} = true]*

Esta semana además tienes la primera compra sin comisión. Si alguna vez ibas a probar, este es un buen momento.

---

**[CTA] → Explorar {{suggested_first_asset}} en Bit2Me**

Y si decides que no es para ti, también está bien. Puedes retirar tu EUR en cualquier momento.

El equipo de Bit2Me

---

*Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.*

*Bit2Me Sociedad de Valores, S.A. — Paseo de la Castellana 141, 28046 Madrid, España*
*[Darme de baja] | [Gestionar preferencias]*

---

**Notas diseño D2:**
- Formato: lista de objeciones con respuesta — fácil de escanear
- Sin imagen hero — email de texto puro con una firma cálida
- Incluir enlace visible a FAQ de seguridad de la plataforma (trust signal)

---

## 4. Creative Briefs por Touchpoint

### CB-A1: In-App Card

| Campo | Detalle |
|---|---|
| Dimensiones | 343 × 120 px (full-width card, iOS + Android) |
| Mood | Clean, confianza, momentum — como ver el saldo bancario y saber que puedes hacer algo con él |
| Paleta | Fondo #F9F9FB, acento #F7931A, texto #1A1A2E |
| Elemento visual | Icono de moneda BTC + flecha de progreso suave. Sin gráficos de velas — demasiado técnico |
| Tipografía | SF Pro / Roboto, título 17px bold, subtítulo 13px regular |
| AI Image Prompt (EN) | "Minimalist mobile UI card, clean white background, Bitcoin orange accent color, small BTC coin icon with subtle upward arrow, no candlestick charts, no price numbers, soft shadow, 343x120 pixels, flat design, professional fintech aesthetic" |

### CB-A2: Push Notification

| Campo | Detalle |
|---|---|
| Dimensiones | No aplica — texto puro + deep link |
| Timing | 19:00 hora local |
| Mood | Amigable, directo, sin presión |
| Icono | Logo Bit2Me circular (estándar sistema) |
| AI Image Prompt (EN) | No aplica (sistema operativo controla visual) |

### CB-A3: Email Body

| Campo | Detalle |
|---|---|
| Ancho | 600 px |
| Hero image | 600 × 300 px — ilustración abstracta de portafolio digital, sin cifras de precio |
| Paleta | Fondo #FFFFFF, bloques de acento #FFF8F0, CTA #F7931A |
| Tipografía | Georgia / serif para cuerpo (confianza), Arial para headers |
| CTA button | 240 × 48 px, border-radius 8px, texto "Comprar mi primera crypto ahora" |
| Footer | Fondo #F4F4F4, texto 10px gris oscuro, disclaimer MICA completo |
| AI Image Prompt (EN) | "Professional fintech email illustration, abstract digital portfolio concept, warm orange and deep blue tones, person on laptop or phone, calm and confident mood, no price charts, no percentage numbers, no bullish/bearish imagery, 600x300px, flat illustration style, white background" |

### CB-A4: Last Chance Email

| Campo | Detalle |
|---|---|
| Ancho | 600 px |
| Visual | Sin imagen hero — carta de texto, más personal |
| Paleta | Fondo #FFFFFF, CTA #1A1A2E (azul oscuro) |
| Tono visual | Conversacional, como un email de una persona real |
| AI Image Prompt (EN) | "Minimal email layout, no hero image, single column text, clean typography, professional but warm, fintech brand, white background, subtle bottom footer in light grey" |

### CB-D1: Dormant Re-engagement Email

| Campo | Detalle |
|---|---|
| Ancho | 600 px |
| Hero image | 600 × 280 px — persona mirando teléfono, entorno neutro, nada eufórico |
| Paleta | Fondo #FFFFFF, acento azul marino #1A1A2E, CTA #F7931A |
| Mood | Reconexión emocional suave — "seguimos aquí, sin presión" |
| AI Image Prompt (EN) | "Lifestyle photo style illustration, person casually looking at smartphone, neutral home or coffee shop environment, calm and relaxed mood, no crypto logos, no price charts, warm light, 600x280px, slightly desaturated, professional editorial feel" |

### CB-D2: Dormant Objection Email

| Campo | Detalle |
|---|---|
| Ancho | 600 px |
| Visual | Sin hero — lista estructurada con iconos inline pequeños por cada objeción |
| Paleta | Fondo #FFFFFF, iconos #F7931A, texto #1A1A2E |
| AI Image Prompt (EN) | "Clean email layout with small inline icons for each list item, minimal flat icons representing: knowledge/book, chart volatility, question mark, money/shield — orange accent color, white background, professional fintech email design, 600px wide" |

---

## 5. A/B Test Register

### TEST-JN05-01: A1 Card — Framing (Endowment vs Curiosidad)

| Campo | Detalle |
|---|---|
| ID | TEST-JN05-01 |
| Touchpoint | A1 — In-App Card |
| Hipótesis | El framing de endowment ("tu EUR ya está listo") genera más CTR que el framing de curiosidad ("¿qué hace tu EUR parado?") porque activa el sentido de propiedad sobre el dinero ya depositado |
| Variante A | "Tu EUR ya está listo para trabajar" + CTA "Comprar ahora" |
| Variante B | "¿Qué hace tu EUR aquí parado?" + CTA "Ver Bitcoin" |
| Métrica primaria | CTR a pantalla de compra (72h post-impresión) |
| Métrica secundaria | Tasa de conversión a primera compra |
| Split | 50/50 |
| Tamaño muestral | 555 usuarios por variante (universo activo: 1,110) |
| Duración | 7 días |
| Criterio de victoria | p < 0.05, diferencia mínima detectable +2pp CTR |

### TEST-JN05-02: A2 Push — Social Proof vs Tiny Step

| Campo | Detalle |
|---|---|
| ID | TEST-JN05-02 |
| Touchpoint | A2 — Push notification D+2 |
| Hipótesis | Social proof ("hoy lo han hecho 847 personas") genera más opens que la táctica de reducción de fricción ("tarda menos de 1 minuto") porque activa el mecanismo de aprobación social |
| Variante A | "{{nombre}}, un paso pequeño" + cuerpo sobre tiempo y facilidad |
| Variante B | "Hoy lo han hecho 847 personas" + cuerpo de social proof |
| Métrica primaria | Open rate de push |
| Métrica secundaria | Tap-through rate + conversión |
| Split | 50/50 |
| Duración | 7 días |
| Criterio de victoria | p < 0.05, diferencia mínima +3pp open rate |

### TEST-JN05-03: A3 Email — Asunto personalización vs balance explícito

| Campo | Detalle |
|---|---|
| ID | TEST-JN05-03 |
| Touchpoint | A3 — Email D+5 |
| Hipótesis | El asunto con balance explícito ("tienes EUR 350 listos") genera mayor open rate que el asunto con días de espera ("lleva 12 días esperando") porque el framing de posesión concreta supera la urgencia temporal |
| Variante A | "Tu dinero en EUR lleva {{dias_sin_compra}} días esperando — ¿lo activamos?" |
| Variante B | "{{nombre}}, tienes {{eur_balance}} listos. Aquí te explico cómo dar el primer paso" |
| Métrica primaria | Open rate email |
| Métrica secundaria | CTR + conversión a primera compra |
| Split | 50/50 |
| Criterio de victoria | p < 0.05, diferencia mínima +2pp open rate |

### TEST-JN05-04: D2 Email — Asunto pregunta directa vs oferta de escucha

| Campo | Detalle |
|---|---|
| ID | TEST-JN05-04 |
| Touchpoint | D2 — Email dormant D+7 |
| Hipótesis | El asunto que formula una pregunta directa ("¿Qué necesitas para dar el primer paso?") genera mayor open rate que el asunto genérico ("Una pregunta directa") porque apela directamente al estado mental del usuario dormant |
| Variante A | "Una pregunta directa, {{nombre}}" |
| Variante B | "¿Qué necesitas para dar el primer paso con crypto?" |
| Métrica primaria | Open rate email |
| Métrica secundaria | CTR + re-login |
| Split | 50/50 |
| Criterio de victoria | p < 0.05, diferencia mínima +2pp open rate |

---

## 6. Fallback Logic + Guardrail Table

| Condición | Acción |
|---|---|
| {{nombre}} no disponible | Usar "inversor" |
| {{eur_balance}} no disponible o < 10 EUR | Omitir mención al importe específico; usar lenguaje genérico "tu saldo en euros" |
| {{suggested_first_asset}} no calculado | Fallback: "Bitcoin" |
| {{suggested_amount_eur}} no calculado | Fallback: "EUR 25" |
| {{weekly_dca}} no calculado | Fallback: "EUR 10" |
| {{incentivo_activo}} = false | Omitir bloque de incentivo completamente — no mencionar comisión |
| total_crypto_purchases > 0 (conversión ocurrida) | STOP INMEDIATO en toda la secuencia para este usuario. Sacar de journey en tiempo real |
| Usuario hace withdrawal EUR > X durante journey | Registrar evento; si tasa global supera 5% vs baseline → PAUSE todos los envíos + alerta a Daniel |
| Usuario hace clic en "Darme de baja" | Unsubscribe inmediato + excluir de todos los journeys activos |
| Push opt-in = false | Skip A2, continuar a A3 |
| Email bounce (hard) | Excluir del journey y marcar en CRM |
| Login sin compra después de A1/A2 | Continuar secuencia — el login no es stop condition |
| GUARDRAIL: EUR withdrawal rate >5% vs baseline | STOP en todos los envíos del journey. Revisión diaria por Daniel. Reactivar solo tras análisis. |

---

## 7. Diego Approval Notes — Revisión Legal Pre-Envío

*Para: Diego (Legal Gate CRM)*
*De: Daniel Ferraro / Growth*
*Journey: JN-05 — EUR Depositors First Crypto*
*Fecha: 2026-03-24*

### Elementos a revisar

**MICA compliance — confirmaciones necesarias:**

- Todos los emails incluyen el disclaimer completo de la CNMV en el footer. Confirmar que el texto está aprobado y es la versión vigente.
- En ningún touchpoint se usa el término "rentabilidad garantizada", "rendimiento", "interés" o "ganancias". Usar: "comprar", "vender", "precio de mercado".
- La frase "puedes vender cuando quieras" está incluida en A1, A3 y A4 para reforzar la reversibilidad. Confirmar que no implica liquidez garantizada en cualquier condición de mercado.
- El email D2 incluye la frase "si desapareciera mañana, no te cambiaría la vida" en referencia al importe a invertir. Confirmar que esta formulación es aceptable como caracterización de riesgo individual.

**Incentivo de comisión ({{incentivo_activo}} = true):**

- El bloque de incentivo se activa solo si la variable booleana es true. En todos los demás casos se omite completamente.
- La exención de comisión es para la primera compra, sin importe mínimo. Confirmar términos y condiciones específicos antes de activar.
- No se menciona ningún porcentaje de APY ni producto de Earn en estos mensajes. Si en versiones futuras se añade cross-sell a Earn, requerirá nuevo ciclo de aprobación con disclaimer adicional.

**Subjects de email:**

- Asunto A3-A: "Tu dinero en EUR lleva X días esperando" — confirmar que la referencia temporal no implica que el dinero "pierde valor" (prohibido bajo MICA). La intención es urgencia de acción, no afirmación sobre inflación.
- Asunto D1-A: "{{nombre}}, aún tienes {{eur_balance}} en Bit2Me" — recordatorio de saldo, no afirmación de pérdida.

**Opt-out:**

- Todos los emails incluyen enlace de baja visible en footer.
- El journey tiene stop condition inmediata en caso de unsubscribe.
- Confirmar que la gestión de preferencias de comunicación está vinculada al CRM correctamente.

**Datos personales:**

- El uso de {{eur_balance}} y {{nombre}} en asuntos de email requiere base legal de ejecución contractual o interés legítimo. Confirmar con DPO si aplica consentimiento adicional.

**Notas adicionales para Diego:**

- El guardrail de withdrawal rate es operativo, no legal — pero si la tasa supera el 5%, el equipo de Growth necesita comunicación inmediata para evaluar si hay un problema de confianza en la plataforma.
- La primera versión de este journey NO incluye referencias a productos de Earn, Staking ni Préstamos — cero cross-sell en esta fase. Simplifica la revisión.

*Versión para aprobación: 1.0 | Siguiente versión tras feedback de Diego: 1.1*

---

## Apéndice — Secuencia Visual del Journey

```
ACTIVE (1,110 usuarios — login <30 días)
│
├─ D+0  → A1: In-App Card (Variante A / B)
│          Stop: total_crypto_purchases > 0
│
├─ D+2  → A2: Push (si no hay acción en A1)
│          Stop: total_crypto_purchases > 0
│
├─ D+5  → A3: Email (cuerpo educacional + incentivo condicional)
│          Stop: total_crypto_purchases > 0
│
└─ D+10 → A4: Email Last Chance (solo no abrieron A3)
           Stop: total_crypto_purchases > 0 | unsubscribe

DORMANT (3,260 usuarios — sin login >90 días)
│
├─ D+0  → D1: Email re-engagement, ángulo soft
│          Stop: total_crypto_purchases > 0
│
└─ D+7  → D2: Email objections (solo no abrieron D1)
           Stop: total_crypto_purchases > 0 | unsubscribe

GUARDRAIL GLOBAL: EUR withdrawal rate >5% vs baseline → PAUSE todo el journey
```

---

*Documento generado: 2026-03-24 | Journey OS — Bit2Me Growth*
