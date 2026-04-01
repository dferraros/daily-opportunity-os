# Activation Data — Funnel & Geographic Reference

## ACTIVATION Export (Feb 22, 2026)
Source: CleverTap / internal activation export. Filed as "ACTIVATION - 22 de febrero de 2026.xlsx"

Columns: RESIDENCE | USERS | EMAIL | %EMAIL | PHONE | %PHONE | VERIFIED | %VERIFIED |
         Nº FIRST MOVEMENTS | % FM | Nº FIRST MON. MOVEMENTS | % FIRST MON. |
         AVG VOL FIRST MON. | Nº FIRST PURCHASE | % FIRST PURCHASE | AVG VOL FIRST PURCHASE |
         VOLUME LAST 365 DAYS | MON VOLUME LAST 365 DAYS | REVENUE LAST 365 DAYS

## Key Country Data (from Feb 22 export)
| Country | Users | Verified % | FM Rate | Avg FM Vol | Revenue (LTD) |
|---------|-------|-----------|---------|-----------|--------------|
| ES | 370,496 | 49.8% | 44.4% | €662 | €11,795,882 |
| BR | 56,559 | 28.7% | 9.1% | €86 | €23,497 |
| PT | 45,810 | 36.5% | 23.1% | €162 | €210,259 |
| AR | 35,593 | 47.2% | 11.3% | €260 | €37,959 |
| MX | 30,530 | 38.0% | 9.2% | €208 | €34,221 |
| IT | 24,602 | 41.8% | 24.2% | €281 | €91,361 |
| CO | 18,500 | 6.5% | 3.1% | €466 | €10,503 |
| FR | 18,414 | 35.0% | 23.1% | €298 | €78,177 |
| DE | 13,553 | 40.8% | 32.9% | €488 | €268,301 |
| GB | 7,866 | 25.0% | 13.6% | €572 | €225 |
| RO | 5,931 | 49.4% | 32.2% | €380 | €35,347 |

Notes:
- US: only 5 verified (regulatory — can't serve US users). Exclude from funnel analysis.
- GB: minimal revenue — Compliance UK3 group blocks mass messaging.
- DE has higher avg ticket (€488) despite lower FM rate — quality market.
- BR: 56K users but only 9.1% FM rate + €23K revenue. Low quality at scale.

## Verification Funnel Drop-off (CORRECTED Feb 25, 2026 — data validated)
| Country | Email% | Phone% | Verified% | Email→Phone Drop | Phone→KYC Drop |
|---------|-------|--------|----------|-----------------|---------------|
| ES | 99.3% | 98.1% | 49.8% | -1.2% | -48.3% |
| BR | 99.2% | 98.0% | 28.7% | -1.2% | -69.3% |
| PT | 99.1% | 97.8% | 36.5% | -1.3% | -61.3% |
| AR | 99.2% | 98.4% | 47.2% | -0.7% | -51.2% |
| MX | 98.6% | 96.3% | 38.0% | -2.3% | -58.3% |
| IT | 99.2% | 97.5% | 41.8% | -1.8% | -55.7% |
| DE | 98.8% | 97.0% | 40.8% | -1.8% | -56.2% |
| CO | 97.3% | 96.7% | 6.5% | -0.5% | -90.3% |

**⚠️ CORRECTED: Drop is NOT at phone step (~1-2% loss). The 50-90% drop happens at KYC (identity verification).** Fix = KYC flow reduction, not phone verification.

## Weekly Funnel Benchmarks (W8 — Feb 2026)
| Step | Rate |
|------|------|
| Registro → Datos | 53.25% |
| Datos → Verificación | 43.90% |
| Verificado → Primera Compra | 50.00% |

## W07 Crisis Week Context
- Registros: -18% WoW (3,032→2,469)
- Verificaciones: -33% WoW (1,538→1,072)
- FM: -47% WoW (901→558)
- Revenue: -74% WoW (€233k→€106k)
- Cause: market contraction (-52% exchange volume). W06 was anomalously high. W05 = correct baseline.

## Portugal Specific
- 45,810 total users. 36.5% verified. 23.1% FM rate.
- W24feb: 160 registrations → 27 purchases (16.9% weekly conversion)
- Portugal KPI: David Dahan Levy (GTM) owns PT dashboard
- 1yr no-tax-on-gains rule: Long-term holders + Loan = potentially huge for PT market
- MB Way (PT payment method) will boost PT acquisition when live
