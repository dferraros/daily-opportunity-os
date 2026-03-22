# Requirements: Playbook Maestro de Trigger Based Notifications — Bit2Me

**Defined:** 2026-03-22
**Core Value:** Un sistema de notificaciones que aumenta reactivación, retención y revenue sin destruir deliverability, push permissions ni confianza del usuario.

---

## v1 Requirements

Requirements for the Playbook deliverable (the document/system design).

### Foundation & Safety

- [x] **FOUND-01**: Diseño del Preference Center — arquitectura de canales, categorías de consentimiento, modelo de datos
- [x] **FOUND-02**: Política de frequency caps — caps diarios/semanales/mensuales por canal y familia de trigger
- [x] **FOUND-03**: Sistema de supresión — compliance suppressions (C8), quiet hours, opt-out handling
- [x] **FOUND-04**: Arquitectura de datos y tracking — event schema mínimo requerido para activar triggers
- [x] **FOUND-05**: Integración BigQuery → CleverTap via Hightouch Reverse ETL — diseño técnico

### Trigger Taxonomy

- [ ] **TAX-01**: Taxonomía completa de 6 familias de triggers con criterios de elegibilidad
- [ ] **TAX-02**: Familia A — User Configured (price above/below, % move, target reached, LTV threshold)
- [ ] **TAX-03**: Familia B — Market Triggered (volatility spike, volume spike, trending asset, breakout)
- [ ] **TAX-04**: Familia C — Behavioral (watched not bought, deposit no trade, abandoned order, repeated views)
- [ ] **TAX-05**: Familia D — Lifecycle (active→at-risk, dormant with balance, first trade, recurring lapsed)
- [ ] **TAX-06**: Familia E — Product Cross-sell (stablecoins not in Earn, eligible for Loan, Space Center missions)
- [ ] **TAX-07**: Familia F — Risk & Protective (LTV approaching threshold, large balance inactivity, failed actions)
- [ ] **TAX-08**: Asset universe mapping — qué activos son elegibles para cada familia de trigger

### Scoring & Formulas

- [ ] **SCORE-01**: Market Relevance Score — fórmula con pct_change, zscore, abnormal_volume_ratio
- [ ] **SCORE-02**: User Asset Affinity Score — basado en holdings, watchlist, search history, trade history
- [ ] **SCORE-03**: Trigger Opportunity Score — oportunidad × relevancia × propensity
- [ ] **SCORE-04**: Notification Pressure Score — sends recientes, opens, dismissals
- [ ] **SCORE-05**: Fatigue Risk Score — fórmula con decaimiento por bajo engagement
- [ ] **SCORE-06**: Cross-sell Eligibility Score — product adoption gap, balance, lifecycle stage
- [ ] **SCORE-07**: Churn Risk Score — days since last action, balance trend, frequency decline
- [ ] **SCORE-08**: Send Score Final — fórmula compuesta que integra todos los scores con compliance gate

### Master Trigger Table

- [ ] **TRIG-01**: Tabla maestra con ≥30 triggers documentados (todas las columnas del brief)
- [ ] **TRIG-02**: Por cada trigger: trigger_id, family, business objective, who receives, who never receives, asset scope, formula, threshold, cooldown, channel, deep link, priority, estimated value, estimated risk
- [ ] **TRIG-03**: Top 10 triggers MVP (30 días) claramente identificados
- [ ] **TRIG-04**: Top 10 triggers NOT to launch (con razonamiento)

### Channel Policy

- [ ] **CHAN-01**: Cuándo push vs in-app vs email vs no enviar — matriz de decisión
- [ ] **CHAN-02**: Deep links por producto y superficie (Brokerage, Pro, Earn, Card, Space Center)
- [ ] **CHAN-03**: Quiet hours por timezone (España, LatAm, EU)
- [ ] **CHAN-04**: Reglas de conflicto entre lifecycle journeys y market alerts en el mismo usuario

### Competitor Benchmark

- [ ] **BENCH-01**: Matriz comparativa de 6 competidores (Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo)
- [ ] **BENCH-02**: Por competidor: tipos de alerta, preference center, canales, asset scope, gaps
- [ ] **BENCH-03**: Recomendaciones concretas: qué copiar, qué evitar, qué innovar

### Measurement System

- [ ] **MEAS-01**: KPIs por trigger y por familia — CTR, session rate, trade rate, deposit rate
- [ ] **MEAS-02**: Métricas de presión y fatiga — notification pressure score, push disable lift, negative action rate
- [ ] **MEAS-03**: Métricas de deliverability — push token health, email reputation, opt-in rate trend
- [ ] **MEAS-04**: Incremental lift framework — holdout design (10% control), A/B test design por trigger
- [ ] **MEAS-05**: Net Notification Value formula — incremental revenue minus opt-out cost minus complaint cost

### Compliance & Risk

- [x] **COMP-01**: Compliance checklist por trigger — MiCA Art. 66, GDPR, ePrivacy, CNMV
- [x] **COMP-02**: Diego review workflow — qué copy necesita aprobación y cuándo
- [x] **COMP-03**: Investment advice vs informational — regla clara y ejemplos concretos
- [x] **COMP-04**: Market abuse risk en price/volume triggers — protocolo de datos públicos y simultaneidad

### Final Recommendations

- [ ] **REC-01**: Executive summary con impacto de negocio estimado (reactivación, retención, revenue)
- [ ] **REC-02**: MVP 30 días — triggers, canales, recursos necesarios, dependencias
- [ ] **REC-03**: V2 90 días — triggers, nuevas capacidades, dependencias técnicas
- [ ] **REC-04**: V3 180 días — sistema completo, ML scoring, portfolio alerts
- [ ] **REC-05**: Dependencias exactas por equipo (Katy CRM, Álvaro data, Diego legal, Engineering)

---

## v2 Requirements

Deferred — not in current playbook scope but documented for V3 planning.

### Advanced Features

- **ADV-01**: Portfolio-level alerts (% drawdown de portfolio total) — requiere portfolio aggregation
- **ADV-02**: ML-based trigger timing optimization (two-tower model user-asset affinity como Coinbase)
- **ADV-03**: Chart-integrated alerts (alert visible en gráfico del activo)
- **ADV-04**: Social signals (trending en Crypto Twitter/Reddit como trigger)
- **ADV-05**: WhatsApp channel integration
- **ADV-06**: Technical indicators como trigger (RSI oversold, MACD crossover)

### Product Integrations

- **PROD-01**: Launchpad trigger (early access notification, allocation results)
- **PROD-02**: Wealth product triggers (portfolio rebalancing alerts)
- **PROD-03**: API user triggers (rate limit warnings, webhook failures)

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Implementación directa en CleverTap | Este playbook es diseño estratégico; ejecución viene después |
| Copies finales aprobados por Diego | El playbook incluye plantillas y guidelines, no copies legales finales |
| BigQuery SQL queries completas | Documentadas como pseudocódigo/lógica; implementación es trabajo de Álvaro |
| Mobile app UI para user-configured alerts | Requiere Product roadmap separado |
| SMS channel | Canal no disponible en Bit2Me actualmente |
| Análisis de datos históricos internos | Sin acceso; se usan benchmarks y estimaciones externas |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1: Foundation + Safety Architecture | Complete |
| FOUND-02 | Phase 1: Foundation + Safety Architecture | Complete |
| FOUND-03 | Phase 1: Foundation + Safety Architecture | Complete |
| FOUND-04 | Phase 1: Foundation + Safety Architecture | Complete |
| FOUND-05 | Phase 1: Foundation + Safety Architecture | Complete |
| TAX-01 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-02 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-03 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-04 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-05 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-06 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-07 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| TAX-08 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| BENCH-01 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| BENCH-02 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| BENCH-03 | Phase 2: Taxonomy + Competitive Benchmark | Pending |
| COMP-01 | Phase 2: Taxonomy + Competitive Benchmark | Complete |
| COMP-02 | Phase 2: Taxonomy + Competitive Benchmark | Complete |
| COMP-03 | Phase 2: Taxonomy + Competitive Benchmark | Complete |
| COMP-04 | Phase 2: Taxonomy + Competitive Benchmark | Complete |
| SCORE-01 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-02 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-03 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-04 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-05 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-06 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-07 | Phase 3: Scoring System + Master Trigger Table | Pending |
| SCORE-08 | Phase 3: Scoring System + Master Trigger Table | Pending |
| TRIG-01 | Phase 3: Scoring System + Master Trigger Table | Pending |
| TRIG-02 | Phase 3: Scoring System + Master Trigger Table | Pending |
| TRIG-03 | Phase 3: Scoring System + Master Trigger Table | Pending |
| TRIG-04 | Phase 3: Scoring System + Master Trigger Table | Pending |
| CHAN-01 | Phase 3: Scoring System + Master Trigger Table | Pending |
| CHAN-02 | Phase 3: Scoring System + Master Trigger Table | Pending |
| CHAN-03 | Phase 3: Scoring System + Master Trigger Table | Pending |
| CHAN-04 | Phase 3: Scoring System + Master Trigger Table | Pending |
| MEAS-01 | Phase 4: Measurement + Final Recommendations | Pending |
| MEAS-02 | Phase 4: Measurement + Final Recommendations | Pending |
| MEAS-03 | Phase 4: Measurement + Final Recommendations | Pending |
| MEAS-04 | Phase 4: Measurement + Final Recommendations | Pending |
| MEAS-05 | Phase 4: Measurement + Final Recommendations | Pending |
| REC-01 | Phase 4: Measurement + Final Recommendations | Pending |
| REC-02 | Phase 4: Measurement + Final Recommendations | Pending |
| REC-03 | Phase 4: Measurement + Final Recommendations | Pending |
| REC-04 | Phase 4: Measurement + Final Recommendations | Pending |
| REC-05 | Phase 4: Measurement + Final Recommendations | Pending |

**Coverage:**
- v1 requirements: 46 total
- Mapped to phases: 46
- Unmapped: 0

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after roadmap creation*
