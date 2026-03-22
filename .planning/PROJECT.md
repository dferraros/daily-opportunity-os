# Playbook Maestro de Trigger Based Notifications — Bit2Me

## What This Is

Diseño completo del sistema de notificaciones basadas en triggers para Bit2Me: un exchange multi-producto (Brokerage, Pro, Earn, Card, Loan, Space Center, Pay, Wealth, Launchpad) con 1.8M de usuarios registrados y 23k MMU activos. El playbook cubre desde la taxonomía de triggers hasta fórmulas de scoring, arquitectura de datos, política anti-fatiga, compliance y roadmap de implementación. El output es un documento estratégico y técnico listo para ser ejecutado por los equipos de Growth, CRM, Product y Engineering.

## Core Value

Un sistema de notificaciones que aumenta reactivación, retención y revenue sin destruir deliverability, push permissions ni confianza del usuario.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Executive summary accionable con impacto de negocio estimado
- [ ] Mapa completo de productos Bit2Me con triggers por producto
- [ ] Benchmark competitivo: Coinbase, Binance, Kraken, Bitpanda, Revolut, Nexo
- [ ] Benchmark de CRM/push best practices (Braze, CleverTap, Iterable, Airship, MoEngage)
- [ ] Taxonomía maestra de triggers (6 familias: User Configured, Market, Behavioral, Lifecycle, Cross-sell, Risk)
- [ ] Sistema de elegibilidad por usuario, activo y producto
- [ ] Sistema de priorización con fórmulas concretas
- [ ] Sistema anti-fatiga con caps, cooldowns y supresiones
- [ ] 10+ fórmulas de scoring (Market Relevance, Fatigue Risk, Send Score final, etc.)
- [ ] Arquitectura de datos y tracking requerido
- [ ] Diseño de eventos y propiedades (event schema)
- [ ] Tabla maestra de triggers (30+ triggers con todas las columnas)
- [ ] Política de canales (push, in-app, email, SMS)
- [ ] Sistema de medición e incremental lift framework
- [ ] Roadmap de experimentos y lanzamiento (MVP 30d, V2 90d, V3 180d)
- [ ] Compliance checks (MiCA, CNMV, GDPR, ePrivacy)
- [ ] Recomendación final priorizada con Top 10 triggers y Top 10 NO lanzar

### Out of Scope

- Implementación técnica en CleverTap (configuración de journeys) — eso es ejecución posterior
- Diseño de copies específicos por cada trigger — se proveen plantillas, no copies finales
- Análisis de datos históricos internos de Bit2Me — se trabaja con benchmarks y estimaciones
- Integración con engineering/backend (BigQuery queries, API calls) — documentadas como dependencias, no implementadas

## Context

- **Plataforma**: Bit2Me exchange multi-producto. Usuarios: 1.8M total, 600k excluidos, 23k MMU, 72.4k dormant con balance (€19.5M AUC)
- **CRM stack**: CleverTap (journeys J1-J6), BigQuery (data layer), Qlik (analytics)
- **Lifecycle stages activos**: 13 etapas (EXCLUDED → CHURNED). M1 Retention: 0.12% actual vs 25% benchmark Coinbase
- **Canales disponibles**: Push, In-App, Email. SMS pendiente.
- **Productos activos**: Brokerage (simple buy/sell), Pro (order book), Earn, Card, Loan, Space Center (gamification), Pay, Launchpad, Wealth, API
- **Asset universe**: diferenciado en visible, holdable, tradable, eligible por producto
- **Compliance scope**: España y UE principalmente. Regulación: MiCA, CNMV, GDPR, ePrivacy Directive
- **Equipo CRM**: Katy (CleverTap), Diego (legal gate), Álvaro (BigQuery/data)
- **Context**: El brief original incluye esquemas completos de usuario (30+ campos), event data (40+ eventos), y campaign data para medición

## Constraints

- **Compliance**: Diego debe aprobar TODOS los copies antes de envío. MiCA prohíbe ciertos mensajes de tipo "investment advice" sin disclaimers. GDPR requiere consentimiento explícito por canal.
- **Tech stack**: CleverTap como CRM. BigQuery como fuente de datos. Cambios de arquitectura requieren Álvaro.
- **Push permissions**: La tasa de opt-in es un KPI crítico. Ninguna táctica puede sacrificar permisos por conversiones corto plazo.
- **Asset scope**: No todos los activos son tradables en Pro o elegibles para Earn — el playbook debe ser preciso sobre qué activos activan qué triggers.
- **No "investment advice"**: Las notificaciones de precio/mercado deben ser informativas, no recomendaciones de compra/venta.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Playbook como output primario vs implementación directa | Alinear a todos los equipos antes de ejecutar en CleverTap | — Pending |
| Benchmarks externos como proxy de verdad | No hay datos históricos de triggers internos disponibles | — Pending |
| Quality model profile (Opus) | Profundidad de análisis requerida justifica coste | — Pending |

---
*Last updated: 2026-03-22 after initialization*
