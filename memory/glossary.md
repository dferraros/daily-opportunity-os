# Glossary — Bit2Me / Daniel Ferraro context

## Product Terms
| Term | Meaning |
|------|---------|
| FM | First Monetizable — primer evento MONETIZABLE. EXCLUYE funding/depósito. |
| EMA | Economically Meaningful Action (Acción Económicamente Significativa). Daniel's framework. |
| FM Brokerage | Primera operación: swap OR sell OR purchase |
| FM Pro / Spot | Primer trade ejecutado (buy o sell). Pro may be renamed "Spot" (Nicolas). |
| FM Loan | Primera REQUEST de préstamo (aunque no aprobada) |
| B2M Token | NO computa como FM. Excluido explícitamente. |
| TAU | Transacting Active User: ≥1 tx monetizable en 28d rolling window |
| LC | Lifecycle — SEGMENTO (not metric). Candidate (FM + ≥1 retorno 30d) / Confirmed (≥2 tx) |
| L0 | Sin KYC (49.1% España, 213,863 users) |
| L1 | KYC'd, no FM. 29,010 users. Primary A/B target (T1). |
| L2 | FM sin retención. 36,866 users. €26M+ potential. |
| L3 | Activo con valor (revenue last 90d). 50,416 users. Core revenue. T1+T2 targets. |
| L4 | Dormido con saldo (90d+ inactive, balance>0). 4,414 users. €3.1M+ potential. T3 target. |
| L5 | Churneado (180d+, balance=0, no login). 101,029 users. |
| DEPOSITED_ONLY | Deposited but no FM. Highest ROI conversion target. |
| Health Score | Churn risk metric per user. Not priority yet (needs major data changes). |
| LTV | (1/ChurnRate) × ARPUSemanal × 52. Owner: Pablo Campos + David Sales. EMPRESA metric. |
| Churn Rate | (usuarios sin operar / TAU inicio período). Owner: David Sales. |
| LT | Life Time. BigQuery algorithm. PENDIENTE David Sales. EMPRESA metric. |
| Smart Holders | c6/c7 cluster users: app-active but not trading (30-120d inactive). €600K potential. |
| C8 | Whale cluster Brokerage. 90.91% of Loan revenue. NEVER mass push. Needs personal relationship. |
| ROAS Blended | Revenue total / Gasto total MK |
| iROAS | Incremental ROAS — revenue incremental atribuido a Paid / Gasto Paid |
| MER | Marketing Efficiency Ratio = Revenue total / Gasto total MK. Sin sesgo de atribución. |
| mROAS | Marginal ROAS = ΔRevenue / ΔSpend. THE scaling metric para Paid. |
| CpR | Cost per Referral to FM = Gasto referidos / FMs referidos |
| K (Viral Coef.) | Invitaciones promedio × tasa conversión referido→FM. K>1 = viral. |
| Ghost Conversions | Usuarios existentes clickando ads de marca. Budget waste. |

## Products
| Term | Meaning |
|------|---------|
| Brokerage | Main crypto exchange product (swap/buy/sell). ~90% of revenue Spain. |
| Pro / Spot | Professional trading product. Nicolas Contasti lead. North Star = volume. |
| Loan | Bit2Me lending product. Traceability: 60% (need 80% before Growth acts). |
| Earn / ERN | Bit2Me savings/staking product. Traceability: 50% (target 80%). |
| Bit Card | Bit2Me debit/crypto card. North Star = "Crypto Assets Usage". |
| Bit2Me Life | Product promoted alongside Bit Card. |
| BTUM / Inversiones | Bit2Me Stocks (stocks, ETFs, funds). Blocked by CNMV. Provisional name "Inversiones". |
| Space Center | New referral/rewards platform replacing legacy system. |
| B to Me | Bit2Me app (internal name). |
| Poly | Internal tool Pablo Paredes building with Claude + Anthropic. |

## Channels
| Term | Meaning |
|------|---------|
| ASO | Apple Store Optimization. Channel #1 volume (37.4% YTD). |
| ASA | Apple Search Ads. Budget channel (needs credit card increase). |
| PID | Paid channel identifier. |
| GEO / SEOGEO | SEO/organic acquisition channel. |
| DSP | Demand-Side Platform for programmatic advertising. Anti-fraud suite active. |

## Tools
| Term | Meaning |
|------|---------|
| CleverTap | CRM/engagement tool. Main LC execution platform. EU1. |
| Qlik | BI dashboards (Pablo Talamantes builds). |
| BigQuery | Data pipelines. Gold Layer = source of truth. |
| N8N | Workflow automation for reports (paired with BigQuery). |
| Jira | Task management. GRW = Growth prefix, CYB = IT/cybersec prefix. |
| Confluence | Documentation, process guides, campaign analysis. |
| Figma | Journey visualization + documentation. |
| Click | Reporting/analytics tool alongside CleverTap. |
| Engage | Another analytics/CRM tool. |
| Singular | Agency/partner search platform. |
| Poly | Internal tool (Pablo Paredes + Claude/Anthropic). |
| cryptgeon.int.bit2me.com | Internal secure one-time message tool (for credentials). |

## Meetings / Reports
| Term | Meaning |
|------|---------|
| Council | Weekly Growth/Product/Data meeting. Attendance: Pablo/Patri/DavidD only (since Feb 19). |
| Pre-Council | Marketing prep meeting before Council. |
| Flash Diario | Daily 4-dashboard report (ADQ/Conv/LC/GTM). Pablo: "first thing to check each morning". |
| Flash Revenues | Quick revenue + gross margin view. Rodrigo Jovani owns. |
| Book of KPIs | 91-slide weekly/biweekly report for board/investors. Rodrigo Jovani. |
| Growth Strategy Weekly | Weekly strategic meeting. Postponed until LC + Paid running well. |
| Cierre de semana | Friday closing meeting. |
| Canal de Comunicación | Internal Google Chat channel: ALL campaigns/landings posted here. |

## Regulations / Compliance
| Term | Meaning |
|------|---------|
| CNMV | Spain's financial market regulator. Blocking Bit2Me Stocks launch. |
| DORA | Digital Operational Resilience Act (EU). Proyecto Dora. Deadline late April/May 2026. |
| MiCA | EU crypto regulation. B2B2C crypto resale requires specific license. |

## LC-OS System (Lifecycle Operating System)
| Term | Meaning |
|------|---------|
| LC-OS | Lifecycle Operating System — 4 layers: Data Sources → BigQuery Gold → Qlik → CleverTap |
| MMU | Monthly Monetizable Users. Target: 30k by Mar 31. Actual: 23k (Feb 2026) |
| M1 Retention | % users who transact again in month 1. Actual: 0.12% (CRISIS). Coinbase: 25% |
| AUC | Assets Under Custody — €19.5M held by 72.4k dormant users |
| Health Score | 100-pt churn risk score: Recency(30)+Frequency(20)+Product Density(15)+Balance Health(20)+Engagement Momentum(15) |
| 13 Stages | EXCLUDED, REGISTERED_ONLY, KYC_COMPLETE, DEPOSITED_ONLY, FIRST_MONETIZATION, ACTIVE, POWER_USER, AT_RISK, PRE_DORMANCY_FEE, DORMANT_WITH_BALANCE, DORMANT_ZERO, REACTIVATED, CHURNED |
| W-shaped | Attribution model: First Touch 30% + KYC Assist 20% + Deposit Assist 20% + FM Last Touch 30% |
| Ghost Conversions | Existing users clicking brand ads, attributed as new. 93% of paid attribution. Real new-user ROAS = 62% vs blended 1,004% |
| 4 Revenue Pools | New(4%), Retention(96%), Reactivation, Expansion |
| 37 Segments | SEG-01 to SEG-37. MECE grid: Lifecycle Stage × Archetype × Geo × Acquisition Channel × B2C/B2B × Space Center Tier |
| J1-J6 | CleverTap Journeys: J1 Brokerage, J2 Pro/Spot, J3 Earn, J4 Card (PAUSED), J5 B2B, J6 Multi-product |
| FOMO Agent | Daily push notification bot for c6+c7 dormant users (16,116). FOMO Score + CoinGecko API |
| FOMO Score | Urgency algorithm: market volatility + peer activity + time-since-last-tx signals |
| Space Center | 7-tier gamification/rewards platform. B2M Token holders advance 100x faster |
| V0a-V10 | BigQuery Gold Layer: 11 SQL views in schema bit2me_lifecycle. V0a target: Mar 10 |
| Flash Report | Daily revenue report. SQL: "dime cómo vamos". Acquisition vs LC split |
| Salvia / S. Rut | Daily LC operational syncs, backlog management. Same person. |
| JIRA_CONFLUENCE_STRUCTURE | Main LC-OS deliverable doc. Path: Desktop/LC-OS-Project/JIRA_CONFLUENCE_STRUCTURE.md. Created Feb 27 2026 |
| Inactive Fee | €10/month charged to accounts inactive 3+ years. Manual execution via admin panel. B2M holders excluded |
| Smart Holders / c6c7 | app-active but not trading users (30-120d inactive). 16,116 users. FOMO Agent target |
| Ghost Conversions Problem | see Ghost Conversions above |
| Pre-Dormancy Fee | Stage before DORMANT. Fee warning system |

## Internal Jargon / Shortcuts
| Term | Meaning |
|------|---------|
| PabloG | Pablo Garcia (Conversión lead) |
| JuanF | Juan Fornell (Product Brokerage/Pro) |
| PabloP | Pablo Paredes (B2Moments/Product) |
| JuanLu | Juan Luis Pascual (B2B sales) |
| ISA | Isabel Sánchez (CRM vision) |
| DavidD | David Dahan Levy (GTM / Portugal) |
| Andrei | Board/investor member. Pablo speaks directly. ≠ André Huidobro. |
| Pepe | IT/sysadmin at Bit2Me. Handles access tickets. |
| Eze | Ezequiel Godoy Sanchis (Data/Finance) |
| Gold Layer | BigQuery source of truth (136 transaction types) |
| Trazabilidad | Data traceability. Brokerage: 80%, Loan: 60%, ERN: 50%, Funding: 40%. |
| B2Moments | Squad led by Pablo Paredes for reactive/proactive market events. |
| MB Way | Portuguese payment method. Will boost PT acquisition. |
| ⚠BI Gap | Dato NO disponible aún, requiere desarrollo BigQuery. |
| ✓Qlik | Dato confirmado, query Qlik disponible. |
| CS: | Consumer Science tag en Col B — behavioral insight rationale. |
| EMPRESA | Métrica de empresa (LTV/Churn/LT). Owner outside MK. |
| Bitumi | Bit2Me product/brand variant name. |
| PICKASO | ASO agency partner working with Bit2Me. |
| INAP | Campaign name (low B2 Meet activity). |
| Velocity challenge | Automated B2B test to incentivize trading operations. |
| Company panel | B2B segmentation tool in CleverTap/BI. |
| CCL | Unknown acronym (likely compliance/regulatory dataset). Needed for Pre-Council. |
| Sentora | Research company/org Daniel spoke with about crypto products. |
| Leif | Unknown person Pablo spoke with (Feb 2). Possibly acquisition advisor. |
