# Lifecycle Stages — España Feb 2026

## L0–L5 (Global User Lifecycle)

| Stage | Nombre | España (n) | % | Definición SQL | Revenue | Test W09 |
|-------|--------|-----------|---|----------------|---------|----------|
| L0 | Sin KYC | 213,863 | 49.1% | kyc ≠ approved | €0 | No |
| L1 | KYC sin monetizar | 29,010 | 6.7% | kyc=ok, deposits=0, trades=0 | €0 potencial | T3 (566 depositados) |
| L2 | FM sin retención | 36,866 | 8.5% | FM hecho, sin 2ª compra | €26M+ potencial | W10+ |
| L3 | Activo con valor | 50,416 | 11.6% | revenue transaccional O recurrente, últimos 90d | Core revenue | T1 (5,523) · T2 (6,681) |
| L4 | Dormido con saldo | 4,414 | 1.0% | 90+ días inactivo, balance>0 | €3.1M+ potencial | W10+ |
| L5 | Churneado | 101,029 | 23.2% | 180+ días, balance=0, no login | Bajo (win-back) | No |

**Total España: 435,598**

## Por qué L0-L5 importa
- 72% de los usuarios generan cero revenue (L0 + L5)
- Solo 11.6% (L3) es el core del negocio
- FM vs LC: €486K vs €11.6M = retener existentes = 24x más impacto que adquirir nuevos
- T1 y T2 de W09 viven en L3. T3 vive en L1 (sub-segmento: depositados sin trade).

## Flujos semanales (aproximados)
- Nuevo → L0: ~1,400/semana
- L0 → L1: ~850/semana
- L1 → L2: ~610/semana
- L2 → L3, L3 → L4, L3 → L5, L4 → L3: desconocido (pendiente BigQuery)

## Supresión C8
C8 = whales del cluster Brokerage. 90.91% del revenue de Loans viene de C8.
NUNCA hacer push masivo a C8. Requiere relación personal.
Archivos: c8-suppression-ES-clevertap.csv / c8-suppression-ALL-clevertap.csv
Proceso: Juan Fornell exporta → Katy sube a CT → verificar antes de envío.
