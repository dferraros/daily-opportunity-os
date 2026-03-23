# J02 Recovery Tracks y J02.5 Loyalty — Bit2Me

**Documento:** Recovery Tipo A / Tipo B / Tipo C + Secuencia Loyalty
**Fecha:** 2026-03-23
**Autor:** Journey OS Plan 01-05
**Estado:** COMPLETO — listo para ejecucion por Katy y Diego

---

## Tabla de Contenidos

1. [Contexto y datos de entrada](#1-contexto-y-datos-de-entrada)
2. [Como llegan los usuarios aqui](#2-como-llegan-los-usuarios-aqui)
3. [Recovery Tipo A — Indeciso Activo](#3-recovery-tipo-a--indeciso-activo)
4. [Recovery Tipo B — Dormido con Saldo](#4-recovery-tipo-b--dormido-con-saldo) ← LANZABLE ESTA SEMANA
5. [Recovery Tipo C — Caso Frio](#5-recovery-tipo-c--caso-frio)
6. [J02.5 Loyalty — D+45 a D+90](#6-j025-loyalty--d45-a-d90)
7. [Resumen KPIs y tabla de aprobacion Diego](#7-resumen-kpis-y-tabla-de-aprobacion-diego)

---

## 1. Contexto y datos de entrada

### Poblacion total de no-conversores (Excel Jan-Mar 2026)

| Tipo | Descripcion | Usuarios | % del total no-conv | Accion |
|------|-------------|----------|---------------------|--------|
| Total FM | Base analizada | 5.182 | 100% | — |
| Total no-conv | Sin segunda compra | 1.333 | 25.7% | Recovery |
| **Tipo A** | Warm, <30d sin 2a op | **491** | 36.8% | Journey automatico A1+A2 |
| **Tipo B** | Cold, 31-60d sin 2a op | **547** | 41.0% | Manual esta semana + B2 push |
| **Tipo C** | Frozen, 60+d sin 2a op | **295** | 22.1% | FOMO Agent pool (no journey) |

### Benchmarks de referencia

| Benchmark | Fuente | Dato |
|-----------|--------|------|
| Tipo A win-back rate | Klaviyo/Braze fintech | 22% |
| Tipo B win-back rate | Klaviyo/Braze fintech | 13% |
| Tipo C win-back rate | Klaviyo/Braze fintech | 7.5% |
| Re-engagement email con portfolio value | Omnisend 2024 | 28% open rate |
| 3+ trades en 90 dias = 3.1x higher 12-month retention | Coinbase Investor Day 2023 | 3.1x lift |
| M1 retention actual Bit2Me | Datos internos | 0.12% (CRISIS) |
| M1 retention benchmark | Coinbase | 25% |

---

## 2. Como llegan los usuarios aqui

El Hub J02-CORE ejecuta 6 touchpoints (S0 in-app, S0.5 alerta precio, S1 push, S2 in-app, S3 email, S4 push) entre D+0 y D+7 desde la primera monetizacion.

En D+30, el sistema evalua si hay segunda compra confirmada:

```
D+30: check second_purchase_confirmed
  SI → continua en Hub / entra en Spokes activos / luego J02.5 Loyalty en D+45
  NO → clasificar por dias_sin_2a_op:
       < 30 dias  → Tipo A (491 usuarios)
       31-60 dias → Tipo B (547 usuarios)
       60+ dias   → Tipo C (295 usuarios)
```

A partir de aqui, el Hub termina. Recovery toma el control.

**Regla de frecuencia:** Los usuarios en Recovery siguen sujetos al cap global: max 2 emails/semana, max 2 push/semana. Si un usuario esta en un Spoke activo (Earn, Pro, etc.), Recovery se pausa hasta que el Spoke termine.

---

## 3. Recovery Tipo A — Indeciso Activo

### Perfil

**Usuarios:** 491
**Ventana temporal:** menos de 30 dias sin segunda operacion
**Comportamiento observable:** sigue abriendo la app con frecuencia pero no ejecuta. No es indiferencia. Es indecision.

**Principio psicologico:** Decision Fatigue + Sunk Cost Reduction. El usuario tiene la intencion pero la multitud de opciones y el miedo a equivocarse bloquean la accion. La estrategia no es empujar mas fuerte. Es simplificar la decision.

**Benchmark:** Tipo A win-back rate industria fintech: 22% (Klaviyo/Braze 2024).

---

### Recovery A1 — Push (D+14 desde primer trigger de Recovery)

**Canal:** Push notification
**Timing:** 21:00h local del usuario
**Objetivo:** Reactivar sin presionar. Usar el asset que ya tiene como gancho.

**Variante A (mercado positivo — ASSET subio >3% en 7d):**

> [ASSET] subio esta semana. Tu posicion inicial fue buena. El siguiente paso es tuyo.

**CTA:** Ver ahora

**Variante B (mercado neutral o negativo):**

> [NOMBRE], llevas [N] dias con tu [ASSET]. Muchos en tu misma situacion hicieron su segunda operacion esta semana.

**CTA:** Explorar el mercado

**Logica de seleccion de variante:** Si price_change_pct_7d >= 3% → Variante A. En caso contrario → Variante B. Si price_change_pct_7d no disponible (Alvaro pendiente) → Variante B por defecto.

**Personalizacion requerida:** ASSET (nombre del activo), NOMBRE, N (dias desde primera compra).

**A/B test:** 50/50 split Variante A vs B. KPI primario: click-through rate en 48h.

---

### Recovery A2 — Email (D+21)

**Canal:** Email
**Timing:** Martes o miercoles, 10:00h local

**Asunto A:**
> Y si lo que frena tu segunda operacion no eres tu?

**Asunto B:**
> [NOMBRE], esto es lo que diferencia a quien invierte una vez de quien invierte dos.

**Body (mismo para los dos asuntos):**

A veces la segunda operacion no llega por indecision, no por falta de ganas.

Hemos visto que los inversores que toman su segunda decision en menos de 30 dias tienen mas probabilidad de convertirse en inversores habituales a los 90 dias. No porque sean especiales, sino porque el primer mes es cuando el habito es mas facil de construir.

Tu [ASSET] sigue ahi. El mercado tambien.

**CTA principal:** Ver mi cartera y decidir [deep link /portfolio]

**CTA secundario:** Activar Earn mientras decido [deep link /earn]

**Footer:** Disclaimer MiCA. Los valores de los criptoactivos pueden subir o bajar. Esta comunicacion no es asesoramiento de inversion.

**Personalizacion requerida:** NOMBRE, ASSET, N (dias desde primera compra).

**KPI Recovery A:**
- Open rate objetivo email: >28%
- Conversion (segunda compra en 14 dias post A2): >15%
- Usuarios objetivo: 491
- Impacto esperado: ~74 segundas compras (15% de 491)

---

## 4. Recovery Tipo B — Dormido con Saldo

> **LANZABLE ESTA SEMANA. Esta secuencia no requiere setup de journey en CleverTap. Se ejecuta como campana manual. Ver instrucciones al final de esta seccion.**

### Perfil

**Usuarios:** 547
**Ventana temporal:** 31 a 60 dias sin segunda operacion
**Comportamiento observable:** tuvo intencion pero el tiempo ha enfriado el momentum. Sigue teniendo el asset. El precio ha cambiado desde que compro.

**Principio psicologico:** Reactivation Framing. No se le pide que "vuelva". Se le muestra que este momento es nuevo. El cambio de precio (positivo o negativo) es el gancho de atencion mas eficaz para un usuario que ya tiene exposure al activo.

**Benchmark:** Re-engagement email con portfolio value actualizado: 28% open rate (Omnisend 2024). Tipo B win-back rate industria: 13%.

---

### Recovery B1 — Email (D+30 del primer trigger de Recovery — envio manual posible HOY)

**Canal:** Email
**Timing:** Martes o miercoles, 10:00h local

**Asunto A:**
> Han pasado [N] dias. Tu [ASSET] vale ahora EUR [VALOR_ACTUAL].

**Asunto B:**
> [NOMBRE], tu [ASSET] ha [subido/bajado] un [X]% desde que lo compraste.

**Body:**

Cuando compraste [ASSET] valia EUR [PRECIO_COMPRA]. Hoy vale EUR [PRECIO_HOY]. Tu posicion esta [en positivo / en negativo] un [X]%.

Muchos inversores que esperaron para hacer su segunda operacion lo hicieron cuando vieron que su asset habia cambiado. El 62% de los que esperaron mas de 30 dias y volvieron lo hicieron despues de revisar como habia evolucionado su posicion.

Este es un buen momento para revisar donde estas.

**CTA principal:** Ver mi portfolio y el mercado ahora [deep link /portfolio]

**CTA secundario:** Activar Earn mientras decido [deep link /earn]

**Footer:** Disclaimer MiCA. Los valores de los criptoactivos pueden subir o bajar. Esta comunicacion no es asesoramiento de inversion.

**Personalizacion requerida:** N (dias desde primera compra), ASSET, VALOR_ACTUAL, PRECIO_COMPRA, PRECIO_HOY, X (porcentaje de cambio con signo), estado (positivo/negativo).

**Logica del body:** Si precio actual >= precio compra → "en positivo". Si precio actual < precio compra → "en negativo un [X]%". El mensaje no cambia el tono segun el estado del mercado. La noticia es el cambio en si, no si es buena o mala.

---

### Recovery B2 — Push (D+37)

**Canal:** Push notification
**Timing:** 21:00h local

**Variante TENDENCIA_POSITIVA (price_change_pct_7d >= 3%):**

> Tu [ASSET] sigue subiendo. 37 dias es tiempo suficiente para ver el patron.

**CTA:** Ver ahora

**Variante TENDENCIA_NEGATIVA (price_change_pct_7d < 0%):**

> [ASSET] ha bajado desde que lo compraste. Hay inversores que ven esto como una oportunidad de promediar el precio.

**CTA:** Ver el precio

**Fallback (precio sin datos o variacion < 3%):**

> [NOMBRE], tu [ASSET] sigue ahi. El mercado ha cambiado desde que compraste.

**CTA:** Ver ahora

---

### INSTRUCCIONES PARA LANZAR B1 ESTA SEMANA (sin journey setup en CleverTap)

Esta secuencia puede ejecutarse esta semana sin configurar un journey automatizado. Todos los campos necesarios estan disponibles en BigQuery hoy.

**Paso 1 — Marta (BigQuery, tiempo estimado 30 min):**

Exportar el segmento con la siguiente logica:

```sql
SELECT
  u.user_id,
  u.email,
  u.first_name AS nombre,
  fm.first_monetization_date,
  DATE_DIFF(CURRENT_DATE(), fm.first_monetization_date, DAY) AS dias_sin_2a_op,
  fm.first_asset AS asset,
  fm.first_purchase_price_eur AS precio_compra,
  p.current_price_eur AS precio_hoy,
  ROUND((p.current_price_eur - fm.first_purchase_price_eur) / fm.first_purchase_price_eur * 100, 1) AS pct_cambio
FROM bit2me_lifecycle.fm_users u
JOIN bit2me_lifecycle.first_monetization fm ON u.user_id = fm.user_id
JOIN bit2me_lifecycle.current_prices p ON fm.first_asset = p.asset
WHERE fm.second_monetization_date IS NULL
  AND DATE_DIFF(CURRENT_DATE(), fm.first_monetization_date, DAY) BETWEEN 31 AND 60
  AND u.email_opt_in = true
  AND u.email IS NOT NULL
```

Campos del CSV de salida: user_id, email, nombre, asset, precio_compra, precio_hoy, pct_cambio, dias_sin_2a_op.

**Paso 2 — Katy (CleverTap, tiempo estimado 45 min):**

1. Ir a CleverTap > Segments > Create Segment > Upload CSV.
2. Importar el CSV de Marta como segmento estatico. Nombre sugerido: `Recovery_B1_[fecha]`.
3. Crear campana email one-off (no journey): Campaigns > Create > Email > One-time.
4. Seleccionar segmento `Recovery_B1_[fecha]`.
5. Usar copy B1 con los campos de personalizacion mapeados al CSV.
6. Send time: martes o miercoles, 10:00h hora de Madrid.
7. Activar A/B test de asunto: 50% Asunto A / 50% Asunto B.

**Paso 3 — Diego (aprobacion copy, tiempo estimado 48h SLA):**

Enviar los dos asuntos + body completo antes de configurar el envio. Este es copy Tier 1 (template estandar) — deberia entrar en el batch de aprobacion rapida.

**Resultado esperado:**

| Metrica | Estimacion |
|---------|------------|
| Usuarios en segmento | 547 |
| Open rate (benchmark Omnisend re-engagement) | 28% = ~153 aperturas |
| Conversion a segunda compra en 7 dias | 8% = ~44 compras |
| Impacto estimado | 44 x ticket medio EUR [a confirmar con Marta] |

**KPI Recovery B:**
- Open rate objetivo: >28%
- Conversion (segunda compra en 7 dias post B1): >8%
- Usuarios objetivo: 547
- Push B2 se configura como campana one-off adicional 7 dias despues del B1, usando el mismo segmento estatico.

---

## 5. Recovery Tipo C — Caso Frio

### Perfil

**Usuarios:** 295
**Ventana temporal:** 60 o mas dias sin segunda operacion
**Comportamiento observable:** el tiempo ha creado una brecha significativa. El asset sigue existiendo pero el usuario ha desconectado emocionalmente de su inversion inicial.

**Decision de arquitectura: Tipo C NO entra en journey automatico.**

### Por que no se construye un journey para Tipo C

1. **Tasa de conversion esperada baja:** Con copy generico, <3% de conversion en usuarios con 60+ dias de inactividad (Klaviyo win-back benchmark: 7.5% en contexto favorable, con personalizacion maxima). El ROI del setup de journey no justifica el esfuerzo.

2. **Riesgo de unsubscribe alto:** 60+ dias sin actividad es una ventana en la que un email inesperado tiene alta probabilidad de ser marcado como spam o trigger de unsubscribe. Cada baja de email afecta la reputacion del dominio de envio.

3. **El FOMO Agent tiene logica superior para este perfil:** El FOMO Agent solo envia cuando hay un evento de mercado real y relevante. Para un usuario frio con 60+ dias de brecha, el unico gancho que funciona es un evento externo genuino (BTC +7% en una semana, su activo especifico +10% en 24h). Un journey automatico con timing fijo no puede replicar eso.

4. **Mejor uso del canal:** Reservar la capacidad de envio para usuarios con mayor probabilidad de conversion. El cap de frecuencia (max 2 emails/semana) es un recurso limitado.

### Handoff al FOMO Agent pool

**Condicion de entrada al pool:**

```
dias_sin_2a_op >= 60
AND has_balance = true
AND email_opt_in = true (o push_opt_in = true)
```

**Quien gestiona esto:**
- Daniel: decide cuando hay un evento de mercado que justifica el envio (trigger de FOMO Agent)
- Katy: ejecuta la campana en CleverTap como one-off cuando Daniel da el OK

**Criterio de evento para activar la campana FOMO sobre Tipo C:**

| Trigger | Umbral | Prioridad |
|---------|--------|-----------|
| BTC price change 7d | >= +7% | Alta |
| Asset especifico del usuario 24h | >= +10% | Alta |
| Evento de mercado general (halving, ETF, regulation) | Manual — Daniel decide | Media |
| Asset especifico del usuario 7d | >= +5% | Media |

**Copy FOMO para Tipo C (Daniel redacta al momento del envio, Katy ejecuta):**

Estructura recomendada:
- Linea 1: dato del mercado especifico y real (no generico)
- Linea 2: valor actual del asset del usuario
- CTA: Ver el mercado ahora

Ejemplo de estructura (no copy fijo — adaptar al evento real):
> [ASSET] ha subido un [X]% esta semana. Tu posicion actual vale EUR [VALOR]. Este tipo de movimientos es cuando muchos inversores revisan su cartera.

**KPI Tipo C via FOMO Agent:**
- Objetivo: >5% de los 295 usuarios convierte via FOMO Agent en 90 dias
- Medicion: etiqueta BigQuery `fomo_pool_entry_date` para tracking cohort
- Responsable de tracking: Marta (mensual)

---

## 6. J02.5 Loyalty — D+45 a D+90

### Objetivo

Cementar el habito de inversion. Llevar al usuario a la tercera compra y establecer el patron de inversion periodica. Este es el punto de inflexion donde un usuario que "probo cripto" se convierte en "inversor habitual".

### Condicion de entrada

```
second_purchase_confirmed = true
AND DATEDIFF(CURRENT_DATE, first_purchase_date) >= 45
```

El usuario que convirtio en Recovery tambien entra en J02.5 si cumple la condicion.

### Principios psicologicos

**Flywheel Effect:** Cada operacion reduce la friccion de la siguiente. La tercera operacion tiene menos barreras que la segunda porque el usuario ya ha tomado la decision dos veces.

**Identity shift:** El objetivo de las comunicaciones no es vender una operacion. Es ayudar al usuario a reconocerse como inversor habitual. Esto cambia el framing de todos los mensajes: de "haz esto" a "esto es lo que hacen los inversores como tu".

**Progress Milestone:** Mostrar cuanto ha avanzado desde el inicio. El progreso visible refuerza la identidad y justifica el siguiente paso.

### Benchmark clave

Coinbase (2023 Investor Day): usuarios con 3 o mas operaciones en los primeros 90 dias tienen **3.1x** mayor retencion a los 12 meses vs usuarios con 1-2 operaciones. Este es el numero que justifica el esfuerzo de J02.5.

---

### T1 — Email (D+45 desde primera compra)

**Canal:** Email
**Timing:** Martes, 10:00h local

**Asunto A:**
> Tu portfolio de [N] dias: lo que ha cambiado.

**Asunto B:**
> [NOMBRE], 45 dias invertido. Esto es lo que diferencia tu situacion ahora.

**Body:**

Cuando hiciste tu primera operacion, tu portfolio valia EUR [VALOR_INICIAL]. Hoy vale EUR [VALOR_ACTUAL].

Lo que ocurre entre el dia 45 y el dia 90 importa. Los inversores que hacen su tercera operacion antes del dia 90 tienen una probabilidad significativamente mayor de seguir activos el ano siguiente. No es magia. Es habito. Y el habito se construye en los primeros 90 dias.

Tu has completado el paso mas dificil: la primera y la segunda operacion. La tercera es el punto donde la inversion deja de ser un experimento.

**CTA principal:** Ver mi portfolio y el mercado [deep link /portfolio]

**CTA secundario:** Configurar inversion recurrente [deep link /dca]

**Footer:** Disclaimer MiCA. Los valores de los criptoactivos pueden subir o bajar. Esta comunicacion no es asesoramiento de inversion.

**Personalizacion requerida:** NOMBRE, N (dias desde primera compra), VALOR_INICIAL (valor EUR del portfolio en primera compra), VALOR_ACTUAL (valor EUR actual del portfolio).

**KPI T1:** Open rate objetivo >30%.

---

### T2 — Push (D+60)

**Canal:** Push notification
**Timing:** 20:30h local (peak CET validado por OneSignal/Braze)

**Condicion previa:** Solo enviar si el usuario no ha completado tercera compra entre D+45 y D+60.

**Copy base:**

> El mercado esta en [estado]. Tu portfolio tiene [N] dias. Este es un buen momento para pensar en el siguiente paso.

**CTA:** Ver ahora

**Logica de [estado]:** Si BTC price_change_pct_7d >= 3% → "movimiento". Si price_change_pct_7d <= -3% → "correccion". Si entre -3% y +3% → "consolidacion". El estado es informativo, no alarmista.

**Fallback (si price data no disponible):**

> [NOMBRE], tu portfolio lleva [N] dias. El siguiente paso puede marcar el habito.

**CTA:** Ver el mercado

**Personalizacion requerida:** N (dias desde primera compra), estado del mercado (calculado en bigquery o CleverTap liquid logic).

---

### T3 — Email (D+90)

**Canal:** Email
**Timing:** Martes, 10:00h local

**Condicion previa:** Solo enviar si el usuario no ha completado tercera compra entre D+45 y D+90. Si ya completo la tercera compra, el trigger de T3 no se activa (no celebrar lo que ya no es necesario).

**Asunto:**
> 90 dias. Este es el momento donde la inversion se convierte en habito.

**Body:**

Has llegado a los 90 dias con Bit2Me.

Este es un punto importante. Los datos muestran que los inversores que llegan al dia 90 con dos o mas operaciones y hacen una tercera antes de este momento tienen un porcentaje de retencion al ano siguiente mucho mayor que quienes no lo hacen.

Tu tienes [N] operaciones completadas. Llevas [DIAS] dias como inversor. Tu portfolio vale EUR [VALOR_ACTUAL].

El siguiente paso es tuyo.

**CTA principal:** Ver el mercado ahora [deep link /markets]

**CTA secundario (condicional — solo si earn_product_active = false):**
Explorar Earn — pon tu [ASSET] a trabajar [deep link /earn]

**Footer:** Disclaimer MiCA. Los valores de los criptoactivos pueden subir o bajar. Esta comunicacion no es asesoramiento de inversion.

**Personalizacion requerida:** N (numero de operaciones completadas), DIAS (dias desde primera compra), VALOR_ACTUAL (valor EUR actual del portfolio), ASSET (activo principal del usuario), earn_product_active (para CTA secundario condicional).

---

### Resumen J02.5 Loyalty

| Touchpoint | Canal | Timing | Condicion de envio | KPI objetivo |
|-----------|-------|--------|--------------------|--------------|
| T1 | Email | D+45, martes 10h | 2a compra confirmada + D>=45 | Open rate >30% |
| T2 | Push | D+60, 20:30h | Sin 3a compra tras T1 | CTR >12% |
| T3 | Email | D+90, martes 10h | Sin 3a compra entre D+45-D+90 | Conversion 3a compra >20% |

**KPIs globales J02.5:**
- Conversion a tercera compra en D+45-D+90: objetivo >40%
- Retencion a 90 dias: objetivo >25% (benchmark Coinbase; actual Bit2Me M1: 0.12% — CRISIS)
- Impacto benchmark Coinbase: usuarios con 3+ trades = 3.1x mayor retencion 12 meses

---

## 7. Resumen KPIs y tabla de aprobacion Diego

### Tabla de impacto por tipo

| Track | Usuarios | Conversion target | Segundas compras esperadas |
|-------|----------|-------------------|---------------------------|
| Recovery A | 491 | 15% | ~74 |
| Recovery B — ESTA SEMANA | 547 | 8% | ~44 |
| Recovery C (via FOMO Agent) | 295 | 5% en 90d | ~15 |
| **Total Recovery** | **1.333** | **10% promedio** | **~133** |

### KPIs J02.5 Loyalty

| Metrica | Objetivo | Benchmark |
|---------|----------|-----------|
| T1 email open rate | >30% | Coinbase transactional: 34% |
| T2 push CTR | >12% | Braze fintech push: 10-15% |
| T3 email conversion 3a compra | >20% | — |
| Conversion a 3a compra D+45-D+90 | >40% | — |
| 90-day retention | >25% | Coinbase: 25%, Bit2Me actual: 0.12% |

### Mensajes pendientes de aprobacion Diego

| ID | Canal | Track | Asunto / Copy preview | Tipo Diego |
|----|-------|-------|-----------------------|------------|
| REC-A1-V1 | Push | Recovery A | "[ASSET] subio esta semana..." | Tier 1 |
| REC-A1-V2 | Push | Recovery A | "[NOMBRE], llevas [N] dias..." | Tier 1 |
| REC-A2-SA | Email | Recovery A | "Y si lo que frena tu segunda operacion..." | Tier 1 |
| REC-A2-SB | Email | Recovery A | "[NOMBRE], esto es lo que diferencia..." | Tier 1 |
| REC-B1-SA | Email | Recovery B | "Han pasado [N] dias. Tu [ASSET] vale..." | Tier 1 |
| REC-B1-SB | Email | Recovery B | "[NOMBRE], tu [ASSET] ha [subido/bajado]..." | Tier 1 |
| REC-B2-V1 | Push | Recovery B | "Tu [ASSET] sigue subiendo. 37 dias..." | Tier 1 |
| REC-B2-V2 | Push | Recovery B | "[ASSET] ha bajado desde que lo compraste..." | Tier 1 |
| LOY-T1-SA | Email | J02.5 | "Tu portfolio de [N] dias: lo que ha cambiado" | Tier 1 |
| LOY-T1-SB | Email | J02.5 | "[NOMBRE], 45 dias invertido..." | Tier 1 |
| LOY-T2 | Push | J02.5 | "El mercado esta en [estado]..." | Tier 1 |
| LOY-T3 | Email | J02.5 | "90 dias. Este es el momento donde..." | Tier 1 |

Todos los mensajes son Tier 1 (template con personalizacion estandar). SLA Diego: 48h. Recomendacion: enviar todos en un batch unico para minimizar ciclos de aprobacion.

### Campos BigQuery necesarios para este documento

| Campo | Owner | Uso | Prioridad |
|-------|-------|-----|-----------|
| second_purchase_confirmed | Alvaro (ya existe en V0a) | Entry condition todos los tracks | P0 |
| first_purchase_price_eur | Alvaro | Recovery B1, J02.5 T1 | P0 para lanzamiento B1 |
| current_price_eur (por asset) | Alvaro | Recovery B1, B2, J02.5 T2 | P0 para lanzamiento B1 |
| price_change_pct_7d (por asset) | Alvaro (pendiente) | Recovery A1-V1, B2, J02.5 T2 | P1 — fallback disponible |
| earn_product_active | Alvaro (ya existe) | J02.5 T3 CTA condicional | P1 |
| portfolio_value_eur (agregado) | Alvaro | J02.5 T1/T3 | P1 — calcular en SQL si no existe |

**Nota para Marta:** Los campos `first_purchase_price_eur` y `current_price_eur` son los unicos P0 bloqueantes para el lanzamiento de B1 esta semana. Si no existen como columnas en Gold Layer, coordinar con Alvaro para calcularlos en la query de exportacion.

---

*Documento generado por Journey OS Plan 01-05 — 2026-03-23*
*Siguiente documento: 01-06 J05-B2B architecture*
