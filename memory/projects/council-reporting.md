# Council & Reporting — Structure and Requirements

## Council Attendance (post-Feb 19 restructure)
- ONLY: Pablo Campos, Patri Gargallo, David Dahan Levy (DavidD)
- Daniel's job: ensure LC section is complete for Council

## Council Slide Requirements (Pablo directives)
1. **Market state slide** (max 1 slide, 1 minute max):
   - Fear & Greed Index (copy from coinmarketcap.com/es/charts/fear-and-greed-index/)
   - "Qué pasa esta semana": FED meeting, jobs data, etc.
   - Standardized format = replicate each week
2. **B2M correlation**: MUST correlate market data with Bit2Me metrics
   - Volume, nº operations, avg ticket vs market
   - "hablar solo del mercado sin explicar cómo impacta en nosotros no sirve"
3. Structure: Big Picture market state → then Bit2Me data. Period explicit.

## Flash Diario (Daily Dashboard)
- Created: Feb 23, 2026 by Pablo Campos
- Purpose: first thing to check each morning
- 4-dashboard structure (group auto-closes when all 4 live):
  - **ADQ**: Luis Ramírez + Consuelo Morcillo
  - **Conversión**: Pablo Garcia
  - **LC**: Daniel Ferraro + S. Rut (Salvia)
  - **GTM por país**: David Dahan Levy
  - Note: Contenido-Studio = Diego Barreira + Isabel Sánchez
- Pablo philosophy: "estamos aquí para tomar decisiones sobre los datos. la ejecución es 'siempre' secundaria"

## ADQ Metrics Definition (Pablo, Feb 24)
- Adquisición: measure nº users registering (NOT €). Quality: % fraud, % que registran y no se validan
- Conversión: metrics between funnel phases + conversion rate completo + FM (7-day window)
- LC: measures everything from semana+1

## Key Dashboard URLs
| Dashboard | URL |
|-----------|-----|
| Qlik Council | https://bit2me.eu.qlikcloud.com/sense/app/c338af75-3b20-4c2e-81b5-0681d06bd740/ |
| Qlik LC | https://bit2me.eu.qlikcloud.com/sense/app/fe70dd0c-9a75-45bb-8f65-450927bb55e0/ |
| Flash Revenue | https://docs.google.com/spreadsheets/d/1vcCZvHL-0ZoRYNsvzMYybZnwwAequp-b8XynrUDcxzY/edit |
| Council W09 | https://docs.google.com/presentation/d/1qZ_3-LOryvl_SdKmxouOUz28HPiY6dELtyrmugBRLmE/edit |
| Council W08 | https://docs.google.com/presentation/d/1CIkCyQF1BYdpm3eSei-9_2bg_L7f84ICEmIi79QQCzc/edit |
| Gold movements | https://docs.google.com/spreadsheets/d/1gD75mrkythn2BWg1gpYw9mwkEQ2RqdOo5pGmXjWl8Os/edit |

## Trazabilidad (Data Traceability) Status
| Product | % | Owner |
|---------|---|-------|
| att brok (Brokerage) | 80% | Juan Fornell |
| att earn (Earn/ERN) | 50% | Álvaro Durán |
| att loan (Loan) | 60% | Álvaro Durán |
| att fund (Funding) | 40% | Boris Escandell |
| att verif / att login / att churn | 0% | Daniel Ferraro |

**Growth policy**: NO actions on products with traceability <80% (Loan blocked at 60%)

## Reports Automation Roadmap (Pablo's vision)
1. Global Report → Flash Report → Growth Report (+metrics) / Product Report
2. Council complete redesign
3. Reports Automation (BigQuery + N8N)
- ADQ report base: "near-zero production time" target
- Meta: Patri/Marta inform → Daniel/Luis/Álvaro maintain
