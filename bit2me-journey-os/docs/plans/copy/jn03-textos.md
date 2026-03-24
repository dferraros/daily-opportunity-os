# JN-03 — Deep Dormant Reactivation: Textos de Copy

---

## S1 — Email (D+0, 10h)

**Asunto A:** {{asset}} lleva un {{change}}% en 7 días. Tu posición se ha movido.

**Asunto B:** Tu portfolio ha cambiado desde {{last_login_month}}.

**Preheader:** Hace más de un año que no nos visitas. Tus activos siguen donde los dejaste.

---

Hola,

Hace más de un año que no entras a Bit2Me. Tu cuenta sigue activa y tus activos siguen exactamente donde los dejaste.

El mercado crypto ha tenido movimientos importantes en este tiempo. Bitcoin, Ethereum y el resto del sector han experimentado cambios significativos — tanto al alza como a la baja. Tu posición se ha movido con el mercado.

No hace falta que hagas nada ahora mismo. Pero si quieres ver en qué punto está tu portfolio hoy, está a un clic.

[Ver mi portfolio]

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S2 — Email (D+4, 10h — solo si S1 NO fue abierto)

**Asunto:** Hace {{days}} días que no entras. Esto es lo que pasó en cripto.

**Preheader:** Un resumen rápido del mercado desde tu última visita.

---

Hola,

Desde tu última visita a Bit2Me, el mercado crypto ha tenido varios movimientos relevantes:

- Bitcoin alcanzó nuevos niveles de precio y consolidó su posición como activo de referencia global.
- Ethereum completó actualizaciones de red que afectaron su rendimiento y su propuesta de valor.
- La regulación crypto en Europa avanzó significativamente, con nuevos marcos legales en vigor.

Tu cuenta sigue activa. Tus activos siguen donde los dejaste.

[Revisar mi cuenta]

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

---

## S2.5 — Push (D+6, 10h — solo si S1 SÍ fue abierto pero NO login)

**Título:** Abriste nuestro email pero no has vuelto

**Cuerpo:** Tu portfolio te espera. Un minuto para ver dónde estás.

**Deep link:** bit2me://portfolio

---

## S3 — Email (D+8, 10h — solo si S1 SÍ fue abierto pero NO login)

**Asunto:** Tu saldo lleva más de un año sin generar nada. Ahora puede.

**Preheader:** Earn: tu saldo trabajando mientras tú no estás.

---

Hola,

Tu saldo en Bit2Me lleva más de un año parado. No genera nada. Pero podría.

Con Earn, tu saldo empieza a generar rendimiento de forma automática, sin que tengas que operar ni seguir el mercado. Solo activarlo, y trabajar por ti mientras tú haces otras cosas.

La activación tarda menos de dos minutos. Puedes retirar cuando quieras.

[Descubrir Earn]

---

Bit2Me Sociedad de Valores, S.A., entidad registrada en la CNMV como proveedor de servicios de criptoactivos. Las criptomonedas son activos de alto riesgo. El valor de tu portfolio puede subir o bajar significativamente. Rentabilidades pasadas no garantizan resultados futuros. Bit2Me no ofrece asesoramiento de inversión. Invierte solo lo que puedas permitirte perder.

Los productos de rendimiento implican riesgo. El APY mostrado es variable y puede cambiar sin previo aviso. Bit2Me no garantiza rendimientos ni la devolución del capital. Lee las condiciones completas en bit2me.com/earn antes de participar.

---

## S4 — In-app (primera sesión post-reactivación)

**Header:** Bienvenido de vuelta, {{nombre}}.

**Body:** Tu saldo podría generar {{earn_apy}}% APY en Earn. ~{{yield_mensual}} EUR/mes. Retira cuando quieras.

**CTA primario:** Activar Earn → bit2me://earn

**CTA secundario:** Ver mi portfolio → bit2me://portfolio

---

## QA Checklist — 10 puntos

- [ ] 1. Lista de envío validada con ZeroBounce antes de cada envío: bounces eliminados, spam traps limpios.
- [ ] 2. NUNCA se muestran valores EUR absolutos en los emails S1, S2 y S3 — solo % de cambio o copy genérico.
- [ ] 3. EUR value ({{yield_mensual}}) se muestra únicamente en S4 in-app, no en emails.
- [ ] 4. Batch warming completado antes del primer envío masivo a los 46,000 usuarios.
- [ ] 5. Kill switches configurados: si tasa de spam > 0.08% o bounce > 2%, la secuencia se pausa automáticamente.
- [ ] 6. Lógica condicional verificada: S2 solo sale si S1 no fue abierto; S2.5 y S3 solo salen si S1 fue abierto pero no hubo login.
- [ ] 7. S4 in-app se dispara únicamente en la primera sesión post-reactivación, no en sesiones posteriores.
- [ ] 8. Footer MiCA presente en todos los emails (S1, S2, S3).
- [ ] 9. Footer Earn presente en S3 (menciona Earn y rendimiento). No en S1 ni S2.
- [ ] 10. Diego aprueba todos los textos de esta secuencia antes del primer envío.
