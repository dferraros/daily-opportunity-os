# VALIDATION PROMPT: FLASH REVENUE REPORT
## Para verificar 100% de exactitud antes de presentar a Pablo y Andrei

**Fecha:** 29 Enero 2026  
**Autor:** Daniel (Head of Growth)  
**Mindset:** Zero tolerance for errors. Every number must trace back to source.

---

## 🔴 REGLA DE ORO

> "Si no puedo señalar la celda exacta en el archivo fuente donde está este número, NO VA EN EL REPORTE."

---

## CHECKLIST DE VALIDACIÓN POR HOJA

### 1. RESUMEN EJECUTIVO

| Dato | Valor en Reporte | Fuente a Verificar | Celda/Filtro Exacto | ✓/✗ |
|------|------------------|-------------------|---------------------|-----|
| ROAS promedio 8 semanas | 3.27x | REVENUE_MARGINS.xlsx o Qlik | Suma(Revenue)/Suma(Spend) de W1-W8 | |
| % semanas con ROAS >2.5x | 7/8 (87.5%) | Paid 8 Semanas (Hoja 6) | Contar filas donde ROAS >2.5 | |
| Conv Paid vs Organic | 41.7% vs 14.8% | CR First MonReg files | Filtrar por channel | |
| Rev/Usuario Organic vs Paid | €236 vs €111 | ⚠️ VERIFICAR CÁLCULO | Revenue/Usuarios con 1st mon | |

**⚠️ ALERTA:** El insight dice "Organic genera 2x más revenue por usuario (€236 vs €111)" pero en Hoja 3 dice Paid €14.68 vs Organic €8.64. **¿CUÁL ES CORRECTO?**

**ACCIÓN:** Recalcular Rev/Usuario:
- ¿Es Revenue / Registros totales?
- ¿Es Revenue / Registros CON primera compra?
- ¿Es LTV de cohorte?

---

### 2. 1ª ADQUISICIÓN vs LIFE CYCLE

| Dato | Valor | Fuente Primaria | Validación |
|------|-------|-----------------|------------|
| 1ª Adq Revenue | €66,465 | REVENUE_MARGINS.xlsx | Filtro: Cohorte mes actual |
| Life Cycle Revenue | €99,533 | REVENUE_MARGINS.xlsx | Filtro: Cohortes anteriores |
| Total | €165,998 | Suma de ambos | ¿Cuadra con total Qlik? |
| Usuarios 1ª Adq | 10,238 | Lifecycle file | Filtro: reg_date = periodo actual |
| Usuarios LC | 7,692 | Lifecycle file | Filtro: reg_date < periodo actual |
| Rev/User 1ª Adq | €6.49 | Cálculo | 66,465 / 10,238 = €6.49 ✓ |
| Rev/User LC | €12.94 | Cálculo | 99,533 / 7,692 = €12.94 ✓ |

**PREGUNTAS DE VALIDACIÓN:**
1. ¿El periodo es 1 Dic - 28 Ene 2026? Confirmar con Qlik
2. ¿Los usuarios de Life Cycle (7,692) son DISTINTOS de los de 1ª Adq (10,238)?
3. ¿La suma 10,238 + 7,692 = 17,930 coincide con total usuarios?

---

### 3. REVENUE POR CANAL

| Canal | Revenue | Registros | Conv % | Rev/Reg | VALIDAR CON |
|-------|---------|-----------|--------|---------|-------------|
| ORGANIC | €73,866 | 8,553 | 28.0% | €8.64 | Qlik: mkt=organic |
| PAID | €34,292 | 2,336 | 21.1% | €14.68 | Qlik: mkt=paid |
| DIRECT | €31,929 | 2,855 | 25.8% | €11.18 | Qlik: mkt=direct |
| REFERIDOS | €8,314 | 882 | 47.8% | €9.43 | Qlik: utm_source=referral |
| NO TRACE | €6,896 | 2,198 | 9.6% | €3.14 | Qlik: mkt=null |
| INTERNAL | €6,606 | 146 | 28.9% | €45.25 | Qlik: mkt=internal |
| PARTNERS | €2,373 | 590 | 30.7% | €4.02 | Qlik: utm_source=partner* |
| AI (LLMs) | €40 | 89 | 3.8% | €0.45 | Qlik: utm_source=*gpt*,*perplexity* |
| **TOTAL** | **€165,998** | | | | |

**CÁLCULOS A VALIDAR:**
- [ ] €73,866 / 8,553 = €8.64 ✓
- [ ] €34,292 / 2,336 = €14.68 ✓
- [ ] €8,314 / 882 = €9.43 ✓
- [ ] Conv % = (Usuarios con 1st mon / Registros) × 100

**⚠️ PREGUNTA CRÍTICA:** ¿Qué significa "Conv %"?
- ¿Es Reg → Verificado?
- ¿Es Reg → 1ª Compra?
- ¿Es Reg → 1ª Monetización?

**DEBE SER CONSISTENTE** con la definición usada en Council.

---

### 4. REVENUE POR PAÍS

| País | Usuarios | Volumen | % Total | Vol/Usuario |
|------|----------|---------|---------|-------------|
| España | 7,630 | €12,312,050 | 91.4% | €1,614 |
| Alemania | 423 | €324,381 | 2.4% | €767 |
| Portugal | 453 | €127,457 | 0.9% | €281 |
| Italia | 577 | €64,059 | 0.5% | €111 |
| Francia | 537 | €46,309 | 0.3% | €86 |
| Argentina | 421 | €8,468 | 0.1% | €20 |

**VALIDAR:**
- [ ] €12,312,050 / 7,630 = €1,614 ✓
- [ ] Suma volúmenes = €13,474,634 (¿coincide con Lifecycle file?)
- [ ] % Total: 12,312,050 / 13,474,634 = 91.4% ✓

**FUENTE:** REVENUE_MARGINS.xlsx → Filtro por country

---

### 5. LIFE CYCLE STATUS

| Métrica | Valor | % | Fuente |
|---------|-------|---|--------|
| Total usuarios nuevos | 17,931 | 100% | Lifecycle file |
| Enabled | 16,544 | 92.3% | status = enabled |
| Banned | 1,083 | 6.0% | status = banned |
| Disabled | 304 | 1.7% | status = disabled |

**CLUSTERS DE CHURN:**
| Cluster | Usuarios | % |
|---------|----------|---|
| Churn | 11,542 | 64.4% |
| Neutro | 2,889 | 16.1% |
| No activados | 2,151 | 12.0% |
| Activos | 680 | 3.8% |
| Riesgo | 669 | 3.7% |

**VALIDAR:**
- [ ] 16,544 + 1,083 + 304 = 17,931 ✓
- [ ] 11,542 + 2,889 + 2,151 + 680 + 669 = 17,931 ✓

---

### 6. PAID 8 SEMANAS

| Semana | Gasto | Revenue | ROAS | Cálculo |
|--------|-------|---------|------|---------|
| W1 (01-07 Dic) | €4,353 | €17,775 | 4.08x | 17,775/4,353 = 4.08 ✓ |
| W2 (08-14 Dic) | €4,382 | €16,408 | 3.74x | 16,408/4,382 = 3.74 ✓ |
| W3 (15-21 Dic) | €3,564 | €11,633 | 3.26x | 11,633/3,564 = 3.26 ✓ |
| W4 (22-28 Dic) | €4,619 | €11,490 | 2.49x | 11,490/4,619 = 2.49 ✓ |
| W5 (29 Dic-04 Ene) | €4,963 | €12,727 | 2.56x | 12,727/4,963 = 2.56 ✓ |
| W6 (05-11 Ene) | €4,892 | €14,674 | 3.00x | 14,674/4,892 = 3.00 ✓ |
| W7 (12-18 Ene) | €4,616 | €17,052 | 3.69x | 17,052/4,616 = 3.69 ✓ |
| W8 (19-25 Ene) | €2,071 | €7,603 | 3.67x | 7,603/2,071 = 3.67 ✓ |
| **TOTAL** | **€33,460** | **€109,362** | **3.27x** | |

**VALIDAR:**
- [ ] Suma Gasto: 4,353+4,382+3,564+4,619+4,963+4,892+4,616+2,071 = €33,460 ✓
- [ ] Suma Revenue: 17,775+16,408+11,633+11,490+12,727+14,674+17,052+7,603 = €109,362 ✓
- [ ] ROAS promedio: 109,362/33,460 = 3.27x ✓

**⚠️ PREGUNTA PARA CONSUELO:**
- ¿Por qué W8 tiene gasto €2,071 (mucho menor)?
- ¿Faltan datos de Apple Ads en alguna semana?
- ¿El revenue es solo de usuarios nuevos (1ª Adq) o también incluye LC de campañas anteriores?

---

### 7. PLAN DE ACCIÓN

| Condición | Responsable | Deadline | Verificar |
|-----------|-------------|----------|-----------|
| Validar tracking DSP | Consuelo | 7 Feb 2026 | ¿Confirmado con ella? |
| ROAS >2.5x al escalar | Consuelo + Daniel | Semanas 1-2 | Criterio claro |
| Portugal activo | Consuelo | 1 Feb 2026 | ¿Status real? |
| Kill-switch definido | Daniel | Continuo | ROAS <2.0x × 2 sem |

---

## 🔍 VALIDACIONES CRUZADAS CRÍTICAS

### Test 1: Consistencia de Totales
```
Revenue Total en Hoja 2 (1ª Adq + LC): €165,998
Revenue Total en Hoja 3 (Suma canales): €165,998
→ ¿COINCIDEN? [ ] Sí [ ] No
```

### Test 2: Consistencia de Usuarios
```
Usuarios en Hoja 2: 10,238 + 7,692 = 17,930
Usuarios en Hoja 5: 17,931
→ ¿Diferencia de 1? Revisar redondeo o fuente
```

### Test 3: Consistencia ROAS
```
ROAS en Resumen Ejecutivo: 3.27x
ROAS calculado en Hoja 6: 109,362/33,460 = 3.27x
→ ¿COINCIDEN? [ ] Sí [ ] No
```

### Test 4: Revenue Paid Consistency
```
Revenue PAID en Hoja 3: €34,292
Revenue PAID en Hoja 6 (8 semanas): €109,362
→ ¿POR QUÉ DIFERENCIA?
   - Hoja 3: Solo periodo específico (Dic-Ene parcial?)
   - Hoja 6: 8 semanas completas (01 Dic - 25 Ene)
   **ACLARAR EN NOTAS DEL REPORTE**
```

---

## ⚠️ ERRORES POTENCIALES DETECTADOS

### ERROR 1: Inconsistencia Rev/Usuario
- **Resumen Ejecutivo:** "Organic genera 2x más revenue por usuario (€236 vs €111)"
- **Hoja 3 Revenue por Canal:** Paid €14.68/reg vs Organic €8.64/reg
- **ESTO ES CONTRADICTORIO** → Verificar cálculo y definición

### ERROR 2: Diferencia en usuarios totales
- Hoja 2: 17,930 usuarios
- Hoja 5: 17,931 usuarios
- **Diferencia de 1** → Verificar fuentes

### ERROR 3: Revenue PAID inconsistente
- Hoja 3: €34,292
- Hoja 6: €109,362
- **¿Diferentes periodos? ¿Diferentes definiciones?**

---

## 📋 CHECKLIST FINAL ANTES DE ENVIAR

### Precisión de Datos
- [ ] Todos los ROAS calculados manualmente coinciden
- [ ] Todas las sumas verificadas
- [ ] Todas las divisiones verificadas
- [ ] Fuentes documentadas para cada número

### Consistencia Interna
- [ ] Revenue total igual en todas las hojas
- [ ] Usuarios total igual en todas las hojas
- [ ] Definiciones consistentes (Conv %, Rev/User)

### Validación Externa
- [ ] Números cruzados con Qlik
- [ ] Confirmado con Consuelo (Paid)
- [ ] Confirmado con Marta (Lifecycle)

### Presentación
- [ ] Sin errores de formato
- [ ] Fechas correctas
- [ ] Nombres correctos (Andrei, Pablo)
- [ ] Sin typos

### Preguntas Anticipadas
- [ ] ¿Por qué ROAS bajó en W4? → Festivos
- [ ] ¿Por qué W8 gasto menor? → [COMPLETAR]
- [ ] ¿Diferencia Rev PAID Hoja 3 vs Hoja 6? → [COMPLETAR]

---

## 🎯 ACCIÓN INMEDIATA

1. **RESOLVER** inconsistencia Rev/Usuario (€236 vs €14.68)
2. **CONFIRMAR** con Consuelo los datos de Paid W8
3. **DOCUMENTAR** por qué Revenue PAID difiere entre hojas
4. **AÑADIR** nota al pie explicando periodos de cada hoja

---

## PREGUNTA FINAL DE VALIDACIÓN

> "Si Andrei pregunta '¿De dónde sale este número?', ¿puedo abrir Qlik/Excel y mostrárselo en <10 segundos?"

Si la respuesta es NO para cualquier número → **NO INCLUIR O VERIFICAR PRIMERO**

---

*Documento generado para validación interna. No enviar a Pablo/Andrei.*
