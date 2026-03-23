# J02 — Jira Backlog: Sistema de Journey Post Primera Monetizacion

**Epic:** J02 — Sistema de Journey Post Primera Monetizacion
**Epic Owner:** Daniel Ferraro
**Descripcion del Epic:** Construir el sistema completo de journey automatico para usuarios que completan su primera operacion. Hub + 8 Spokes + Recovery + Loyalty + LatAm + B2B. Objetivo: tasa de segunda operacion >50% en D+30, M1 retention de 0.12% a >25%.
**Diagrama de referencia:** `docs/plans/2026-03-23-j02-diagram.mmd`
**Especificaciones:** `docs/plans/2026-03-23-j02-hub-spain.md`, `docs/plans/2026-03-23-j02-spokes-01-05.md`, `docs/plans/2026-03-23-j02-recovery-loyalty.md`

---

## Sprint 1 — 24 Mar al 4 Abr
**Foco:** Hub setup + Diego approval batch + Recovery B manual + Holdout
**Bloqueantes criticos:** Diego copia (J02-20), Alvaro BigQuery (J02-01, J02-05)

---

### TICKET: J02-01
**Titulo:** Configurar segmento FM en BigQuery y exponer propiedades en CleverTap
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Alvaro
**Estimacion:** 4h

**Descripcion:**
El Journey J02 se activa con el evento `first_monetization`. Este evento debe estar disponible en BigQuery Gold Layer y mapeado como evento de usuario en CleverTap. Sin esto, ningun touchpoint del Hub puede activarse.

Exponer como propiedades de usuario en CleverTap: `first_monetization_date`, `second_purchase_confirmed`, `dias_sin_2a_op`, `first_asset`, `earn_product_active`.

Dependencia: antes de J02-02, J02-03.

**Criterios de aceptacion:**
- [ ] Evento `first_monetization` disponible en BigQuery `bit2me_lifecycle` schema
- [ ] Evento mapeado en CleverTap como trigger de Journey
- [ ] Propiedades `first_monetization_date`, `second_purchase_confirmed`, `dias_sin_2a_op` visibles en CleverTap user profile
- [ ] `first_asset`, `earn_product_active` visibles en CleverTap user profile
- [ ] Test con 10 usuarios reales: evento dispara correctamente en CleverTap

**Bloqueado por:** ninguno (P0 inicial)

---

### TICKET: J02-02
**Titulo:** Configurar evento first_monetization como entry trigger del Journey J02 en CleverTap
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
Crear el Journey J02 en CleverTap con el evento `first_monetization` como entry trigger. Configurar las condiciones de parada: exit si `second_purchase_confirmed` = true, exit a Recovery si D+30 sin conversion. Configurar la logica de holdout (excluir 10% de usuarios) y el flag `spoke_active`.

Dependencia: J02-01 (Alvaro debe haber entregado el evento).

**Criterios de aceptacion:**
- [ ] Journey J02 creado en CleverTap con estado DRAFT (no publicar hasta J02-20 aprobado)
- [ ] Entry trigger: evento `first_monetization`
- [ ] Exit condition 1: `second_purchase_confirmed` = true
- [ ] Exit condition 2: D+30 sin conversion → rama Recovery
- [ ] Holdout configurado: 10% excluido del journey (segmento HOLDOUT_J02)
- [ ] Flag `spoke_active` configurado como propiedad de usuario

**Bloqueado por:** J02-01

---

### TICKET: J02-03
**Titulo:** Construir S0 in-app banner en CleverTap — D+0 post-compra
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
S0 es el touchpoint de mayor impacto potencial: se activa 60 segundos post-compra, en el momento de maxima motivacion del usuario. Benchmarking Binance: usuarios que configuran alerta de precio convierten 4.1x mas a segunda compra.

Copy: Titulo "Tu primera operacion esta lista." + Body "[NOMBRE], acabas de comprar [CANTIDAD] [ASSET]. Configura una alerta para saber cuando moverlo." + CTA "Activar alerta" deep link `/alerts/create?asset=[ASSET]`

**Criterios de aceptacion:**
- [ ] In-App banner creado en CleverTap con personalizacion NOMBRE, CANTIDAD, ASSET
- [ ] Timing: delay de 60s desde evento `first_monetization`
- [ ] Deep link CTA: `/alerts/create?asset=[ASSET]` funciona en iOS y Android
- [ ] Exit condition: si usuario activa alerta → marca conversion S0 y salta S0.5
- [ ] Preview aprobado por Daniel antes de activar

**Bloqueado por:** J02-01, J02-20 (aprobacion Diego)

---

### TICKET: J02-04
**Titulo:** Construir S0.5 in-app modal de alerta de precio en CleverTap — D+0 fallback
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
S0.5 se activa 2 minutos despues de S0 si el usuario NO configuro la alerta. Usa el dato de precio en tiempo real del asset comprado. Si `price_change_pct_24h` no esta disponible (Alvaro pendiente), usar copia neutral de fallback.

Principio: Peak-End Rule. El usuario sigue en la app, la motivacion sigue alta, el siguiente prompt debe ser especifico y accionable.

**Criterios de aceptacion:**
- [ ] Modal creado con delay de 2min post S0 si S0 no convirtio
- [ ] Personalizacion ASSET, PRECIO_ACTUAL funciona si dato disponible
- [ ] Copia fallback neutral configurada cuando `price_change_pct_24h` no disponible
- [ ] CTA deep link `/alerts/create?asset=[ASSET]` funciona
- [ ] No aparece si usuario ya activo alerta en S0

**Bloqueado por:** J02-01, J02-20 (aprobacion Diego)

---

### TICKET: J02-05
**Titulo:** Configurar evento price_change_pct_24h en tiempo real para S0.5 y S1
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Alvaro
**Estimacion:** 6h

**Descripcion:**
El touchpoint S0.5 (alerta precio) y S1 (push D+1) usan el dato de variacion de precio en 24h del asset del usuario para personalizar el copy. Sin este dato, ambos usan copia neutral (fallback ya documentado en hub-spain.md).

Este evento es P0 porque desbloquea la personalizacion dinamica de los touchpoints con mayor probabilidad de conversion. Fuente: CoinGecko API o datos internos de precio.

**Criterios de aceptacion:**
- [ ] Campo `price_change_pct_24h` disponible por asset en BigQuery (actualizado cada hora minimo)
- [ ] Campo mapeado como propiedad de evento en CleverTap
- [ ] Logica de variante en S1: si pct >= 3% → Variante SUBIDA, si <= -3% → Variante BAJADA, resto → NEUTRAL
- [ ] Fallback documentado y configurado en CleverTap para cuando el campo no llega
- [ ] Test: simular 3 escenarios (subida, bajada, neutral) y verificar variante correcta

**Bloqueado por:** ninguno (trabajo de infra independiente)

---

### TICKET: J02-06
**Titulo:** Construir S1 push con 3 variantes de mercado en CleverTap — D+1 21:00h
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy
**Estimacion:** 3h

**Descripcion:**
S1 es el primer push del Hub, 24 horas post-compra. Opera con logica de mercado: variante SUBIDA si asset sube >3% en 24h, variante BAJADA si baja >3%, variante NEUTRAL como fallback. El timing 21:00h local esta validado por datos OneSignal/Braze como peak de engagement fintech.

**Criterios de aceptacion:**
- [ ] Push S1 creado con 3 variantes en CleverTap
- [ ] Timing: D+1 desde first_monetization, 21:00h hora local del usuario
- [ ] Personalizacion NOMBRE, ASSET funcionando en las 3 variantes
- [ ] Logica de seleccion de variante conectada a `price_change_pct_24h` (o fallback NEUTRAL)
- [ ] No se envia si usuario ya realizo segunda compra

**Bloqueado por:** J02-01, J02-05, J02-20 (aprobacion Diego)

---

### TICKET: J02-07
**Titulo:** Construir S2 in-app full-screen card en CleverTap — D+3 primer login
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
S2 se activa en el primer login del usuario en D+3, si no ha realizado segunda compra. Es una full-screen card (no banner). Usa endowment framing: el usuario ya tiene un asset, se le muestra el potencial de lo que tiene, no se le pide que "compre mas".

**Criterios de aceptacion:**
- [ ] Full-screen in-app card creada en CleverTap
- [ ] Trigger: primer session en D+3 (no por tiempo fijo, por evento de login)
- [ ] No aparece si `second_purchase_confirmed` = true
- [ ] Personalizacion NOMBRE, ASSET, VALOR_ACTUAL funcionando
- [ ] CTA deep link a portfolio del usuario

**Bloqueado por:** J02-01, J02-20 (aprobacion Diego)

---

### TICKET: J02-08
**Titulo:** Escribir y enviar a Diego batch de aprobacion copy Hub (S0 a S4) — CRITICO
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Daniel + Diego
**Estimacion:** 3h prep Daniel + 48h SLA Diego

**Descripcion:**
Diego debe aprobar TODOS los copies antes de que Katy publique cualquier touchpoint. Este ticket es CAMINO CRITICO. Sin aprobacion Diego, ningun mensaje puede salir al aire. Enviar todos los copies del Hub en un unico batch para maximizar velocidad (evitar idas y vueltas).

Batch Hub incluye: S0, S0.5, S1 (3 variantes), S2, S3 (3 asuntos), S4 (2 variantes). Total: 17 piezas de copy para revision.

**Criterios de aceptacion:**
- [ ] Daniel prepara tabla de batch con: ID, canal, copy completo, disclaimer MiCA donde aplique
- [ ] Batch enviado a Diego con fecha limite de respuesta (48h SLA)
- [ ] Diego confirma aprobacion o solicita cambios en <= 48h
- [ ] Todos los cambios solicitados por Diego implementados antes de publicar Journey
- [ ] Diego firma aprobacion escrita (Lark o email) antes de publicar

**Bloqueado por:** ninguno (Daniel puede preparar batch ahora)

---

### TICKET: J02-09
**Titulo:** Construir S3 email con disclaimer MiCA en CleverTap — D+5 10:00h
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
S3 es el unico touchpoint del Hub que requiere disclaimer MiCA por ser email (regulacion europea). Timing D+5, martes o miercoles 10:00h local. Tres variantes de asunto para A/B test. El body usa framing de identidad inversor con benchmark real (39.6% conversion D+0).

**Criterios de aceptacion:**
- [ ] Email S3 creado en CleverTap con 3 variantes de asunto
- [ ] Footer MiCA incluido: "Los valores de los criptoactivos pueden subir o bajar. Esta comunicacion no es asesoramiento de inversion."
- [ ] Timing: D+5 10:00-11:00h local del usuario
- [ ] Personalizacion NOMBRE, ASSET, N (dias) funcionando
- [ ] A/B test configurado: 3 asuntos en split igualitario
- [ ] No se envia si `second_purchase_confirmed` = true

**Bloqueado por:** J02-01, J02-08 (aprobacion Diego)

---

### TICKET: J02-10
**Titulo:** Construir S4 push D+7 con variantes de mercado en CleverTap
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
S4 es el ultimo touchpoint del Hub antes del check D+30. Push a las 21:00h del D+7. Dos variantes: mercado positivo (asset sube >3%) y neutral/negativo. Si el usuario no convierte tras S4, entra en check D+30 y classification Recovery.

**Criterios de aceptacion:**
- [ ] Push S4 creado con 2 variantes (positivo / neutral)
- [ ] Timing: D+7 desde first_monetization, 21:00h hora local
- [ ] Logica variante conectada a `price_change_pct_24h` con fallback neutral
- [ ] No se envia si `second_purchase_confirmed` = true
- [ ] Despues de S4: trigger de check D+30 activo en CleverTap

**Bloqueado por:** J02-01, J02-05, J02-08 (aprobacion Diego)

---

### TICKET: J02-11
**Titulo:** Configurar logica de clasificacion Tipo A/B/C post-D+30 en BigQuery y CleverTap
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P1
**Owner:** Alvaro + Katy
**Estimacion:** 5h (3h Alvaro BigQuery + 2h Katy CleverTap logic)

**Descripcion:**
En D+30, si no hay segunda compra, el sistema debe clasificar automaticamente al usuario como Tipo A (<30d), Tipo B (31-60d) o Tipo C (60+d) y enrutarlo al Recovery track correspondiente. Tipo B debe poder ejecutarse como campana manual esta semana sin esperar el journey automatico.

Logica: `dias_sin_2a_op < 30` → Tipo A, `BETWEEN 31 AND 60` → Tipo B, `>= 60` → Tipo C.

**Criterios de aceptacion:**
- [ ] Alvaro: campo `dias_sin_2a_op` calculado y disponible en BigQuery (DATE_DIFF desde first_monetization_date)
- [ ] Alvaro: segmentos estaticos exportables por tipo disponibles via SQL (ver query en recovery-loyalty.md)
- [ ] Katy: logica de ramificacion en CleverTap post-D+30: 3 ramas (A, B, C)
- [ ] Tipo C: usuarios entran en segmento FOMO_POOL con campo `fomo_pool_entry_date`
- [ ] Test: verificar con 10 usuarios en cada tipo que el enrutamiento es correcto

**Bloqueado por:** J02-01

---

### TICKET: J02-12
**Titulo:** Lanzar Recovery B1 como campana manual ESTA SEMANA — 547 usuarios Tipo B
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy + Marta
**Estimacion:** 1h Marta (BigQuery export) + 1h Katy (CleverTap one-off) + 48h Diego

**Descripcion:**
ACCION URGENTE. 547 usuarios llevan entre 31 y 60 dias sin segunda compra. Tienen saldo. Este email puede recuperar ~44 compras esta semana usando datos ya disponibles en BigQuery. NO requiere configurar el journey automatico. Se ejecuta como campana one-off.

Proceso: Marta exporta CSV con SQL de recovery-loyalty.md (seccion INSTRUCCIONES LANZAR B1) → Katy sube CSV como segmento estatico en CleverTap → Katy configura email one-off → Diego aprueba copy → envio martes o miercoles 10:00h.

Copy B1: Asunto A "Han pasado [N] dias. Tu [ASSET] vale ahora EUR [VALOR_ACTUAL]." Asunto B: "[NOMBRE], tu [ASSET] ha [subido/bajado] un [X]% desde que lo compraste." Body: portfolio value actualizado con framing neutro sobre el cambio de precio.

**Criterios de aceptacion:**
- [ ] Marta: SQL ejecutado, CSV con campos (user_id, email, nombre, asset, precio_compra, precio_hoy, pct_cambio, dias_sin_2a_op) exportado y validado
- [ ] Marta: campos `first_purchase_price_eur` y `current_price_eur` confirmados disponibles en BigQuery (P0 blocker)
- [ ] Katy: segmento estatico `Recovery_B1_[fecha]` creado en CleverTap con CSV importado
- [ ] Katy: campana email one-off configurada con copy B1 y A/B test de asunto (50/50)
- [ ] Diego: copy aprobado (batch con J02-08 para ahorrar ciclos)
- [ ] Envio programado martes o miercoles 10:00h Madrid
- [ ] KPIs configurados en CleverTap: open rate y conversion (segunda compra en 7d) trackeables

**Bloqueado por:** campos BigQuery (Marta confirmar con Alvaro), aprobacion Diego (J02-08 batch)

---

### TICKET: J02-20
**Titulo:** Aprobar batch de copies Hub con Diego — 17 piezas CAMINO CRITICO
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Diego + Daniel
**Estimacion:** 3h prep + 48h SLA Diego

**Descripcion:**
CAMINO CRITICO. Sin este ticket completado, Katy no puede publicar ningun touchpoint del Hub (J02-03 a J02-10 bloqueados). Todos los copies son Tier 1 (template con personalizacion estandar) — Diego puede revisarlos en batch en una sola sesion.

Incluye: S0 banner (1), S0.5 modal (1), S1 push x3 variantes, S2 in-app card (1), S3 email x3 asuntos + body (1 body), S4 push x2 variantes. Tambien incluir Recovery B1 (J02-12) para no abrir otro ciclo de revision.

**Criterios de aceptacion:**
- [ ] Daniel prepara tabla batch con columnas: ID, canal, copy completo, disclaimer MiCA si aplica, tipo Diego
- [ ] Tabla enviada a Diego con fecha limite clara (48h SLA)
- [ ] Diego aprueba o solicita cambios en <= 48h
- [ ] Todos los cambios implementados por Katy antes de publicar
- [ ] Aprobacion documentada por escrito (Lark thread o email)
- [ ] Recovery B1 incluido en el mismo batch

**Bloqueado por:** Daniel debe preparar tabla (no requiere nada tecnico — puede hacerse hoy)

---

### TICKET: J02-22
**Titulo:** Configurar holdout 10% en CleverTap — grupo control global J02
**Epic:** J02
**Sprint:** Sprint 1
**Prioridad:** P0
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
10% de los usuarios que disparan `first_monetization` deben ser excluidos de TODOS los journeys y campanas del sistema J02 (Hub + Spokes + Recovery + Loyalty). Este grupo control permite medir el impacto real del sistema completo via Welch t-test.

Asignacion aleatoria en el momento del evento `first_monetization`. El holdout debe ser estable (mismos usuarios siempre excluidos, no re-aleatorizado).

**Criterios de aceptacion:**
- [ ] Segmento HOLDOUT_J02 creado en CleverTap con 10% aleatorio de usuarios FM
- [ ] Excluido de: Journey J02, todos los Spokes, Recovery A/B, Loyalty J02.5
- [ ] Exclusion verificada: enviar test con 100 usuarios y confirmar 10% no recibe nada
- [ ] Marta: campo `holdout_j02 = true` disponible en BigQuery para analisis posterior
- [ ] Metodologia documentada: Welch t-test, alpha=0.05, metrica primaria segunda_compra_30d

**Bloqueado por:** J02-01

---

## Sprint 2 — 5 Abr al 18 Abr
**Foco:** Todos los Spokes + A/B tests + LatAm WhatsApp setup
**Prerequisito:** Hub publicado y en produccion (todos los tickets Sprint 1 completos)

---

### TICKET: J02-13
**Titulo:** Construir SP-01 Earn secuencia 3 emails en CleverTap
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P0
**Owner:** Katy + Daniel
**Estimacion:** 4h

**Descripcion:**
SP-01 Earn es el Spoke con mayor impacto monetario del sistema. Segmento elegible: hasta 72.4k usuarios con EUR 19.5M AUC dormant. 3 emails en 10 dias (E1 dia 0, E2 dia 4, E3 dia 10 si no convirtio). El A/B test de framing (loss vs gain) esta en J02-25 — este ticket es la construccion del spoke en CleverTap.

Trigger: `balance_idle_days >= 7 AND earn_product_active = false`. Exit: evento `earn_activation_confirmed` o expiracion 14 dias.

**Criterios de aceptacion:**
- [ ] Journey SP-01 creado en CleverTap con trigger `balance_idle_days >= 7 AND earn_product_active = false`
- [ ] 3 emails configurados: E1 (dia 0), E2 (dia 4), E3 (dia 10)
- [ ] Personalizacion: NOMBRE, ASSET, BALANCE_EUR, APY_ACTUAL funcionando en cada email
- [ ] Exit condition: `earn_activation_confirmed` → salida inmediata sin enviar emails restantes
- [ ] Exit por expiracion: 14 dias sin conversion
- [ ] Hub pausa cuando SP-01 activo (`spoke_active` flag)
- [ ] Coordinar con J02-25: A/B test de framing configurado sobre este spoke

**Bloqueado por:** J02-01 (campos BigQuery), J02-21 (aprobacion Diego Spokes)

---

### TICKET: J02-14
**Titulo:** Construir SP-02 Pro Upgrade secuencia 2 emails en CleverTap
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 3h

**Descripcion:**
SP-02 Pro targeting usuarios que han generado suficiente volumen para beneficiarse de tarifa Pro. Trigger: `cumulative_fee_spend >= umbral` (umbral exacto a definir con Alvaro). 2 emails en 7 dias. Fee-savings framing validado por benchmarking Kraken (+31% conversion).

**Criterios de aceptacion:**
- [ ] Journey SP-02 creado con trigger en `cumulative_fee_spend` (Alvaro confirma campo disponible)
- [ ] 2 emails: E1 (dia 0 fee savings anchor), E2 (dia 7 urgencia limitada)
- [ ] Personalizacion: NOMBRE, FEE_PAGADO_MES, AHORRO_POTENCIAL_PRO funcionando
- [ ] Exit condition: upgrade Pro confirmado → salida inmediata
- [ ] Duracion maxima spoke: 14 dias

**Bloqueado por:** J02-01, J02-21 (aprobacion Diego), umbral fee_spend confirmado por Alvaro

---

### TICKET: J02-15
**Titulo:** Construir SP-03 DCA secuencia 2 emails en CleverTap
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 3h

**Descripcion:**
SP-03 DCA targeting usuarios sin inversion periodica activa. Copy: "cuenta de ahorro en USD" (no "inversion periodica" — framing validado para LatAm y Spain). Trigger: `no_dca_active = true AND second_purchase_confirmed = true`. 2 emails en 7 dias.

**Criterios de aceptacion:**
- [ ] Journey SP-03 creado con trigger `no_dca_active = true AND second_purchase_confirmed = true`
- [ ] 2 emails: E1 (DCA framing ahorro USD), E2 (social proof + CTA)
- [ ] Personalizacion: NOMBRE, ASSET funcionando
- [ ] Exit condition: DCA configurado confirmado → salida inmediata
- [ ] Duracion maxima spoke: 14 dias

**Bloqueado por:** J02-01, J02-21 (aprobacion Diego)

---

### TICKET: J02-16
**Titulo:** Construir SP-04 Diversify secuencia 2 emails en CleverTap
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 3h

**Descripcion:**
SP-04 Diversify targeting usuarios con portfolio de un solo activo. Trigger: `portfolio_assets == 1 AND second_purchase_confirmed = true`. Framing: riesgo de concentracion (endowment protection). 2 emails en 7 dias.

**Criterios de aceptacion:**
- [ ] Journey SP-04 creado con trigger `portfolio_assets == 1 AND second_purchase_confirmed = true`
- [ ] Campo `portfolio_assets` disponible en CleverTap (confirmar con Alvaro)
- [ ] 2 emails: E1 (riesgo concentracion), E2 (diversificacion en 3 clics CTA)
- [ ] Exit condition: segundo activo comprado → salida inmediata
- [ ] Duracion maxima spoke: 14 dias

**Bloqueado por:** J02-01, J02-21 (aprobacion Diego)

---

### TICKET: J02-17
**Titulo:** Construir SP-05 Referidos email post-segunda compra en CleverTap
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P2
**Owner:** Katy
**Estimacion:** 2h

**Descripcion:**
SP-05 Referidos tiene una regla de negocio CRITICA: NUNCA puede activarse antes de que `second_purchase_confirmed` = true. Activar el programa de referidos con un usuario que solo tiene una compra viola el principio de comportamiento economico (pedirle que refiera antes de que el mismo este comprometido aumenta el riesgo de abandono).

1 email, timing D+14 post-segunda compra. Framing: comunidad de inversores.

**Criterios de aceptacion:**
- [ ] Journey SP-05 creado con trigger ESTRICTO: `second_purchase_confirmed = true AND days_since_second_purchase >= 14`
- [ ] NUNCA activar con solo primera compra — verificar logica en QA
- [ ] 1 email con link de referido unico del usuario
- [ ] Personalizacion: NOMBRE, REF_LINK funcionando
- [ ] Exit condition: primer referido completado

**Bloqueado por:** J02-01, J02-21 (aprobacion Diego)

---

### TICKET: J02-18
**Titulo:** Configurar WhatsApp Business API para LatAm — prerequisito J02-LATAM
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P1
**Owner:** Producto + Katy
**Estimacion:** 8h (incluyendo aprobacion Meta 48-72h)

**Descripcion:**
WhatsApp es el canal PRIMARIO para todos los touchpoints S1 y S4 en mercados LatAm (VE, MX, CO, AR). Sustituye al push notification. Meta requiere pre-aprobacion de templates (48-72h proceso). Katy debe iniciar este proceso INMEDIATAMENTE — es el bloqueante mas largo del Sprint 2.

Se necesitan 22 templates de WhatsApp pre-aprobados por Meta. Campo `whatsapp_marketing_opt_in` debe existir en CleverTap (Alvaro P1).

**Criterios de aceptacion:**
- [ ] WhatsApp Business API integrada en CleverTap
- [ ] Campo `whatsapp_marketing_opt_in` disponible como propiedad de usuario (Alvaro)
- [ ] 22 templates enviados a Meta para pre-aprobacion (Katy inicia proceso en Sprint 1 si es posible)
- [ ] Al menos 8 templates aprobados por Meta antes del inicio de Sprint 2
- [ ] Fallback configurado: si WA no entregado en 2h → trigger push notification
- [ ] Frecuencia cap: max 1 WhatsApp/semana por usuario configurado en CleverTap

**Bloqueado por:** Alvaro (`whatsapp_marketing_opt_in` field), Meta approval process (iniciar cuanto antes)

---

### TICKET: J02-21
**Titulo:** Aprobar batch copies Spokes con Diego — SP-01 a SP-05 CAMINO CRITICO Sprint 2
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P0
**Owner:** Diego + Daniel
**Estimacion:** 3h prep + 48h SLA Diego

**Descripcion:**
Todos los copies de Spokes deben estar aprobados por Diego antes de que Katy publique los journeys en Sprint 2. Enviar en batch unico para minimizar ciclos. Spokes son Tier 1 (template con personalizacion). Incluir tambien Recovery A (A1 push + A2 email) si no entro en batch Sprint 1.

Incluye: SP-01 E1/E2/E3, SP-02 E1/E2, SP-03 E1/E2, SP-04 E1/E2, SP-05 E1. Total: 11 piezas.

**Criterios de aceptacion:**
- [ ] Daniel prepara batch con copies de SP-01 a SP-05 + Recovery A
- [ ] Batch enviado al inicio de Sprint 2 con fecha limite Diego
- [ ] Diego aprueba en <= 48h
- [ ] Todos los cambios implementados en CleverTap antes de publicar spokes
- [ ] Aprobacion documentada por escrito

**Bloqueado por:** copies finalizados (dependencia logica con J02-13 a J02-17)

---

### TICKET: J02-25
**Titulo:** Configurar A/B test SP-01 Earn — loss framing vs gain framing
**Epic:** J02
**Sprint:** Sprint 2
**Prioridad:** P0
**Owner:** Daniel + Katy
**Estimacion:** 3h

**Descripcion:**
Este es EL test mas importante del sistema J02. Loss aversion (Kahneman) predice que el framing de perdida convierte mejor que el framing de ganancia. Hipotesis: "Tu BTC pierde X EUR/mes sin Earn" convierte mas que "Tu BTC puede generar X EUR/mes".

**Hipotesis:** El copy de loss framing en E1 de SP-01 genera una tasa de activacion de Earn mayor que el copy de gain framing, con una diferencia minima detectable del 20% (de base 6% a 7.2%).

**Especificaciones del test:**
- Variante A (Control — Gain): "Tu BTC puede generar EUR [X] al mes con Earn. Activalo ahora."
- Variante B (Treatment — Loss): "Tu BTC pierde EUR [X] al mes sin Earn. Cada dia sin activarlo es dinero que no llega."
- Split: 50/50
- Metrica primaria: tasa de activacion de Earn en 14 dias (evento `earn_activation_confirmed`)
- Metrica secundaria: CTR en E1
- Tamano de muestra: 600 usuarios por variante (1.200 total) — calculo de poder estadistico para detectar 20% de lift con alpha=0.05, poder=0.80
- Duracion estimada: 3-4 semanas para alcanzar tamano de muestra
- Analisis: Welch t-test sobre tasa de conversion, IC 95%
- Owner analisis: Marta + Daniel

**Criterios de aceptacion:**
- [ ] A/B test configurado en CleverTap sobre E1 de SP-01 (50/50 split)
- [ ] Ambas variantes aprobadas por Diego (incluir en batch J02-21)
- [ ] Tracking de `earn_activation_confirmed` como conversion event en CleverTap
- [ ] Tamano de muestra alcanzado antes de declarar ganador
- [ ] Duracion minima: 2 semanas (no detener antes aunque una variante parezca ganar)
- [ ] Resultado documentado en Notion con metodologia completa

**Bloqueado por:** J02-13 (spoke construido), J02-21 (aprobacion Diego)

---

## Sprint 3 — 19 Abr al 2 May
**Foco:** LatAm variant + B2B + Loyalty J02.5
**Prerequisito:** Hub + Spokes en produccion y sin issues criticos

---

### TICKET: J02-19
**Titulo:** Construir J02-LATAM variant en CleverTap — WhatsApp primary
**Epic:** J02
**Sprint:** Sprint 3
**Prioridad:** P1
**Owner:** Katy
**Estimacion:** 6h

**Descripcion:**
Construir la variante LatAm del Hub J02 con las diferencias clave: S1 y S4 usan WhatsApp en lugar de push, el copy usa framing USD/inflacion, Venezuela requiere gate de `kyc_enhanced_confirmed` antes de cualquier touchpoint financiero, Argentina usa "activos digitales" en lugar de "criptomonedas" por restricciones BCRA.

Mercados: VE, MX, CO, AR. Trigger de entrada: `first_monetization AND geo IN (VE, MX, CO, AR)`.

**Criterios de aceptacion:**
- [ ] Journey J02-LATAM creado en CleverTap separado del Hub Spain/EU
- [ ] S1 y S4 usan WhatsApp (no push) con templates pre-aprobados de Meta
- [ ] Venezuela: gate `kyc_enhanced_confirmed` = true antes de S0.5 y cualquier touchpoint posterior
- [ ] Argentina: copy sin "criptomonedas", usa "activos digitales"
- [ ] Frecuencia cap: max 1 WhatsApp/semana (separado del cap de push)
- [ ] Fallback push activo si WhatsApp no entregado en 2h
- [ ] Copy LatAm aprobado por Diego (incluir en batch LATAM separado)

**Bloqueado por:** J02-18 (WhatsApp Business API), Meta templates aprobados

---

### TICKET: J02-23
**Titulo:** Construir J02.5 Loyalty 3 touchpoints en CleverTap — D+45 a D+90
**Epic:** J02
**Sprint:** Sprint 3
**Prioridad:** P2
**Owner:** Katy
**Estimacion:** 4h

**Descripcion:**
J02.5 Loyalty cementa el habito de inversion entre D+45 y D+90. Condicion de entrada: `second_purchase_confirmed = true AND days_since_first_purchase >= 45`. 3 touchpoints: T1 email D+45, T2 push D+60, T3 email D+90. Objetivo: 40% de usuarios alcanzan 3a compra.

Benchmark clave: Coinbase (2023) — usuarios con 3+ trades en 90 dias tienen 3.1x mayor retencion a 12 meses.

**Criterios de aceptacion:**
- [ ] Journey J02.5 creado con entry condition correcta
- [ ] T1 email D+45: personalizacion VALOR_INICIAL vs VALOR_ACTUAL del portfolio
- [ ] T2 push D+60: solo si sin 3a compra, logica de estado mercado (movimiento/correccion/consolidacion)
- [ ] T3 email D+90: solo si sin 3a compra entre D+45 y D+90, CTA condicional Earn si `earn_product_active = false`
- [ ] Todos los touchpoints no se envian si el usuario ya completo 3a compra
- [ ] KPIs en CleverTap: T1 open rate, T2 CTR, T3 conversion a 3a compra

**Bloqueado por:** J02-01 (campos BigQuery), Diego aprobacion batch Sprint 3

---

### TICKET: J02-24
**Titulo:** Construir J05 B2B secuencia 3 emails en CleverTap
**Epic:** J02
**Sprint:** Sprint 3
**Prioridad:** P2
**Owner:** Katy + Sales
**Estimacion:** 4h

**Descripcion:**
J05 es arquitecturalmente separado de J02 (B2C). Trigger: `kyc_type = empresa`. Sin push, sin WhatsApp — solo email. Tono ROI/treasury, nunca emocional. 3 emails en 20 dias (E1 D+1 fee savings, E2 D+8 MiCA compliance, E3 D+20 demo CTA). Firmado por nombre del Sales lead asignado (+12% open rate benchmark).

Escalacion a Daniel si primera operacion > EUR 50.000.

**Criterios de aceptacion:**
- [ ] Journey J05 creado en CleverTap con trigger `kyc_type = empresa`
- [ ] `kyc_type` disponible como propiedad de usuario en CleverTap (Alvaro prerequisito)
- [ ] 3 emails en 20 dias: E1 (D+1), E2 (D+8), E3 (D+20)
- [ ] Personalizacion: NOMBRE_EMPRESA, NOMBRE_SALES, FEE_SAVINGS_ESTIMADO funcionando
- [ ] Frecuencia max: 1 email/semana
- [ ] Alerta automatica a Daniel cuando usuario empresa supera EUR 50.000 en operaciones
- [ ] Diego aprueba batch B2B (SLA 3-5 dias por mayor complejidad legal)

**Bloqueado por:** J02-01 (kyc_type field), Diego aprobacion B2B

---

## Appendix — Tabla Resumen por Sprint

| Ticket | Titulo resumido | Sprint | Prioridad | Owner | Bloqueante principal |
|--------|----------------|--------|-----------|-------|---------------------|
| J02-01 | BigQuery FM segment + CT props | 1 | P0 | Alvaro | Ninguno |
| J02-02 | Entry trigger Journey J02 CT | 1 | P0 | Katy | J02-01 |
| J02-03 | S0 in-app banner | 1 | P0 | Katy | J02-01, J02-20 |
| J02-04 | S0.5 price alert modal | 1 | P0 | Katy | J02-01, J02-20 |
| J02-05 | price_change_pct_24h evento | 1 | P0 | Alvaro | Ninguno |
| J02-06 | S1 push 3 variantes | 1 | P0 | Katy | J02-01, J02-05, J02-20 |
| J02-07 | S2 in-app full-screen | 1 | P1 | Katy | J02-01, J02-20 |
| J02-08 | Copy S3 email + Diego prep | 1 | P0 | Daniel+Diego | Ninguno |
| J02-09 | S3 email MiCA | 1 | P1 | Katy | J02-01, J02-08 |
| J02-10 | S4 push D+7 | 1 | P1 | Katy | J02-01, J02-05, J02-08 |
| J02-11 | Clasificacion A/B/C D+30 | 1 | P1 | Alvaro+Katy | J02-01 |
| J02-12 | Recovery B1 manual ESTA SEMANA | 1 | P0 | Katy+Marta | BigQuery fields, Diego |
| J02-20 | Batch aprobacion Diego Hub | 1 | P0 | Diego+Daniel | Daniel prep |
| J02-22 | Holdout 10% CleverTap | 1 | P0 | Katy | J02-01 |
| J02-13 | SP-01 Earn 3 emails | 2 | P0 | Katy+Daniel | J02-01, J02-21 |
| J02-14 | SP-02 Pro 2 emails | 2 | P1 | Katy | J02-01, J02-21 |
| J02-15 | SP-03 DCA 2 emails | 2 | P1 | Katy | J02-01, J02-21 |
| J02-16 | SP-04 Diversify 2 emails | 2 | P1 | Katy | J02-01, J02-21 |
| J02-17 | SP-05 Referidos email | 2 | P2 | Katy | J02-01, J02-21 |
| J02-18 | WhatsApp Business API LatAm | 2 | P1 | Producto+Katy | Meta approval |
| J02-21 | Batch aprobacion Diego Spokes | 2 | P0 | Diego+Daniel | Copies listos |
| J02-25 | A/B test SP-01 loss vs gain | 2 | P0 | Daniel+Katy | J02-13, J02-21 |
| J02-19 | J02-LATAM WhatsApp variant | 3 | P1 | Katy | J02-18, Meta templates |
| J02-23 | J02.5 Loyalty 3 touchpoints | 3 | P2 | Katy | J02-01, Diego S3 |
| J02-24 | J05 B2B 3 emails | 3 | P2 | Katy+Sales | J02-01, Diego B2B |

---

## Camino Critico (ruta mas larga)

```
J02-01 (Alvaro BigQuery) [dia 1]
  → J02-20 (Daniel prep batch Diego) [dia 1, paralelo]
    → Diego aprueba Hub [dia 3]
      → J02-02 Journey setup CT [dia 3]
      → J02-03 S0, J02-04 S0.5, J02-06 S1, J02-07 S2, J02-09 S3, J02-10 S4 [dias 3-4]
        → Hub publicado [dia 5]

J02-12 Recovery B1 ESTA SEMANA (paralelo — no esperar Hub) [dia 1-2]
  → Marta SQL export → Katy one-off email → Diego aprueba [dia 3-4]
    → Envio [dia 4-5]
```

**Tiempo minimo para tener Hub en produccion:** 5 dias habiles desde hoy si Alvaro entrega J02-01 el dia 1.

**Tiempo minimo para Recovery B1:** 4 dias habiles (puede ir en paralelo al Hub).

---

*Documento generado por Journey OS Plan 01-07 — 2026-03-23*
*Diagrama de referencia: docs/plans/2026-03-23-j02-diagram.mmd*
*Spec Hub: docs/plans/2026-03-23-j02-hub-spain.md*
*Spec Spokes: docs/plans/2026-03-23-j02-spokes-01-05.md*
*Spec Recovery + Loyalty: docs/plans/2026-03-23-j02-recovery-loyalty.md*
